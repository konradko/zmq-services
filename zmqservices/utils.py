import zmq


class RequiredAttributesMixin(object):
    required_attributes = []

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


class Socket(RequiredAttributesMixin):
    required_attributes = ['socket_type']

    def __init__(self, *args, **kwargs):
        super(Socket, self).__init__(*args, **kwargs)
        self.socket = self.get_socket(self.socket_type)

    @staticmethod
    def get_socket(socket_type):
        context = zmq.Context()
        return context.socket(socket_type)


class BoundSocket(Socket):

    def __init__(self, *args, **kwargs):
        self.required_attributes.append('port')

        super(BoundSocket, self).__init__(*args, **kwargs)

        self.socket.bind(self.port)


class LastMessageMixin(object):

    @staticmethod
    def get_socket(socket_type):
        context = zmq.Context()
        socket = context.socket(socket_type)
        socket.setsockopt(zmq.CONFLATE, 1)
        return socket
