import logging
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.Update_Create_Issues import JiraClass


class GetFieldsFomIssue:
    def __init__(self):

        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_tests_keys_from_test_set(self, test_set):
        if test_set:
            try:
                tests_from_test_set = JiraClass().fetch_issue(test_set).fields.customfield_10990
                return [JiraClass().fetch_issue(test) for test in tests_from_test_set]
            except Exception:
                self.logger.exception('')
                return None
        else:
            self.logger.error('test_set is None')
            return None
