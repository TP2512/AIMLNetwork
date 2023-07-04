import datetime
import os.path
from pathlib import Path
from shutil import copyfile
from shutil import SameFileError
import yaml
from inspect import currentframe, getframeinfo
from InfrastructureSVG.Files_Infrastructure.Log_Analyzer.preprocessing.PrettyYAMLDumper import PrettyYAMLDumper
from InfrastructureSVG.Files_Infrastructure.Log_Analyzer.tracking.Logger import Logger


class Output:
    def __init__(self):
        self.logger = Logger()
        self.time_stats = {}

    def output_validation_results(
            self,
            test_folder_path,
            results,
            flow_yaml_file_path,
            is_log_analyzer_test,
            is_create_yamls):
        """
        Creates the validation results string print it and store YAMLs.
        Arguments:
            test_folder_path: The path to the test (SIR) folder.
            results: The results object.
            flow_yaml_file_path: The path to the flow YAML file.
            is_log_analyzer_test: Weather is in test mode.
        """
        info_str = ''
        info_str += f"yaml_path: {flow_yaml_file_path}\n"
        yaml_dump = yaml.dump(results['yaml_data'],
                              Dumper=PrettyYAMLDumper,
                              default_flow_style=False,
                              sort_keys=False)
        info_str += f"The flow that has been validated was: \n{flow_yaml_file_path}\n"
        info_str += '\n'
        info_str += f"Flow Analysis started at {results['time_stats']['start_run_datetime_str']}\n"
        for flow in results['validated_flows']:
            info_str = self.create_result_info_str(info_str, flow, results['validated_flows'][flow])
        info_str += f"The analysis has ended with status: {results['valid']}\n"
        info_str += f"The end reason is: {results['validation_end_reason']}\n"
        info_str += f"Flow Analysis ended at {results['time_stats']['end_run_datetime_str']}\n"
        frame_info = getframeinfo(currentframe())
        self.logger.info(frame_info, info_str)
        if test_folder_path and is_create_yamls:
            self.store_results_as_yaml(results, test_folder_path)

    def output_validation_results_log_list_error(
            self,
            test_folder_path,
            results,
            flow_yaml_file_path,
            is_log_analyzer_test):
        """
        Creates the final validation result string and print it.
        Arguments:
            test_folder_path: The path to the test (SIR) folder.
            results: The results object.
            flow_yaml_file_path: The path to the flow YAML file.
            is_log_analyzer_test: Weather is in test mode.
        """
        info_str = ''
        info_str += f"Flow Analysis started at {results['time_stats']['start_run_datetime_str']}\n"
        info_str += f"The analysis has ended with status: {results['valid']}\n"
        info_str += f"The end reason is: {results['validation_end_reason']}\n"
        info_str += f"Flow Analysis ended at {results['time_stats']['end_run_datetime_str']}\n"
        frame_info = getframeinfo(currentframe())
        self.logger.info(frame_info, info_str)
        self.store_results_as_yaml(results, test_folder_path)

    def store_flow_yaml(self, test_folder_path, flow_yaml_file_path):
        """
        Stores the flow YAML
        Arguments:
            flow_yaml_file_path: The path to the source flow YAML file.
            test_folder_path: The path to the test (SIR) folder.
        """
        flow_yaml_file_name = Path(flow_yaml_file_path).stem.replace('Valid_', '')
        flow_yaml_ext = os.path.splitext(flow_yaml_file_path)[1]
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')
        yaml_flow_folder_path = self.create_flow_yaml_folder(test_folder_path)
        new_flow_yaml_file_path = os.path.join(yaml_flow_folder_path, f'{flow_yaml_file_name}_{now_str}{flow_yaml_ext}')
        try:
            if not os.path.basename(
                    os.path.dirname(flow_yaml_file_path)).startswith('flows'):
                copyfile(flow_yaml_file_path, new_flow_yaml_file_path)
        except SameFileError:
            pass

    def store_results_as_yaml(self, results, test_folder_path):
        """
        Stores the results YAML
        Arguments:
            results: The results object.
            test_folder_path: The path to the test (SIR) folder.
        """
        results_folder_path = self.create_results_folder(test_folder_path)
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')
        results_yaml_file_name = f'LogAnalyzerResultsYAML_{now_str}.yml'
        results_yaml_file_path = os.path.join(results_folder_path, results_yaml_file_name)
        with open(results_yaml_file_path, 'w', encoding='utf-8') as new_flow_yaml_file:
            yaml.dump(results,
                      new_flow_yaml_file,
                      Dumper=PrettyYAMLDumper,
                      default_flow_style=False,
                      sort_keys=False)

    @staticmethod
    def create_results_folder(test_folder_path):
        """
        Creates the results' folder
        Arguments:
            test_folder_path: The test folder path.
        Returns:
            results_folder_path: The results' folder path.
        """
        results_folder_path = os.path.join(
            test_folder_path, 'LogAnalyzerResults')
        if os.path.basename(os.path.dirname(
                results_folder_path)).startswith('SIR-'):
            Path(results_folder_path).mkdir(parents=True, exist_ok=True)
        return results_folder_path

    @staticmethod
    def create_flow_yaml_folder(test_folder_path):
        """
        Creates the destination YAML folder
        Arguments:
            test_folder_path: The test folder path.
        Returns:
            yaml_flow_folder_path: The destination YAML folder path.
        """
        yaml_flow_folder_path = os.path.join(test_folder_path, 'YAML_flow')
        Path(yaml_flow_folder_path).mkdir(parents=True, exist_ok=True)
        return yaml_flow_folder_path

    def create_results_dict(
            self,
            results,
            global_validation_info,
            validation_flow_dict_list,
            yaml_data):
        """
        Creates the results' object
        Arguments:
            results: The results object.
            global_validation_info: The global validation information object.
            validation_flow_dict_list: A list of dictionaries with the flows' validation objects.
            yaml_data: The YAML data object.
        Returns:
            results: The results object.
        """
        results['valid'] = 'PASS'
        results['validated_flows'] = {}
        sequence_flow_validation_result_dict = {}
        for validation_flow_dict in validation_flow_dict_list:
            validated_sequence_flow = None
            if validation_flow_dict['validation_state']['validation_type'] == 'per_sequence_flow':
                validated_sequence_flow = validation_flow_dict['validation_state']['yaml_sequence_state']['validated_yaml_sequence_dict']
                flow_info = validation_flow_dict['flow_info']
            else:
                flow_info = None
            sequence_flow_validation_result_dict = {
                'sequence_flow_validation_result': validation_flow_dict['validation_state']['valid'],
                'sequence_flow_validation_end_reason': validation_flow_dict['validation_state']['validation_end_reason'],
                'validated_sequence_flow': validated_sequence_flow,
                'flow_info': flow_info,
                'fails_sequence_dicts': validation_flow_dict['validation_state']['fails_sequence_dicts'],
                'validation_info': validation_flow_dict['validation_state']['validation_info'],
                'validation_state': validation_flow_dict['validation_state'],
                'actions_info': validation_flow_dict['validation_state']['actions_info'],
                'log_start_timestamp': validation_flow_dict['log_start_timestamp'],
                'log_end_timestamp': validation_flow_dict['log_end_timestamp'],
                'start_message_id': validation_flow_dict['start_message_id'],
                'end_message_id': validation_flow_dict['end_message_id'],
                'device_id': validation_flow_dict['device_id'],
                'device_name': validation_flow_dict['device_name'],
                'log_type': validation_flow_dict['log_type'],
                'log_file_path': validation_flow_dict['log_file_path'],
                'log_file_name': validation_flow_dict['log_file_name'],
            }
            results['validated_flows'][validation_flow_dict['sequence_flow_name']] = sequence_flow_validation_result_dict
            if sequence_flow_validation_result_dict['sequence_flow_validation_result'] == 'FAIL':
                results['valid'] = 'FAIL'
                results['validation_end_reason'] = sequence_flow_validation_result_dict['sequence_flow_validation_end_reason']
        results['global_validation_info'] = global_validation_info
        if results['valid'] == 'PASS':
            if 'Handover_Result' in results['global_validation_info']:
                results['validation_end_reason'] = results['global_validation_info']['Handover_Result']
            else:
                results['validation_end_reason'] = sequence_flow_validation_result_dict['sequence_flow_validation_end_reason']
        results['time_stats'] = self.time_stats
        results['yaml_data'] = yaml_data
        if not results['validation_end_reason'] and results['valid'] == 'PASS':
            results['validation_end_reason'] = 'validated'
        return results

    def create_result_info_str(self, info_str, flow_name, flow):
        """
        Create the final information string.
        Arguments:
            info_str: The information string.
            flow_name: The name of the flow.
            flow: A single flow result object.
        Returns:
            info_str: The information string.
        """
        if flow['validation_state']['validation_type'] == 'per_sequence_flow':
            info_str += f"The flow: {flow_name} has been analyzed\n"
            info_str += f"Validation info: {flow['validation_info']}\n"
            action_info_output_str = ''
            for action_info_name in flow['actions_info']:
                action_info = flow['actions_info'][action_info_name]
                for action_name in action_info:
                    if action_info[action_name]['output_str']:
                        action_info_output_str += action_info[action_name]['output_str']
            if action_info_output_str:
                info_str += f"Actions info:\n" + action_info_output_str
        elif flow['validation_state']['validation_type'] == 'per_message_flow':
            if len(flow['fails_sequence_dicts']['global_fail_message_failed']) > 0:
                for fail_message_dict in flow['fails_sequence_dicts']['global_fail_message_failed']:
                    validation_info_str = flow['fails_sequence_dicts']['global_fail_message_failed'][fail_message_dict]['validation_info_str']
                    info_str += f"{validation_info_str}\n"
            if len(flow['fails_sequence_dicts']['global_fail_message_passed']) > 0:
                for fail_message_dict in flow['fails_sequence_dicts']['global_fail_message_passed']:
                    validation_info_str = flow['fails_sequence_dicts']['global_fail_message_passed'][fail_message_dict]['validation_info_str']
                    info_str += f"{validation_info_str}\n"
        return info_str

    def init_time_stats(self):
        """
        Initialize time statistics object.
        """
        self.time_stats = {'start_run_datetime': datetime.datetime.now(datetime.timezone.utc)}
        self.time_stats['start_run_datetime_str'] = self.time_stats['start_run_datetime'].strftime(
            '%Y-%m-%d %H:%M:%S')

    def finalize_time_stats(self):
        """
        Finalize time statistics object.
        """
        self.time_stats['end_run_datetime'] = datetime.datetime.now(datetime.timezone.utc)
        self.time_stats['end_run_datetime_str'] = self.time_stats['end_run_datetime'].strftime(
            '%Y-%m-%d %H:%M:%S')
        self.time_stats['time_delta'] = self.time_stats['end_run_datetime'] - \
            self.time_stats['start_run_datetime']

    @staticmethod
    def copy_debug_mark_tests(sir_folder_path):
        """
        Copy the Powershell scripts that mark weather tests are Valid or not and copies them to the test(SIR) folder inside LogAnalyzerResults.
        Arguments:
            sir_folder_path: the sir folder path.
        """
        mark_debug_folder_path = os.path.realpath(r'\\192.168.127.231\LabShare\Automation\LogAnalyzer\debug')
        for file_name in os.listdir(mark_debug_folder_path):
            if file_name.startswith('Results'):
                src_file_path = os.path.join(mark_debug_folder_path, file_name)
                dst_file_path = os.path.join(sir_folder_path, 'LogAnalyzerResults', file_name)
                if not os.path.isfile(dst_file_path):
                    copyfile(src_file_path, dst_file_path)
#
