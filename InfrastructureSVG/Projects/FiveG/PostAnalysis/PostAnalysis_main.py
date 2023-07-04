import logging
import msgpack

from InfrastructureSVG.Jira_Infrastructure.GetTestSIRListByTestPlanID import get_test_sir_list_by_test_plan
from InfrastructureSVG.Projects.FiveG.DeepAnalysis.DeepAnalysis_main import LinkQuality
from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchForDashboard.ELKDashboardFillData.SendDataToDashboard import ReportToELK


class GetTestResults:
    def __init__(self, full_test_path: str):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.full_test_path = full_test_path
        self.test_results_object = self.get_test_results_object()
        self.check_scenario_status()

    def get_test_results_object(self):
        self.logger.debug('Start "get_test_results_object" function')

        with open(f'{self.full_test_path}\\final_result_object.json', "rb") as json_file:
            test_results_object = msgpack.unpackb(json_file.read(), strict_map_key=False)
        return test_results_object

    def check_scenario_status(self):
        self.logger.debug('Start "check_gnb_link_quality" function')
        test_status_list = [self.test_results_object['gnb'][gnb_name]['test_status'] for gnb_name in self.test_results_object['gnb']]
        self.logger.info(f"test_status_list is: {test_status_list}")

        if 'ABORTED' in test_status_list:
            self.logger.info("scenario_status == ABORTED, doesn't need to report this scenario to ELK")
            self.test_results_object['test_info']['scenario_status'] = 'ABORTED'
        elif 'AUTOMATION_FAIL' in test_status_list:
            self.test_results_object['test_info']['scenario_status'] = 'AUTOMATION_FAIL'
        elif 'FAIL' in test_status_list:
            self.test_results_object['test_info']['scenario_status'] = 'FAIL'
        elif set(test_status_list) == {'PASS'}:
            self.test_results_object['test_info']['scenario_status'] = 'PASS'
        else:
            self.test_results_object['test_info']['scenario_status'] = 'FAIL_TO_GENERATE_STATUS'

        self.logger.info(f"scenario_status is: {self.test_results_object['test_info']['scenario_status']}")


def main(setup_name: str, build_id: str, test_plan_id: str, debug: bool = False):
    if not (test_set := get_test_sir_list_by_test_plan(test_plan_id)):
        return

    for sir_id in test_set.fields.customfield_10990:
        test_path = f'\\\\192.168.127.230\\AutomationResults\\old_runs\\{setup_name}\\{build_id}\\RobotFrameworkSVG\\Test_Logs_And_Files\\{sir_id}'
        get_test_results = GetTestResults(full_test_path=test_path)

        if get_test_results.test_results_object['test_info']['scenario_status'] == 'ABORTED' or not debug:  # ! remove "or not debug"
            continue

        if get_test_results.test_results_object['test_info']['scenario_status'] != 'PASS':
            link_quality = LinkQuality(test_results_object=get_test_results.test_results_object)
            link_quality.check_gnb_link_quality()

        # Report to ELK
        global_information_reporter = ReportToELK(
            test_results_object=get_test_results.test_results_object,
            debug=debug
        )
        global_information_reporter.process(
            # jira_test_run_time=30,
            deep_analysis=True,
        )

    print()


if __name__ == '__main__':
    import sys
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger_and_build_logger

    logger = print_before_logger_and_build_logger(project_name='PostAnalysis', site=None, class_name=True, timestamp=True, debug=True)

    jenkins_parameters = sys.argv

    main(
        setup_name=jenkins_parameters[1],  # 'ASIL-RAAS3'
        build_id=jenkins_parameters[2],  # '11709'
        test_plan_id=jenkins_parameters[3],  # SVGA-55130
        debug=True
    )

    print()
