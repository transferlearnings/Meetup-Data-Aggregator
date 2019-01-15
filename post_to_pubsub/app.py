__author__ = 'rpereira'

import datetime
import threading
import json
import os
from requests.exceptions import ChunkedEncodingError, ConnectionError, ConnectTimeout

from google.cloud import pubsub_v1
from google.cloud import logging

from utils.pubsub import *
from utils.stream import *


def run_app(url, publisher, topic_name, logging_client):
    """Run application

    :param url: Chunk stream URL
    :param publisher: Publisher client
    :param topic_name: PubSub topic name
    :param logging_client: Logging client
    :return:
    """

    topic = create_topic(publisher, topic_name, logging_client)

    stream = read_stream_chunk(url, logging_client)
    for items in stream:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mtime = items["mtime"]

        try:
            publish_to_topic(publisher, topic_name, items, logging_client)
        except (ConnectionError, ConnectTimeout, ChunkedEncodingError):
            logging_client.log_text("Failed to write to topic {} at {}.".format(topic_name, current_time))

            url = url.split("?")[0]
            if url == "http://stream.meetup.com/2/open_venues":
                url = url + "?trickle&since_mtime={}".format(str(mtime))
            else:
                url = url + "?since_mtime={}".format(str(mtime))
            stream = read_stream_chunk(url, logging_client)
            continue
        else:
            logging_client.log_text("Wrote to topic {} at {}.".format(topic_name, current_time))


if __name__ == "__main__":

    # Set up publisher client
    publisher = pubsub_v1.PublisherClient()

    # Set up logging client
    logging_client = logging.Client().logger("post_to_pubsub")

    # Open topic:url file
    with open('config.json') as f:
        data = list(json.load(f).items())

    # Create threads
    threads = [
        threading.Thread(target=run_app, args=(x[1], publisher, 'projects/{project_id}/topics/{topic}'\
                                               .format(project_id=os.environ.get('project_id'), topic=x[0]),
                                               logging_client)) for x in data]
    # Run Threads
    for thread in threads:
        thread.start()

