import logging
import requests
from requests import ConnectionError, Timeout
import time

from InfrastructureSVG.Jira_Infrastructure.ConnectionException import ConnectionErrors


class TestExecution:

    def __init__(self):
        self.connection_timeout = 30
        self.start_time = time.time()
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def __recoverable(self, error, url, request, counter=1):
        if hasattr(error, 'status_code'):
            if error.status_code in [502, 503, 504]:
                error = f"HTTP {error.status_code}"
            else:
                return False
        DELAY = 10 * counter
        self.logger.warning(f"Got recoverable error [{error}] from {request} {url}, retry #{counter} in {DELAY}s")

        time.sleep(DELAY)
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
                url = f'https://{user}:{password}@helpdesk.airspan.com/rest/raven/1.0/testruns?testExecKey={str(execution)}'
                # data = requests.get(url=url, timeout=240).json()
                data_ = requests.get(url=url, timeout=600)
                data = data_.json()
                return data[0]['status']
            except ValueError:
                return None
            except ConnectionError as e:
                if time.time() > self.start_time + self.connection_timeout:
                    raise ConnectionErrors(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e

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
            url = f'https://TestspanAuto:air_auto1@helpdesk.airspan.com/rest/raven/1.0/api/testrun/{str(execution_id)}/?status={status}'

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
                url = f'https://{user}:{password}@helpdesk.airspan.com/rest/raven/1.0/testruns?testExecKey={str(execution)}'

                data = requests.get(url=url, timeout=600).json()
                return data[0]['id']
            except ValueError:
                self.logger.exception('Json Decoder error')
                return None
            except ConnectionError as e:
                if time.time() > self.start_time + self.connection_timeout:
                    raise ConnectionErrors(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e

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
                url = f'https://{user}:{password}@helpdesk.airspan.com/rest/raven/1.0/testruns?testExecKey={str(execution)}'

                data = requests.get(url=url, timeout=600).json()
                return data[0]['testKey']

            except ValueError:
                self.logger.exception('Json Decoder error')
                return None
            except ConnectionError as e:
                if time.time() > self.start_time + self.connection_timeout:
                    raise ConnectionErrors(self.logger.exception(f'Unable to get updates after {self.connection_timeout} seconds of ConnectionErrors')) from e

                else:
                    time.sleep(1)
