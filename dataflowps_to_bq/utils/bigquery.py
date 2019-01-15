__author__ = 'rpereira'

import datetime
import json

from google.cloud import bigquery
from google.api_core.exceptions import *


class BigQueryDataSet(object):
    """
    BigQuery dataset object with functionality to create datasets and tables
    """
    def __init__(self, bq_client, logging_client=None):
        """
        :param bq_client: BigQuery Client
        :param logging_client: Stackdriver logging client
        """
        self.client = bq_client
        if logging_client:
            self.logging_client = logging_client
        else:
            self.logging_client = None
        self.dataset = None

    def create_bq_dataset(self, dataset_id, location="US"):
        """ Create a new BigQuery dataset in a project if it does not exist

        :param dataset_id: Name of dataset
        :param location: Dataset location
        :return: None
        """

        dataset_ref = self.client.dataset(dataset_id)

        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        self.dataset = dataset_ref

        try:
            dataset = self.client.create_dataset(dataset)  # API request
        except Conflict:
            if self.logging_client:
                self.logging_client.log_text("Dataset {} already exists.".format(dataset_id))

            print("Dataset {} already exists.".format(dataset_id))
        else:
            if self.logging_client:
                self.logging_client.log_text("Dataset {} created at {}."
                                    .format(dataset_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            print("Dataset {} created at {}.".format(dataset_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    def _get_field_schema(self, field):
        name = field['name']
        field_type = field['type']
        description = field['description']
        mode = field['mode']
        fields = field.get('fields', [])

        if fields:
            subschema = []
            for f in fields:
                fields_res = self._get_field_schema(f)
                subschema.append(fields_res)
        else:
            subschema = []

        field_schema = bigquery.SchemaField(name=name,
            field_type=field_type,
            description=description,
            mode=mode,
            fields=subschema
        )
        return field_schema

    def _parse_bq_json_schema(self, schema_filename):
        schema = []
        with open(schema_filename, 'r') as infile:
            jsonschema = json.load(infile)

        for field in jsonschema:
            schema.append(self._get_field_schema(field))

        return schema

    def _table_exists(self, table_id):
        """Check if a table exists in a dataset

        :param table_id: BigQuery table name
        :return:
        """
        tables = list(self.client.list_tables(self.dataset))

        if len(tables) == 0:
            return False
        else:
            count = 0
            for table in tables:
                if table.table_id == table_id:
                    count += 1
            if count > 0:
                return True
            else:
                False

    def create_table(self, table_id, schema_file, source_uri):
        """Creates a BigQuery table in a Dataset. If the table exists, it will be overwritten.

        :param table_id: BigQuery table name
        :param schema_file: Location of schema file
        :param source_uri: List of source URIs
        :return:
        """

        if self.dataset:
            if self._table_exists(table_id):
                table_ref = self.dataset.table(table_id)
                self.client.delete_table(table_ref)

            schema = self._parse_bq_json_schema(schema_file)
            table_ref = self.dataset.table(table_id)
            table = bigquery.Table(table_ref)

            external_config = bigquery.ExternalConfig('NEWLINE_DELIMITED_JSON')
            external_config.source_uris = source_uri
            external_config.schema = schema
            external_config.ignore_unknown_values = True
            table.external_data_configuration = external_config

            table = self.client.create_table(table)

            if self.logging_client:
                self.logging_client.log_text("Table created created at {}."
                                             .format(table_id, datetime.datetime.now()
                                             .strftime('%Y-%m-%d %H:%M:%S')))
            print("Table created created at {}.".format(table_id, datetime.datetime.now()\
                                                        .strftime('%Y-%m-%d %H:%M:%S')))
        else:
            print("Dataset is not initialized")


