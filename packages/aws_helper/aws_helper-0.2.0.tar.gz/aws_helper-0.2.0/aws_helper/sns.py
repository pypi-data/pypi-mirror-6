class SNSTopic(object):
    """ Helper for SNS Topic creation/management.

    Working with SNS topics is kind of annoying by default.  This provides a
    more simple interface for working with them.
    """
    def __init__(self, connection, topic_name):
        self._conn = connection
        self._topic_name = topic_name
        self._topic_arn = None

    def _setup_topic(self):
        if self._topic_arn:
            return

        conn = self._conn
        response = conn.create_topic(self._topic_name)['CreateTopicResponse']
        self._topic_arn = response['CreateTopicResult']['TopicArn']

    def publish(self, *args, **kwargs):
        self._setup_topic()
        return self._conn.publish(self._topic_arn, *args, **kwargs)

    def subscribe_sqs_queue(self, *args, **kwargs):
        self._setup_topic()
        return self._conn.subscribe_sqs_queue(self._topic_arn, *args, **kwargs)
