import os
import yaml
from InfrastructureSVG.Files_Infrastructure.Log_Analyzer.tracking.Logger import Logger
from inspect import currentframe, getframeinfo


class InputValidation:

    def __init__(self):
        self.logger = Logger()

    def load_yaml_from_file(self, flow_yaml_file_path):
        """
        Loading YAML data from input YAML file.
        Arguments:
            flow_yaml_file_path: The input YAML file path.
        Returns:
            yaml_data: The YAML Data Object
        """
        try:
            with open(flow_yaml_file_path, 'r') as stream:
                try:
                    yaml_data = yaml.safe_load(stream)
                    return yaml_data
                except yaml.YAMLError as YAML_exception:
                    frame_info = getframeinfo(currentframe())
                    self.logger.error(frame_info, YAML_exception)
        except BaseException:
            pass

    def validate_input_log(self, validate_input_info, log_list):
        """
        input validation tests:
            Is the log input file exist.

        Arguments:
            validate_input_info: The input validation object.
            log_list: The input log file list.
        Returns:
            validate_input_info: The input validation information object.
            validate_input_info_str: The input validation information string.
        """
        for log in log_list:
            if os.path.isfile(log['log_file_path']):
                test_dict = {
                    'test_name': 'log_file_exist',
                    'test_description': "log file path validated and file exist",
                    'test_result': True}
                validate_input_info['pass_tests_list'].append(test_dict)
            else:
                test_dict = {
                    'test_name': 'log_file_exist',
                    'test_description': "log file path error, file doesn't exist",
                    'test_result': False}
                validate_input_info['fail_tests_list'].append(test_dict)
        if len(validate_input_info['fail_tests_list']) == 0:
            validate_input_info['valid'] = True
        else:
            validate_input_info['valid'] = False
        validate_input_info_str = self.validate_input_info_str(
            validate_input_info)
        return validate_input_info, validate_input_info_str

    def validate_sir_folder(self, sir_folder_path):
        """
        input validation tests:
            Is SIR folder path exists.
        Arguments:
            sir_folder_path: the sir folder path.
        Returns:
            validate_input_info: The input validation information object.
            validate_input_info_str: The input validation information string.
        """
        validate_input_info = {'pass_tests_list': [],
                               'fail_tests_list': []}
        if os.path.isdir(sir_folder_path):
            test_dict = {
                'test_name': 'sir_folder_path_exist',
                'test_description': "sir folder path validated and exist",
                'test_result': True}
            validate_input_info['pass_tests_list'].append(test_dict)
        else:
            test_dict = {
                'test_name': 'sir_folder_path_exist',
                'test_description': "sir folder path error, directory doesn't exist",
                'test_result': False}
            validate_input_info['fail_tests_list'].append(test_dict)
        if len(validate_input_info['fail_tests_list']) == 0:
            validate_input_info['valid'] = True
        else:
            validate_input_info['valid'] = False
        return validate_input_info

    def validate_input_yaml(self, validate_input_info, flow_yaml_file_path):
        """
        input validation tests:
            1. Is the YAML input file exist.
            2. is the YAML input file being parsed correctly.
        Arguments:
            validate_input_info: The input validation information object.
            flow_yaml_file_path: The input YAML file path.
        Returns:
            validate_input_info: The input validation information object.
            validate_input_info_str: The input validation information string.
        """
        if os.path.isfile(flow_yaml_file_path):
            test_dict = {
                'test_name': 'yaml_file_exist',
                'test_description': "yaml file path validated and file exist",
                'test_result': True}
            validate_input_info['pass_tests_list'].append(test_dict)
        else:
            test_dict = {
                'test_name': 'yaml_file_exist',
                'test_description': "yaml file path error, file doesn't exist",
                'test_result': False}
            validate_input_info['fail_tests_list'].append(test_dict)
        try:
            validate_input_info['yaml_data'] = self.load_yaml_from_file(
                flow_yaml_file_path)
            test_dict = {
                'test_name': 'yaml_data_parsed',
                'test_description': "yaml data has been parsed successfully",
                'test_result': True}
            validate_input_info['pass_tests_list'].append(test_dict)
        except Exception:
            test_dict = {'test_name': 'yaml_data_parsed',
                         'test_description': "yaml data parse fail",
                         'test_result': False}
            validate_input_info['fail_tests_list'].append(test_dict)
        if len(validate_input_info['fail_tests_list']) == 0:
            validate_input_info['valid'] = True
        else:
            validate_input_info['valid'] = False
        validate_input_info_str = self.validate_input_info_str(
            validate_input_info)
        return validate_input_info, validate_input_info_str

    @staticmethod
    def validate_input_info_str(validate_input_info):
        """
        Creates a string that describe the input validation results.
        Arguments:
            validate_input_info: The input validation object that contains the validation info and parsed YAML info.
        Return:
            validate_input_info_str: The input validation information string.
        """
        validate_input_info_str = '\n'
        if len(validate_input_info['fail_tests_list']) == 0:
            validate_input_info_str += 'The input validation passed, the following tests have been made:\n'
            for test_dict in validate_input_info['pass_tests_list']:
                validate_input_info_str += f"{test_dict['test_name']}: {test_dict['test_description']}\n"
        else:
            validate_input_info_str += 'The input validation failed, the following tests have failed:\n'
            for test_dict in validate_input_info['fail_tests_list']:
                validate_input_info_str += f"{test_dict['test_name']}: {test_dict['test_description']}\n"
            validate_input_info_str += 'The following tests has passed:\n'
            for test_dict in validate_input_info['pass_tests_list']:
                validate_input_info_str += f"{test_dict['test_name']}: {test_dict['test_description']}\n"
        return validate_input_info_str
