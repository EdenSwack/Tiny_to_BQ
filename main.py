import os
import requests
import pandas as pd
import base64
from google.cloud import bigquery
from dotenv import load_dotenv

from fetch_hashes import fetch_all_hashes, split_hashes_by_date, load_fetched_hashes, save_uploaded_hashes, save_empty_hashes
from config import BQ_PROJECT_ID, BQ_DATASET_ID, BQ_TABLE_ID, BASE_URL, TINY_USERNAME

load_dotenv()

API_KEY = os.getenv("TINYCC_API_KEY")

def get_tinycc_stats(hash_value):
    print(f"Fetching stats for hash: {hash_value}...")
    STATS_URL = BASE_URL + "stats/"
    url = f"{STATS_URL}{hash_value}"

    credentials = f"{TINY_USERNAME}:{API_KEY}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Tinycc-Client/1.0"
    }

    response = requests.get(url, headers=headers, allow_redirects=False)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {hash_value}: Status Code {response.status_code}")
        print(response.text)
        return None

def parse_stats(hash_value, json_data):
    records = []
    stats = json_data.get("stats", [])
    for stat in stats:
        total_clicks = stat.get("total_clicks")
        unique_clicks = stat.get("unique_clicks")
        daily_clicks = stat.get("daily_clicks", {})
        for date, clicks in daily_clicks.items():
            record = {
                "hash": hash_value,
                "date": date,
                "daily_total_clicks": clicks.get("total", 0),
                "daily_unique_clicks": clicks.get("unique", 0),
                "total_clicks": total_clicks,
                "unique_clicks": unique_clicks
            }
            records.append(record)
    return records

def main(url_hashes):
    all_records = []
    empty_hashes = []
    successful_hashes = []

    for url_hash in url_hashes:
        json_data = get_tinycc_stats(url_hash)
        if json_data:
            records = parse_stats(url_hash, json_data)
            if records:  # Only if stats were found
                all_records.extend(records)
                successful_hashes.append(url_hash)
            else:
                print(f"No stats for {url_hash}")
                empty_hashes.append(url_hash)

        else:
            print("API Error occured, stoping get stats")
            break
    save_empty_hashes(empty_hashes)

    if not all_records:
        print("No new stats to upload.")
        return []

    df = pd.DataFrame(all_records)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.drop_duplicates(subset=['hash', 'date'])
    df = df.rename(columns={"hash": "tag", "date": "record_date"})


    print(f"Uploading {len(df)} rows to BigQuery...")

    client = bigquery.Client(project=BQ_PROJECT_ID)
    table_ref = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}"
    job = client.load_table_from_dataframe(df, table_ref)
    job.result()

    print(f"Uploaded {len(df)} rows successfully.")
    return successful_hashes

if __name__ == "__main__":
    # Step 1: Fetch all hashes (with pagination)
    url_entries = fetch_all_hashes()

    # Step 2: Split into older and recent
    older_hashes, recent_hashes = split_hashes_by_date(url_entries)

    print(f"Total hashes (last 12 months): {len(older_hashes)}")
    print(f"Recent hashes (last 4 months): {len(recent_hashes)}")

    # Step 3: Load already uploaded hashes
    already_uploaded = load_fetched_hashes(filepath="uploaded_hashes")
    empty_hashes=load_fetched_hashes(filepath="empty_hashes")

    # Step 4: Find hashes we still need to fetch
    hashes_to_fetch = [h for h in older_hashes if h not in already_uploaded and h not in empty_hashes]
    print(f"Hashes to fetch now (new): {len(hashes_to_fetch)}")

    # Step 5: Fetch stats and upload
    successful_hashes = main(hashes_to_fetch)

    # Step 6: Save only successful uploads
    save_uploaded_hashes(successful_hashes)
