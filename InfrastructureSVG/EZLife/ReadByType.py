import logging
from typing import Optional, Union


class ReadFromUser:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def read_list(self, question: str) -> Union[list, None]:
        value: Optional[list] = None
        while value is None:
            _ = input(f"{question} ")
            try:
                value = _.split(',')
            except ValueError:
                self.logger.exception("Invalid input.")
        return [v.strip() for v in value]

    def read_str(self, question: str) -> Union[str, None]:
        value: Optional[str] = None
        while value is None:
            _ = input(f"{question} ")
            try:
                if not _ and question != 'Press Enter to exit.':
                    _ = None
                    raise ValueError()
                value = str(_)
            except ValueError:
                self.logger.exception("Invalid input.")
        return value

    def read_int(self, question: str, min_value: int = 0):
        value: Optional[int] = None
        while value is None or value < min_value:
            _ = input(f"{question} ")
            try:
                value = int(_)
            except ValueError:
                self.logger.exception("Invalid input. Please enter a number.")
        return value
