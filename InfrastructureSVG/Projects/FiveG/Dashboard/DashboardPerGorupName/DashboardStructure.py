import logging
# import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

from InfrastructureSVG.Projects.FiveG.Dashboard.DashboardPerGorupName.ThroughputStructure import ThroughputForTester, ThroughputForExecutive
from InfrastructureSVG.Projects.FiveG.Dashboard.DashboardPerGorupName.HandoverStructure import HandoverForTester, HandoverForExecutive
from InfrastructureSVG.Projects.FiveG.Dashboard.DashboardPerGorupName.PassOrFailStructure import PassOrFailForTester, PassOrFailForExecutive


class DashboardHelper:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_dataframe_per_column_name(self, column_name):
        dashboard_columns = []
        if hasattr(self, 'dataframe'):
            for i in self.dataframe[column_name].drop_duplicates(keep='first'):
                if i is np.nan or i is None:
                    continue

                if type(i) is list:
                    dashboard_columns.append('\n'.join(i))
                else:
                    dashboard_columns.append(i)
        return dashboard_columns

    def get_dashboard_columns(self):
        dashboard_by_columns = self.get_dataframe_per_column_name(column_name='Dashboard Column')
        print(f'\n\ndashboard_by_columns is:')
        for index, dashboard_column in enumerate(dashboard_by_columns, start=0):
            print(f'Dashboard_old column index {index} is: \n{dashboard_column}\n')
        return dashboard_by_columns


class Dashboard(ABC, DashboardHelper):
    def __init__(self, dataframe):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.dataframe = dataframe
        self.dataframe_per_group_per_feature = None
        self.dashboard_type = None

        super(Dashboard, self).__init__()
        super(DashboardHelper, self).__init__()

    @abstractmethod
    def throughput_group_name(self):
        self.logger.debug('This is "Throughput" group name')

    @abstractmethod
    def handover_group_name(self):
        self.logger.debug('This is "Handover" group name')

    @abstractmethod
    def other_group_name(self):
        self.logger.debug('This is "Other" group name')

    @abstractmethod
    def get_dashboard_groups_name(self):
        pass

    @abstractmethod
    def get_dashboard_features(self):
        dashboard_by_features_name = self.get_dataframe_per_column_name(column_name='Feature Name')
        print(f'\n\ndashboard_by_groups_name is:')
        for index, dashboard_column in enumerate(dashboard_by_features_name, start=0):
            print(f'Dashboard_old Group Name index {index} is: \n{dashboard_column}\n')
        return dashboard_by_features_name

    def get_dataframe_per_group_name(self, group_name):
        if self.dashboard_type == 'Tester':
            self.dataframe.drop_duplicates(keep='first', subset='Regression Group Name')
            return self.dataframe.loc[(self.dataframe['Regression Group Name'] == group_name)]
        elif self.dashboard_type == 'Executive':
            self.dataframe.drop_duplicates(keep='first', subset='Executive Group Name')
            return self.dataframe.loc[(self.dataframe['Executive Group Name'] == group_name)]

    def build_table_per_feature_name(self):
        if 'Throughput' in list(self.dataframe_per_group_per_feature['Labels'].values[0]):
            self.throughput_group_name()
        elif 'Handover' in list(self.dataframe_per_group_per_feature['Labels'].values[0]):
            self.handover_group_name()
        else:
            self.other_group_name()

    def run_dashboard_main(self):
        # dashboard_columns = self.get_dashboard_columns()
        groups_name = self.get_dashboard_groups_name()
        features_name = self.get_dashboard_features()

        for group_name in groups_name:
            dataframe_per_group_name = self.get_dataframe_per_group_name(group_name)
            for feature_name in features_name:
                self.dataframe_per_group_per_feature = dataframe_per_group_name.loc[(dataframe_per_group_name['Feature Name'] == feature_name)]
                if self.dataframe_per_group_per_feature.empty or not list(self.dataframe_per_group_per_feature.get('Labels')):
                    continue
                else:
                    self.build_table_per_feature_name()
                print()
                # self.set_html_to_confluence(html_table)
            print()
        print()

        print()


class TesterDashboard(Dashboard, DashboardHelper):
    def __init__(self, dataframe):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(TesterDashboard, self).__init__(dataframe)
        super(DashboardHelper, self).__init__()

        self.dashboard_type = 'Tester'

    def throughput_group_name(self):
        super(TesterDashboard, self).throughput_group_name()

        ThroughputForTester(self.dataframe_per_group_per_feature).build_throughput_group_name_table()

    def handover_group_name(self):
        super(TesterDashboard, self).handover_group_name()

        HandoverForTester().build_handover_group_name_table()

    def other_group_name(self):
        super(TesterDashboard, self).other_group_name()

        PassOrFailForTester().build_handover_group_name_table()

    def get_dashboard_groups_name(self):
        dashboard_by_groups_name = []
        if self.dashboard_type == 'Tester':
            dashboard_by_groups_name = self.get_dataframe_per_column_name(column_name='Regression Group Name')
        elif self.dashboard_type == 'Executive':
            dashboard_by_groups_name = self.get_dataframe_per_column_name(column_name='Executive Group Name')
        print(f'\n\ndashboard_by_groups_name is:')
        for index, dashboard_column in enumerate(dashboard_by_groups_name, start=0):
            print(f'Dashboard Group Name index {index} is: \n{dashboard_column}\n')
        return dashboard_by_groups_name

    def get_dashboard_features(self):
        return super(TesterDashboard, self).get_dashboard_features()


class ExecutiveDashboard(Dashboard, DashboardHelper):
    def __init__(self, dataframe):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(ExecutiveDashboard, self).__init__(dataframe)
        super(DashboardHelper, self).__init__()

        self.dashboard_type = 'Executive'

    def throughput_group_name(self):
        super(ExecutiveDashboard, self).throughput_group_name()

        ThroughputForExecutive(self.dataframe_per_group_per_feature).build_throughput_group_name_table()

    def handover_group_name(self):
        super(ExecutiveDashboard, self).handover_group_name()

        HandoverForExecutive().build_handover_group_name_table()

    def other_group_name(self):
        super(ExecutiveDashboard, self).other_group_name()

        PassOrFailForExecutive().build_handover_group_name_table()

    def get_dashboard_groups_name(self):
        dashboard_by_groups_name = self.get_dataframe_per_column_name(column_name='Executive Group Name')
        print(f'\n\ndashboard_by_groups_name is:')
        for index, dashboard_column in enumerate(dashboard_by_groups_name, start=0):
            print(f'Dashboard_old Group Name index {index} is: \n{dashboard_column}\n')
        return dashboard_by_groups_name

    def get_dashboard_features(self):
        return super(ExecutiveDashboard, self).get_dashboard_features()
