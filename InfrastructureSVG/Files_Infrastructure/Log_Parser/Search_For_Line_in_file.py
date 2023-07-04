import logging


class SearchForLineInFilesClass:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def search_for_string_in_files(self, lines, string, time):
        try:
            return any(line.startswith(time) and string in line for line in lines) if lines else False

        except Exception:
            self.logger.exception('')
