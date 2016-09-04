from zmqservices import pubsub


class TestPublisher(object):
    publisher = pubsub.Publisher(port='tcp://*:48640')

    def test_send(self):
        self.publisher.send()


class TestSubscriber(object):

    def __init__(self):
        self.topics = ('test', )
        self.publishers = (pubsub.Publisher(port='tcp://*:48641'), )
        self.subscriber = pubsub.Subscriber(
            publishers=self.publishers,
            topics=self.topics
        )

    def test_connect(self):
        self.subscriber.connect()

    def test_subscribe(self):
        self.subscriber.subscribe()

    def test_receive(self):
        self.subscriber.receive()


class TestMessageForwarder(object):

    def __init__(self):
        self.topics = ('test', )
        self.publisher = pubsub.Publisher(port='tcp://*:48642')
        self.publishers = (pubsub.Publisher(port='tcp://*:48643'), )
        self.message_forwarder = pubsub.MessageForwarder(
            publisher=self.publisher,
            publishers=self.publishers,
            topics=self.topics
        )

    def test_read(self):
        self.message_forwarder.read()

    def test_forward(self):
        self.message_forwarder.forward()


class TestLastMessagePublisher(object):
    publisher = pubsub.LastMessagePublisher(port='tcp://*:48644')

    def test_send(self):
        self.publisher.send()


class TestLastMessageSubscriber(object):
    def __init__(self):
        self.topics = ('test', )
        self.publishers = (pubsub.Publisher(port='tcp://*:48645'), )
        self.subscriber = pubsub.Subscriber(
            publishers=self.publishers,
            topics=self.topics
        )

    def test_receive(self):
        self.subscriber.receive()
