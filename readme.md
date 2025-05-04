# Tiny.cc URL Analytics Collector

A Python application that fetches analytics data for shortened URLs from the Tiny.cc API and stores it in Google BigQuery for further analysis.

## Overview

This tool automates the collection of click statistics for Tiny.cc URLs. It:

1. Fetches all shortened URLs from your Tiny.cc account
2. Filters URLs created within the last 12 months
3. Retrieves detailed click statistics for each URL
4. Uploads the data to Google BigQuery
5. Tracks which URLs have been processed to avoid duplicates

## Features

- **Pagination Support**: Handles large collections of URLs by paginating through the API
- **Date-Based Filtering**: Separates URLs into "recent" (last 4 months) and "older" (last 12 months) groups
- **Deduplication**: Avoids reuploading data that's already in BigQuery
- **Progress Tracking**: Maintains lists of processed URLs and URLs without click data
- **Error Handling**: Gracefully handles API errors and rate limits

## Prerequisites

- Python 3.6+
- Google Cloud Platform account with BigQuery access
- Tiny.cc Pro account with API access

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/tinycc-analytics-collector.git
   cd tinycc-analytics-collector
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your Tiny.cc API key:
   ```
   TINYCC_API_KEY=your_api_key_here
   ```

4. Set up Google Cloud credentials:
   - Create a service account with BigQuery access
   - Download the JSON key file
   - Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to point to your key file:
     ```
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
     ```

## Configuration

Edit `config.py` to set your specific configuration:

- `TINY_USERNAME`: Your Tiny.cc username
- `BASE_URL`: The Tiny.cc API base URL (shouldn't need to change)
- `BQ_PROJECT_ID`: Your Google Cloud project ID
- `BQ_DATASET_ID`: The BigQuery dataset to use
- `BQ_TABLE_ID`: The BigQuery table to store the data

## Usage

Run the main script to fetch and upload URL statistics:

```
python main.py
```

### Advanced Usage

To only fetch the list of URLs without processing stats:

```
python fetch_hashes.py
```

This will create `older_hashes.txt` and `recent_hashes.txt` files.

## Data Structure

The data uploaded to BigQuery has the following schema:

| Column | Description |
| ------ | ----------- |
| tag | The Tiny.cc URL hash/identifier |
| record_date | The date of the click statistics |
| daily_total_clicks | Total clicks for that specific date |
| daily_unique_clicks | Unique clicks for that specific date |
| total_clicks | Cumulative total clicks for the URL |
| unique_clicks | Cumulative unique clicks for the URL |

## Project Structure

- `main.py`: Main script to run the full pipeline
- `fetch_hashes.py`: Utilities to fetch and filter URL hashes from Tiny.cc
- `config.py`: Configuration variables
- `bq_utils.py`: BigQuery helper functions
- `requirements.txt`: Python dependencies
- `hashes_temp_storage/`: Directory storing tracking files for processed URLs

## Temporary Files

The script maintains several files to track progress:
- `uploaded_hashes.txt`: URLs that have been successfully processed
- `empty_hashes.txt`: URLs that returned no click data
- `older_hashes.txt`: All URLs from the last 12 months
- `recent_hashes.txt`: URLs from the last 4 months

## Limitations

- The Tiny.cc API has rate limits. If you hit them, the script will stop processing.
- Only collects data for URLs created in the last 12 months.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Acknowledgements

- Tiny.cc for providing the API
- Google Cloud Platform for BigQuery services