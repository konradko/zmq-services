import zmq

from zmqservices import messages, logger


class Socket(object):

    @staticmethod
    def get_socket(socket_type):
        context = zmq.Context()
        return context.socket(socket_type)


class Publisher(Socket):
    """ZMQ publisher"""

    def __init__(self, port):
        """Init publisher

        Args:
            port (int): Port to bind on
        """
        self.socket = self.get_socket(zmq.PUB)
        self.port = port
        self.socket.bind(port)
        logger.info("Started a publisher on port '{}'".format(self.port))

    def send(self, message):
        """Publish topic data

        Args:
            message (Message): Message to send
        """
        logger.debug("Sending message '{}'' to topic '{}'".format(
            message.uuid, message.topic
        ))
        self.socket.send(message.serialize())
        logger.debug("Message '{}'' sent".format(message.uuid))


class Subscriber(Socket):
    """ZMQ subscriber"""

    def __init__(self, publishers, topics):
        """Init subscriber

        Args:
            publishers ([str]): List of "<host>:<port>" publisher addresses
            topics ([str]): List of topics to subscribe to
        """
        self.socket = self.get_socket(zmq.SUB)

        for publisher in publishers:
            self.connect(publisher)

        for topic in topics:
            self.subscribe(topic)

    def connect(self, publisher):
        logger.info("Connecting to publisher '{}'".format(publisher))
        self.socket.connect(publisher)

    def subscribe(self, topic):
        """Subscribe to a topic

        Args:
            topic (str): Topic to subscribe to
        """
        logger.info("Subscribing to topic '{}'".format(topic))
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    def receive(self):
        """Returns a single message from the publishers

        Returns:
            Message: deserialized message
        """
        logger.debug("Getting a message...")
        message = self.socket.recv()
        return messages.parse(raw_message=message)


class MessageForwarder(Subscriber):

    def __init__(self, publisher, *args, **kwargs):
        super(MessageForwarder, self).__init__(*args, **kwargs)
        self.publisher = publisher

    def read(self, *args, **kwargs):
        """Returns a single message from the publishers

        Returns:
            Message: deserialized message
        """
        message = super(MessageForwarder, self).read(*args, **kwargs)
        self.forward(message)
        return message

    def forward(self, message):
        """Forward a message

        Args:
            message (Message): Message to forward
        """
        logger.debug("Forwarding message '{}'".format(message.uuid))
        self.publisher.send(message)


class LastMessageMixin(object):

    @staticmethod
    def get_socket(socket_type):
        context = zmq.Context()
        socket = context.socket(socket_type)
        socket.setsockopt(zmq.CONFLATE, 1)
        return socket


class LastMessagePublisher(LastMessageMixin, Publisher):
    """ZMQ publisher sending only the latest message"""
    pass


class LastMessageSubscriber(LastMessageMixin, Subscriber):
    """ZMQ subscriber reading only the latest message"""
    pass
