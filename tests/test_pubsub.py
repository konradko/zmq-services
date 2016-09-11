from zmqservices import pubsub, messages

from tests.utils import mock_zmq


class TestPublisher(object):

    def test_send(self):
        pubsub.Publisher(port='tcp://*:48640').send(
            message=messages.JSON(data='test')
        )


class TestSubscriber(object):

    def test_receive(self):
        with mock_zmq() as zmq_mock:
            topics = ('test', )
            publisher_address = 'tcp://localhost:48641'

            subscriber = pubsub.Subscriber(
                publishers=(publisher_address, ),
                topics=topics
            )

            message = messages.JSON(topic=topics[0], data='test')
            zmq_mock.recv.return_value = message.serialize()

            subscriber.receive()


class TestMessageForwarder(object):

    def test_receive(self):
        with mock_zmq() as zmq_mock:
            topics = ('test', )
            publisher_to_forward_address = 'tcp://localhost:48642'
            forwarder = pubsub.Publisher(port='tcp://*:48643')

            subscriber = pubsub.MessageForwarder(
                publisher=forwarder,
                publishers=(publisher_to_forward_address, ),
                topics=topics
            )

            message = messages.JSON(topic=topics[0], data='test')
            zmq_mock.recv.return_value = message.serialize()

            subscriber.receive()


class TestLastMessagePublisher(object):

    def test_send(self):
        pubsub.LastMessagePublisher(port='tcp://*:48644').send(
            message=messages.JSON(data='test')
        )


class TestLastMessageSubscriber(object):

    def test_receive(self):
        with mock_zmq() as zmq_mock:
            topics = ('test', )
            publisher_address = 'tcp://localhost:48645'

            subscriber = pubsub.LastMessageSubscriber(
                publishers=(publisher_address, ),
                topics=topics
            )

            message = messages.JSON(topic=topics[0], data='test')
            zmq_mock.recv.return_value = message.serialize()
            received = subscriber.receive()

            assert received.data == message.data
