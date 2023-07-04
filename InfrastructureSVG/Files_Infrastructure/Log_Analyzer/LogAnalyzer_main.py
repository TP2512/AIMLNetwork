import datetime

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging
from LogAnalyzerI import LogAnalyzerI

if __name__ == "__main__":
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')
    PROJECT_NAME = 'LogAnalyzer'
    ACTIVE_DATE_TIME = datetime.datetime.now(datetime.timezone.utc)
    DATE_STRING = ACTIVE_DATE_TIME.strftime("%Y.%m.%d")
    TIME_STRING = ACTIVE_DATE_TIME.strftime("%H.%M")
    SITE = 'IL SVG'
    logger = ProjectsLogging('Regression_Dashboard').project_logging()
    # preprocess_args = {
    #                     'start_message': {'message_timestamp': '15/07/2021 15:38:24.941'},
    #                     'end_message': {'message_timestamp': '08/09/2021 13:05:04.167000'}
    #                     }
    log_file_path = r"R:\LogAnalyzer\LogAnalyzer_Tests\SIR-42723-IODT_Attach_Detach_UE_F\CUCP_SSH_Log\Valid_CUCP_2021-09-08 16_04_21.log"
    preprocess_args = None
    log_analyzer = LogAnalyzerI()
    # is_log_analyzer_test = False
    is_log_analyzer_test = False
    # is_create_yamls = True
    is_create_yamls = True
    under_or_supporting_test = 'under_test'
    if is_log_analyzer_test:
        log_analyzer.test_log_analyzer(under_or_supporting_test=under_or_supporting_test, )
    else:
        sir_folder_path = r"\\192.168.127.231\AutomationResults\old_runs\ASIL-SATURN\773\RobotFrameworkSVG\Test_Logs_And_Files\SIR-47049"
        flow_yaml_file_path = r"C:\Users\Administrator\PycharmProjects\RobotFrameworkSVG\RobotFrameworkSVG\Resources\LogAnalyzerFlows\MTBF.yml"
        # set_filter = {'gnb_set_index': None,
        #               'device_set_index': None}
        set_filter = None
        results = log_analyzer.analyze_log(sir_folder_path=sir_folder_path,
                                           flow_yaml_file_path=flow_yaml_file_path,
                                           set_filter=set_filter,
                                           preprocess_args=preprocess_args,
                                           is_log_analyzer_test=is_log_analyzer_test,
                                           is_create_yamls=is_create_yamls,
                                           under_or_supporting_test=under_or_supporting_test, )
        pass
