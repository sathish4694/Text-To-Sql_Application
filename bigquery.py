# bigquery.py
from google.cloud import bigquery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to run queries on BigQuery
def run_bigquery_query(sql_query):
    try:
        # Set path to Google Cloud credentials (service account key)
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Initialize BigQuery client
        client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))

        # Run the query
        query_job = client.query(sql_query)  # Make an API request
        results = query_job.result()  # Wait for query to complete

        # Fetch and return results
        output = [dict(row.items()) for row in results]
        return output

    except Exception as e:
        raise Exception(f"Error running query on BigQuery: {e}")
