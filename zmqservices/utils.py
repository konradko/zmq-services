import multiprocessing
import logging
from logging.handlers import RotatingFileHandler
import threading
import traceback
import sys

import zmq


class MultiprocessingRotatingFileHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self)

        self._handler = RotatingFileHandler(*args, **kwargs)
        self.queue = multiprocessing.Queue()

        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self._handler.close()
        logging.Handler.close(self)


class RequiredAttributesMixin(object):
    required_attributes = ()

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
    required_attributes = ('socket_type', )

    def __init__(self, *args, **kwargs):

        super(Socket, self).__init__(*args, **kwargs)
        self.socket = self.get_socket(self.socket_type)

    @staticmethod
    def get_socket(socket_type):
        context = zmq.Context()
        return context.socket(socket_type)


class BoundSocket(Socket):

    def __init__(self, *args, **kwargs):
        self.required_attributes = self.required_attributes + ('port', )

        super(BoundSocket, self).__init__(*args, **kwargs)

        self.socket.bind(self.port)


class LastMessageMixin(object):

    @staticmethod
    def get_socket(socket_type):
        context = zmq.Context()
        socket = context.socket(socket_type)
        socket.setsockopt(zmq.CONFLATE, 1)
        return socket
