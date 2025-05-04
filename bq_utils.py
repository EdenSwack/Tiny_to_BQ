from google.cloud import bigquery


def remove_existing_hash_date_rows(df, url_hashes, project_id, dataset_id, table_id):
    """
    Removes rows from df that already exist in BigQuery based on (hash, date).
    """
    print("Checking for already uploaded (hash, date) combinations in BigQuery...")
    
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    query = f"""
        SELECT `tag`, `record_date`
        FROM `{table_ref}`
        WHERE `tag` IN UNNEST(@hashes)
    """


    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("hashes", "STRING", url_hashes)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    existing_pairs = query_job.result().to_dataframe()

    print(f"Found {len(existing_pairs)} existing (hash, date) rows in BigQuery.")

    if not existing_pairs.empty:
        df = df.merge(existing_pairs, left_on=["hash", "date"], right_on=["tag", "record_date"], how="left", indicator=True)
        df = df[df["_merge"] == "left_only"]
        df = df.drop(columns=["_merge", "tag", "record_date"])
        print(f"Remaining new rows to upload after filtering: {len(df)}")
    else:
        print("No duplicates found, all rows are new.")

    return df