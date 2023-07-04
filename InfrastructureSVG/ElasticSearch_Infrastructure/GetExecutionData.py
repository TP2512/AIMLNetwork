from elasticsearch_dsl import Search
from datetime import datetime
import logging


class GetDataFromElasticSearch:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def search_by_exec_id_and_sir_number(self, client, exec_id, execution):
        """
           This function responsible searching for scenario results from Testspan ElasticSearch_Infrastructure
           database

           The function get 3 parameters:
               - "client" - parameter need to be a client of ElasticSearch_Infrastructure
               - "exec_id" - execution id number as it appear in Difido reporter
               - "execution" - scenario name as it appear in Difido ('UDP_TP_TEST=SIR-30710')

           The function return search results
        """
        try:
            s = Search(using=client)
            return s.filter('term', executionId=exec_id).extra(size=1000).query(
                'match', execution=execution).extra(size=1000).execute()
        except Exception:
            self.logger.exception('')

    def search_by_exec_id_and_test_name(self, client, exec_id, test_name):
        """
           This function responsible searching for scenario results from Testspan ElasticSearch_Infrastructure
           database

           The function get 3 parameters:
               - "client" - parameter need to be a client of ElasticSearch_Infrastructure
               - "exec_id" - execution id number as it appear in Difido reporter
               - "test_name" - scenario name as it appear in Difido ('UDP_TP_TEST=SIR-30710')

           The function return search results
        """
        try:
            s = Search(using=client)
            return s.filter('term', executionId=exec_id).extra(size=1000).query(
                'match', name=test_name).extra(size=1000).execute()
        except Exception:
            self.logger.exception('')

    def search_by_exec_id_and_ho_type(self, client, exec_id, ho_type):
        """
           This function responsible searching for Handover test scenario results from Testspan ElasticSearch_Infrastructure
           database

           The function get 3 parameters:
               - "client" - parameter need to be a client of ElasticSearch_Infrastructure
               - "exec_id" - execution id number as it appear in Difido reporter
               - "ho_type" - Handover type parameter (X2_Handover/S1_Handover)

           The function return search results
        """
        try:
            s = Search(using=client)
            return s.filter('term', executionId=exec_id).extra(size=1000).query(
                'match', parameters__HandoverType=ho_type).execute()

        except Exception:
            self.logger.exception('')

    def search_by_exec_id_and_iperf_test(self, client, exec_id, ho_type):
        """
           This function responsible searching for Handover test scenario results from Testspan ElasticSearch_Infrastructure
           database

           The function get 3 parameters:
               - "client" - parameter need to be a client of ElasticSearch_Infrastructure
               - "exec_id" - execution id number as it appear in Difido reporter
               - "ho_type" - Handover type parameter (X2_Handover/S1_Handover)

           The function return search results
        """
        try:
            s = Search(using=client)
            return s.filter('term', executionId=exec_id).extra(size=1000).query(
                'match', parameters__HandoverType=ho_type).execute()

        except Exception:
            self.logger.exception('')

    def get_actual_result_from_execution(self, slave, result, execution):
        """
           This function responsible for iterating on ElasticSearch_Infrastructure response object
           and extracting actual result or failure reason result

           The function get 1 parameter:
               - "result" - ElasticSearch_Infrastructure response object

           The function return actual result or failure reason result
        """
        try:
            test_actual_result = ''
            for response in result:
                try:
                    if slave != response.machine or execution not in response.execution:
                        continue
                    test_actual_result = response.properties.actualResult
                    self.logger.info(response.properties.actualResult)
                    break
                except AttributeError:
                    try:
                        if slave != response.machine or execution not in response.execution:
                            continue
                        test_actual_result = response.properties.failureReason
                        self.logger.info(response.properties.failureReason)
                        break
                    except AttributeError:
                        continue

            return test_actual_result

        except Exception:
            self.logger.exception('')

    def get_uid_from_execution(self, result, test_name, description):
        """
           This function responsible for iterating on ElasticSearch_Infrastructure response object
           and extracting uid

           The function get 1 parameter:
               - "result" - ElasticSearch_Infrastructure response object

           The function return uid based on test name and test description (Stop Enodeb Logs/Serial logs)
        """
        try:
            return next((i.uid for i in result if i.name == test_name and i.description == description), '')

        except Exception:
            self.logger.exception('')

    def get_uid_from_tp_tests(
            self, result, test_name=None, second_value=None, sut=None, sir=None, other_parameter=None):
        """
           This function responsible for iterating on ElasticSearch_Infrastructure response object
           and extracting uid

           The function get 1 parameter:
               - "result" - ElasticSearch_Infrastructure response object

           The function return uid based on test name and test description (Stop Enodeb Logs/Serial logs)
        """
        try:
            uid = ''
            if test_name == 'Stop an SSH (XLP) session to enodeb and send commands.':
                for i in result:
                    if i.name == test_name and i.parameters.SessionName == second_value and \
                            sut in i.scenarioProperties.sutFile:
                        uid = i.uid
                        break
            if test_name in ['Iperf throughput test', 'IxLoad throughput report', 'New stop iperf']:
                for i in result:
                    if i.name == test_name and i.execution == sir and sut in i.scenarioProperties.sutFile:
                        if other_parameter:
                            if other_parameter == 'PassCriteria':
                                return i.parameters.PassCriteria

                            elif other_parameter == 'Threshold':
                                return i.parameters.Threshold

                            else:
                                return None

                        else:
                            uid = i.uid
                            break
            if test_name == 'Validate IXIA Traffic':
                for i in result:
                    if i.name == test_name and i.execution == sir and sut in i.scenarioProperties.sutFile:
                        uid = i.uid
                        break
                    if other_parameter and i.name == 'Summarize Tp Results':
                        threshold = i.parameters.Threshold
                        return threshold
            elif test_name == 'Validate STC traffic':
                for i in result:
                    if i.name == test_name and sut in i.scenarioProperties.sutFile:
                        if other_parameter:
                            if other_parameter == 'Threshold':
                                threshold = i.parameters.Threshold
                                return threshold
                        else:
                            uid = i.uid
                            break
            elif test_name == 'Stop Enodeb Logs':
                for i in result:
                    if i.name == test_name and sut in i.scenarioProperties.sutFile and 'Serial logs' in i.description:
                        uid = i.uid
                        break
            return uid

        except Exception:
            self.logger.exception('')

    def get_freason_from_tp_tests(self, result, test_name, second_value, sut, sir):
        """
           This function responsible for iterating on ElasticSearch_Infrastructure response object
           and extracting uid

           The function get 1 parameter:
               - "result" - ElasticSearch_Infrastructure response object

           The function return uid based on test name and test description (Stop Enodeb Logs/Serial logs)
        """
        try:
            freason = ''
            if test_name in ['Iperf throughput test', 'IxLoad throughput report', 'New stop iperf']:
                for i in result:
                    if i.name == test_name and i.execution == sir and sut in i.scenarioProperties.sutFile:
                        freason = i.properties.failureReason
                        break
            elif test_name == 'Validate STC traffic':
                for i in result:
                    time = str(i.timestamp).split(' ')
                    datetime_object = datetime.strptime(time[0], '%Y/%m/%d')
                    if i.name == test_name and sut in i.scenarioProperties.sutFile:
                        delta = second_value - datetime_object
                        if delta.days < 7:
                            freason = i.properties.failureReason
                            break
            return freason
        except Exception:
            self.logger.exception('')

    def search_for_cores_in_scenario(self, result):
        """
           This function responsible for iterating on ElasticSearch_Infrastructure response object
           and searches for CoreDump occurrence in scenario

           The function get 1 parameter:
               - "result" - ElasticSearch_Infrastructure response object

           The function return failure reason result
        """
        try:
            for i, response in enumerate(result, start=0):
                try:
                    failure_reason = response.properties.failureReason
                    if 'CoreDump' in failure_reason or 'PhyAssert' in failure_reason:
                        failure_reason = response.properties.failureReason

                        return failure_reason
                    else:
                        continue

                except AttributeError:
                    continue
        except Exception:
            self.logger.exception('')

    def get_slave_name(self, result, sut):
        """
           This function responsible for iterating on ElasticSearch_Infrastructure response object
           and searches for automation slave name in scenario

           The function get 1 parameter:
               - "result" - ElasticSearch_Infrastructure response object

           The function return automation slave name
        """
        try:
            for i, response in enumerate(result, start=0):
                try:
                    if sut in response.scenarioProperties.sutFile:
                        slave = response.machine
                    else:
                        continue

                    return slave

                except AttributeError:
                    continue
        except Exception:
            self.logger.exception('')
