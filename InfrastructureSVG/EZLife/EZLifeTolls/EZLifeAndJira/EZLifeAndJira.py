import logging

from InfrastructureSVG.EZLife.EZLifeMethods import EZLifeMethod
from InfrastructureSVG.EZLife.GlobalParameters import EZLifeGlobalParameters, GlobalClassAndFunctions
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


JIRA_FIELDS = ['reporter', 'fixVersions', 'customfield_11004', 'issuelinks', 'customfield_11003']


class EZLifeJira:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.global_parameters = EZLifeGlobalParameters()
        self.global_class_and_functions = GlobalClassAndFunctions()
        self.ezlife_method_fn = EZLifeMethod()
        self.jira_client = JiraActions(app_credentials=self.global_parameters.user_jira_credentials)


class EZLifeJiraTestPlanCorrelation(EZLifeJira):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super().__init__()

        self.ezlife_tree_objects = self.get_ezlife_tree_objects()
        self.jira_test_plan_list = self.get_jira_automation_test_plan_obj_list()
        self.ezlife_tree_test_plan_list = self.get_ezlife_tree_test_plan_list()

    def get_jira_automation_test_plan_obj_list(self):
        automation_filter_test_plan = 'project = "SVG Automation (IL)" AND issuetype = "Test Plan"'
        return self.jira_client.search_by_filter(str_filter=automation_filter_test_plan, fields=JIRA_FIELDS)

    def get_ezlife_tree_objects(self):  # sourcery skip: raise-specific-error
        tree_objects = self.ezlife_method_fn.ezlife_get.get_by_url(url=f'{self.global_parameters.base_url}/TreeApp/')
        if tree_objects[0] not in [200, 201]:
            raise Exception(f'The URL: "{self.global_parameters.base_url}/TreeApp/ return with status code: tree_objects[0]')
        return tree_objects

    def get_ezlife_tree_test_plan_list(self):
        return [tree_object['test_plan'] for tree_object in self.ezlife_tree_objects[1] if tree_object['test_plan']]

    def get_ezlife_tree_test_plan_list_not_exist_on_jira(self):
        return self.check_if_test_plan_list_exist_on_jira(test_plan_list=self.ezlife_tree_test_plan_list)

    def get_jira_test_plan_list_not_exist_on_tree_ezlife(self):
        return self.check_if_test_plan_list_exist_on_tree_ezlife(
            jira_test_plan_list=self.jira_test_plan_list,
            ezlife_tree_test_plan_list=self.ezlife_tree_test_plan_list
        )

    def get_jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter(self):
        jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict = {}
        for test_plan in self.jira_test_plan_list:
            if test_plan.key not in self.ezlife_tree_test_plan_list:
                if jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict.get(test_plan.fields.reporter.key):
                    jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict[test_plan.fields.reporter.name].append(test_plan.key)
                else:
                    jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict[test_plan.fields.reporter.name] = [test_plan.key]
        return jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict

    def check_if_test_plan_list_exist_on_jira(self, test_plan_list):
        test_plan_list_not_exist_on_jira = []
        for test_plan in test_plan_list:
            test_plan_obj = self.jira_client.search_by_filter(str_filter=f'key = {test_plan}', fields=JIRA_FIELDS)
            if len(test_plan_obj) == 0:
                test_plan_list_not_exist_on_jira.append(test_plan)
        return test_plan_list_not_exist_on_jira

    @staticmethod
    def check_if_test_plan_list_exist_on_tree_ezlife(jira_test_plan_list, ezlife_tree_test_plan_list):
        return [
            test_plan.key
            for test_plan in jira_test_plan_list
            if test_plan.key not in ezlife_tree_test_plan_list
        ]
