from __future__ import absolute_import

import logging
import os
import tempfile


logger = logging.getLogger()

FILE_MESSAGE_STORAGE_PATH = os.getenv(
    'FILE_MESSAGE_STORAGE_PATH',
    os.path.join(tempfile.gettempdir(), 'zmqservices')
)
if not os.path.exists(FILE_MESSAGE_STORAGE_PATH):
    os.makedirs(FILE_MESSAGE_STORAGE_PATH)
