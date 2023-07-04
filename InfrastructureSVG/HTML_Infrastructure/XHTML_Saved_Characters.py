import logging


class SavedCharacters:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def saved_char_replacement(self, string):
        try:
            return str(string).replace('"', '&quot;	').replace('\'', '	&apos;').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') if string else None

        except Exception:
            self.logger.exception('')
