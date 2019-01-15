__author__ = 'rpereira'

import os
import datetime

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials


def launch_ps_to_gcs(topic, bucket_name, output_prefix, output_suffix, gcsPath='gs://dataflow-templates/latest/Cloud_PubSub_to_GCS_Text'):
    """Lauch DataFlow template job to import data from PubSub into a GCS bucket

    :param topic: PubSub topic
    :param bucket_name: The path and filename prefix for writing output files. This value must end in a slash.
    :param output_prefix: The prefix to place on each windowed file. For example, output-
    :param output_suffix: The suffix to place on each windowed file, typically a file extension such as .txt or .csv.
    :return: None
    """

    if os.environ["project_id"]:
        credentials = GoogleCredentials.get_application_default()
        service = build('dataflow', 'v1b3', credentials=credentials)
        project_id = os.environ.get("project_id")
        print(project_id)

        input_topic = "projects/{project_id}/topics/{topic}".format(project_id=project_id, topic=topic)
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        jobname = "Import from topic{inputTopic} at {time}"\
                       .format(inputTopic=input_topic, time=time)

        body = {
           "jobName": "{jobname}".format(jobname=jobname),
           "parameters": {
               "inputTopic": input_topic,
               "outputDirectory": "gs://{bucket_name}/output/".format(bucket_name=bucket_name),
               "outputFilenamePrefix": output_prefix,
               "outputFilenameSuffix": output_suffix,
           },
           "environment": {"zone": "us-central1-f"}
        }

        request = service.projects().templates().launch(projectId=project_id, gcsPath=gcsPath, body=body)
        response = request.execute()

        print(response)

        return {"outputDirectory": "gs://{bucket_name}/output/".format(bucket_name=bucket_name),
               "outputFilenamePrefix": output_prefix,
               "outputFilenameSuffix": output_suffix}

