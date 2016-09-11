from zmqservices import services, messages


class TestService(object):
    service = services.Service(name='test', resource=services.Resource)

    def test_start(self):
        self.service.start()


class TestPublisherService(object):
    service = services.PublisherService(
        name='test', resource=services.PublisherResource,
        address='tcp://localhost:48660', port='tcp://*:48660'
    )

    def test_get_subscriber(self):
        self.service.get_subscriber(publisher_address=self.service.address)

    def test_get_publisher(self):
        self.service.get_publisher(publisher_port=self.service.port)


class TestServerService(object):
    service = services.ServerService(
        name='test', resource=services.ServerResource,
        address='tcp://localhost:48661', port='tcp://*:48661'
    )

    def test_get_client(self):
        self.service.get_client(server_address=self.service.address)

    def test_get_server(self):
        self.service.get_server(server_port=self.service.port)


class TestJsonrpcServerResource(object):
    request = messages.JSON(data={'method': 'test', 'params': True})
    resource = services.JsonrpcServerResource(
        server=services.JsonrpcServer(
            address='tcp://localhost:48662', port='tcp://*:48662',
            endpoints={
                'test': lambda x: True if x is True else False
            }
        )
    )
    resource.test = lambda x: True if x is True else False

    def test_parse_jrpc(self):
        self.resource.parse_jrpc(request=self.request)

    def test_process_request(self):
        self.resource.process_request(request=self.request)
