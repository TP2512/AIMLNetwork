from inspect import currentframe, getframeinfo
import datetime
import logging


class KibanaVisualizationValidation:
    def __init__(self):
        self.logger = logging.getLogger(f'MLSystemAnalyzerSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def validate_fields_definition(self, fields_definition):
        if len(fields_definition) > 20:
            frame_info = getframeinfo(currentframe())
            error_dict = {
                'type': 'error',
                'error_time': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S'),
                'message': 'The number of fields currently supported is up to 20.',
                'error_file': frame_info.filename,
                'error_line_num': frame_info.lineno,
                'traceback': None
            }

            self.logger.error(error_dict['message'])
            return False
        for field_definition in fields_definition:
            if 'field_name' not in field_definition:
                frame_info = getframeinfo(currentframe())
                error_dict = {
                    'type': 'error',
                    'error_time': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S'),
                    'message': 'field name is missing in field definition.',
                    'error_file': frame_info.filename,
                    'error_line_num': frame_info.lineno,
                    'traceback': None
                }

                self.logger.error(error_dict['message'])
                return False
            if 'field_title' not in field_definition:
                frame_info = getframeinfo(currentframe())
                error_dict = {
                    'type': 'error',
                    'error_time': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S'),
                    'message': f"field title is missing in field name: {field_definition['field_name']}.",
                    'error_file': frame_info.filename,
                    'error_line_num': frame_info.lineno,
                    'traceback': None
                }
                self.logger.error(error_dict['message'])
                return False
        return True
