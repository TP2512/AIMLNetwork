import logging
import time
from jira import JIRA, JIRAError


""" 
In this py file have 1 class
    - JiraConnectionClass
"""


class JiraConnection:
    """ This class ("JiraConnectionClass") responsible for connections to Jira_Infrastructure server """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def jira_real_connection(self, jira_username_domain='TestspanAuto', jira_password_domain='air_auto1'):
        """
        This function responsible for connections to Jira_Infrastructure real server

        The function get 0 parameter:

        The function return 1 parameters:
            - "jira" - client of jira (real)
        """

        c = 0
        while True:
            try:
                c = c + 1  # count
                server = 'https://helpdesk.airspan.com'  # Jira_real
                return JIRA(basic_auth=(jira_username_domain, jira_password_domain), options={'server': server}, timeout=580)

            except JIRAError:
                self.logger.exception("still error - The Core doesnt open")
                if c > 10:
                    time.sleep(1800)
                time.sleep(20)
            except Exception:
                self.logger.exception('')

    def jira_test_connection(self, jira_username_domain='TestspanAuto', jira_password_domain='air_auto1'):
        """
        This function responsible for connections to Jira_Infrastructure test server

        The function get 0 parameter:

        The function return 1 parameters:
            - "jira" - client of jira (test)
        """
        c = 0
        while True:
            try:
                c = c + 1  # count
                server = 'https://testhelpdesk.airspan.com'  # Jira_test
                return JIRA(basic_auth=(jira_username_domain, jira_password_domain), options={'server': server})

            except JIRAError:
                self.logger.exception("still error - The Core doesnt open")
                if c > 10:
                    time.sleep(1800)
                time.sleep(20)
            except Exception:
                self.logger.exception('')
