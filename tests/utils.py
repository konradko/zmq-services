from contextlib import contextmanager

import mock


@contextmanager
def mock_zmq():
    with mock.patch('zmq.Context.socket') as zmq_mock:
        yield zmq_mock()
