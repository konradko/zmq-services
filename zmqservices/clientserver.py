import zmq

from zmqservices import messages, logger
from zmqservices.utils import Socket, BoundSocket


class Server(BoundSocket):
    """ZMQ server"""
    socket_type = zmq.REP
    port = None

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        logger.info("Started a server on port '{}'".format(self.port))

    def respond(self, response):
        """Respond to a request

        Args:
            request (Message): Request to respond to
        """
        logger.debug("Sending response '{}'".format(response.uuid))
        self.socket.send(response.serialize())
        logger.debug("Response '{}' sent".format(response.uuid))

    def receive(self):
        """Returns a single message from the publishers

        Returns:
            Message: deserialized message
        """
        logger.debug("Waiting for requests...")
        request = self.socket.recv()
        return messages.parse(raw_message=request)


class Client(Socket):
    """ZMQ client"""
    socket_type = zmq.REQ

    def __init__(self, servers, *args, **kwargs):
        """Init client

        Args:
            servers ([str]): List of "<host>:<port>" server addresses
        """
        super(Client, self).__init__(*args, **kwargs)

        for server in servers:
            self.connect(server)

    def connect(self, server):
        logger.info("Connecting to server '{}'".format(server))
        self.socket.connect(server)

    def process_response(self, response):
        logger.debug("Processing a response...")
        return messages.parse(raw_message=response)

    def request(self, message):
        """Returns a single message from the servers

        Returns:
            Message: deserialized message
        """
        logger.debug("Sending request...")
        self.socket.send(message.serialize())
        logger.debug("Getting response...")
        response = self.socket.recv()
        logger.debug("Processing response...")
        return self.process_response(response)
