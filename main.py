import os
from google.cloud import bigquery
from google.cloud import storage

# Set the BigQuery dataset and table names
BQ_DATASET_NAME = 'my_dataset'
BQ_TABLE_NAME = 'my_table'

# Define the Cloud Function entry point
def moveDataToBigQuery(event, context):
    # Get the file name and bucket name from the GCS event data
    file_name = event['name']
    bucket_name = event['bucket']

    # Set up the GCS and BigQuery clients
    storage_client = storage.Client()
    bq_client = bigquery.Client()

    # Get the GCS bucket and file objects
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(file_name)

    # Read the data from the GCS file
    data = blob.download_as_string()

    # Parse the data as a string and split it into rows
    rows = data.decode('utf-8').splitlines()

    # Create the BigQuery table schema
    table_ref = bq_client.dataset(BQ_DATASET_NAME).table(BQ_TABLE_NAME)
    table = bigquery.Table(table_ref)
    table.schema = [
        bigquery.SchemaField('column1', 'STRING'),
        bigquery.SchemaField('column2', 'INTEGER'),
        # Add more columns as needed
    ]
    table.create()

    # Insert the data into the BigQuery table
    errors = bq_client.insert_rows(table, [row.split(',') for row in rows])

    if errors:
        print('Encountered errors while inserting rows: {}'.format(errors))
    else:
        print('Successfully inserted rows into BigQuery.')

# For local testing
if __name__ == '__main__':
    event = {'name': 'test_file.csv', 'bucket': 'my-gcs-bucket'}
    context = {}
    moveDataToBigQuery(event, context)

