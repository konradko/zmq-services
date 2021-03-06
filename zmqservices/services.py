from multiprocessing import Process

from zmqservices import messages, pubsub, clientserver, logger
from zmqservices.utils import RequiredAttributesMixin


class Resource(object):

    def run(self):
        raise NotImplementedError()


class Service(RequiredAttributesMixin):
    required_attributes = ('name', 'resource')
    running = False
    # daemonic process is not allowed to create child processes and when main
    # process exit it attempts to terminate all of its daemonic child processes
    daemon = False

    def start(self):
        if self.running:
            logger.warning("Service already running")
            return

        logger.info("Starting {} service...".format(self.name))
        self.process = Process(target=self.run_resource)

        if self.daemon:
            self.process.daemon = True

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
    address = None
    port = None

    def __init__(self, *args, **kwargs):
        self.required_attributes = self.required_attributes + (
            'address', 'port'
        )
        super(PublisherService, self).__init__(*args, **kwargs)

    @classmethod
    def get_subscriber(cls, publisher_address=None):
        return cls.subscriber(
            publishers=(publisher_address or cls.address, ),
            topics=cls.resource.topics.values(),
        )

    @classmethod
    def get_publisher(cls, publisher_port=None):
        return cls.publisher(port=publisher_port or cls.port)

    def run_resource(self):
        resource_instance = self.resource(publisher=self.get_publisher())
        resource_instance.run()


class ServerResource(Resource):

    def __init__(self, server, *args, **kwargs):
        self.server = server

    def process_request(self, request):
        raise NotImplementedError()

    def run(self):
        while True:
            request = self.server.receive()
            response = self.process_request(request)
            self.server.respond(response)


class ServerService(Service):
    name = 'server'
    resource = ServerResource
    server = clientserver.Server
    client = clientserver.Client
    address = None
    port = None

    def __init__(self, *args, **kwargs):
        self.required_attributes = self.required_attributes + (
            'address', 'port'
        )
        super(ServerService, self).__init__(*args, **kwargs)

    @classmethod
    def get_client(cls, server_address=None):
        return cls.client(
            servers=(server_address or cls.address, ),
        )

    @classmethod
    def get_server(cls, server_port=None):
        return cls.server(port=server_port or cls.port)

    def run_resource(self):
        resource_instance = self.resource(server=self.get_server())
        resource_instance.run()


class JsonrpcServerResource(ServerResource):
    # {<method name>: <params validator>}
    endpoints = {}

    def parse_jrpc(self, request):
        method = request.data.get('method')
        params = request.data.get('params', {})
        error = None

        if method in self.endpoints:
            # validate params
            if not self.endpoints[method](params):
                error = 'Invalid params'
        else:
            error = 'Invalid method'

        return method, params, error

    def process_request(self, request):
        method, params, error = self.parse_jrpc(request)

        if not error:
            response_data = getattr(self, method)(**params)
        else:
            response_data = error

        return messages.JSON(data=response_data)


class JsonrpcServer(ServerService):
    name = 'jsonrpc_server'
    resource = JsonrpcServerResource
