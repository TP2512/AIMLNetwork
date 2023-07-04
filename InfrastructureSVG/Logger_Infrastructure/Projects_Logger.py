import logging
from datetime import datetime, timezone
from pathlib import Path
from colorlog import ColoredFormatter
import time


class ProjectsLogging:
    def __init__(self, project_name: str, path: str = None, file_name: str = None):
        self.project_name = project_name

        now = datetime.now(tz=timezone.utc)
        self.date_string = now.strftime("%d.%m.%Y")
        self.time_string = now.strftime("%H_%M_%S")

        self.path = path or 'C:/' + 'Python Logs/' + self.project_name + '/' + self.date_string

        self.file_name = file_name or f'{self.time_string}_{self.project_name}'
        Path(self.path).mkdir(parents=True, exist_ok=True)

    def project_logging(self, class_name: bool = False, timestamp: bool = False, log_level=logging.DEBUG):
        # sourcery skip: merge-else-if-into-elif
        logger = logging.getLogger(__name__)
        stream = logging.StreamHandler()

        log_level = log_level
        logger.setLevel(log_level)
        # logging.root.setLevel(LOG_LEVEL)

        if class_name:
            if timestamp:
                log_format_file = "%(asctime)s | %(levelname)-8s:%(name)s | %(message)s"
                # log_format_console = "%(log_color)s %(asctime)s | %(levelname)-8s%(name)s %(log_color)s | " \
                #                      "%(log_color)s%(message)s%(reset)s"
                log_format_console = "%(log_color)s %(asctime)s | %(levelname)-8s%(reset)s %(log_color)s | " \
                                     "%(log_color)s%(message)s%(reset)s"
            else:
                log_format_console = "%(log_color)s %(levelname)-8s%(reset)s %(log_color)s | " \
                                     "%(log_color)s%(message)s%(reset)s"
                log_format_file = "%(levelname)-8s:%(name)s | %(message)s"
        else:
            if timestamp:
                log_format_file = "%(asctime)s | %(levelname)-8s | %(message)s"
                log_format_console = "%(log_color)s %(asctime)s | %(levelname)-8s%(reset)s %(log_color)s | " \
                                     "%(log_color)s%(message)s%(reset)s"
            else:
                log_format_file = "%(levelname)-8s | %(message)s"
                log_format_console = "%(log_color)s %(levelname)-8s%(reset)s %(log_color)s | " \
                                     "%(log_color)s%(message)s%(reset)s"

        formatter_file = logging.Formatter(log_format_file)
        formatter_console = ColoredFormatter(log_format_console)
        file_handler = logging.FileHandler(f'{self.path}/{self.file_name}.log', mode='a')

        # file_handler = logging.FileHandler('c:/tmp/test.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter_file)

        stream.setLevel(log_level)
        stream.setFormatter(formatter_console)

        logger.setLevel(log_level)
        logger.addHandler(file_handler)
        logger.addHandler(stream)

        return logger

    @staticmethod
    def project_logging_robot_framework():
        logger = logging.getLogger(__name__)
        stream = logging.StreamHandler()

        log_level = logging.DEBUG
        logger.setLevel(log_level)

        log_format_console = "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s | %(log_color)s%(message)s%(reset)s"

        formatter_console = ColoredFormatter(log_format_console)

        stream.setLevel(log_level)
        stream.setFormatter(formatter_console)

        logger.setLevel(log_level)
        logger.addHandler(stream)

        return logger

    def project_logging_reset(self, logger, class_name: bool = False):
        logger.handlers[0].stream.close()
        logger.removeHandler(logger.handlers[0])

        log_level = logging.DEBUG
        logger.setLevel(log_level)

        if class_name:
            log_format_file = "%(asctime)s | %(levelname)-8s:%(name)s | %(message)s"
        else:
            log_format_file = "%(asctime)s | %(levelname)-8s | %(message)s"

        formatter_file = logging.Formatter(log_format_file)
        file_handler = logging.FileHandler(f'{self.path}/{self.file_name}.log', mode='a')

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter_file)

        logger.setLevel(log_level)
        logger.addHandler(file_handler)

        return logger


class BuildLogger:  # Do not change this class without Aviz permission !!!
    def __init__(self, project_name: str, log_file_name: str = None, log_path: str = None, site: str = None):
        self.project_name = project_name
        self.log_file_name = log_file_name
        self.log_path = log_path
        self.site = site

    def _build_log_file_name(self):
        active_date_time = datetime.now(tz=timezone.utc)
        date_string = active_date_time.strftime("%Y.%m.%d")
        time_string = active_date_time.strftime("%H.%M")
        if self.site:
            self.log_file_name = f'{date_string}_{time_string} - {self.project_name.replace(" ", "_")}_Logs_{self.site.replace(" ", "_")}'
        else:
            self.log_file_name = f'{date_string}_{time_string} - {self.project_name.replace(" ", "_")}_Logs'

    def _build_log_path(self):
        self.log_path = f'C:\\Python Logs\\{self.project_name}\\{self.site}'

    def build_logger(self, debug: bool = False, print_log: bool = True, class_name: bool = False, timestamp: bool = False):
        # Do not change this function without Aviz permission !!!

        if not self.log_file_name:
            self._build_log_file_name()
        if not self.log_path:
            self._build_log_path()

        log_level = logging.DEBUG if debug else logging.INFO
        logger = ProjectsLogging(project_name=self.project_name, path=self.log_path, file_name=self.log_file_name). \
            project_logging(class_name=class_name, timestamp=timestamp, log_level=log_level)

        if print_log:
            if self.site:
                logger.info(f'Start {self.project_name} ({self.site}) Logs {self.site} Main')
            else:
                logger.info(f'Start {self.project_name} Logs Main')
            print()

        return logger


def print_before_logger(project_name: str, site: str = None):  # Do not change this function without Aviz permission !!!
    if site:
        main_string = f'Start {project_name} ({site}) Process'
    else:
        main_string = f'Start {project_name} Process'

    number_of_ladder = "#" * len(f"### {main_string} ###")
    print(f"\n{number_of_ladder}")
    print(f"### {main_string} ###")
    print(f"{number_of_ladder}\n")
    time.sleep(1)


def print_before_logger_and_build_logger(project_name: 'str', site: ['str', None], class_name: bool = False, timestamp: bool = False, debug=False):
    print_before_logger(project_name=project_name, site=site)
    return BuildLogger(project_name=project_name, site=site).build_logger(class_name=class_name, timestamp=timestamp, debug=debug)


if __name__ == '__main__':
    PROJECT_NAME = 'CoreCare'
    SITE = None

    print_before_logger(project_name=PROJECT_NAME, site=SITE)
    logger_test = BuildLogger(project_name=PROJECT_NAME, site=SITE).build_logger(debug=False)

    logger_test.info('logger.info test')
    logger_test.debug('logger.debug test')
