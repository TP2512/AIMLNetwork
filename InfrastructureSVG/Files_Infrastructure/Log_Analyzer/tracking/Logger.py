import datetime
import logging

from InfrastructureSVG.Singletons_Package.Singletons import Singleton


class Logger(metaclass=Singleton):

    def __init__(self):
        self.external_logger = logging.getLogger(
            'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' +
            self.__class__.__name__)
        self.logger_lists = {'info_list': [],
                             'warnings_list': [],
                             'error_list': []}

    def error(self, frame_info, track_message):
        log_dict = {'type': 'error',
                    'time': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S'),
                    'message': track_message,
                    'file': frame_info.filename,
                    'line_num': frame_info.lineno,
                    'traceback': None}
        self.external_logger.error(track_message)
        self.logger_lists['error_list'].append(log_dict)

    def warning(self, frame_info, track_message):
        log_dict = {'type': 'info',
                    'time': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S'),
                    'message': track_message,
                    'file': frame_info.filename,
                    'line_num': frame_info.lineno,
                    'traceback': None}
        self.external_logger.warning(log_dict['message'])
        self.logger_lists['warnings_list'].append(log_dict)

    def info(self, frame_info, track_message):
        log_dict = {'type': 'info',
                    'time': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S'),
                    'message': track_message,
                    'file': frame_info.filename,
                    'line_num': frame_info.lineno,
                    'traceback': None}
        self.external_logger.info(log_dict['message'])
        self.logger_lists['info_list'].append(log_dict)
