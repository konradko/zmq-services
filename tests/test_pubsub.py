from zmqservices import pubsub, messages


class TestPublisher(object):

    def test_send(self):
        pubsub.Publisher(port='tcp://*:48640').send(
            message=messages.JSON(data='test')
        )


class TestSubscriber(object):
    topics = ('test', )
    publisher = pubsub.Publisher(port='tcp://*:48641')
    publisher_address = 'tcp://localhost:48641'

    def test_receive(self):
        subscriber = pubsub.Subscriber(
            publishers=(self.publisher_address, ),
            topics=self.topics
        )

        self.publisher.send(
            message=messages.JSON(topic='test', data='test')
        )

        subscriber.receive()


class TestMessageForwarder(object):
    topics = ('test', )
    publisher_to_forward = pubsub.Publisher(port='tcp://*:48642')
    publisher_to_forward_address = 'tcp://localhost:48642'
    forwarder = pubsub.Publisher(port='tcp://*:48643')

    def test_receive(self):
        subscriber = pubsub.MessageForwarder(
            publisher=self.forwarder,
            publishers=(self.publisher_to_forward_address, ),
            topics=self.topics
        )

        self.publisher_to_forward.send(
            message=messages.JSON(topic='test', data='test')
        )

        subscriber.receive()


class TestLastMessagePublisher(object):
    publisher = pubsub.LastMessagePublisher(port='tcp://*:48644')

    def test_send(self):
        self.publisher.send(message=messages.JSON(data='test'))


class TestLastMessageSubscriber(object):
    topics = ('test', )
    publisher = pubsub.Publisher(port='tcp://*:48645')
    publisher_address = 'tcp://localhost:48645'

    def test_receive(self):
        subscriber = pubsub.LastMessageSubscriber(
            publishers=(self.publisher_address, ),
            topics=self.topics
        )

        message = messages.JSON(topic='test', data='test')
        self.publisher.send(
            message=message
        )

        message.data = 'test2'

        self.publisher.send(
            message=message
        )

        received = subscriber.receive()

        assert received.data == message.data
