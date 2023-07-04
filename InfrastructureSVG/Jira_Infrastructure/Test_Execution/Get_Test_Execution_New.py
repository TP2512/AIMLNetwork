import logging
import time
import json
import requests
from requests import ConnectionError, Timeout

from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials


class TestExecution:
    def __init__(self, app_credentials='TestspanAuto'):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self._user, self._password = Credentials().credentials_per_app(app_credentials)
        self.base_url = f'https://{self._user}:{self._password}@helpdesk.airspan.com/rest/raven/1.0'

        self.connection_timeout = 30
        self.start_time = time.time()

    def __recoverable(self, error, url, request, counter=1):
        if hasattr(error, 'status_code'):
            if error.status_code in [502, 503, 504]:
                error = f"HTTP {error.status_code}"
            else:
                return False
        delay = 10 * counter
        self.logger.warning(f"Got recoverable error [{error}] from {request} {url}, retry #{counter} in {delay}s")

        time.sleep(delay)
        return True

    def get_test_execution_status(self, execution, user, password):
        """
           This function responsible for retrieving test execution status from
           jira test execution

           The function get 1 parameter:
               - "execution" - parameter need to be a jira object (test execution object)

           The function return test execution status (PASS/FAIL/Automation_Fail/TO DO)
        """
        counter = 0
        while True:
            counter += 1
            try:
                url = f'{self.base_url}/testruns?testExecKey={execution}'
                # data = requests.get(url=url, timeout=240).json()
                data_ = requests.get(url=url, timeout=600)
                data = data_.json()
                return data[0]['status']
            except ValueError:
                return None
            except ConnectionError as e:
                if time.time() > self.start_time + self.connection_timeout:
                    raise Exception(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e
                else:
                    time.sleep(1)

    def set_test_execution_status(self, execution_id, status):
        """
           This function responsible for updating test execution status (PASS/FAIL/Automation_Fail/TO DO) in
           self.jira test execution

           The function get 2 parameters:
               - "execution_id" - parameter need to be a string (execution key)
               - execution_id parameter should be retrieved by following function:
                    exec_id = TestExecution_class().get_test_execution_id('SVG1-xxx', user, password)
               - "status" -  parameter need to be a string (PASS/FAIL/Automation_Fail/TO DO)

           The function return PUT response (200 = ok, else = fail)
        """
        try:
            body = {"status": status}
            url = f'{self.base_url}/api/testrun/{execution_id}/?status={status}'
            return requests.put(url=url, json=body, timeout=240)
        except Timeout:
            self.logger.exception('The request timed out')

    def get_test_execution_id(self, execution, user, password):
        """
           This function responsible for retrieving test execution id from
           jira test execution

           The function get 1 parameter:
               - "execution" - parameter need to be a jira object (test execution object)

           The function return test execution id
        """
        while True:
            try:
                url = f'{self.base_url}/testruns?testExecKey={execution}'
                data = requests.get(url=url, timeout=600).json()
                return data[0]['id']
            except ValueError:
                self.logger.exception('Json Decoder error')
                return None
            except ConnectionError as e:
                if time.time() > self.start_time + self.connection_timeout:
                    raise Exception(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e
                else:
                    time.sleep(1)

    def get_test_execution_sir(self, execution, user, password):
        """
           This function responsible for retrieving Test(SIR number) test execution from
           jira test execution

           The function get 1 parameter:
               - "execution" - parameter need to be a jira object (test execution object)

           The function return test execution SIR number
        """
        while True:
            try:
                url = f'{self.base_url}/testruns?testExecKey={execution}'
                data = requests.get(url=url, timeout=600).json()
                return data[0]['testKey']
            except ValueError:
                self.logger.exception('Json Decoder error')
                return None
            except ConnectionError as e:
                if time.time() > self.start_time + self.connection_timeout:
                    raise Exception(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e
                else:
                    time.sleep(1)

    def get_test_exec_id(self, test_exec_key: str) -> tuple[int, int]:
        url = f'{self.base_url}/testruns?testExecKey={test_exec_key}'
        response_data = requests.get(url=url, timeout=600)
        return response_data.status_code, json.loads(response_data.text)[0]['id']

    def add_defects_to_execution_defects(self, test_exec_key: str, defects: list) -> bool:
        status_code, test_exec_id = self.get_test_exec_id(test_exec_key)
        if status_code == 200:
            body = defects
            url = f'{self.base_url}/testrun/{test_exec_id}/defects'
            response_data = requests.post(url=url, json=body, timeout=240)
            if response_data.status_code == 200:
                return True
        return False
