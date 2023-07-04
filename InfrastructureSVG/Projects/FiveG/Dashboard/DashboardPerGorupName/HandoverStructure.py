import logging
from abc import ABC, abstractmethod


class HandoverGroupName(ABC):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    @abstractmethod
    def build_handover_group_name_table(self):
        self.logger.debug('Start to build handover group name table')
        print()


class HandoverForTester(HandoverGroupName):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(HandoverForTester, self).__init__()

    def build_handover_group_name_table(self):
        super(HandoverForTester, self).build_handover_group_name_table()
        print()


class HandoverForExecutive(HandoverGroupName):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(HandoverForExecutive, self).__init__()

    def build_handover_group_name_table(self):
        super(HandoverForExecutive, self).build_handover_group_name_table()
        print()
