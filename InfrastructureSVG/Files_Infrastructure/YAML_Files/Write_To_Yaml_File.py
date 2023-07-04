import logging

import yaml


class WriteToYAMLFile:
    def __init__(self, file, body):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.file = file
        self.body = body

    def dump_object_to_file(self):
        with open(self.file, 'w') as file:
            yaml.dump(self.body, file)
