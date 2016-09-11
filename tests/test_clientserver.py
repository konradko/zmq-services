from zmqservices import clientserver, messages

from tests.utils import mock_zmq


class TestServer(object):
    message = messages.JSON(data='test')
    port = 'tcp://*:{}'

    def test_respond(self):
        with mock_zmq():
            clientserver.Server(
                port=self.port.format(48650)
            ).respond(self.message)

    def test_receive(self):
        with mock_zmq() as zmq_mock:
            zmq_mock.recv.return_value = self.message.serialize()

            clientserver.Server(port=self.port.format(48651)).receive()


class TestClient(object):
    message = messages.JSON(data='test')
    servers = ('tcp://localhost:48640', )

    def test_connect(self):
        clientserver.Client(servers=self.servers).connect(self.servers[0])

    def test_process_response(self):
        clientserver.Client(servers=self.servers).process_response(
            self.message.serialize()
        )

    def test_request(self):
        with mock_zmq() as zmq_mock:
            message = messages.JSON(data='test')
            zmq_mock.recv.return_value = message.serialize()

            clientserver.Client(servers=self.servers).request(self.message)
