import logging
import requests
from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials
from InfrastructureSVG.Jira_Infrastructure.ConnectionException import ConnectionErrors
from InfrastructureSVG.Jira_Infrastructure.Deffects_Handler.DefectsHandlerPackage import DefectsHandler
from InfrastructureSVG.Jira_Infrastructure.Connection.Connection import JiraConnection
from requests import ConnectionError
import time


class XrayActionClass:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.connection_timeout = 30
        self.start_time = time.time()
        self.process = DefectsHandler()

    def get_test_plan(self, test_plan_key, user, password):
        try:
            url = f'https://{user}:{password}@helpdesk.airspan.com/rest/api/2/issue/{str(test_plan_key)}'

            return requests.get(url=url).json()

        except ConnectionError as e:
            if time.time() > self.start_time + self.connection_timeout:
                raise ConnectionErrors(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e

            else:
                time.sleep(1)

    def get_open_defects_from_issue(self, issue):
        def_list = []
        try:
            if hasattr(issue.fields, 'issuelinks'):
                for i in issue.fields.issuelinks:
                    if hasattr(i, 'outwardIssue') and 'DEF' in i.outwardIssue.key:
                        def_status = i.outwardIssue.fields.status.name
                        if self.process.check_for_current_status(def_status, True):
                            def_list.append(i.outwardIssue.key)
            return def_list

        except ConnectionError as e:
            if time.time() > self.start_time + self.connection_timeout:
                raise ConnectionErrors(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e

            else:
                time.sleep(1)

    def get_duplicates(self, defect):
        def_list = []
        try:
            if defect[0].fields.issuelinks:
                for i in defect[0].fields.issuelinks:
                    if hasattr(i, 'outwardIssue'):
                        tmp = []
                        try:
                            if 'DEF' in i.outwardIssue.key:
                                def_key = i.outwardIssue.key
                                def_status = i.outwardIssue.fields.status.name
                                if self.process.check_for_current_status(def_status, True):
                                    defect_link = f'https://helpdesk.airspan.com/browse/{str(def_key)}'
                                    tmp.extend((def_key, def_status, defect_link))
                                    def_list.append(tmp)
                        except AttributeError:
                            continue

            return def_list
        except TabError:
            self.logger.exception("TypeError: 'IssueLink' object is not iterable")
            return None

        except AttributeError:
            self.logger.exception("'IssueLink' object is not subscribable")
            return None
        except ConnectionError as e:
            if time.time() > self.start_time + self.connection_timeout:
                raise ConnectionErrors(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e

            else:
                time.sleep(1)

    def get_all_tests_keys_from_test_set(self, user, password, test_set_key):
        try:
            url = f'https://{user}:{password}@helpdesk.airspan.com/rest/api/2/issue/{str(test_set_key)}'

            data = requests.get(url=url).json()
            return data['fields']['customfield_10990'] or []

        except ConnectionError as e:
            if time.time() > self.start_time + self.connection_timeout:
                raise ConnectionErrors(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e

            else:
                time.sleep(1)

    def get_test_set_from_test_plan(self, jira_issue):
        test_set = ''
        if jira_issue and type(jira_issue) == str:
            user, password = Credentials().credentials_per_app('Dashboard_old')
            jira = JiraConnection().jira_real_connection(user, password)
            jira_issue = jira.issue(jira_issue)
        if jira_issue.fields.issuelinks:
            for i in jira_issue.fields.issuelinks:
                if hasattr(i, 'inwardIssue'):
                    test_set = i.inwardIssue.key
                    self.logger.info(test_set)
        return test_set

    def get_tests_keys_from_test_set(self, jira, test_set):
        if jira:
            try:
                tests_from_test_set = jira.issue(test_set).fields.customfield_10990
                return [jira.issue(test) for test in tests_from_test_set]
            except Exception:
                self.logger.exception('')
                return None
        else:
            self.logger.error('Jira is None')
            return None
