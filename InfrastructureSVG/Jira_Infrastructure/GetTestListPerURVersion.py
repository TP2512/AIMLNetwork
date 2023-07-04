import logging

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


def get_value_from_issuelinks(jira_obj, issuetype_name):
    test_set_list = []
    issue_links_name_list = ['inwardIssue', 'outwardIssue']
    for i in jira_obj.fields.issuelinks:
        for name in issue_links_name_list:
            if getattr(i, name, None) and getattr(i, name).fields.issuetype.name == issuetype_name:
                test_set_list.append(getattr(i, name))
    return test_set_list


class GetTestListPerURVersion:
    def __init__(self, ur_version):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = JiraActions(app_credentials='EZlife')

        self.ur_version = ur_version
        self.automation_versions_unreleased = []
        self.manual_versions_unreleased = []
        self.test_list = {
            'automation_test_list': {},
            'manual_test_list': {},
        }

    def get_test_list_per_ur_versions(self, filter_):
        unique_test_dict = dict()
        automation_test_plan_list = self.jira_client.search_by_filter(str_filter=filter_, fields=['fixVersions', 'customfield_11004', 'issuelinks', 'customfield_11003'])

        for jira_obj in automation_test_plan_list:
            if self.ur_version in [i.name for i in jira_obj.fields.fixVersions]:
                for test in jira_obj.fields.customfield_11004:
                    fields = [
                        'project',
                        'fixVersions',
                        'issuelinks',
                        'issuetype',
                        'labels',
                        'summary',
                        'customfield_10974',
                        'customfield_10985',
                        'customfield_10987',
                        'customfield_11200',
                        'customfield_11801',
                        'customfield_12671',
                        'customfield_17100',
                        'customfield_19601',

                        'customfield_11004',
                    ]

                    test_obj = self.jira_client.search_by_filter(str_filter=f'key={test}', fields=fields)[0]
                    env_config = get_value_from_issuelinks(jira_obj=jira_obj, issuetype_name='Epic')

                    if not env_config:
                        continue

                    if env_config[0].key not in unique_test_dict:
                        unique_test_dict[env_config[0].key] = {
                            'environment_config': env_config[0],
                            'SIR': set(),
                            'TEST-SET': dict(),
                            'test_plan_obj': dict(),
                            'slave_name_per_test_set': dict(),
                        }

                    # Fill "TEST-SET"
                    test_set_list = get_value_from_issuelinks(jira_obj=jira_obj, issuetype_name='Test Set')
                    if not test_set_list:
                        self.logger.error(f'test_set_list is empty for Test Plan "{jira_obj.key}"')
                        continue
                    elif len(test_set_list) > 1:
                        self.logger.error(f'len(test_set_list) > 1 for Test Plan "{jira_obj.key}"')
                        continue
                    else:
                        test_set_obj = test_set_list[0]
                        unique_test_dict[env_config[0].key]['SIR'].add(test_obj)

                    if test_obj.key not in list(unique_test_dict[env_config[0].key]['slave_name_per_test_set'].keys()):
                        unique_test_dict[env_config[0].key]['test_plan_obj'].update({test_obj.key: set()})
                        unique_test_dict[env_config[0].key]['TEST-SET'].update({test_obj.key: set()})
                        unique_test_dict[env_config[0].key]['slave_name_per_test_set'].update({test_obj.key: set()})

                    unique_test_dict[env_config[0].key]['test_plan_obj'][test_obj.key].add(jira_obj)
                    unique_test_dict[env_config[0].key]['TEST-SET'][test_obj.key].add(test_set_obj)
                    [unique_test_dict[env_config[0].key]['slave_name_per_test_set'][test_obj.key].add(slave_name) for slave_name in jira_obj.fields.customfield_11003]

        return unique_test_dict

    def get_automation_test_list_per_ur_versions_per_env_config(self):
        automation_filter_test_plan = 'project = "SVG Automation (IL)" AND issuetype = "Test Plan" and fixVersion in (unreleasedVersions())'
        self.test_list['automation_test_list'] = self.get_test_list_per_ur_versions(filter_=automation_filter_test_plan)

    def get_manual_test_list_per_ur_versions(self):
        manual_filter_test_plan = 'project = "SVG-5G" AND issuetype = "Test Plan" and fixVersion in (unreleasedVersions())'
        self.test_list['manual_test_list'] = self.get_test_list_per_ur_versions(filter_=manual_filter_test_plan)


if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    get_ur_versions_ins = GetTestListPerURVersion(ur_version='SR19.50_UR1')

    get_ur_versions_ins.get_automation_test_list_per_ur_versions_per_env_config()
    print(len(get_ur_versions_ins.test_list['automation_test_list']))
    print()

    get_ur_versions_ins.get_manual_test_list_per_ur_versions()
    print(len(get_ur_versions_ins.test_list['manual_test_list']))
    print()
