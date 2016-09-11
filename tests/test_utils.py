import os
import tempfile

import logging.config
from multiprocessing import Process


class TestMultiprocessingRotatingFileHandler(object):
    log_file_descriptor, log_file_path = tempfile.mkstemp(suffix='.log')

    def test_log(self):
        logging.config.dictConfig({
            'version': 1,
            'formatters': {
                'default': {
                    'format': (
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )
                },
            },
            'handlers': {
                'rotating_file': {
                    'class': (
                        'zmqservices.utils.MultiprocessingRotatingFileHandler'
                    ),
                    'filename': self.log_file_path,
                    'formatter': 'default',
                },
            },
            'root': {
                'handlers': [
                    'rotating_file',
                ],
                'level': logging.DEBUG,
            },
        })

        self.logger = logging.getLogger()

        exception_text = "exception text"
        try:
            raise Exception(exception_text)
        except:
            logging.exception('Exception: ')

        children_text = ('child1', 'child2', 'child3', 'child4')
        processes = []
        for child_text in children_text:
            process = Process(target=self.log, kwargs={'text': child_text})
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

        with open(self.log_file_path, 'r') as log_file:
            log = log_file.read()

            assert exception_text in log
            assert all(child_text in log for child_text in children_text)

        self.cleanup_temp_file()

    def log(self, text):
        self.logger.info(text)

    def cleanup_temp_file(self):
        os.close(self.log_file_descriptor)
        os.unlink(self.log_file_path)
