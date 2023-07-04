import logging
from typing import Union
import jira

from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX


class AutomationFilters:
    def __init__(self, jira_client=None):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = jira_client

    def get_open_defects_by_filter(self, labels: list) -> jira.client.ResultList:
        str_filter = 'project = "Defect Tracking" AND issuetype = Defect'
        for label in labels:
            str_filter += f' AND labels = "{label}"'
        str_filter = f'{str_filter} AND (status = '

        for status in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX:
            str_filter += f'{status} OR status = '
        str_filter = f'{str_filter[:-13]})'
        return self.jira_client.search_by_filter(str_filter=str_filter)

    def get_defects_by_filter(self, labels: list) -> Union[jira.client.ResultList, None]:
        if not labels:
            return None

        str_filter = 'project = "Defect Tracking" AND issuetype = Defect'
        for label in labels:
            str_filter += f' AND labels = "{label}"'
        str_filter = f'{str_filter}'

        return self.jira_client.search_by_filter(str_filter=str_filter)


class CoreCareFilters:
    def __init__(self, jira_client=None):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = jira_client

    def get_core_system_uptime_min_by_filter(self, epic: str, last_version: str) -> jira.client.ResultList:
        return self.jira_client.search_by_filter(str_filter=f'project = CoreCare AND "Epic Link" = {epic} AND "g/eNodeB SW version" = {last_version}')

    def get_total_core_occurrence_count_by_filter(self, epic: str) -> int:
        return self.jira_client.search_by_filter(str_filter=f'project = CoreCare AND "Epic Link" = {epic}').__len__()

    def found_epic_bt_by_filter(self, type_crash_name: str, back_trace_hash: str) -> jira.client.ResultList:
        if type_crash_name in {'vCU-CP', 'vCU-UP', 'vDU'}:
            return self.jira_client.search_by_filter(str_filter=f'project = CoreCare AND type = Epic AND labels = "{back_trace_hash}" AND "Product At Fault" = "{type_crash_name}"')
        else:
            return self.jira_client.search_by_filter(str_filter=f'project = CoreCare AND type = Epic AND labels = "{back_trace_hash}"')

    def get_open_defects_by_filter(self, epic: str) -> jira.client.ResultList:
        str_filter = f'issue in linkedissues({epic}) AND (status = '
        for status in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX:
            str_filter += f'{status} OR status = '
        str_filter = f'{str_filter[:-13]})'
        return self.jira_client.search_by_filter(str_filter=str_filter)

    def get_defects_by_filter(self, epic: str) -> jira.client.ResultList:
        return self.jira_client.search_by_filter(str_filter=f'project = "Defect Tracking" AND issue in linkedissues({epic}) AND issuetype = Defect')

    def get_last_version_core_occurrence_count_by_filter(self, epic: str, last_version: str) -> int:
        str_filter = f'project = CoreCare AND "Epic Link" = {epic} AND "g/eNodeB SW version" = {last_version}'
        return self.jira_client.search_by_filter(str_filter=str_filter).__len__()

    def get_cores_for_versions_by_filter(self, epic: str, versions: list) -> list:
        versions_list = []
        for version in versions:
            if v := self.jira_client.search_by_filter(
                    str_filter=f'project = CoreCare AND "Epic Link" = {epic} AND "g/eNodeB SW version" = {version}'
            ):
                versions_list.extend(v)
        return list({vv.key: vv for vv in versions_list}.values())


class JiraFilters:
    def __init__(self, jira_client=None):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = jira_client

        self.corecare_filters = CoreCareFilters(jira_client=jira_client)
        self.automation_filters = AutomationFilters(jira_client=jira_client)

    def get_by_filter(self, str_filter: str) -> Union[jira.client.ResultList, None]:
        return self.jira_client.search_by_filter(str_filter=f'{str_filter}')
