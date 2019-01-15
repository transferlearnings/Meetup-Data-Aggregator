__author__ = 'rpereira'

import os

from google.cloud import bigquery
from google.cloud import logging
from google.cloud import storage
from google.api_core.exceptions import *


from utils.bigquery import *
from utils.dataflow import *


if __name__ == "__main__":


    bucket_name = "meetup_stream_example"

    # Set up Storage client
    client = storage.Client()
    # Set up BigQuery Client
    bq_client = bigquery.Client()
    # Set up logging client
    logging_client = logging.Client().logger("post_to_pubsub")

    # Create bucket if it does not exist
    try:
        client.create_bucket(bucket_name=bucket_name)
    except Conflict:
        print("Bucket {} already exists".format(bucket_name))
    else:
        print("Bucket {} created".format(bucket_name))

    #Initialize dataset
    dataset = BigQueryDataSet(bq_client=bq_client, logging_client=logging_client)

    dataset_id = "meetup_stream_example"
    #Create dataset
    dataset.create_bq_dataset(dataset_id=dataset_id, location="US")

    for items in os.listdir("./bq_table_schema"):
        table_id = items.split(".")[0]
        schema_file = "/".join(["./bq_table_schema", items])
        gcs_info = launch_ps_to_gcs(topic=table_id, bucket_name=bucket_name,
                        output_prefix=table_id + "---", output_suffix=".txt")
        dataset.create_table(table_id=table_id, schema_file=schema_file,
                             source_uri=[gcs_info['outputDirectory']
                                         + gcs_info['outputFilenamePrefix'] +
                                         "*"+gcs_info['outputFilenameSuffix']])



