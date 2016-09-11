import tempfile

import zmq

import logging.config
from multiprocessing import Process


class TestMultiprocessingRotatingFileHandler(object):
    temp_log_file = tempfile.TemporaryFile().name

    def test_log(self):
        logging.config.dictConfig({
            'version': 1,
            'handlers': {
                'rotating_file': {
                    'class': (
                        'zmqservices.utils.MultiprocessingRotatingFileHandler'
                    ),
                    'filename': self.temp_log_file,
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

        main_process_text = "Main process"
        self.logger.info(main_process_text)

        children_text = ('child1', 'child2', 'child3', 'child4')
        processes = []
        for child_text in children_text:
            process = Process(target=self.log, kwargs={'text': child_text})
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

        with open(self.temp_log_file, 'r') as log_file:
            log = log_file.read()

            assert main_process_text in log
            assert all(child_text in log for child_text in children_text)

    def log(self, text):
        self.logger.info(text)
