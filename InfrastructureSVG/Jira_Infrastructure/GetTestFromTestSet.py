import logging

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import get_basic_field_list


class GetTestFromTestSet:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = JiraActions(app_credentials='EZlife')

    def get_test_list_by_test_plan(self, test_plan):
        test_set_filter = f'project = "SVG IL repository" AND issuetype = "Test Set" AND issue in linkedissues("{test_plan}")'
        test_set_obj = self.jira_client.search_by_filter(str_filter=test_set_filter, fields=get_basic_field_list('customfield_10990'))[0]

        test_list_filter = f'project = "SVG IL repository" AND issuetype = "Test" AND issue in testSetTests("{test_set_obj.key}")'
        test_list_obj = self.jira_client.search_by_filter(str_filter=test_list_filter, fields=get_basic_field_list())

        d = {}
        for index, test in enumerate(test_set_obj.fields.customfield_10990, start=1):
            test_obj = [i for i in test_list_obj if i.key == test][0]
            d[index] = {
                'key': test_obj.key,
                'summary': test_obj.fields.summary
            }

        return d


if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    get_sub_tasks_ins = GetTestFromTestSet()
    test_list = get_sub_tasks_ins.get_test_list_by_test_plan(test_plan='SVGA-3315')

    print()
