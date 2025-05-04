import os
import requests
import base64
from dotenv import load_dotenv
import datetime
from config import TINY_USERNAME, BASE_URL

load_dotenv()

API_KEY = os.getenv("TINYCC_API_KEY")

def load_fetched_hashes(filepath):
    filepath="hashes_temp_storage/"+filepath+".txt"
    print("local file path: "+ filepath)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            hashes = {line.strip() for line in f if line.strip()}
        print(f"Loaded {len(hashes)} already fetched hashes from {filepath}.")
        return hashes
    else:
        print(f"No existing {filepath} found. Starting fresh.")
        return set()

def save_uploaded_hashes(hashes, filepath="uploaded_hashes.txt"):
    """
    Append newly fetched hashes to the uploaded.txt file.
    Avoid duplicates if possible.
    """
    if not hashes:
        print("No new hashes to save.")
        return

    with open(filepath, "a") as f:
        for h in hashes:
            f.write(f"{h}\n")

    print(f"Saved {len(hashes)} new hashes to {filepath}.")


def fetch_all_hashes():
    print("Fetching all shortened URLs (with pagination)...")
    
    credentials = f"{TINY_USERNAME}:{API_KEY}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Tinycc-Client/1.0"
    }
    URL = BASE_URL + "urls/"

    all_url_entries = []
    offset = 0
    page_size = 50

    while True:
        url = f"{URL}?offset={offset}"
        response = requests.get(url, headers=headers, allow_redirects=False)

        if response.status_code == 200:
            data = response.json()
            url_entries = data.get("urls", [])
            if not url_entries:
                print(f"No more URLs returned at offset {offset}.")
                break  # Exit loop if no more data
            all_url_entries.extend(url_entries)
            print(f"Fetched {len(url_entries)} URLs at offset {offset}. Total so far: {len(all_url_entries)}")
            offset += page_size  # Next page
        else:
            print(f"Failed to fetch URLs at offset {offset}. Status Code: {response.status_code}")
            print(response.text)
            break  # Exit loop on error

    print(f"Finished fetching all shortened URLs. Total fetched: {len(all_url_entries)}")
    return all_url_entries

def split_hashes_by_date(url_entries):
    now = datetime.datetime.now()
    twelve_months_ago = now - datetime.timedelta(days=365)
    four_months_ago = now - datetime.timedelta(days=120)

    recent_hashes = []
    older_hashes = []

    for entry in url_entries:
        created_str = entry.get("created")
        if created_str:
            created = datetime.datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
            hash_val = entry.get("hash")
            if created >= twelve_months_ago:
                older_hashes.append(hash_val)
                if created >= four_months_ago:
                    recent_hashes.append(hash_val)

    return older_hashes, recent_hashes

def save_empty_hashes(empty_hashes, filepath="empty_hashes.txt"):
    if not empty_hashes:
        return

    existing = set()
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            existing = {line.strip() for line in f}

    new_hashes = [h for h in empty_hashes if h not in existing]

    if new_hashes:
        with open(filepath, "a") as f:
            for h in new_hashes:
                f.write(f"{h}\n")
        print(f"Saved {len(new_hashes)} new empty hashes to {filepath}")
    else:
        print("No new empty hashes to save.")



if __name__ == "__main__":
    url_entries = fetch_all_hashes()
    older_hashes, recent_hashes = split_hashes_by_date(url_entries)

    print(f"\nHashes created in last 12 months: {len(older_hashes)}")
    print(f"Hashes created in last 4 months (for daily refresh): {len(recent_hashes)}")

    # Save hashes to local files if needed
    with open("older_hashes.txt", "w") as f:
        for h in older_hashes:
            f.write(f"{h}\n")

    with open("recent_hashes.txt", "w") as f:
        for h in recent_hashes:
            f.write(f"{h}\n")
