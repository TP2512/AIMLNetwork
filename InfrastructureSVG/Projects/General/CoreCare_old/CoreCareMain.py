import re
import logging
from InfrastructureSVG.Files_Infrastructure.Log_Analyzer.LogAnalyzerI import LogAnalyzerI
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger
# from RobotFrameworkSVGInfra.TestResultsAndStatusObject.ResultsAndStatusObject import ResultsAndStatus


class CoreCare:
    def __init__(self, sir_folder_path: str, flow_yaml_file_path: str):
        self.logger = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)
        self.log_analyzer = LogAnalyzerI()
        self.sir_folder_path = sir_folder_path
        self.flow_yaml_file_path = flow_yaml_file_path

    def extract_core_name(self):
        REGEX = 'airspaninfo[a-zA-Z0-9_-]+.tgz'

        with open(self.sir_folder_path, 'r') as f:
            for line in f:
                print(re.match(REGEX, line))

    def get_summary_from_log_analyzer(self):
        preprocess_args = None
        is_log_analyzer_test = False
        set_filter = None
        is_create_yamls = True

        log_analyzer_obj = self.log_analyzer.analyze_log(sir_folder_path=self.sir_folder_path,
                                                         flow_yaml_file_path=self.flow_yaml_file_path,
                                                         set_filter=set_filter,
                                                         preprocess_args=preprocess_args,
                                                         is_log_analyzer_test=is_log_analyzer_test,
                                                         is_create_yamls=is_create_yamls
                                                         )
        print()
        message_summary = log_analyzer_obj['global_validation_info'].get('message_stats_summary')

        all_bt_rows_list = []
        for _, device in message_summary.items():
            all_bt_rows_list.extend(device_info.get("message_text") for device_info in device.get("log_message_1.1"))

        bt_rows_list = []
        backtrace_list = []
        for row_info in all_bt_rows_list:
            if 'BT[0]' in row_info:
                print(row_info)
                if backtrace_list:
                    print(backtrace_list)
                    bt_rows_list.append(backtrace_list.copy())
                backtrace_list = [row_info]
            else:
                backtrace_list.append(row_info)
        bt_rows_list.append(backtrace_list.copy())

        print()


def main():
    sir_folder_path_ = r"C:\Users\opeltzman\AirspanSprints\CoreCare_sprint\SIR-44201\gnb_1_lexus\du_1_SSH_Log_(DU-at2200-eab85a00544f-1)"
    flow_yaml_file_path_ = "C:\\Users\\opeltzman\\AirspanSprints\\CoreCare_sprint\\SIR-44201\\YAML_flow\\IODT_HO_flow_20220405-073939.yml"
    core_care_obj = CoreCare(sir_folder_path=sir_folder_path_, flow_yaml_file_path=flow_yaml_file_path_)
    # core_care_obj.get_summary_from_log_analyzer()
    core_care_obj.extract_core_name()


if __name__ == '__main__':
    project_name = 'CoreCare'
    site = 'IL SVG'
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(debug=True)
    main()
