__author__ = 'rpereira'

import requests
from requests.exceptions import ChunkedEncodingError, ConnectionError, ConnectTimeout
import json

import datetime


def read_stream_chunk(url, logging_client):
    """ Read and yield chunk stream json data from the given MeetUp URL

    :param url: Chunk stream URL
    :param logging_client: StackDriver logging client
    :return: MeetUp dictionary object
    """

    while True:
        try:
            with requests.get(url, stream=True) as r:
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        yield json.loads(decoded_line)
        except (ChunkedEncodingError, ConnectionError, ConnectTimeout):
            logging_client.log_text(
                "Streaming error at {}".format(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))))
            continue

