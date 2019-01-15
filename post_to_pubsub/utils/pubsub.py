__author__ = 'rpereira'

import json
import datetime


def create_topic(publisher, topic_name, logging_client):
    """Create PubSub topic

    :param publisher: Publisher client
    :param topic_name: PubSub topic name
    :param logging_client: Logging client
    :return: None
    """

    topic = publisher.create_topic(topic_name)
    logging_client.log_text('Topic created: {} at {}.'.format(topic_name, str(datetime.datetime.now()
                                                                             .strftime('%Y-%m-%d %H:%M:%S'))))


def publish_to_topic(publisher, topic_name, message, logging_client):
    """Publish message json to PubSub topic

    :param publisher: Publisher client
    :param topic_name: PubSub topic name
    :param message: Message dictionary
    :param logging_client: Logging client
    :return: None
    """

    publisher.publish(topic_name, str.encode(json.dumps(message)))
    logging_client.log_text("Published message to topic {} at {}.".format(topic_name, str(datetime.datetime.now()
                                                                             .strftime('%Y-%m-%d %H:%M:%S'))))


