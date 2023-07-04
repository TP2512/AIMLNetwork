import logging
from abc import ABC, abstractmethod


class ThroughputGroupName(ABC):
    def __init__(self, dataframe_per_group_per_feature):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.dataframe_per_group_per_feature = dataframe_per_group_per_feature
        self.expected_ul_throughput = self.dataframe_per_group_per_feature['Expected UL Throughput']
        self.expected_dl_throughput = self.dataframe_per_group_per_feature['Expected DL Throughput']

    @abstractmethod
    def check_threshold(self, throughput):
        pass

    def get_throughput_by_traffic_direction(self):
        self.dataframe_per_group_per_feature['DL Throughput (Mbps)'] = 900
        if self.dataframe_per_group_per_feature['Automation Traffic Direction'].values[0] == 'DL':
            return {
                'DL': {
                    'Throughput': self.dataframe_per_group_per_feature['DL Throughput (Mbps)'].max(),
                    'Expected': self.dataframe_per_group_per_feature['Expected DL Throughput'].max(),
                }
            }
        elif self.dataframe_per_group_per_feature['Automation Traffic Direction'].values[0] == 'UL':
            return {
                'UL': {
                    'Throughput': self.dataframe_per_group_per_feature['UL Throughput (Mbps)'].max(),
                    'Expected': self.dataframe_per_group_per_feature['Expected UL Throughput'].max(),
                }
            }
        elif self.dataframe_per_group_per_feature['Automation Traffic Direction'].values[0] == 'BiDi':
            return {
                'DL': {
                    'Throughput': self.dataframe_per_group_per_feature['DL Throughput (Mbps)'].max(),
                    'Expected': self.dataframe_per_group_per_feature['Expected DL Throughput'].max(),
                },
                'UL': {
                    'Throughput': self.dataframe_per_group_per_feature['UL Throughput (Mbps)'].max(),
                    'Expected': self.dataframe_per_group_per_feature['Expected UL Throughput'].max(),
                }
            }
        else:
            return

    @abstractmethod
    def build_throughput_group_name_table(self):
        self.logger.debug('Start to build throughput group name table')
        return self.get_throughput_by_traffic_direction()


class ThroughputForTester(ThroughputGroupName):
    def __init__(self, dataframe_per_group_per_feature):
        super(ThroughputForTester, self).__init__(dataframe_per_group_per_feature)

        self.threshold = self.dataframe_per_group_per_feature['Threshold']

    def check_threshold(self, throughput):
        if int(throughput['Throughput']) > int(throughput['Expected']) * (int(self.threshold.max()) / 100):
            self.logger.warning('Green')
        else:
            self.logger.warning('Red')

    def check_failure_reason(self):
        self.logger.debug(self.dataframe_per_group_per_feature['Automation Error Message'])
        print()

    def build_throughput_group_name_table(self):
        throughput = super(ThroughputForTester, self).build_throughput_group_name_table()
        for throughput_key, throughput_value in throughput.items():
            if not throughput_value:
                continue

            self.check_threshold(throughput_value)
            print()
        self.check_failure_reason()
        print()


class ThroughputForExecutive(ThroughputGroupName):
    def __init__(self, dataframe_per_group_per_feature):
        super(ThroughputForExecutive, self).__init__(dataframe_per_group_per_feature)

        self.threshold = 80

    def check_threshold(self, throughput):
        if int(throughput['Expected']) * (int(self.threshold) / 100) > \
                throughput['Throughput'] > \
                int(throughput['Expected']) * (int(self.threshold) / 100):
            self.logger.warning('Green')
        elif int(throughput['Expected']) * (int(self.threshold) / 100) > \
                throughput['Throughput'] > \
                int(throughput['Expected']) * (int(self.threshold)-10 / 100):
            self.logger.warning('Orange')
        else:  # self.threshold * (80/100):
            self.logger.warning('Red')

    def build_throughput_group_name_table(self):
        throughput = super(ThroughputForExecutive, self).build_throughput_group_name_table()
        for throughput_key, throughput_value in throughput.items():
            if not throughput_value:
                continue

            self.check_threshold(throughput_value)
