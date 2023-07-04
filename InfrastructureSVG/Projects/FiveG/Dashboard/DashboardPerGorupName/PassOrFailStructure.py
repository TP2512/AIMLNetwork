import logging
from abc import ABC, abstractmethod


class PassOrFailGroupName(ABC):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    @abstractmethod
    def build_handover_group_name_table(self):
        self.logger.debug('Start to build handover group name table')
        print()


class PassOrFailForTester(PassOrFailGroupName):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(PassOrFailForTester, self).__init__()

    def build_handover_group_name_table(self):
        super(PassOrFailForTester, self).build_handover_group_name_table()
        print()


class PassOrFailForExecutive(PassOrFailGroupName):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(PassOrFailForExecutive, self).__init__()

    def build_handover_group_name_table(self):
        super(PassOrFailForExecutive, self).build_handover_group_name_table()
        print()
