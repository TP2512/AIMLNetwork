import copy
import datetime
import filecmp
import os
import random
import re
import subprocess
from inspect import currentframe, getframeinfo
from io import StringIO
from pathlib import Path

import yaml

from InfrastructureSVG.Files_Infrastructure.Log_Analyzer.preprocessing.PrettyYAMLDumper import PrettyYAMLDumper
from InfrastructureSVG.Files_Infrastructure.Log_Analyzer.tracking.Logger import Logger


class Preprocessing:

    def __init__(self):
        self.logger = Logger()
        prefix_list = ['sequence', 'log_message', 'fail_log_message']
        self.compiled_regexes = {}
        for prefix in prefix_list:
            self.compiled_regexes[prefix] = re.compile(f"{prefix}(.*)?_(.*)")
        self.sed_executable_path = r'C:\Program Files\sed\sed-4.8-x64.exe'
        self.perl_executable_path = r'C:\Strawberry\perl\bin\perl.exe'
        self.regex_dict = {}
        self.debug_test_lines_file_path = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)),
            'data',
            'text_files',
            'debug_test_lines.log')
        self.actions_types = self.define_actions_types()
        self.regex_dict = self.define_regex_dict()

    @staticmethod
    def define_actions_types():
        """
        Define the actions types.
        Returns
            actions_types: The actions types definitions.
        """
        return [{'action_name': 'get_message_stats',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_info_type': [],
                 'actions_config': False,
                 'prepare': False,
                 'result': 'Not Found'},
                {'action_name': 'verify_hex_content',
                 'message_extraction_requirements': 'next_message',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_info_type': [],
                 'actions_config': ['verify_value'],
                 'prepare': False,
                 'result': False},
                {'action_name': 'verify_max_repeat',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_info_type': 0,
                 'actions_config': ['max_repeat'],
                 'prepare': False,
                 'result': 'PASS'},
                {'action_name': 'verify_repeat',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_info_type': 0,
                 'actions_config': ['repeat_num'],
                 'prepare': False,
                 'result': 'FAIL'},
                {'action_name': 'verify_min_repeat',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_info_type': 0,
                 'actions_config': ['min_repeat'],
                 'prepare': False,
                 'result': 'FAIL'},
                {'action_name': 'extract_regex_from_message',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_info_type': [],
                 'actions_config': ['regex_type', 'regex_extraction_pattern', 'regex_format_pattern'],
                 'prepare': 'prepare_action_regex',
                 'result': False},
                {'action_name': 'get_regex_extraction_summary',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_validation',
                 'action_scope': 'message',
                 'actions_info_type': [],
                 'actions_config': False,
                 'prepare': False,
                 'result': 'PASS'},
                {'action_name': 'verify_sequences_conditions',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_validation',
                 'action_scope': 'message',
                 'actions_info_type': [],
                 'actions_config': ['sequences_conditions'],
                 'prepare': False,
                 'result': 'FAIL'},
                {'action_name': 'get_sequences_stats',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_validation',
                 'action_scope': 'message',
                 'actions_info_type': [],
                 'actions_config': False,
                 'prepare': False,
                 'result': 'PASS'},
                {'action_name': 'get_message_stats_summary',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_validation',
                 'action_scope': 'message',
                 'actions_info_type': [],
                 'actions_config': False,
                 'prepare': False,
                 'result': 'PASS'},
                {'action_name': 'log_message_before',
                 'message_extraction_requirements': 'previous_message',
                 'action_flow_position': 'pre_log_forward_step',
                 'action_scope': 'message',
                 'actions_config': False},
                {'action_name': 'log_message_after',
                 'message_extraction_requirements': 'next_message',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_config': False},
                {'action_name': 'sequence_before',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'pre_yaml_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'sequence_after',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_yaml_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_messages_time_delta_first_to_first',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_messages_time_delta_first_to_last',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_messages_time_delta_last_to_first',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_messages_time_delta_last_to_last',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_messages_time_delta_first_to_following',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_messages_time_delta_last_to_following',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_sequences_time_delta_first_to_first',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_yaml_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_sequences_time_delta_first_to_last',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_yaml_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_sequences_time_delta_last_to_first',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_yaml_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_sequences_time_delta_last_to_last',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_yaml_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_sequences_time_delta_first_to_following',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_yaml_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'find_sequences_time_delta_last_to_following',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_yaml_forward_step',
                 'action_scope': 'message',
                 'actions_config': True},
                {'action_name': 'verify_sequence_max_repeat',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'sequence',
                 'actions_info_type': 0,
                 'actions_config': ['max_repeat'],
                 'prepare': False,
                 'result': 'PASS'},
                {'action_name': 'verify_sequence_repeat',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'sequence',
                 'actions_info_type': 0,
                 'actions_config': ['repeat_num'],
                 'prepare': False,
                 'result': 'FAIL'},
                {'action_name': 'verify_sequence_min_repeat',
                 'message_extraction_requirements': 'None',
                 'action_flow_position': 'post_log_forward_step',
                 'action_scope': 'sequence',
                 'actions_info_type': 0,
                 'actions_config': ['min_repeat'],
                 'prepare': False,
                 'result': 'FAIL'},
                ]

    @staticmethod
    def define_regex_dict():
        """
        Defines the regex dictionary.
        Returns
            regex_dict: The regex dictionary.
        """
        return {
            'regular': {
                'regex_str': r"\[(\d*)] (\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2}):(\d{3}) <(.*?)> (.*)",
                'groups': {
                    'message_id': None,
                    'day': None,
                    'month': None,
                    'year': None,
                    'hours': None,
                    'minutes': None,
                    'seconds': None,
                    'microseconds': None,
                    'message_type': None,
                    'message_text': None}},
            'with_ignore_PC_time': {
                'regex_str': r"\d{2}-\d{2}-\d{4}-\d{2}:\d{2}:\d{2}::"
                             r"\[(\d*)] "
                             r"(\d{2})/(\d{2})/(\d{4}) "
                             r"(\d{2}):(\d{2}):(\d{2}):(\d{3}) <(.*?)> (.*)",
                'groups': {
                    'message_id': None,
                    'day': None,
                    'month': None,
                    'year': None,
                    'hours': None,
                    'minutes': None,
                    'seconds': None,
                    'microseconds': None,
                    'message_type': None,
                    'message_text': None}},
            'DU_PHY': {
                'regex_str': r"(.*)",
                'groups': {
                    'message_text': None}}}

    def get_regex_obj_by_log_type(self, regex_type):
        """
        Gets the regex object by the regex type.
        Arguments:
            regex_type: The regex type defined in the regex_dict.
        Returns:
            regex_obj: The regex Object.
            groups: The regex groups.
        """
        groups = None
        try:
            regex_str = self.regex_dict[regex_type]['regex_str']
            groups = self.regex_dict[regex_type]['groups']
        except Exception:
            regex_str = None
            frame_info = getframeinfo(currentframe())
            track_message = "Failed to get regex pattern, the log type doesn't exist."
            self.logger.error(frame_info, track_message)
        try:
            regex_obj = re.compile(regex_str)
        except Exception:
            regex_obj = None
            frame_info = getframeinfo(currentframe())
            track_message = "Failed to compile regex."
            self.logger.error(frame_info, track_message)
        return regex_obj, groups

    def preprocess(self,
                   log_list,
                   validate_input_info,
                   validation_state,
                   preprocess_args):
        """
        Pre-process the log files based on the input validation info object.
        Arguments:
            log_list: the input log file path.
            validate_input_info: the input validation result information.
            validation_state: the current validation state.
            preprocess_args: custom arguments for the preprocess function.
        Returns:
            flows_dict_list: A list of dictionaries with the flows' validation objects.
            validation_type: per_sequence_flow or per_message_flow.
            yaml_data: The YAML data object.
        """
        flows_dict_list = []
        message_flow_dict_list = []
        sequence_flow_dict_list = []
        validation_type = None
        if validate_input_info['yaml_data']['global_configuration'] and 'fail_messages' in validate_input_info['yaml_data']['global_configuration']:
            sequence_dict_list = []
            sequences_dict = {}
            for log_dict in log_list:
                message_flow_dict_list, validation_type = self.get_sequence_flow_dict(log_dict,
                                                                                      sequence_dict_list,
                                                                                      sequences_dict,
                                                                                      validate_input_info,
                                                                                      validation_state,
                                                                                      None,
                                                                                      sequence_flow_dict_list)
            if validation_type is None:
                return None, None, None
            if message_flow_dict_list:
                flows_dict_list.append(message_flow_dict_list)
        for log_dict in log_list:
            if 'sequence_flows' in validate_input_info['yaml_data']:
                for sequence_flow_name in validate_input_info['yaml_data']['sequence_flows']:
                    sequence_dict_list = []
                    sequences_dict = {}
                    if validate_input_info['yaml_data']['sequence_flows'][sequence_flow_name]['flow_configuration']['enabled'] == 'True':
                        if preprocess_args:
                            if 'start_message' in preprocess_args and 'end_message' in preprocess_args:
                                frame_info = getframeinfo(currentframe())
                                track_message = f"The preprocessing function preprocess_without_truncate was called but" \
                                                f" arguments for truncate where given."
                                self.logger.error(frame_info, track_message)
                            else:
                                sequence_flow_dict, validation_type = self.get_sequence_flow_dict(log_dict,
                                                                                                  sequence_dict_list,
                                                                                                  sequences_dict,
                                                                                                  validate_input_info,
                                                                                                  validation_state,
                                                                                                  sequence_flow_name,
                                                                                                  sequence_flow_dict_list,
                                                                                                  preprocess_args)
                                if validation_type is None:
                                    return None, None, None
                                if validation_type != 'skip':
                                    flows_dict_list.append(sequence_flow_dict)
                        else:
                            sequence_flow_dict, validation_type = self.get_sequence_flow_dict(log_dict,
                                                                                              sequence_dict_list,
                                                                                              sequences_dict,
                                                                                              validate_input_info,
                                                                                              validation_state,
                                                                                              sequence_flow_name,
                                                                                              sequence_flow_dict_list)
                            if validation_type is None:
                                return None, None, None
                            if validation_type != 'skip':
                                flows_dict_list.append(sequence_flow_dict)
                    else:
                        frame_info = getframeinfo(currentframe())
                        track_message = f"The flow: {validate_input_info['yaml_data']['sequence_flows'][sequence_flow_name]} is disabled."
                        self.logger.info(frame_info, track_message)
        return flows_dict_list, validation_type, validate_input_info['yaml_data']

    # def check_stream_processing(self, log_file_path, validate_input_info, validation_state, parsed_log_file_path, preprocess_args):
    #     """
    #     Gets the log file, the input validation object that contains the YAML data
    #     analyze the log and prints the results
    #     Arguments:
    #         log_file_path: the input log file path
    #         validate_input_info: the input validation result information
    #         validation_state: the current validation state
    #         parsed_log_file_path: the output file path that the parsed data is being written to
    #         preprocess_args: custom arguments for the preprocess function
    #     """
    #     test_logs_folder = r'C:\Users\rblumberg\main\backup\LogAnalyzerData\test_logs'
    #     for subdir, dirs, files in os.walk(test_logs_folder):
    #         for file in files:
    #             file_path = os.path.join(subdir, file)
    #             if os.path.splitext(file)[1] == '.log':
    #                 file_output_path = os.path.join(os.path.dirname(os.path.dirname(subdir)), 'test_logs_output', os.path.basename(subdir), file)
    #                 self.verify_clean_control_codes(file_path, file_output_path)

    def get_sequence_flow_dict(self,
                               log_dict,
                               sequence_dict_list,
                               sequences_dict,
                               validate_input_info,
                               validation_state,
                               sequence_flow_name,
                               sequence_flow_dict_list,
                               preprocess_args=None):
        """
        For each sequence in the flow  gets a dictionary containg it's log messages from the log file.
        Arguments:
            log_dict: The log dictionary.
            sequence_dict_list: A list that holds the expected sequence dictionary objects.
            sequences_dict: The entire sequences' dictionary.
            validate_input_info: The input validation result information.
            validation_state: The current validation state.
            sequence_flow_name: The name of the validated flow.
            sequence_flow_dict_list: A list that holds the flows dictionary objects.
            preprocess_args: Custom arguments for the preprocess function
        Returns:
            fail_messages_flow_dict: A fail message flow dictionary, if it exists
            validation_type: per_sequence_flow or per_message_flow.
        """
        flow_info, sequence_dict_list, sequences_dict, flow_fail_messages_list, actions_info, flow_configuration, validation_type, has_subsequence \
            = self.get_sequence_dict_list(validate_input_info['yaml_data'], sequence_flow_name, sequence_dict_list, sequences_dict, log_dict['log_type'], log_dict['device_name'])
        if not sequence_dict_list:
            return sequence_flow_dict_list, 'skip'
        # is_cleaned = self.clean_control_codes(log_dict['log_file_path'])
        # if not is_cleaned:
        #     return None, None
        if validation_type == 'per_sequence_flow':
            if flow_info['has_sub_flow']:
                sequence_dict_list = {}
                line_dict_list = []
                for sub_flow_name in flow_info:
                    if sub_flow_name == 'has_sub_flow':
                        continue
                    line_dict_list_sub_flow, test_lines_list = self.get_keywords_from_log(log_dict['log_file_path'],
                                                                                          flow_info[sub_flow_name]['sequence_dict_list'],
                                                                                          log_dict['regex_type'],
                                                                                          sub_flow_name)
                    flow_info[sub_flow_name]['ordered_line_dict_list'] = line_dict_list_sub_flow
                    line_dict_list.extend(line_dict_list_sub_flow)
            else:
                line_dict_list, test_lines_list = self.get_keywords_from_log(log_dict['log_file_path'], sequence_dict_list, log_dict['regex_type'], None)
            if not line_dict_list:
                frame_info = getframeinfo(currentframe())
                track_message = "No messages from the YAML file were found."
                self.logger.info(frame_info, track_message)
            ordered_line_dict_list = self.order_line_dict_list(line_dict_list)
            # self.write_test_lines(test_lines_list)
            # self.write_test_yaml(ordered_line_dict_list, parsed_log_file_path)
            if preprocess_args:
                if 'start_message' in preprocess_args or 'end_message' in preprocess_args:
                    truncated_ordered_line_dict_list = \
                        self.truncate_ordered_line_dict_list_by_time_stamp(validation_state['global_configuration'],
                                                                           validate_input_info['yaml_data']['sequence_flows'][sequence_flow_name]
                                                                           ['flow_configuration'],
                                                                           ordered_line_dict_list, preprocess_args)
                    ordered_line_dict_list = truncated_ordered_line_dict_list
                else:
                    frame_info = getframeinfo(currentframe())
                    track_message = "The function preprocess_with_truncate was called but there was no start_message or end_message."
                    self.logger.error(frame_info, track_message)
            log_final_sequence_num = len(ordered_line_dict_list)
            yaml_final_sequence = self.get_yaml_last_valid_sequence(sequence_dict_list)
            validation_state = self.init_validation_flow(
                ordered_line_dict_list,
                sequence_dict_list,
                validate_input_info['yaml_data'],
                sequence_flow_name,
                actions_info,
                flow_configuration,
                validation_type,
                log_final_sequence_num,
                yaml_final_sequence)
            validation_state['yaml_sequence_state']['current_yaml_sequence_dict'] = sequences_dict
            validation_state['validation_type'] = validation_type
            sequence_flow_dict = {
                'sequence_flow_name': f"{sequence_flow_name}_{log_dict['device_id']}",
                'sequence_flow_configuration': validate_input_info['yaml_data']['sequence_flows'][sequence_flow_name]['flow_configuration'],
                'device_id': log_dict['device_id'],
                'device_name': log_dict['device_name'],
                'flow_type_device_count': log_dict['flow_type_device_count'],
                'log_type': log_dict['log_type'],
                'log_file_path': log_dict['log_file_path'],
                'log_file_name': os.path.basename(log_dict['log_file_path']),
                'log_start_timestamp': log_dict['log_start_timestamp'],
                'log_end_timestamp': log_dict['log_end_timestamp'],
                'start_message_id': log_dict['start_message_id'],
                'end_message_id': log_dict['end_message_id'],
                'flow_fail_messages': flow_fail_messages_list,
                'flow_info': flow_info,
                'sequence_dict_list': sequence_dict_list,
                'sequences_dict': sequences_dict,
                'ordered_line_dict_list': ordered_line_dict_list,
                'validation_state': validation_state,
                'has_subsequence': has_subsequence}
            return sequence_flow_dict, validation_type
        elif validation_type == 'per_message_flow':
            if sequences_dict:
                if 'fail_messages' in sequences_dict:
                    sequence_flow_name = sequences_dict['sequence_name']
                    fail_messages_list, test_lines_list = self.get_fail_messages_from_log(log_dict['log_file_path'], sequence_dict_list, log_dict['regex_type'])
                    log_final_sequence_num = len(fail_messages_list)
                    yaml_final_sequence = self.get_yaml_last_valid_sequence(sequence_dict_list)
                    validation_state = self.init_validation_flow(
                        fail_messages_list,
                        None,
                        validate_input_info['yaml_data'],
                        sequence_flow_name,
                        actions_info,
                        flow_configuration,
                        validation_type,
                        log_final_sequence_num,
                        yaml_final_sequence)
                    if validation_state is None:
                        return None, None
                    validation_state['validation_type'] = validation_type
                    fail_messages_flow_dict = {
                        'sequence_flow_name': sequence_flow_name,
                        'global_fail_messages': sequences_dict['fail_messages'],
                        'global_fail_messages_list': fail_messages_list,
                        'validation_state': validation_state,
                        'device_id': log_dict['device_id'],
                        'device_name': log_dict['device_name'],
                        'flow_type_device_count': log_dict['flow_type_device_count'],
                        'log_type': log_dict['log_type'],
                        'log_file_path': log_dict['log_file_path'],
                        'log_file_name': os.path.basename(log_dict['log_file_path']),
                        'log_start_timestamp': log_dict['log_start_timestamp'],
                        'log_end_timestamp': log_dict['log_end_timestamp'],
                        'start_message_id': log_dict['start_message_id'],
                        'end_message_id': log_dict['end_message_id'],
                    }
                    return fail_messages_flow_dict, validation_type

    def get_sequence_flow_dict(self,
                               log_dict,
                               sequence_dict_list,
                               sequences_dict,
                               validate_input_info,
                               validation_state,
                               sequence_flow_name,
                               sequence_flow_dict_list,
                               preprocess_args=None):
        """
        For each sequence in the flow  gets a dictionary containg it's log messages from the log file.
        Arguments:
            log_dict: The log dictionary.
            sequence_dict_list: A list that holds the expected sequence dictionary objects.
            sequences_dict: The entire sequences' dictionary.
            validate_input_info: The input validation result information.
            validation_state: The current validation state.
            sequence_flow_name: The name of the validated flow.
            sequence_flow_dict_list: A list that holds the flows dictionary objects.
            preprocess_args: Custom arguments for the preprocess function
        Returns:
            fail_messages_flow_dict: A fail message flow dictionary, if it exists
            validation_type: per_sequence_flow or per_message_flow.
        """
        flow_info, sequence_dict_list, sequences_dict, flow_fail_messages_list, actions_info, flow_configuration, validation_type, has_subsequence \
            = self.get_sequence_dict_list(validate_input_info['yaml_data'], sequence_flow_name, sequence_dict_list, sequences_dict, log_dict['log_type'], log_dict['device_name'])
        if not sequence_dict_list:
            return sequence_flow_dict_list, 'skip'
        # is_cleaned = self.clean_control_codes(log_dict['log_file_path'])
        # is_cleaned = True
        # if not is_cleaned:
        #     return None, None
        if validation_type == 'per_sequence_flow':
            if flow_info['has_sub_flow']:
                sequence_dict_list = {}
                line_dict_list = []
                for sub_flow_name in flow_info:
                    if sub_flow_name == 'has_sub_flow':
                        continue
                    line_dict_list_sub_flow, test_lines_list = self.get_keywords_from_log(log_dict['log_file_path'],
                                                                                          flow_info[sub_flow_name]['sequence_dict_list'],
                                                                                          log_dict['regex_type'],
                                                                                          sub_flow_name)
                    flow_info[sub_flow_name]['ordered_line_dict_list'] = line_dict_list_sub_flow
                    line_dict_list.extend(line_dict_list_sub_flow)
            else:
                line_dict_list, test_lines_list = self.get_keywords_from_log(log_dict['log_file_path'], sequence_dict_list, log_dict['regex_type'], None)
            if not line_dict_list:
                frame_info = getframeinfo(currentframe())
                track_message = "No messages from the YAML file were found."
                self.logger.info(frame_info, track_message)
            ordered_line_dict_list = self.order_line_dict_list(line_dict_list)
            # self.write_test_lines(test_lines_list)
            # self.write_test_yaml(ordered_line_dict_list, parsed_log_file_path)
            if preprocess_args:
                if 'start_message' in preprocess_args or 'end_message' in preprocess_args:
                    truncated_ordered_line_dict_list = \
                        self.truncate_ordered_line_dict_list_by_time_stamp(validation_state['global_configuration'],
                                                                           validate_input_info['yaml_data']['sequence_flows'][sequence_flow_name]
                                                                           ['flow_configuration'],
                                                                           ordered_line_dict_list, preprocess_args)
                    ordered_line_dict_list = truncated_ordered_line_dict_list
                else:
                    frame_info = getframeinfo(currentframe())
                    track_message = "The function preprocess_with_truncate was called but there was no start_message or end_message."
                    self.logger.error(frame_info, track_message)
            log_final_sequence_num = len(ordered_line_dict_list)
            yaml_final_sequence = self.get_yaml_last_valid_sequence(sequence_dict_list)
            validation_state = self.init_validation_flow(
                ordered_line_dict_list,
                sequence_dict_list,
                validate_input_info['yaml_data'],
                sequence_flow_name,
                actions_info,
                flow_configuration,
                validation_type,
                log_final_sequence_num,
                yaml_final_sequence)
            validation_state['yaml_sequence_state']['current_yaml_sequence_dict'] = sequences_dict
            validation_state['validation_type'] = validation_type
            sequence_flow_dict = {
                'original_sequence_flow_name': sequence_flow_name,
                'sequence_flow_name': f"gnb_{log_dict['gnb_id']}_{sequence_flow_name}_{log_dict['device_id']}",
                'sequence_flow_configuration': validate_input_info['yaml_data']['sequence_flows'][sequence_flow_name]['flow_configuration'],
                'gnb_id': log_dict['gnb_id'],
                'gnb_name': log_dict['gnb_name'],
                'device_id': log_dict['device_id'],
                'device_name': log_dict['device_name'],
                'flow_type_device_count': log_dict['flow_type_device_count'],
                'log_type': log_dict['log_type'],
                'log_file_path': log_dict['log_file_path'],
                'log_file_name': os.path.basename(log_dict['log_file_path']),
                'log_start_timestamp': log_dict['log_start_timestamp'],
                'log_end_timestamp': log_dict['log_end_timestamp'],
                'start_message_id': log_dict['start_message_id'],
                'end_message_id': log_dict['end_message_id'],
                'flow_fail_messages': flow_fail_messages_list,
                'flow_info': flow_info,
                'sequence_dict_list': sequence_dict_list,
                'sequences_dict': sequences_dict,
                'ordered_line_dict_list': ordered_line_dict_list,
                'validation_state': validation_state,
                'has_subsequence': has_subsequence}
            return sequence_flow_dict, validation_type
        elif validation_type == 'per_message_flow':
            if sequences_dict:
                if 'fail_messages' in sequences_dict:
                    sequence_flow_name = sequences_dict['sequence_name']
                    fail_messages_list, test_lines_list = self.get_fail_messages_from_log(log_dict['log_file_path'], sequence_dict_list, log_dict['regex_type'])
                    log_final_sequence_num = len(fail_messages_list)
                    yaml_final_sequence = self.get_yaml_last_valid_sequence(sequence_dict_list)
                    validation_state = self.init_validation_flow(
                        fail_messages_list,
                        None,
                        validate_input_info['yaml_data'],
                        sequence_flow_name,
                        actions_info,
                        flow_configuration,
                        validation_type,
                        log_final_sequence_num,
                        yaml_final_sequence)
                    if validation_state is None:
                        return None, None
                    validation_state['validation_type'] = validation_type
                    fail_messages_flow_dict = {
                        'sequence_flow_name': sequence_flow_name,
                        'global_fail_messages': sequences_dict['fail_messages'],
                        'global_fail_messages_list': fail_messages_list,
                        'validation_state': validation_state,
                        'device_id': log_dict['device_id'],
                        'device_name': log_dict['device_name'],
                        'flow_type_device_count': log_dict['flow_type_device_count'],
                        'log_type': log_dict['log_type'],
                        'log_file_path': log_dict['log_file_path'],
                        'log_file_name': os.path.basename(log_dict['log_file_path']),
                        'log_start_timestamp': log_dict['log_start_timestamp'],
                        'log_end_timestamp': log_dict['log_end_timestamp'],
                        'start_message_id': log_dict['start_message_id'],
                        'end_message_id': log_dict['end_message_id'],
                    }
                    return fail_messages_flow_dict, validation_type

    def init_validation_flow(
            self,
            ordered_line_dict_list,
            sequence_dict_list,
            yaml_data,
            sequence_flow_name,
            actions_info,
            flow_configuration,
            validation_type,
            log_final_sequence_num,
            yaml_final_sequence):
        """
        Initialize the validation flow
        Arguments:
            ordered_line_dict_list: An ordered list that holds the parsed message log dictionary objects.
            sequence_dict_list: A list of sequence dictionaries.
            yaml_data: the YAML information that was parsed from the YAML input file.
            sequence_flow_name: the name of the validated flow.
            actions_info: An object that holds the actions' info.
            flow_configuration: The configuration of the flow.
            validation_type: The type of validation.
            log_final_sequence_num: the final sequence count
        Returns:
            validation_state: The current validation state.
        """
        validation_state = None
        if validation_type == 'per_sequence_flow':
            log_sequence_state = {
                'log_state_name': 'init',
                'log_sequence_num': 0,
                'log_subsequence_num': 0,
                'previous_log_sequence': 'init',
                'log_sequence': 'init',
                'next_log_sequence': {
                    'sequence_name': 'init'},
                'last_log_sequence_valid': False,
                'current_log_sequence_dict': {},
                'log_final_sequence_num': log_final_sequence_num,
            }
            yaml_sequence_state = {
                'yaml_state_name': 'init',
                'yaml_sequence_num': 0,
                'log_sequence_repeat': 0,
                'previous_yaml_sequence': 'init',
                'yaml_sequence': 'init',
                'next_yaml_sequence': {
                    'sequence_name': 'init'},
                'last_yaml_sequence_valid': False,
                'last_yaml_subsequence_valid': False,
                'sequence_flow_name': sequence_flow_name,
                'current_yaml_sequence_dict': {},
                'validated_yaml_sequence_dict': {},
                'yaml_final_sequence': yaml_final_sequence,
                'yaml_final_sequence_num': len(sequence_dict_list) - 1,
            }

            if flow_configuration is None:
                flow_configuration = 'None'
            global_configuration = yaml_data['global_configuration']
            validation_state = {
                'global_configuration': global_configuration,
                'flow_configuration': flow_configuration,
                'log_sequence_state': log_sequence_state,
                'yaml_sequence_state': yaml_sequence_state,
                'next_yaml_sequence_valid': True,
                'fails_num': 0,
                'fails_sequence_dicts': {
                    'flow_fail_message_passed': {},
                    'flow_fail_message_failed': {},
                    'global_fail_message_passed': {},
                    'global_fail_message_failed': {}
                },
                'valid': 'PASS',
                'validation_end': False,
                'validation_end_reason': None,
                'validation_info': {},
                'actions_info': actions_info}
        elif validation_type == 'per_message_flow':
            log_sequence_state = {
                'log_state_name': 'init',
                'log_sequence_num': 0,
                'previous_log_sequence': 'init',
                'log_sequence': 'init',
                'next_log_sequence': {
                    'sequence_name': 'init'},
                'last_log_sequence_valid': False,
                'current_log_sequence_dict': {},
            }
            if yaml_data['global_configuration'] is not None:
                global_configuration = yaml_data['global_configuration']
            else:
                global_configuration = 'None'
            validation_state = {
                'global_configuration': global_configuration,
                'log_sequence_state': log_sequence_state,
                'next_yaml_sequence_valid': True,
                'fails_num': 0,
                'fails_sequence_dicts': {
                    'flow_fail_message_passed': {},
                    'flow_fail_message_failed': {},
                    'global_fail_message_passed': {},
                    'global_fail_message_failed': {}
                },
                'valid': 'PASS',
                'validation_end': False,
                'validation_end_reason': None,
                'validation_info': {},
                'actions_info': actions_info}
        return validation_state

    @staticmethod
    def get_yaml_last_valid_sequence(yaml_sequence_list_or_dict):
        """
        Gets the last valid YAML sequence
        Arguments:
            yaml_sequence_list_or_dict: YAML sequence list or dictionary.
        Returns:
            yaml_sequence: The last YAML sequence.
        """
        if isinstance(yaml_sequence_list_or_dict, list):
            for sequence in yaml_sequence_list_or_dict[::-1]:
                if (('log_messages' in sequence) and sequence['log_messages']) or (
                        'has_subsequence' in sequence and sequence['has_subsequence']):
                    return sequence
        else:
            for sequence_name in list(yaml_sequence_list_or_dict.keys())[::-1]:
                if (('log_messages' in yaml_sequence_list_or_dict[sequence_name]) and yaml_sequence_list_or_dict[sequence_name]['log_messages']) or (
                        'has_subsequence' in yaml_sequence_list_or_dict[sequence_name] and yaml_sequence_list_or_dict[sequence_name]['has_subsequence']):
                    return yaml_sequence_list_or_dict[sequence_name]

    def get_sequence_dict_list(
            self,
            yaml_data,
            sequence_flow_name,
            sequence_dict_list,
            sequences_dict,
            log_type,
            device_name):
        """
        Gets a list of YAML sequences dictionaries
        Arguments:
            yaml_data: The YAML data object.
            sequence_flow_name: the name of the validated flow.
            sequence_dict_list: A list of sequence dictionaries.
            sequences_dict: The entire sequences' dictionary.
            log_type: The types of logs currently supported: CUCP, CUUP, DU_MAC, DU_PHY.
        Returns:
            sequence_dict_list: A list of sequence dictionaries.
            sequences_dict: The entire sequences' dictionary.
            actions_info: An object that holds the actions' info.
            validation_type: per_sequence_flow or per_message_flow.
            has_subsequence: Weather the sequence has subsequence or not.
        """
        actions_info = {}
        flow_fail_messages_list = []
        flow_configuration = None
        if sequence_flow_name:
            validation_type = 'per_sequence_flow'
            has_subsequence = None
            if any(key.startswith('sub_flow') for key in yaml_data['sequence_flows'][sequence_flow_name].keys()):
                flow_info = {'has_sub_flow': True}
            else:
                flow_info = {'has_sub_flow': False}
            for item_name in yaml_data['sequence_flows'][sequence_flow_name]:
                if item_name == 'flow_configuration':
                    flow_configuration = yaml_data['sequence_flows'][sequence_flow_name]['flow_configuration']
                    if 'flow_type' not in flow_configuration:
                        frame_info = getframeinfo(currentframe())
                        track_message = "flow_type is missing from flow configuration."
                        self.logger.error(frame_info, track_message)
                        return None, None, None, None, None, None, None, None
                    if flow_configuration['flow_type'] != log_type:
                        return None, None, None, None, None, None, None, None
                    if 'fail_messages' in flow_configuration:
                        sub_item_name = None
                        flow_fail_messages_list, _, is_actions_config_valid = self.convert_sequence_item_to_dict_list_multi_types(device_name,
                                                                                                                                  item_name,
                                                                                                                                  sub_item_name,
                                                                                                                                  flow_configuration['fail_messages'],
                                                                                                                                  {'message_text': None,
                                                                                                                                   'repeat_num': 0, 'max_repeat': 0}, None)
                        if not is_actions_config_valid:
                            return None, None, None, None, None, None, None, None
                else:
                    if flow_info and flow_info['has_sub_flow']:
                        sub_flow = yaml_data['sequence_flows'][sequence_flow_name][item_name]
                        sequence_dict_list = []
                        sequences_dict = {}
                        flow_info[item_name] = {}
                        flow_info[item_name]['sequence_dict_list'] = sequence_dict_list
                        if 'actions_info' not in flow_info[item_name]:
                            flow_info[item_name]['actions_info'] = {}
                        flow_info[item_name]['sequences_dict'] = sequences_dict
                        for sequence_name in sub_flow:
                            sequence_dict_list = self.extract_sequence(
                                sub_flow[sequence_name],
                                flow_info['has_sub_flow'],
                                item_name,
                                sequence_name,
                                flow_configuration,
                                sequences_dict,
                                sequence_dict_list,
                                flow_info[item_name]['actions_info'],
                                device_name)
                            actions_info.update(flow_info[item_name]['actions_info'])
                        if not sequence_dict_list:
                            return None, None, None, None, None, None, None, None
                    else:
                        flow_info[item_name] = {}
                        if 'actions_info' not in flow_info[item_name].keys():
                            flow_info[item_name]['actions_info'] = {}
                        sequence = yaml_data['sequence_flows'][sequence_flow_name][item_name]
                        sequence_dict_list = self.extract_sequence(
                            sequence,
                            False,
                            None,
                            item_name,
                            flow_configuration,
                            sequences_dict,
                            sequence_dict_list,
                            actions_info,
                            device_name)
                        if not sequence_dict_list:
                            return None, None, None, None, None, None, None, None
            if item_name != 'flow_configuration':
                return flow_info, \
                    sequence_dict_list, \
                    sequences_dict, \
                    flow_fail_messages_list, \
                    actions_info, \
                    flow_configuration, \
                    validation_type, \
                    has_subsequence
            else:
                return flow_info, \
                    sequence_dict_list, \
                    sequences_dict, \
                    flow_fail_messages_list, \
                    None, \
                    flow_configuration, \
                    validation_type, \
                    has_subsequence
        else:
            flow_info = {'has_sub_flow': False}
            validation_type = 'per_message_flow'
            if 'fail_messages' in yaml_data['global_configuration']:
                sub_item_name = None
                has_subsequence = False
                flow_fail_messages_list, actions_info, is_actions_config_valid = \
                    self.convert_sequence_item_to_dict_list_multi_types(device_name,
                                                                        'fail_messages',
                                                                        sub_item_name,
                                                                        yaml_data['global_configuration']['fail_messages'],
                                                                        {'message_text': None,
                                                                         'repeat_num': 0},
                                                                        actions_info)
                if not is_actions_config_valid:
                    return None, None, None, None, None, None, None, None
                sequences_dict = {'sequence_name': 'global_fail_messages',
                                  'fail_messages': flow_fail_messages_list}
                sequence_dict_list.append(sequences_dict)
                return flow_info, sequence_dict_list, sequences_dict, None, actions_info, None, validation_type, has_subsequence

    def extract_sequence(self, sequence,
                         in_sub_flow,
                         sub_flow_name,
                         item_name,
                         flow_configuration,
                         sequences_dict,
                         sequence_dict_list,
                         actions_info,
                         device_name):
        """
        Extract sequence data
        Arguments:
            sequence: The sequence being extracted.
            in_sub_flow: Weather the sequence is inside a sub-flow or not.
            sub_flow_name: The name of the sub-flow.
            item_name: The name of the sequence.
            flow_configuration: The flow configuration object.
            sequences_dict: The entire sequences' dictionary.
            sequence_dict_list: A list of sequence dictionaries.
            actions_info: An object that holds the actions' info.
        Returns:
            sequence_dict_list: A list of sequence dictionaries.
        """
        fail_messages_list = []
        log_messages = None
        if any(sub_item_name.startswith('subsequence') for sub_item_name in sequence):
            has_subsequence = True
            if 'fail_messages' in sequence:
                sub_item_name = None
                fail_messages_list, _, is_actions_config_valid = self.convert_sequence_item_to_dict_list_multi_types(device_name,
                                                                                                                     item_name,
                                                                                                                     sub_item_name,
                                                                                                                     flow_configuration['fail_messages'],
                                                                                                                     {'message_text': None,
                                                                                                                      'repeat_num': 0,
                                                                                                                      'max_repeat': 0}, None)
                if not is_actions_config_valid:
                    return None
            sequence_dict = {
                'sequence_num': self.compiled_regexes['sequence'].search(item_name).groups()[-1],
                'sequence_name': item_name,
                'fail_messages': fail_messages_list,
                'has_subsequence': has_subsequence,
                'in_sub_flow': in_sub_flow,
                'sub_flow_name': sub_flow_name,
                'sequence_valid_count': 0,
                'subsequences_dict': {},
                'curr_subsequence_index': 0}
            subsequence_index = 0
            sequence_identifier = None
            for sub_item_name in sequence:
                if sub_item_name == 'sequence_identifier':
                    sequence_identifier = sequence['sequence_identifier']
                    sequence_dict['sequence_identifier'] = sequence_identifier
                elif 'log_messages' in sequence[sub_item_name]:
                    log_messages, actions_info, is_actions_config_valid = \
                        self.convert_sequence_item_to_dict_list_multi_types(device_name,
                                                                            item_name,
                                                                            sub_item_name,
                                                                            sequence[sub_item_name]['log_messages'],
                                                                            {'message_text': None,
                                                                             'repeat_num': 0,
                                                                             'sequence_identifier': sequence_identifier,
                                                                             'subsequence_name': sub_item_name},
                                                                            actions_info)
                    if not is_actions_config_valid:
                        return None
                    subsequence_dict = {
                        'subsequence_index': subsequence_index,
                        'subsequence_num': self.compiled_regexes['sequence'].search(item_name).groups()[-1],
                        'subsequence_name': sub_item_name,
                        'sequence_identifier': sequence_identifier,
                        'subsequence_log_messages': log_messages,
                        'sub_fail_messages': fail_messages_list,
                        'validated': False}
                    sequence_dict['subsequences_dict'][subsequence_dict['subsequence_name']
                    ] = subsequence_dict
                    sequence_dict['subsequence_final_index'] = subsequence_index
                    sequences_dict[item_name] = sequence_dict
                    subsequence_index += 1
                    if not log_messages:
                        frame_info = getframeinfo(currentframe())
                        track_message = "Failed to convert log message to dictionary."
                        self.logger.error(frame_info, track_message)
                        return None
            # if 'actions' in sequence:
            #     sequence_dict['actions'] = {}
            #     actions_info[sequence_identifier] = {}
            #     _ = self.get_actions_sequence(item_name,
            #                                   sequence_dict,
            #                                   actions_info)
            sequence_dict_list.append(sequence_dict)
        elif 'log_messages' in sequence:
            has_subsequence = False
            sub_item_name = None
            log_messages, actions_info, is_actions_config_valid = self.convert_sequence_item_to_dict_list_multi_types(device_name,
                                                                                                                      item_name,
                                                                                                                      sub_item_name,
                                                                                                                      sequence['log_messages'],
                                                                                                                      {'message_text': None, 'repeat_num': 0},
                                                                                                                      actions_info)
            if not is_actions_config_valid:
                return None
            if not log_messages:
                frame_info = getframeinfo(currentframe())
                track_message = "Failed to convert log message to dictionary."
                self.logger.error(frame_info, track_message)
                return None
            sequence_dict = {
                'sequence_num': self.compiled_regexes['sequence'].search(item_name).groups()[
                    -1],
                'sequence_name': item_name,
                'has_subsequence': has_subsequence,
                'log_messages': log_messages,
                'fail_messages': fail_messages_list}
            try:
                sequence_dict_list.append(sequence_dict)
            except:
                pass
            sequences_dict[item_name] = sequence_dict
        else:
            log_messages = None
        if 'fail_messages' in sequence:
            fail_messages_list, _, is_actions_config_valid = self.convert_sequence_item_to_dict_list_multi_types(device_name,
                                                                                                                 item_name,
                                                                                                                 'fail_messages',
                                                                                                                 sequence['fail_messages'],
                                                                                                                 {'message_text': None,
                                                                                                                  'repeat_num': 0,
                                                                                                                  'max_repeat': 0},
                                                                                                                 None)
            if not is_actions_config_valid:
                return None
            sequence_dict = {'sequence_num': self.compiled_regexes['sequence'].search(item_name).groups()[-1],
                             'sequence_name': item_name,
                             'log_messages': log_messages,
                             'fail_messages': fail_messages_list}
            sequence_dict_list.append(sequence_dict)
            sequences_dict[item_name] = sequence_dict
        if not any('messages' in sub_item_name for sub_item_name in sequence) and not any(
                sub_item_name.startswith('subsequence') for sub_item_name in sequence):
            frame_info = getframeinfo(currentframe())
            track_message = "There is a sequence with no log messages or subsequence."
            self.logger.error(frame_info, track_message)
        return sequence_dict_list

    def parse_timestamps(self, flow_configuration):
        """
        Parses timestamps
        Arguments:
            flow_configuration: The flow configuration object.
        Returns:
            start_message_timestamp_datetime: The start datetime object from the timestamp string.
            end_message_timestamp_datetime: The end datetime object from the timestamp string.
        """
        start_message_timestamp_datetime = None
        end_message_timestamp_datetime = None
        if 'start_message' in flow_configuration:
            start_message = flow_configuration['start_message']
            if 'message_timestamp' in start_message:
                message_timestamp = start_message['message_timestamp']
                try:
                    start_message_timestamp_datetime = datetime.datetime.strptime(
                        message_timestamp, '%d/%m/%Y %H:%M:%S:%f')
                except Exception:
                    frame_info = getframeinfo(currentframe())
                    track_message = "unable to parse start message timestamp."
                    self.logger.error(frame_info, track_message)
        if 'end_message' in flow_configuration:
            end_message = flow_configuration['end_message']
            if 'message_timestamp' in end_message:
                message_timestamp = end_message['message_timestamp']
                try:
                    end_message_timestamp_datetime = datetime.datetime.strptime(
                        message_timestamp, '%d/%m/%Y %H:%M:%S:%f')
                except Exception:
                    frame_info = getframeinfo(currentframe())
                    track_message = "unable to parse end message timestamp."
                    self.logger.error(frame_info, track_message)
        return start_message_timestamp_datetime, end_message_timestamp_datetime

    def truncate_ordered_line_dict_list_by_time_stamp(
            self,
            global_configuration,
            flow_configuration,
            ordered_line_dict_list,
            preprocess_args):
        """
        Truncates the ordered_line_dict by given timestamp
        Arguments:
            global_configuration: The global configuration object.
            flow_configuration: The flow configuration object.
            ordered_line_dict_list: An ordered list that holds the parsed message log dictionary objects.
            preprocess_args: Custom arguments for the preprocess function
        Returns:
            truncated_ordered_line_dict_list: An ordered list that holds the truncated parsed message log dictionary objects.
        """
        for configuration in [
            global_configuration,
            flow_configuration,
            preprocess_args]:
            start_message_timestamp_datetime, end_message_timestamp_datetime = self.parse_timestamps(
                configuration)
            truncated_ordered_line_dict_list = []
            if start_message_timestamp_datetime is not None and end_message_timestamp_datetime is not None:
                for line_dict in ordered_line_dict_list:
                    if line_dict['datetime'] <= end_message_timestamp_datetime:
                        if line_dict['datetime'] >= start_message_timestamp_datetime:
                            truncated_ordered_line_dict_list.append(line_dict)
                    else:
                        break
            elif start_message_timestamp_datetime is not None and end_message_timestamp_datetime is None:
                for line_dict in ordered_line_dict_list:
                    if line_dict['datetime'] >= start_message_timestamp_datetime:
                        truncated_ordered_line_dict_list.append(line_dict)
            elif start_message_timestamp_datetime is None and end_message_timestamp_datetime is not None:
                for line_dict in ordered_line_dict_list:
                    if line_dict['datetime'] <= end_message_timestamp_datetime:
                        truncated_ordered_line_dict_list.append(line_dict)
                    else:
                        break
            elif start_message_timestamp_datetime is None and end_message_timestamp_datetime is None:
                truncated_ordered_line_dict_list = ordered_line_dict_list
        return truncated_ordered_line_dict_list

    def convert_sequence_item_to_dict_list_multi_types(self,
                                                       device_name,
                                                       item_name,
                                                       sub_item_name,
                                                       sequence_items,
                                                       attributes_dict,
                                                       actions_info):
        """
        Converts sequence item to dict list (fail_log_message or log_message).
        Arguments:
            item_name: The name of the sequence.
            sub_item_name: The name of the sub-sequence.
            sequence_items: The items in the sequence.
            attributes_dict: The attributes' dictionary.
            actions_info: An object that holds the actions' info.
        Returns:
            sequence_item_to_dict_list: list of the sequence dictionary items.
            actions_info: An object that holds the actions' info.
        """
        sequence_item_to_dict_list = []
        is_actions_config_valid = None
        if len(sequence_items) > 0:
            for sequence_sub_item in sequence_items:
                if 'fail_log_message' in sequence_sub_item:
                    sequence_item_dict = {'fail_message_num': self.compiled_regexes['fail_log_message'].search(sequence_sub_item).groups()[-1], 'fail_message_name': sequence_sub_item}
                    if 'max_repeat' in sequence_items[sequence_sub_item]:
                        attributes_dict['max_repeat'] = sequence_items[sequence_sub_item]['max_repeat']
                    else:
                        attributes_dict['max_repeat'] = 1
                    is_actions_config_valid = self.convert_sequence_item_to_dict_list(device_name,
                                                                                      item_name,
                                                                                      sub_item_name,
                                                                                      sequence_items,
                                                                                      attributes_dict,
                                                                                      actions_info,
                                                                                      sequence_sub_item,
                                                                                      sequence_item_dict,
                                                                                      sequence_item_to_dict_list)
                    if not is_actions_config_valid:
                        return None, None, None
                elif 'log_message' in sequence_sub_item:
                    sequence_item_dict = {'log_message_num': self.compiled_regexes['log_message'].search(sequence_sub_item).groups()[-1], 'log_message_name': sequence_sub_item}
                    is_actions_config_valid = self.convert_sequence_item_to_dict_list(device_name,
                                                                                      item_name,
                                                                                      sub_item_name,
                                                                                      sequence_items,
                                                                                      attributes_dict,
                                                                                      actions_info,
                                                                                      sequence_sub_item,
                                                                                      sequence_item_dict,
                                                                                      sequence_item_to_dict_list)
                    if not is_actions_config_valid:
                        return None, None, None
        return sequence_item_to_dict_list, actions_info, is_actions_config_valid

    def convert_sequence_item_to_dict_list(self,
                                           device_name,
                                           item_name,
                                           sub_item_name,
                                           sequence_items,
                                           attributes_dict,
                                           actions_info,
                                           sequence_sub_item,
                                           sequence_item_dict,
                                           sequence_item_to_dict_list):
        """
        Appends to the sequence items dictionary list (fail_log_message or log_message).
        Arguments:
            item_name: The name of the sequence.
            sub_item_name: The name of the sub-sequence.
            sequence_items: The items in the sequence.
            attributes_dict: The attributes' dictionary.
            actions_info: An object that holds the actions' info.
            sequence_sub_item: The sequence sub-item.
            sequence_item_dict: A sequence item dictionary.
            sequence_item_to_dict_list: A sequence items dictionary list.
        """
        for attribute in attributes_dict:
            if attributes_dict[attribute] is None:
                sequence_item_dict[attribute] = sequence_items[sequence_sub_item][attribute]
            else:
                sequence_item_dict[attribute] = attributes_dict[attribute]
        if sub_item_name:
            sequence_item_dict['in_subsequence'] = True
            sequence_item_dict['subsequence_name'] = sub_item_name
        if 'has_regex' in sequence_items[sequence_sub_item] and sequence_items[sequence_sub_item]['has_regex']:
            sequence_item_dict['has_regex'] = True
            sequence_item_dict['compiled_regex'] = re.compile(
                sequence_items[sequence_sub_item]['message_text'])
        if 'actions' in sequence_items[sequence_sub_item]:
            sequence_item_dict['actions'] = {}
            actions_info[sequence_sub_item] = {}
            is_actions_config_valid = self.get_actions(device_name,
                                                       sequence_items,
                                                       item_name,
                                                       sequence_item_dict,
                                                       sequence_sub_item,
                                                       actions_info)
        else:
            is_actions_config_valid = True
        if is_actions_config_valid:
            sequence_item_to_dict_list.append(sequence_item_dict)
        return is_actions_config_valid

    def get_actions(
            self,
            device_name,
            sequence_items,
            item_name,
            sequence_item_dict,
            sequence_sub_item,
            actions_info):
        """
        Gets actions from the sequence items.
        Arguments:
            sequence_items: The items in the sequence.
            item_name: The name of the sequence.
            sequence_item_dict: A sequence item dictionary.
            sequence_sub_item: The sequence sub-item.
            actions_info: An object that holds the actions' info.
        Returns:
            actions_info: An object that holds the actions' info.
        """
        for action in sequence_items[sequence_sub_item]['actions']:
            if sequence_items[sequence_sub_item]['actions'][action] and 'action_name' in sequence_items[sequence_sub_item]['actions'][action]:
                action_name = sequence_items[sequence_sub_item]['actions'][action]['action_name']
                action_type = self.get_action_type(action_name)
                if action_type:
                    action_flow_position = action_type['action_flow_position']
                    if action_flow_position not in sequence_item_dict['actions']:
                        sequence_item_dict['actions'][action_flow_position] = []
                    if 'action_config' in sequence_items[sequence_sub_item]['actions'][action]:
                        action_dict = {
                            'action_name': action_name,
                            'action_config': sequence_items[sequence_sub_item]['actions'][action]['action_config'],
                            'action_flow_position': action_flow_position}
                    else:
                        action_dict = {
                            'action_name': action_name,
                            'action_flow_position': action_flow_position}
                    sequence_item_dict['actions'][action_flow_position].append(action_dict)
                    sequence_item_dict['actions']['message_extraction_requirements'] = action_type['message_extraction_requirements']
                    if sequence_sub_item not in actions_info:
                        actions_info[sequence_sub_item] = {}
                    actions_info[sequence_sub_item][action_type['action_name']] = {}
                    actions_info[sequence_sub_item][action_type['action_name']]['action_info'] = {}
                    actions_info[sequence_sub_item][action_type['action_name']]['action_info']['global_action_info'] = {}
                    actions_info[sequence_sub_item][action_type['action_name']]['action_sequence_name'] = item_name
                    if 'message_text' in sequence_items[sequence_sub_item]:
                        actions_info[sequence_sub_item][action_type['action_name']
                        ]['action_message_text'] = sequence_items[sequence_sub_item]['message_text']
                    actions_info[sequence_sub_item][action_type['action_name']]['action_name'] = action_type['action_name']
                    actions_info[sequence_sub_item][action_type['action_name']]['action_info'][device_name] = copy.deepcopy(action_type['actions_info_type'])
                    if action_type['actions_config']:
                        if 'action_config' in sequence_items[sequence_sub_item]['actions'][action]:
                            action_config_valid, config, track_message = self.validate_action_config(action_type, sequence_items, sequence_sub_item, action)
                            if not action_config_valid:
                                frame_info = getframeinfo(currentframe())
                                self.logger.error(frame_info, track_message)
                                return False
                            actions_info[sequence_sub_item][action_type['action_name']]['action_config'] = \
                                sequence_items[sequence_sub_item]['actions'][action]['action_config']
                        else:
                            frame_info = getframeinfo(currentframe())
                            track_message = "An action requires action config, but it's missing."
                            self.logger.error(frame_info, track_message)
                            return False
                    actions_info[sequence_sub_item][action_type['action_name']]['output_str'] = ''
                    actions_info[sequence_sub_item][action_type['action_name']]['result'] = action_type['result']
                    actions_info[sequence_sub_item][action_type['action_name']]['prepare'] = action_type['prepare']
                else:
                    frame_info = getframeinfo(currentframe())
                    track_message = f'action: {action_name} is not a valid type'
                    self.logger.error(frame_info, track_message)
            else:
                frame_info = getframeinfo(currentframe())
                track_message = "action was specified but an action name wasn't specified."
                self.logger.error(frame_info, track_message)
                return False
        return actions_info

    # def get_actions_sequence(self,
    #                          item_name,
    #                          sequence_dict,
    #                          actions_info):
    #     """
    #     Gets actions from the sequence items.
    #     Arguments:
    #         sequence_items: The items in the sequence.
    #         item_name: The name of the sequence.
    #         sequence_item_dict: A sequence item dictionary.
    #         sequence_sub_item: The sequence sub-item.
    #         actions_info: An object that holds the actions' info.
    #     Returns:
    #         actions_info: An object that holds the actions' info.
    #     """
    #     for action in sequence_dict['actions']:
    #         if sequence_items[sequence_sub_item]['actions'][action] and 'action_name' in sequence_items[sequence_sub_item]['actions'][action]:
    #             action_name = sequence_items[sequence_sub_item]['actions'][action]['action_name']
    #             action_type = self.get_action_type(action_name)
    #             if action_type:
    #                 action_flow_position = action_type['action_flow_position']
    #                 if action_flow_position not in sequence_item_dict['actions']:
    #                     sequence_item_dict['actions'][action_flow_position] = [
    #                     ]
    #                 if 'action_config' in sequence_items[sequence_sub_item]['actions'][action]:
    #                     action_dict = {
    #                         'action_name': action_name,
    #                         'action_config': sequence_items[sequence_sub_item]['actions'][action]['action_config'],
    #                         'action_flow_position': action_flow_position}
    #                 else:
    #                     action_dict = {
    #                         'action_name': action_name,
    #                         'action_flow_position': action_flow_position}
    #                 sequence_item_dict['actions'][action_flow_position].append(
    #                     action_dict)
    #                 sequence_item_dict['actions']['message_extraction_requirements'] = action_type['message_extraction_requirements']
    #                 if sequence_sub_item not in actions_info:
    #                     actions_info[sequence_sub_item] = {}
    #                 actions_info[sequence_sub_item][action_type['action_name']] = {}
    #                 actions_info[sequence_sub_item][action_type['action_name']
    #                                                 ]['action_sequence_name'] = item_name
    #                 if 'message_text' in sequence_items[sequence_sub_item]:
    #                     actions_info[sequence_sub_item][action_type['action_name']
    #                                                     ]['action_message_text'] = sequence_items[sequence_sub_item]['message_text']
    #                 actions_info[sequence_sub_item][action_type['action_name']
    #                                                 ]['action_name'] = action_type['action_name']
    #                 actions_info[sequence_sub_item][action_type['action_name']
    #                                                 ]['action_info'] = action_type['actions_info_type']
    #                 if action_type['actions_config']:
    #                     if 'action_config' in sequence_items[sequence_sub_item]['actions'][action]:
    #                         action_config_valid, config = self.validate_action_config(
    #                             action_type, sequence_items, sequence_sub_item, action)
    #                         if not action_config_valid:
    #                             frame_info = getframeinfo(currentframe())
    #                             track_message = "action_config information invalid."
    #                             self.logger.error(frame_info, track_message)
    #                             return None, None
    #                         actions_info[sequence_sub_item][action_type['action_name']]['action_config'] = \
    #                             sequence_items[sequence_sub_item]['actions'][action]['action_config']
    #                     else:
    #                         frame_info = getframeinfo(currentframe())
    #                         track_message = "An action requires action config, but it's missing."
    #                         self.logger.error(frame_info, track_message)
    #                         return None, None
    #                 actions_info[sequence_sub_item][action_type['action_name']
    #                                                 ]['output_str'] = ''
    #                 actions_info[sequence_sub_item][action_type['action_name']
    #                                                 ]['result'] = action_type['result']
    #                 actions_info[sequence_sub_item][action_type['action_name']
    #                                                 ]['prepare'] = action_type['prepare']
    #             else:
    #                 frame_info = getframeinfo(currentframe())
    #                 track_message = f'action: {action_name} is not a valid type'
    #                 self.logger.error(frame_info, track_message)
    #         else:
    #             frame_info = getframeinfo(currentframe())
    #             track_message = "action was specified but an action name wasn't specified."
    #             self.logger.error(frame_info, track_message)
    #             return None
    #     return actions_info

    @staticmethod
    def validate_action_config(action_type,
                               sequence_items,
                               sequence_sub_item,
                               action):
        """
        Validates action config
        Arguments:
            action_type: The action type.
            sequence_items: The items in the sequence.
            sequence_sub_item: The sequence sub-item.
            action: The action.
        Returns:
            action_config_valid: Weather the action's config is valid.
            config: The action config.
        """
        for config in action_type['actions_config']:
            if config not in sequence_items[sequence_sub_item]['actions'][action]['action_config']:
                track_message = f"The definition of the action: {action_type['action_name']} contains a configuration: {config}, " \
                                f"but it was missing in the action configuration in the YAML."
                return False, config, track_message
        for config in sequence_items[sequence_sub_item]['actions'][action]['action_config']:
            if config not in action_type['actions_config']:
                track_message = f"The the action configuration in the YAML of the action: {sequence_items[sequence_sub_item]['actions'][action]['action_name']} " \
                                f"contains a configuration: {config}, but this configuration is not in the action definitions."
                return False, config, track_message
        return True, None, None

    def get_sed_random_lines(self, num_of_lines, log_file_path):
        line_count = self.get_file_line_count(log_file_path)
        if line_count == 'sed_missing':
            return 'sed_missing'
        if (line_count or line_count == 0) and line_count <= num_of_lines:
            return False
        if os.path.isfile(self.sed_executable_path):
            lines_list = random.sample(range(1, line_count), num_of_lines)
            results = []
            for line_num in lines_list:
                random_line_sed_str = f'{line_num}q;d'
                result = subprocess.run(
                    [self.sed_executable_path, random_line_sed_str, log_file_path], stdout=subprocess.PIPE)
                try:
                    results.append(result.stdout.decode("utf-8"))
                except UnicodeDecodeError:
                    last_line_str = result.stdout.decode("unicode_escape")
            return results

    def get_sed_first_line(self, log_file_path, num_of_test_lines, regex_type):
        if os.path.isfile(self.sed_executable_path):
            regex_obj, groups = self.get_regex_obj_by_log_type(regex_type)
            log_message_dict = {'log_message_name': 'first_line'}
            first_test_lines_sed_str = f'{num_of_test_lines}q;'
            result = subprocess.run([self.sed_executable_path, first_test_lines_sed_str, log_file_path], stdout=subprocess.PIPE)
            first_test_lines_str = result.stdout.decode("utf-8")
            for line in first_test_lines_str.splitlines():
                line_dict = self.parse_line(
                    'first_line',
                    log_message_dict,
                    line,
                    regex_obj,
                    groups,
                    None,
                    None,
                    None,
                    'log_message',
                    False)
                if line_dict:
                    if line_dict['datetime'] and line_dict['message_id']:
                        return line_dict['datetime'], int(line_dict['message_id'])
                    else:
                        pass

            frame_info = getframeinfo(currentframe())
            track_message = f'Getting of the log file: \n{log_file_path}\nfirst message timestamp and id has failed.'
            self.logger.info(frame_info, track_message)
            return None, None
        else:
            frame_info = getframeinfo(currentframe())
            track_message = 'The sed GNU windows application is not installed, or is not at the default path.\n' \
                            'please run with admin privileges the environment preparation PowerShell script located at: ' \
                            r'"\\192.168.126.182\c$\Environment Installation\powershell_scripts-master\install_scripts\install_LogAnalyzer_requirements.ps1".'
            self.logger.error(frame_info, track_message)
            return None, None

    def run_powershell_command(self, cmd):
        powershell_command = ["powershell", "-Command"]
        powershell_command.extend(cmd)
        p = subprocess.Popen(powershell_command, stdout=subprocess.PIPE)
        command_result, p_err = p.communicate()
        return command_result

    def get_sed_last_line(self, log_file_path, num_of_test_lines, regex_type):
        if os.path.isfile(self.sed_executable_path):
            regex_obj, groups = self.get_regex_obj_by_log_type(regex_type)
            log_message_dict = {}
            log_message_dict['log_message_name'] = 'last_line'
            last_line_str = self.run_powershell_command(["Get-Content", f"'{os.path.abspath(log_file_path)}'", "-Tail 10"])
            last_line_str = last_line_str.decode("utf-8")
            for line in last_line_str.splitlines()[::-1]:
                line_dict = self.parse_line(
                    'last_line',
                    log_message_dict,
                    line,
                    regex_obj,
                    groups,
                    None,
                    None,
                    None,
                    'log_message',
                    False)
                if line_dict:
                    if line_dict['datetime'] and line_dict['message_id']:
                        return line_dict['datetime'], int(line_dict['message_id'])
                    else:
                        return None, None
                frame_info = getframeinfo(currentframe())
                track_message = f'Getting of the log file: \n{log_file_path}\nlast message timestamp and id has failed.'
                self.logger.info(frame_info, track_message)
                return None, None
        else:
            frame_info = getframeinfo(currentframe())
            track_message = 'The sed GNU windows application is not installed, or is not at the default path.\n' \
                            'please run with admin privileges the environment preparation PowerShell script located at: ' \
                            r'"\\192.168.126.182\c$\Environment Installation\powershell_scripts-master\install_scripts\install_LogAnalyzer_requirements.ps1".'
            self.logger.error(frame_info, track_message)
            return None, None

    def check_regex_type(self, flow_type, log_file_path):
        """
        Checks which regex type is compatible to the current log file.
        Arguments:
            flow_type: The flow type.
            log_file_path: The input log file path.
        Returns:
            regex_type: The compatible regex type for the current log.
        """
        if flow_type == 'DU_PHY':
            regex_type = flow_type
            return regex_type
        else:
            num_of_lines = 20
            random_lines = self.get_sed_random_lines(num_of_lines, log_file_path)
            if random_lines == 'sed_missing':
                return 'sed_missing'
            if random_lines:
                for regex_type_name in self.regex_dict:
                    if regex_type_name == 'DU_PHY':
                        continue
                    regex_obj, groups = self.get_regex_obj_by_log_type(regex_type_name)
                    success_count = 0
                    for random_line in random_lines:
                        is_line_parsed = self.check_parse_line(regex_obj, random_line)
                        if is_line_parsed:
                            success_count += 1
                    self.regex_dict[regex_type_name]['success_count'] = success_count
                max_success_regex_type = self.get_max_success_regex(log_file_path)
                return max_success_regex_type
            else:
                frame_info = getframeinfo(currentframe())
                track_message = f"The log file had less than {num_of_lines} lines."
                self.logger.info(frame_info, track_message)
                return 'regular'

    def get_max_success_regex(self, log_file_path):
        """
        Gets the regex with the maximum count of compatible log lines.
        Arguments:
            log_file_path: The input log file path.
        Returns:
            max_success_regex_type: The regex with maximum count of compatible log lines.
        """
        max_success_regex_count = 0
        for regex_type_name in self.regex_dict:
            if regex_type_name == 'DU_PHY':
                continue
            if self.regex_dict[regex_type_name]['success_count'] > max_success_regex_count:
                max_success_regex_count = self.regex_dict[regex_type_name]['success_count']
        max_success_regex_type_list = []
        for regex_type_name in self.regex_dict:
            if regex_type_name == 'DU_PHY':
                continue
            if self.regex_dict[regex_type_name]['success_count'] == max_success_regex_count:
                max_success_regex_type_list.append(regex_type_name)
        if len(max_success_regex_type_list) > 1:
            if 'regular' not in max_success_regex_type_list:
                frame_info = getframeinfo(currentframe())
                track_message = f"More than one regex type has matched the log file: {log_file_path}."
                self.logger.error(frame_info, track_message)
                return None
            else:
                return max_success_regex_type_list[0]
        else:
            return max_success_regex_type_list[0]

    @staticmethod
    def check_parse_line(regex_obj, random_line):
        """
        Check weather a regex is compatible with a random log line.
        Arguments:
            regex_obj: The regex Object.
            random_line: A random log line.
        Returns:
            is_line_parsed: Weather the line was parsed successfully by the regex object.
        """
        match = regex_obj.match(random_line)
        if not match:
            return False
        else:
            return True

    def get_file_line_count(self, log_file_path):
        """
        Gets how many lines are in the log file.
        Arguments:
            log_file_path: The input log file path.
        Returns:
            line_count: Number of lines in the log file.
        """
        if os.path.isfile(self.sed_executable_path):
            result = subprocess.run(
                [self.sed_executable_path, '-n', "$=", log_file_path], stdout=subprocess.PIPE)
            result_str = result.stdout.decode("utf-8").replace('\r\n', '')
            if result_str:
                line_count = int(result.stdout.decode("utf-8").replace('\r\n', ''))
            else:
                line_count = 0
            if line_count == 1:
                self.replace_line_ending(log_file_path)
                result = subprocess.run([self.sed_executable_path, '-n', "$=", log_file_path], stdout=subprocess.PIPE)
                result_str = result.stdout.decode("utf-8").replace('\r\n', '')
                if result_str:
                    line_count = int(result.stdout.decode("utf-8").replace('\r\n', ''))
                else:
                    line_count = 0
            return line_count
        else:
            frame_info = getframeinfo(currentframe())
            track_message = 'The sed GNU windows application is not installed, or is not at the default path.\n' \
                            'please run with admin privileges the environment preparation PowerShell script located at: ' \
                            r'"\\192.168.126.182\c$\Environment Installation\powershell_scripts-master\install_scripts\install_LogAnalyzer_requirements.ps1".'
            self.logger.error(frame_info, track_message)
            return 'sed_missing'

    def replace_line_ending(self, file_path):
        WINDOWS_LINE_ENDING = r'\r\n'
        UNIX_LINE_ENDING = r'\n'
        with open(file_path, 'r') as open_file:
            content = open_file.read()
        content = content.replace(UNIX_LINE_ENDING, WINDOWS_LINE_ENDING)
        with open(file_path, 'w') as open_file:
            open_file.write(content)

    def get_keywords_from_log(self, log_file_path, sequence_dict_list, regex_type, sub_flow_name):
        """
        Parse the log file according to the YAML sequence info and creates an ordered list that contains the parsed relevant messages
        with relevant information.
        Arguments:
            log_file_path: The input log file path.
            sequence_dict_list: A list that holds the expected sequence dictionary objects.
            regex_type: The regex type.
            sub_flow_name: The name of the sub flow.
        Returns:
            line_dict_list: A list of dictionaries with the parsed lines from the log file.
            test_lines_list: A list of the line (not parsed) that where found.
        """
        line_dict_list = []
        test_lines_list = []
        regex_obj, groups = self.get_regex_obj_by_log_type(regex_type)
        for sequence_dict_index, sequence_dict in enumerate(sequence_dict_list):
            if any(sub_item_name.startswith('subsequence') for sub_item_name in sequence_dict_list[sequence_dict_index]):
                final_subsequence_index = len(sequence_dict_list[sequence_dict_index]['subsequences_dict']) - 1
                for index_sub_item_name, sub_item_name in enumerate(
                        sequence_dict_list[sequence_dict_index]['subsequences_dict']):
                    for log_message_dict in sequence_dict_list[sequence_dict_index]['subsequences_dict'][sub_item_name]['subsequence_log_messages']:
                        if 'has_regex' not in log_message_dict:
                            log_message_dict['has_regex'] = False
                        sed_results = self.get_relevant_messages_from_log(log_message_dict, log_file_path, log_message_dict['has_regex'])
                        if sed_results:
                            self.parse_results(sed_results,
                                               sequence_dict,
                                               log_message_dict,
                                               regex_obj,
                                               groups,
                                               sub_item_name,
                                               final_subsequence_index,
                                               sub_flow_name,
                                               line_dict_list,
                                               test_lines_list,
                                               'log_message')
                        else:
                            pass
            else:
                final_subsequence_index = None
                self.parse_messages(sequence_dict_list,
                                    sequence_dict_index,
                                    'log_message',
                                    log_file_path,
                                    sequence_dict,
                                    regex_obj,
                                    groups,
                                    final_subsequence_index,
                                    sub_flow_name,
                                    line_dict_list,
                                    test_lines_list)
                self.parse_messages(sequence_dict_list,
                                    sequence_dict_index,
                                    'fail_message',
                                    log_file_path,
                                    sequence_dict,
                                    regex_obj,
                                    groups,
                                    final_subsequence_index,
                                    sub_flow_name,
                                    line_dict_list,
                                    test_lines_list)
        return line_dict_list, test_lines_list

    def parse_messages(self,
                       sequence_dict_list,
                       sequence_dict_index,
                       message_type,
                       log_file_path,
                       sequence_dict,
                       regex_obj,
                       groups,
                       final_subsequence_index,
                       sub_flow_name,
                       line_dict_list,
                       test_lines_list):
        """
        Parse log messages per message type
        Arguments:
            sequence_dict_list: A list that holds the expected sequence dictionary objects.
            sequence_dict_index: The index of the sequence dictionary.
            message_type: The messages type (log_messages or fail_messages).
            log_file_path: The input log file path.
            sequence_dict: The sequence dictionary.
            regex_obj: The regex Object.
            groups: The regex groups.
            final_subsequence_index: The final index of the last subsequence in the sequence.
            sub_flow_name: The name of the sub flow.
            line_dict_list: A list of dictionaries with the parsed lines from the log file.
            test_lines_list: A list of the line (not parsed) that where found.
        """
        if sequence_dict_list[sequence_dict_index][f"{message_type}s"]:
            for log_message_dict in sequence_dict_list[sequence_dict_index][f"{message_type}s"]:
                if 'has_regex' not in log_message_dict:
                    log_message_dict['has_regex'] = False
                sed_results = self.get_relevant_messages_from_log(log_message_dict, log_file_path, log_message_dict['has_regex'])
                if sed_results:
                    self.parse_results(sed_results,
                                       sequence_dict,
                                       log_message_dict,
                                       regex_obj,
                                       groups,
                                       None,
                                       final_subsequence_index,
                                       sub_flow_name,
                                       line_dict_list,
                                       test_lines_list,
                                       message_type)

    def parse_results(self,
                      sed_results,
                      sequence_dict,
                      log_message_dict,
                      regex_obj,
                      groups,
                      sub_item_name,
                      final_subsequence_index,
                      sub_flow_name,
                      line_dict_list,
                      test_lines_list,
                      message_type):
        """
        Parse messages results
        Arguments:
            sed_results: The relevant Sed results from log.
            sequence_dict: The sequence dictionary.
            log_message_dict: The log message dictionary object.
            sub_item_name: The name of the sub-sequence.
            regex_obj: The regex Object.
            groups: The regex groups.
            final_subsequence_index: The final index of the last subsequence in the sequence.
            sub_flow_name: The name of the sub flow.
            line_dict_list: A list of dictionaries with the parsed lines from the log file.
            test_lines_list: A list of the line (not parsed) that where found.
            message_type: The type of message (log message/fail message).
        """
        num_of_lines = 0
        for result in sed_results:
            line = result['current_message_result'].rstrip()
            if 'previous_message_result' in result:
                previous_line = result['previous_message_result'].rstrip(
                )
                line_dict = self.parse_line_with_previous_message(
                    sequence_dict['sequence_name'],
                    log_message_dict,
                    line,
                    previous_line,
                    regex_obj,
                    groups,
                    sub_item_name,
                    final_subsequence_index,
                    sub_flow_name,
                    message_type)
            elif 'next_message_result' in result:
                next_line = result['next_message_result'].rstrip(
                )
                line_dict = self.parse_line_with_next_message(
                    sequence_dict['sequence_name'],
                    log_message_dict,
                    line,
                    next_line,
                    regex_obj,
                    groups,
                    sub_item_name,
                    final_subsequence_index,
                    sub_flow_name,
                    message_type)
            else:
                line_dict = self.parse_line(
                    sequence_dict['sequence_name'],
                    log_message_dict,
                    line,
                    regex_obj,
                    groups,
                    sub_item_name,
                    final_subsequence_index,
                    sub_flow_name,
                    message_type,
                    True)
            line_dict_list.append(line_dict)
            test_lines_list.append(line)
            num_of_lines += 1

    def get_relevant_messages_from_log(
            self,
            log_message_dict,
            log_file_path,
            has_regex):
        """
        Gets the relevant messages from the log using Sed command.
        Arguments:
            log_message_dict: The log message dictionary object.
            log_file_path: The input log file path.
            has_regex: (currently not in use) Weather the Sed string contains regex or not.
        return
            sed_results: The relevant Sed results from log.
        """
        sed_results = []
        escaped_log_message_text = log_message_dict['message_text'].translate(
            str.maketrans({'[': r"\["}))
        sed_str = f"s/{escaped_log_message_text}/&/p"
        if 'actions' in log_message_dict:
            if log_message_dict['actions']:
                if log_message_dict['actions']['message_extraction_requirements'] == 'None':
                    result, num_of_result_lines = self.get_sed_results(
                        sed_str, log_file_path, has_regex)
                    for result_pos in range(num_of_result_lines):
                        result_dict = {
                            'current_message_result': list(
                                StringIO(
                                    result.stdout.decode("utf-8")))[result_pos]}
                        sed_results.append(result_dict)
                if log_message_dict['actions']['message_extraction_requirements'] == 'previous_message':
                    sed_str = f"N;s/{escaped_log_message_text}/&/p"
                    result, num_of_result_lines = self.get_sed_results(
                        sed_str, log_file_path, has_regex)
                    for result_pos in range(0, num_of_result_lines, 2):
                        result_dict = {
                            'previous_message': list(
                                StringIO(
                                    result.stdout.decode("utf-8")))[result_pos],
                            'current_message_result': list(
                                StringIO(
                                    result.stdout.decode("utf-8")))[
                                result_pos + 1]}
                        sed_results.append(result_dict)
                elif log_message_dict['actions']['message_extraction_requirements'] == 'next_message':
                    sed_str = f"N;N;s/{escaped_log_message_text}/&/p"
                    result, num_of_result_lines = self.get_sed_results(
                        sed_str, log_file_path, has_regex)
                    for result_pos in range(1, num_of_result_lines, 3):
                        result_dict = {
                            'current_message_result': list(
                                StringIO(
                                    result.stdout.decode("utf-8")))[result_pos],
                            'next_message_result': list(
                                StringIO(
                                    result.stdout.decode("utf-8")))[
                                result_pos + 1]}
                        sed_results.append(result_dict)
            else:
                frame_info = getframeinfo(currentframe())
                track_message = f"A non existent action was specified."
                self.logger.error(frame_info, track_message)
                return None
        else:
            result, num_of_result_lines = self.get_sed_results(sed_str, log_file_path, has_regex)
            for result_pos in range(num_of_result_lines):
                result_dict = {
                    'current_message_result': list(
                        StringIO(
                            result.stdout.decode("utf-8")))[result_pos]}
                sed_results.append(result_dict)
        return sed_results

    def get_fail_messages_from_log(
            self,
            log_file_path,
            flow_fail_messages_list,
            regex_type):
        """
        Parse the log file according to the YAML sequence info and creates an ordered list that contains the parsed relevant messages
        with relevant information.
        Arguments:
            log_file_path: the input log file path
            flow_fail_messages_list: a list that holds the fail messages
            regex_type: The regex type
        """
        line_dict_list = []
        test_lines_list = []
        regex_obj, groups = self.get_regex_obj_by_log_type(regex_type)
        for sequence_dict_index, sequence_dict in enumerate(flow_fail_messages_list):
            self.parse_messages(flow_fail_messages_list,
                                sequence_dict_index,
                                'fail_message',
                                log_file_path,
                                sequence_dict,
                                regex_obj,
                                groups,
                                None,
                                None,
                                line_dict_list,
                                test_lines_list)
        return line_dict_list, test_lines_list

    def get_sed_results(self, sed_str, log_file_path, has_regex):
        """
        Gets the Sed results for the Sed string and the log file.
        Arguments:
            sed_str: The Sed string.
            log_file_path: the input log file path
        Returns:
            sed_results: The relevant Sed results from log.
            num_of_result_lines: The number of Sed results.
        """
        if os.path.isfile(self.sed_executable_path):
            sed_result = subprocess.run([self.sed_executable_path, '-n', '-E', sed_str, log_file_path], stdout=subprocess.PIPE)
            # if has_regex:  // need to test
            #     sed_result = subprocess.run([self.sed_executable_path, '-n', '-E', sed_str, log_file_path], stdout=subprocess.PIPE)
            # else:
            #     sed_result = subprocess.run([self.sed_executable_path, '-n', sed_str, log_file_path], stdout=subprocess.PIPE)
        else:
            frame_info = getframeinfo(currentframe())
            track_message = 'The sed GNU windows application is not installed, or is not at the default path.\n' \
                            'please run with admin privileges the environment preparation PowerShell script located at: ' \
                            r'"\\192.168.126.182\c$\Environment Installation\powershell_scripts-master\install_scripts\install_LogAnalyzer_requirements.ps1".'
            self.logger.error(frame_info, track_message)
            return None
        num_of_result_lines = len(list(StringIO(sed_result.stdout.decode("utf-8"))))
        return sed_result, num_of_result_lines

    def parse_line(
            self,
            sequence_name,
            log_message_dict,
            line,
            regex_obj,
            groups,
            subsequence_name,
            final_subsequence_index,
            sub_flow_name,
            message_prefix,
            warn):
        """
        Parse a log line and convert it into a dictionary object using regex.
        Arguments:
            sequence_name: The current relevant YAML sequence.
            log_message_dict: The log message dictionary object.
            line: The current line from the log file.
            regex_obj: The regex object.
            groups: The expected pattern groups.
            subsequence_name: The name of the subsequence.
            final_subsequence_index: The index of the last subsequence.
            sub_flow_name: The name of the sub flow.
            message_type: The type of message (log message/fail message).
        Returns:
            line_dict: The line dictionary.
        """
        if sub_flow_name:
            in_sub_flow = True
        else:
            in_sub_flow = False
        if subsequence_name:
            in_subsequence = True
        else:
            in_subsequence = False
        match = regex_obj.match(line)
        if not match:
            if warn:
                frame_info = getframeinfo(currentframe())
                track_message = 'The regex pattern matcher has failed.'
                self.logger.error(frame_info, track_message)
        else:
            match_groups = match.groups()
            for group_index, group_name in enumerate(groups):
                if match_groups[group_index]:
                    groups[group_name] = match_groups[group_index]
                else:
                    groups[group_name] = ''

            if 'microseconds' in groups:
                line_datetime = self.parse_date_time([groups['day'],
                                                      groups['month'],
                                                      groups['year'],
                                                      groups['hours'],
                                                      groups['minutes'],
                                                      groups['seconds'],
                                                      groups['microseconds']])
            else:
                if 'day' in groups:
                    line_datetime = self.parse_date_time([groups['day'],
                                                          groups['month'],
                                                          groups['year'],
                                                          groups['hours'],
                                                          groups['minutes'],
                                                          groups['seconds'],
                                                          0])
                else:
                    line_datetime = None
            if 'message_type' in groups:
                message_type = groups['message_type']
            else:
                message_type = None
            if log_message_dict and 'actions' in log_message_dict:
                line_dict = {
                    'sequence_name': sequence_name,
                    'in_sub_flow': in_sub_flow,
                    'sub_flow_name': sub_flow_name,
                    'in_subsequence': in_subsequence,
                    'subsequence_name': subsequence_name,
                    'final_subsequence_index': final_subsequence_index,
                    'message_id': groups['message_id'] if 'message_id' in groups else None,
                    'log_message_name': log_message_dict[f"{message_prefix}_name"],
                    'datetime': line_datetime,
                    'type': message_type,
                    'message_text': groups['message_text'],
                    'actions': log_message_dict['actions'],
                }
            else:
                line_dict = {
                    'sequence_name': sequence_name,
                    'in_sub_flow': in_sub_flow,
                    'sub_flow_name': sub_flow_name,
                    'in_subsequence': in_subsequence,
                    'subsequence_name': subsequence_name,
                    'final_subsequence_index': final_subsequence_index,
                    'message_id': groups['message_id'] if 'message_id' in groups else None,
                    'log_message_name': log_message_dict[f"{message_prefix}_name"],
                    'datetime': line_datetime,
                    'type': message_type,
                    'message_text': groups['message_text']
                }
            return line_dict

    def parse_line_with_previous_message(self, sequence_name,
                                         log_message_dict,
                                         line,
                                         previous_line,
                                         regex_obj,
                                         groups,
                                         subsequence_name,
                                         final_subsequence_index,
                                         sub_flow_name,
                                         message_type):
        """
        Parse a log line and its previous line and convert it into a dictionary object using regex.
        Arguments:
            sequence_name: The current relevant YAML sequence.
            log_message_dict: The log message dictionary object.
            line: The current line from the log file.
            previous_line: The previous line from the log file.
            regex_obj: The regex object.
            groups: The expected pattern groups.
            subsequence_name: The name of the subsequence.
            final_subsequence_index: The index of the last subsequence.
            sub_flow_name: The name of the sub flow.
            message_type: The type of message (log message/fail message).
        Returns:
            line_dict: The line dictionary.
        """
        line_dict = self.parse_line(sequence_name,
                                    log_message_dict,
                                    line,
                                    regex_obj,
                                    groups,
                                    subsequence_name,
                                    final_subsequence_index,
                                    sub_flow_name,
                                    message_type,
                                    True)
        previous_line_dict = self.parse_line(sequence_name,
                                             log_message_dict,
                                             previous_line,
                                             regex_obj,
                                             groups,
                                             subsequence_name,
                                             final_subsequence_index,
                                             sub_flow_name,
                                             message_type,
                                             True)
        line_dict['previous_line_dict'] = previous_line_dict
        return line_dict

    def parse_line_with_next_message(self,
                                     sequence_name,
                                     log_message_dict,
                                     line,
                                     next_line,
                                     regex_obj,
                                     groups,
                                     subsequence_name,
                                     final_subsequence_index,
                                     sub_flow_name,
                                     message_type):
        """
        Parse a log line and its next line and convert it into a dictionary object using regex.
        Arguments:
            sequence_name: The current relevant YAML sequence.
            log_message_dict: The log message dictionary object.
            line: The current line from the log file.
            next_line: The next line from the log file.
            regex_obj: The regex object.
            groups: The expected pattern groups.
            subsequence_name: The name of the subsequence.
            final_subsequence_index: The index of the last subsequence.
            sub_flow_name: The name of the sub flow.
            message_type: The type of message (log messages/fail messages)
        Returns:
            line_dict: The line dictionary.
        """
        line_dict = self.parse_line(sequence_name,
                                    log_message_dict,
                                    line,
                                    regex_obj,
                                    groups,
                                    subsequence_name,
                                    final_subsequence_index,
                                    sub_flow_name,
                                    message_type,
                                    True)
        next_line_dict = self.parse_line(sequence_name,
                                         log_message_dict,
                                         next_line,
                                         regex_obj,
                                         groups,
                                         subsequence_name,
                                         final_subsequence_index,
                                         sub_flow_name,
                                         message_type,
                                         True)
        line_dict['next_line_dict'] = next_line_dict
        return line_dict

    @staticmethod
    def order_line_dict_list(line_dict_list):
        """
        order the line_dict_list according to the message_id index
        Arguments:
            line_dict_list: A list of dictionaries with the parsed lines from the log file.
        Returns:
            ordered_line_dict_list: An ordered list that holds the parsed message log dictionary objects.
        """
        if len(line_dict_list) > 0:
            if 'message_id' in line_dict_list[0]:
                ordered_line_dict_list = sorted(
                    line_dict_list, key=lambda line_dict: int(
                        line_dict['message_id']))
                return ordered_line_dict_list
            else:
                return line_dict_list
        else:
            return line_dict_list

    @staticmethod
    def parse_date_time(date_time_list):
        """
        Convert the log time stamp to a readable string format
        Arguments:
            date_time_list: A list that contains the datetime information from the log line.
        Returns:
            line_datetime: The parsed datetime object.
        """
        line_datetime = datetime.datetime.strptime(
            f'{date_time_list[0]}/{date_time_list[1]}/{date_time_list[2]} '
            f'{date_time_list[3]}:{date_time_list[4]}:{date_time_list[5]}:{date_time_list[6]}',
            '%d/%m/%Y %H:%M:%S:%f')
        return line_datetime

    def write_test_lines(self, lines_list):
        """
        Writing the relevant log lines to a separate file for debugging
        Arguments:
            lines_list: A list of relevant lines from the log file.
        """
        with open(self.debug_test_lines_file_path, 'w') as debug_test_lines_file:
            for line in lines_list:
                debug_test_lines_file.write("%s\n" % line)

    @staticmethod
    def write_test_yaml(ordered_line_dict_list, output_yaml_file_path):
        """
        Dumps the parsed relevant log lines to a YAML file
        Arguments:
             ordered_line_dict_list: An ordered list that holds the parsed message log dictionary objects.
             output_yaml_file_path: The path the YAML data will be written to.
        """
        json_obj = yaml.dump(
            ordered_line_dict_list,
            Dumper=PrettyYAMLDumper,
            default_flow_style=False)
        with open(output_yaml_file_path, 'w') as output_json_file:
            output_json_file.write(json_obj)

    def get_action_type(self, action_name):
        """
        Gets the action type from its name
        Arguments:
            action_name: The action name.
        Returns:
            action_type: The action type.
        """
        for action_type in self.actions_types:
            if action_type['action_name'] == action_name:
                return action_type
        return False

    def clean_control_codes(self, log_file_path):
        """
        Cleans control codes from the log using perl (In place).
        Arguments:
            log_file_path: the input log file path
        """
        stream_processing_str = "s/\\[.[^='_\\[\\]\\(,a-z]{0,6}m//g; s/\\[m\r/\r/g; s/\\[K[^M]//g; s/\x1b//g; s/ \x08//g; s/ESC/ /g; s/ \\[m \\[m//g; s/>  \\[m/> /g;"
        if os.path.isfile(self.perl_executable_path):
            subprocess.run([self.perl_executable_path, '-pi', '-e', stream_processing_str, log_file_path])
            return True
        else:
            frame_info = getframeinfo(currentframe())
            track_message = "Perl executable path wasn't found, or is not at the default path.\n" \
                            'please run with admin privileges the environment preparation PowerShell script located at: ' \
                            r'"\\192.168.126.182\c$\Environment Installation\powershell_scripts-master\install_scripts\install_LogAnalyzer_requirements.ps1".'
            self.logger.error(frame_info, track_message)
            return None

    def clean_control_codes_from_file_to_different_file(self, log_file_path):
        """
        Cleans control codes from the log using perl to a different file.
        Arguments:
            log_file_path: the input log file path
        """
        stream_processing_str = "s/\\[.[^='_\\[\\]\\(,a-z]{0,6}m//g; s/\\[m\r/\r/g; s/\\[K[^M]//g; s/\x1b//g; s/ \x08//g; s/ESC/ /g; s/ \\[m \\[m//g; s/>  \\[m/> /g;"
        if os.path.isfile(self.perl_executable_path):
            log_file_output_path = f'{os.path.splitext(log_file_path)[0]}_output.log'
            with open(log_file_output_path, 'w', encoding='utf-8') as log_file_output:
                subprocess.run([self.perl_executable_path,
                                '-pe',
                                stream_processing_str,
                                log_file_path],
                               stdout=log_file_output)
            return True
        else:
            frame_info = getframeinfo(currentframe())
            track_message = "Perl executable path wasn't found, or is not at the default path.\n" \
                            'please run with admin privileges the environment preparation PowerShell script located at: ' \
                            r'"\\192.168.126.182\c$\Environment Installation\powershell_scripts-master\install_scripts\install_LogAnalyzer_requirements.ps1".'
            self.logger.error(frame_info, track_message)
            return None

    def verify_clean_control_codes(self, log_file_path, output_log_file_path):
        """
        A function to test the clean control codes string on the bulk logs folder.
        Arguments:
            log_file_path: the input log file path
            output_log_file_path: the output log file path
        """
        stream_processing_str = "s/\\[.[^='_\\[\\]\\(,a-z]{1,6}m//g; s/\\[m\r/\r/g; s/\\[K[^M]//g; s/\x1b//g; s/ \x08//g; s/ESC/ /g; s/ \\[m \\[m//g; s/>  \\[m/> /g;"
        if os.path.isfile(self.perl_executable_path):
            Path(
                os.path.dirname(output_log_file_path)).mkdir(
                parents=True,
                exist_ok=True)

            with open(output_log_file_path, 'w', encoding='utf-8') as output_log_file:
                subprocess.run([self.perl_executable_path,
                                '-pe',
                                stream_processing_str,
                                log_file_path],
                               stdout=output_log_file)
            cmp_result = filecmp.cmp(
                log_file_path,
                output_log_file_path,
                shallow=False)
            if cmp_result:
                os.remove(output_log_file_path)
            return True
        else:
            frame_info = getframeinfo(currentframe())
            track_message = "Perl executable path wasn't found, or is not at the default path.\n" \
                            'please run with admin privileges the environment preparation PowerShell script located at: ' \
                            r'"\\192.168.126.182\c$\Environment Installation\powershell_scripts-master\install_scripts\install_LogAnalyzer_requirements.ps1".'
            self.logger.error(frame_info, track_message)
            return None

    def get_log_start_end_timestamps(self, regex_type, last_log_file_path):
        log_start_timestamp, start_message_id = self.get_log_start_or_end_ids_and_timestamps(regex_type, last_log_file_path, 'start')
        log_end_timestamp, end_message_id = self.get_log_start_or_end_ids_and_timestamps(regex_type, last_log_file_path, 'end')
        return log_start_timestamp, start_message_id, log_end_timestamp, end_message_id

    def get_log_start_or_end_ids_and_timestamps(self, regex_type, last_log_file_path, start_or_end):
        if start_or_end == 'start':
            num_of_test_lines = 10
            timestamp, message_id = self.get_sed_first_line(last_log_file_path, num_of_test_lines, regex_type)
        elif start_or_end == 'end':
            num_of_test_lines = 10
            timestamp, message_id = self.get_sed_last_line(last_log_file_path, num_of_test_lines, regex_type)
        return timestamp, message_id
