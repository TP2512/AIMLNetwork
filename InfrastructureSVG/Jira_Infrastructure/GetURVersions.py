import logging
import requests
import json

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


class GetURVersions:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = JiraActions(app_credentials='EZlife')

        self.automation_versions_unreleased = []
        self.manual_versions_unreleased = []
        self.ur_dict = {
            'automation_test_plan_list': set(),
            'manual_test_plan_list': set(),
        }

    def get_versions_unreleased_per_project(self, project):  # SVGA, SVG5G
        url_versions_unreleased = f'https://{self.jira_client._username}:{self.jira_client._password}@helpdesk.airspan.com/rest/api/2/project/{project}/versions'
        response_data = requests.get(url=url_versions_unreleased, timeout=600)
        return [i['name'] for i in json.loads(response_data.text) if not i['released']] if response_data.status_code in [200, 201] else []

    def get_automation_versions_unreleased_per_project(self):  # SVGA, SVG5G
        self.automation_versions_unreleased = self.get_versions_unreleased_per_project(project='SVGA')

    def get_manual_versions_unreleased_per_project(self):
        self.manual_versions_unreleased = self.get_versions_unreleased_per_project(project='SVG5G')

    def get_automation_ur_versions(self):
        automation_filter_test_plan = 'project = "SVG Automation (IL)" AND issuetype = "Test Plan" and fixVersion in (unreleasedVersions())'
        automation_test_plan_list = self.jira_client.search_by_filter(str_filter=automation_filter_test_plan, fields=['fixVersions'])
        for test_plan in automation_test_plan_list:
            self.ur_dict['automation_test_plan_list'].update([fix_versions.name for fix_versions in test_plan.fields.fixVersions])
        self.ur_dict['automation_test_plan_list'] = set(self.ur_dict['automation_test_plan_list'])

    def get_manual_ur_versions(self):
        manual_filter_test_plan = 'project = "SVG-5G" AND issuetype = "Test Plan" and fixVersion in (unreleasedVersions())'
        manual_test_plan_list = self.jira_client.search_by_filter(str_filter=manual_filter_test_plan, fields=['fixVersions'])
        for test_plan in manual_test_plan_list:
            self.ur_dict['manual_test_plan_list'].update([fix_versions.name for fix_versions in test_plan.fields.fixVersions])
        self.ur_dict['manual_test_plan_list'] = set(self.ur_dict['manual_test_plan_list'])

    def get_automation_ur_versions_unreleased(self):
        self.get_automation_ur_versions()
        self.get_automation_versions_unreleased_per_project()
        return set(self.ur_dict['automation_test_plan_list']) & set(self.automation_versions_unreleased)

    def get_manual_ur_versions_unreleased(self):
        self.get_manual_ur_versions()
        self.get_manual_versions_unreleased_per_project()
        return set(self.ur_dict['manual_test_plan_list']) & set(self.manual_versions_unreleased)


if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    get_ur_versions_ins = GetURVersions()

    automation_ur_versions_unreleased = get_ur_versions_ins.get_automation_ur_versions_unreleased()
    print(automation_ur_versions_unreleased)

    print()

    manual_ur_versions_unreleased = get_ur_versions_ins.get_manual_ur_versions_unreleased()
    print(manual_ur_versions_unreleased)

    print()
