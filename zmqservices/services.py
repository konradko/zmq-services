from multiprocessing import Process

from zmqservices import pubsub, logger


class Resource(object):

    def run():
        raise NotImplementedError()


class Service(object):
    required_attributes = ['name', 'resource']

    def __init__(self, *args, **kwargs):
        for attr in self.required_attributes:
            if kwargs.get(attr):
                setattr(self, attr, kwargs.pop(attr))

        if not all((getattr(self, attr) for attr in self.required_attributes)):
            raise NotImplementedError(
                "Not all required attributes set: {}".format(
                    ", ".join(self.required_attributes)
                )
            )

    def start(self):
        if self.running:
            logger.warning("Service already running")
            return

        logger.info("Starting {} service...".format(self.name))
        self.process = Process(target=self.run_resource)
        self.process.start()
        self.running = True

    def run_resource(self):
        raise NotImplementedError()


class PublisherResource(Resource):
    topics = {}

    def __init__(self, publisher, *args, **kwargs):
        self.publisher = publisher


class PublisherService(Service):
    name = 'publisher'
    resource = PublisherResource
    publisher = pubsub.Publisher
    subscriber = pubsub.Subscriber

    def __init__(self, *args, **kwargs):
        self.required_attributes += ['address', 'port']
        super(PublisherService, self).__init__(*args, **kwargs)

    @classmethod
    def get_subscriber(cls, publisher_address=None):
        return cls.subscriber(
            publishers=(publisher_address or cls.address, ),
            topics=cls.resource.topics.values(),
        )

    @classmethod
    def get_publisher(cls):
        return cls.publisher(port=cls.port)

    def run_resource(self):
        resource_instance = self.resource(publisher=self.get_publisher())
        resource_instance.run()
