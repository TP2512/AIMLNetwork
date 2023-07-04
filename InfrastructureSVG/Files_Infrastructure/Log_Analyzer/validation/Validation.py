from InfrastructureSVG.Files_Infrastructure.Log_Analyzer.tracking.Logger import Logger
import datetime
import re
from inspect import currentframe, getframeinfo
from InfrastructureSVG.Files_Infrastructure.Log_Analyzer.ASN_1.Parse_F1AP_hex import ASN1Parse


class Validation:
    def __init__(self):
        self.logger = Logger()
        self.asn1_parse = ASN1Parse()
        self.validation_state = None
        self.validation_data = None

    def validate(self, preprocessing, validation_data, yaml_data):
        """
        This function loops each flow dictionary in validates it.
        Arguments:
            preprocessing: The pre-processing object.
            validation_data: The validation data object.
            yaml_data: The YAML data object.
        Returns:
            validation_results: The validation results.
        """
        validation_results = {'valid': 'PASS'}
        for flow_dict in validation_data:
            if flow_dict['validation_state']['validation_type'] == 'per_sequence_flow':
                if len(flow_dict['ordered_line_dict_list']) > 0:
                    if flow_dict['flow_info']['has_sub_flow']:
                        for sub_flow_name in flow_dict['flow_info']:
                            if sub_flow_name == 'has_sub_flow':
                                continue
                            log_final_sequence_num = len(flow_dict['flow_info'][sub_flow_name]['ordered_line_dict_list'])
                            yaml_final_sequence = preprocessing.get_yaml_last_valid_sequence(flow_dict['flow_info'][sub_flow_name]['sequence_dict_list'])
                            flow_dict['flow_info'][sub_flow_name]['validation_state'] = preprocessing.init_validation_flow(
                                flow_dict['ordered_line_dict_list'],
                                flow_dict['sequence_dict_list'],
                                yaml_data,
                                flow_dict['sequence_flow_name'],
                                flow_dict['flow_info'][sub_flow_name]['actions_info'],
                                flow_dict['sequence_flow_configuration'],
                                'per_sequence_flow',
                                log_final_sequence_num,
                                yaml_final_sequence)
                            flow_dict['flow_info'][sub_flow_name]['validation_state']['validation_type'] = 'per_sequence_flow'
                            flow_dict['flow_info'][sub_flow_name]['validation_state']['yaml_sequence_state']['current_yaml_sequence_dict'] =\
                                flow_dict['flow_info'][sub_flow_name]['sequences_dict']
                            self.validate_sequence_flow(preprocessing, flow_dict['flow_info'][sub_flow_name], flow_dict['device_name'])
                        for sub_flow_name in flow_dict['flow_info']:
                            if sub_flow_name == 'has_sub_flow':
                                continue
                            if flow_dict['flow_info'][sub_flow_name]['validation_state']['valid'] == 'FAIL':
                                flow_dict['validation_state']['valid'] = 'FAIL'
                                flow_dict['validation_state']['validation_end_reason'] = 'sub_flow_fail'
                    else:
                        self.validate_sequence_flow(preprocessing, flow_dict, flow_dict['device_name'])
                        if flow_dict['validation_state']['valid'] == 'FAIL':
                            validation_results['valid'] = 'FAIL'
                else:
                    if flow_dict['flow_info']['has_sub_flow']:
                        for sub_flow_name in flow_dict['flow_info']:
                            if sub_flow_name == 'has_sub_flow':
                                continue
                            log_final_sequence_num = len(flow_dict['flow_info'][sub_flow_name]['ordered_line_dict_list'])
                            yaml_final_sequence = preprocessing.get_yaml_last_valid_sequence(flow_dict['flow_info'][sub_flow_name]['sequence_dict_list'])
                            flow_dict['flow_info'][sub_flow_name]['validation_state'] = preprocessing.init_validation_flow(
                                flow_dict['ordered_line_dict_list'],
                                flow_dict['sequence_dict_list'],
                                yaml_data,
                                flow_dict['sequence_flow_name'],
                                flow_dict['flow_info'][sub_flow_name]['actions_info'],
                                flow_dict['sequence_flow_configuration'],
                                'per_sequence_flow',
                                log_final_sequence_num,
                                yaml_final_sequence)
                            flow_dict['flow_info'][sub_flow_name]['validation_state']['validation_type'] = 'per_sequence_flow'
                            flow_dict['flow_info'][sub_flow_name]['validation_state']['yaml_sequence_state']['current_yaml_sequence_dict'] = \
                                flow_dict['flow_info'][sub_flow_name]['sequences_dict']
                            flow_name = flow_dict['sequence_flow_name']
                            frame_info = getframeinfo(currentframe())
                            track_message = f'None of the current flow: {flow_name} log messages has been found in the log.'
                            self.logger.info(frame_info, track_message)
                            flow_dict['flow_info'][sub_flow_name]['validation_state']['validation_end_reason'] = 'None of the specific log messages has been found'
                            flow_dict['flow_info'][sub_flow_name]['validation_state']['valid'] = 'FAIL'
                            flow_dict['flow_info'][sub_flow_name]['validation_state']['validation_end'] = True
                    else:
                        flow_name = flow_dict['sequence_flow_name']
                        frame_info = getframeinfo(currentframe())
                        track_message = f'None of the current flow: {flow_name} log messages has been found in the log.'
                        self.logger.info(frame_info, track_message)
                        flow_dict['validation_state']['validation_end_reason'] = 'None of the specific log messages has been found'
                        flow_dict['validation_state']['valid'] = 'FAIL'
                        flow_dict['validation_state']['validation_end'] = True
            elif flow_dict['validation_state']['validation_type'] == 'per_message_flow':
                self.validate_message_flow(flow_dict)
        return validation_results

    def validate_message_flow(self, message_flow_dict):
        """
        The validation loop function for message flow.
        Arguments:
            validation_data: The validation data object.
        """
        if message_flow_dict['global_fail_messages_list']:
            self.validation_state = message_flow_dict['validation_state']
            self.prepare_actions(message_flow_dict)
            if message_flow_dict['global_fail_messages'] and 'fail_messages' in message_flow_dict['validation_state']['global_configuration']:
                self.validation_state['log_sequence_state'][f'log_final_sequence_num'] = len(message_flow_dict['global_fail_messages_list'])
                while not self.validation_state['validation_end']:
                    self.forward_state_per_message_flow(self.validation_state['log_sequence_state'],
                                                        message_flow_dict['global_fail_messages'],
                                                        message_flow_dict['global_fail_messages_list'],
                                                        message_flow_dict['device_name'])
                    if not self.validation_state['validation_end'] and self.validation_state['log_sequence_state']['log_state_name'] != 'log_sequence_started':
                        self.validate_fail_message_message_flow(self.validation_state['log_sequence_state']['next_log_sequence'], message_flow_dict['global_fail_messages'])
                self.process_actions_message_flow()


    def validate_sequence_flow(self, preprocessing, sequence_flow_dict, device_name):
        """
        The validation loop function for sequence flow.
        Arguments:
            preprocessing: The pre-processing object.
            sequence_flow_dict: A dictionary with the sequence flow data.
        """
        self.validation_state = sequence_flow_dict['validation_state']
        self.prepare_actions(sequence_flow_dict)
        self.forward_yaml_state_per_sequence_flow(self.validation_state['yaml_sequence_state'], sequence_flow_dict['sequence_dict_list'], False)
        while not self.validation_state['validation_end']:
            self.forward_log_state_per_sequence_flow(preprocessing, self.validation_state['log_sequence_state'], sequence_flow_dict['ordered_line_dict_list'], device_name)
            if not self.validation_state['valid'] == 'FAIL':
                self.validate_log_sequence(preprocessing)
            if self.validation_state['valid'] == 'PASS' and not self.validation_state['validation_end']:
                if self.validation_state['log_sequence_state']['last_log_sequence_valid']:
                    if self.validation_state['yaml_sequence_state']['yaml_state_name'] != 'log_message_repeat':
                        is_last_log_sequence_reached = (self.validation_state['log_sequence_state']['log_sequence_num'] + 1) >= self.validation_state['log_sequence_state']['log_final_sequence_num']
                        self.forward_yaml_state_per_sequence_flow(self.validation_state['yaml_sequence_state'], sequence_flow_dict['sequence_dict_list'], is_last_log_sequence_reached)
            else:
                self.create_validation_info()
                break
        self.process_actions_sequence_flow()

    def create_validation_info(self):
        """
        Creates the validation information object.
        """
        if self.validation_state['validation_type'] == 'per_sequence_flow':
            if (len(self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict'].keys()) > 0):
                last_validated_sequence_name = list(
                    self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict'])[-1]
                last_validated_sequence = self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict'][last_validated_sequence_name]
                if 'has_subsequence' in last_validated_sequence and last_validated_sequence['has_subsequence']:
                    last_valid_subsequence = None
                    for subsequence_name in last_validated_sequence['subsequences_dict']:
                        subsequence = last_validated_sequence['subsequences_dict'][subsequence_name]
                        if subsequence['validated']:
                            last_valid_subsequence = subsequence
                    if len(last_valid_subsequence['subsequence_log_messages']) == 1:
                        self.validation_state['validation_info']['end_sequence_name'] = last_validated_sequence['sequence_name']
                        self.validation_state['validation_info']['end_sequence_subsequence'] = last_valid_subsequence['subsequence_name']
                        self.validation_state['validation_info']['end_subsequence_message'] = last_valid_subsequence[
                            'subsequence_log_messages'][0]['message_text']
                    else:
                        messages_list = []
                        for log_message in last_valid_subsequence['subsequence_log_messages']:
                            messages_list.append(log_message['message_text'])
                        messages_str = ' or '.join(messages_list)
                        self.validation_state['validation_info']['end_sequence_name'] = last_validated_sequence['sequence_name']
                        self.validation_state['validation_info']['end_sequence_subsequence'] = last_valid_subsequence['subsequence_name']
                        self.validation_state['validation_info']['end_sequence_message'] = messages_str
                else:
                    if last_validated_sequence['log_messages']:
                        if len(last_validated_sequence['log_messages']) == 1:
                            self.validation_state['validation_info']['end_sequence_name'] = last_validated_sequence['sequence_name']
                            self.validation_state['validation_info']['end_subsequence_message'] = last_validated_sequence['log_messages'][0]['message_text']
                        else:
                            messages_list = []
                            for log_message in last_validated_sequence['log_messages']:
                                messages_list.append(log_message['message_text'])
                            messages_str = ' or '.join(messages_list)
                            self.validation_state['validation_info']['end_sequence_name'] = last_validated_sequence['sequence_name']
                            self.validation_state['validation_info']['end_sequence_message'] = messages_str
                    elif last_validated_sequence['fail_messages']:
                        if len(last_validated_sequence['fail_messages']) == 1:
                            self.validation_state['validation_info']['end_sequence_name'] = last_validated_sequence['sequence_name']
                            self.validation_state['validation_info']['end_subsequence_message'] = last_validated_sequence['fail_messages'][0]['message_text']
                        else:
                            messages_list = []
                            for fail_message in last_validated_sequence['fail_messages']:
                                messages_list.append(fail_message['message_text'])
                            messages_str = ' or '.join(messages_list)
                            self.validation_state['validation_info']['end_sequence_name'] = last_validated_sequence['sequence_name']
                            self.validation_state['validation_info']['end_sequence_message'] = messages_str
        else:
            self.validation_state['validation_info'] = {}
        return

    # def create_validation_info_with_fail_message(self, fail_message):
    #     """
    #     Creates the validation information object which contains fail messages.
    #     """
    #     self.create_validation_info()
    #     self.validation_state['validation_info']['fail_message'] = fail_message

    def process_actions_sequence_flow(self):
        """
        Processes actions at the end of the sequence
        flow validation.
        """
        self.copy_current_yaml_sequence_dict_data_to_validated_yaml_sequence_dict_data()
        for action_info_name in self.validation_state['actions_info']:
            actions = self.validation_state['actions_info'][action_info_name]
            for action_name in actions:
                for device_name in list(actions[action_name]['action_info']):
                    process_function_name = f"process_{action_name}"
                    getattr(self, process_function_name)(actions[action_name], device_name)

    def process_actions_message_flow(self):
        """
        Processes actions at the end of the message flow validation.
        """
        pass

    def copy_current_yaml_sequence_dict_data_to_validated_yaml_sequence_dict_data(self):
        """
        Copies the current YAML sequence to the validated YAML sequence object.
        """
        for sequence_name in self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict']:
            sequence = self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict'][sequence_name]
            if 'has_subsequence' in sequence and sequence['has_subsequence']:
                sequence['sequence_valid_count'] = self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][sequence_name]['sequence_valid_count']

    def prepare_actions(self, validation_data):
        """
        Prepares the actions for processing.
        """
        for action_info_name in validation_data['validation_state']['actions_info']:
            for action_name in validation_data['validation_state']['actions_info'][action_info_name]:
                if validation_data['validation_state']['actions_info'][action_info_name][action_name]['prepare']:
                    getattr(self, validation_data['validation_state']['actions_info'][action_info_name][action_name]['prepare'])(validation_data,
                                                                                                                                 validation_data['validation_state']['actions_info'][action_info_name][action_name])

    def prepare_action_regex(self, validation_data, action):
        """
        Prepares the regex for actions
        """
        try:
            action['regex_obj'] = re.compile(action['action_config']['regex_extraction_pattern'])
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = f'failed to compile regex pattern for extraction.',
            self.logger.error(frame_info, track_message)

    def process_get_message_stats(self, action_info_set, device_name):
        """
        Processes the get_message_stats action.
        Arguments:
            action_info_set: A set of an action information.
        """
        if len(action_info_set['action_info'][device_name]) > 0:
            if 'datetime' in action_info_set['action_info'][device_name][0]:
                previous_action_info_item = action_info_set['action_info'][device_name][0]['datetime']
                time_delta_sum = datetime.timedelta(0)
                action_info_item_index = 0
                for action_info_item_index, action_info_item in enumerate(action_info_set['action_info'][device_name]):
                    current_action_info_item = action_info_set['action_info'][device_name][action_info_item_index]['datetime']
                    if current_action_info_item:
                        time_delta = current_action_info_item - previous_action_info_item
                        action_info_item['time_delta_from_previous'] = time_delta
                        time_delta_sum += time_delta
                if len(action_info_set['action_info'][device_name]) == 0:
                    action_info_set['output_str'] = f"The message: \"{action_info_set['action_message_text']}\" has not been found.\n"
                if len(action_info_set['action_info'][device_name]) == 1:
                    action_info_set['output_str'] = f"The message: \"{action_info_set['action_message_text']}\" has been found one time.\n" \
                                                    f" a list of all occurrences exist in the extra info dictionary."
                else:
                    action_info_set['time_delta_average'] = time_delta_sum / \
                                                            action_info_item_index
                    action_info_set['output_str'] = f"The message: \"{action_info_set['action_message_text']}\" has been found {action_info_item_index} " \
                                                    f"times.\n The average time between messages is {action_info_set['time_delta_average']}, a list of all " \
                                                    f"occurrences exist in the extra info dictionary."
            else:
                frame_info = getframeinfo(currentframe())
                track_message = f'A get_message_stats action has been specified but datetime timestamp is missing from extraction.',
                self.logger.error(frame_info, track_message)
        else:
            action_info_set['time_delta_average'] = -1
            action_info_set['output_str'] = f"The message: {action_info_set['action_message_text']} has not been found in the log.\n"

    @staticmethod
    def process_verify_hex_content(action_info_set, device_name):
        """
        Final processing of the verify_hex_content action.
        Arguments:
            action_info_set: A set of an action information.
        """
        action_info_set['output_str'] = f"The hex content has been found {len(action_info_set['action_info'][device_name])} times," \
                                        f" right after the message: \"{action_info_set['action_message_text']}\" \nand its values:\n" \
                                        f"{action_info_set['action_config']}\nvalidated on all occurrences.\n"

    def process_verify_min_repeat(self, action_info_set, device_name):
        """
        Final processing of the verify_min_repeat action.
        Arguments:
            action_info_set: A set of an action information.
        """
        try:
            if not self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['has_subsequence']:
                for log_message in self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['log_messages']:
                    if action_info_set['action_message_text'] == log_message['message_text']:
                        self.min_repeat_update_fail(log_message, device_name)
            else:
                for subsequences_dict_name in self.validation_state['yaml_sequence_state'][
                    'current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['subsequences_dict']:
                    subsequences_dict = self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][
                        action_info_set['action_sequence_name']]['subsequences_dict'][subsequences_dict_name]
                    for subsequence_log_message in subsequences_dict['subsequence_log_messages']:
                        if action_info_set['action_message_text'] == subsequence_log_message['message_text']:
                            self.min_repeat_update_fail(subsequence_log_message, device_name)
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'process_verify_min_repeat error.',
            self.logger.error(frame_info, track_message)
        action_info_set['output_str'] = f"A min_repeat verification with value {action_info_set['action_config']['min_repeat']} has been performed " \
                                        f"on the message \"{action_info_set['action_message_text']}\", with result: {action_info_set['result']}.\n The message" \
                                        f" repeated {action_info_set['action_info'][device_name]} times.\n"

    def min_repeat_update_fail(self, log_message, device_name):
        """
        Process of the verify_min_repeat action.
        Arguments:
            log_message: The log message dictionary.
        """
        is_repeat_num = self.verify_min_repeat_message_scope(log_message, device_name)
        if is_repeat_num == 'FAIL':
            self.validation_state[
                'validation_end_reason'] = 'A message min repeat verification failed the test.'
            self.create_validation_info()
            self.validation_state['valid'] = 'FAIL'
            self.validation_state['validation_end'] = True

    def verify_min_repeat_message_scope(self, log_message, device_name):
        """
        Process of the verify_min_repeat action based on its scope.
        Arguments:
            log_message: The log message dictionary.
        """
        try:
            for action in log_message['actions']['post_log_forward_step']:
                if 'min_repeat' in action['action_config']:
                    self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['action_info'][device_name] = log_message['repeat_num']
                    if log_message['repeat_num'] >= action['action_config']['min_repeat']:
                        self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['result'] = 'PASS'
                        return 'PASS'
                    else:
                        self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['result'] = 'FAIL'
                        self.validation_state['valid'] = 'FAIL'
                        return 'FAIL'
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'verify_min_repeat_message_scope error.',
            self.logger.error(frame_info, track_message)

    def process_verify_repeat(self, action_info_set, device_name):
        """
        Final processing of the verify_repeat action.
        Arguments:
            action_info_set: A set of an action information.
        """
        try:
            if not self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['has_subsequence']:
                for log_message in self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['log_messages']:
                    if action_info_set['action_message_text'] == log_message['message_text']:
                        self.repeat_num_update_fail(log_message, device_name)
            else:
                for subsequences_dict_name in self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['subsequences_dict']:
                    subsequences_dict = self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['subsequences_dict'][subsequences_dict_name]
                    for subsequence_log_message in subsequences_dict['subsequence_log_messages']:
                        if action_info_set['action_message_text'] == subsequence_log_message['message_text']:
                            self.repeat_num_update_fail(subsequence_log_message, device_name)
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'process_verify_repeat error.',
            self.logger.error(frame_info, track_message)
        action_info_set['output_str'] = f"A verify_repeat verification with value {action_info_set['action_config']['repeat_num']} has been performed " \
                                        f"on the message \"{action_info_set['action_message_text']}\", with result: {action_info_set['result']}.\n The message" \
                                        f" repeated {action_info_set['action_info'][device_name]} times.\n"

    def repeat_num_update_fail(self, log_message, device_name):
        """
        Process of the repeat_num action.
        Arguments:
            log_message: The log message dictionary.
        """
        is_repeat_num = self.verify_repeat_num_message_scope(log_message, device_name)
        if is_repeat_num == 'FAIL':
            self.validation_state['validation_end_reason'] = 'A message repeat num verification failed the test.'
            self.create_validation_info()
            self.validation_state['valid'] = 'FAIL'
            self.validation_state['validation_end'] = True

    def verify_repeat_num_message_scope(self, log_message, device_name):
        """
        Process of the repeat_num action based on its scope.
        Arguments:
            log_message: The log message dictionary.
        """
        try:
            for action in log_message['actions']['post_log_forward_step']:
                if 'repeat_num' in action['action_config']:
                    self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['action_info'][device_name] = log_message['repeat_num']
                    if log_message['repeat_num'] == action['action_config']['repeat_num']:
                        self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['result'] = 'PASS'
                        return 'PASS'
                    else:
                        self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['result'] = 'FAIL'
                        self.validation_state['valid'] = 'FAIL'
                        return 'FAIL'
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'verify_repeat_num_message_scope error.',
            self.logger.error(frame_info, track_message)

    def process_verify_max_repeat(self, action_info_set, device_name):
        """
        Final processing of the verify_max_repeat action.
        Arguments:
            action_info_set: A set of an action information.
        """
        try:
            if not self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['has_subsequence']:
                for log_message in self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['log_messages']:
                    if action_info_set['action_message_text'] == log_message['message_text']:
                        self.max_repeat_update_fail(log_message, device_name)
            else:
                for subsequences_dict_name in self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['subsequences_dict']:
                    subsequences_dict = self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'][action_info_set['action_sequence_name']]['subsequences_dict'][subsequences_dict_name]
                    for subsequence_log_message in subsequences_dict['subsequence_log_messages']:
                        if action_info_set['action_message_text'] == subsequence_log_message['message_text']:
                            self.max_repeat_update_fail(subsequence_log_message, device_name)
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'process_verify_max_repeat error.',
            self.logger.error(frame_info, track_message)
        action_info_set['output_str'] = f"A verify_max_repeat verification with value {action_info_set['action_config']['max_repeat']} has been performed " \
                                        f"on the message \"{action_info_set['action_message_text']}\", with result: {action_info_set['result']}.\n The message" \
                                        f" repeated {action_info_set['action_info'][device_name]} times.\n"

    def max_repeat_update_fail(self, log_message, device_name):
        """
        Process of the repeat_num action.
        Arguments:
            log_message: The log message dictionary.
        """
        is_repeat_num = self.verify_max_repeat_message_scope(log_message, device_name)
        if is_repeat_num == 'FAIL':
            self.validation_state['validation_end_reason'] = 'A message repeat num verification failed the test.'
            self.create_validation_info()
            self.validation_state['valid'] = 'FAIL'
            self.validation_state['validation_end'] = True

    def verify_max_repeat_message_scope(self, log_message, device_name):
        """
        Process of the repeat_num action based on its scope.
        Arguments:
            log_message: The log message dictionary.
        """
        try:
            for action in log_message['actions']['post_log_forward_step']:
                if 'max_repeat' in action['action_config']:
                    self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['action_info'][device_name] = log_message['repeat_num']
                    if log_message['repeat_num'] <= action['action_config']['max_repeat']:
                        self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['result'] = 'PASS'
                        return 'PASS'
                    else:
                        self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['result'] = 'FAIL'
                        self.validation_state['valid'] = 'FAIL'
                        return 'FAIL'
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'verify_max_repeat_message_scope error.',
            self.logger.error(frame_info, track_message)

    @staticmethod
    def process_extract_regex_from_message(action_info_set, device_name):
        """
        Process of the extract_regex_from_message action.
        Arguments:
            action_info_set: A set of an action information.
        """
        return

    @staticmethod
    def is_fail_message(next_log_sequence, yaml_sequence):
        """
        Checks weather a fail message for specific message has been found.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            yaml_sequence: The current YAML validation sequence.
        Returns:
            is_fail_message: weather a fail message for specific message has been found.
            fail_message: The fail message that was searched for.
        """
        if yaml_sequence['sequence_name'] != 'init' and yaml_sequence['fail_messages']:
            for fail_message_index, fail_message in enumerate(yaml_sequence['fail_messages']):
                if 'has_regex' in fail_message and fail_message['has_regex']:
                    try:
                        if re.search(
                                fail_message['compiled_regex'].pattern,
                                next_log_sequence['message_text']).group(0):
                            return True, fail_message
                        else:
                            return False, None
                    except Exception:
                        pass
                if next_log_sequence['message_text'] == yaml_sequence['fail_messages'][fail_message_index]['message_text']:
                    return True, fail_message
        return False, None

    def is_config_fail_message(self, next_log_sequence, configuration):
        """
        Checks weather a configuration fail message has been received.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            configuration: The configuration dictionary.
        Returns:
            is_flow_fail_message: Weather a flow configuration fail message has been received.
            flow_fail_message: The flow fail message.
        """
        try:
            if 'fail_messages' in configuration:
                for fail_message_name in configuration['fail_messages']:
                    if next_log_sequence['message_text'] == configuration['fail_messages'][fail_message_name]['message_text']:
                        return True, configuration['fail_messages'][fail_message_name]['message_text']
        except KeyError:
            frame_info = getframeinfo(currentframe())
            track_message = 'KeyError from the getting fail message configuration.',
            self.logger.error(frame_info, track_message)
            return False, None
        return False, None

    def validate_log_sequence(self, preprocessing):
        """
        Checks the validation conditions for the current validation state.
        Arguments:
            preprocessing: The pre-processing object.
        """
        if len(list(self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict'].keys(
        ))) == 0 or not self.is_last_yaml_sequence_reached(preprocessing, is_last_log_sequence_reached=False):
            self.validate_fail_message_sequence_flow()
            yaml_sequence_forward = self.validate_yaml_sequence(self.validation_state['log_sequence_state']['next_log_sequence'])
            if yaml_sequence_forward == 'sequence_forward' or yaml_sequence_forward == 'subsequence_forward':
                self.validation_state['log_sequence_state']['last_log_sequence_valid'] = True
                self.validation_state['yaml_sequence_state']['last_yaml_subsequence_valid'] = True
                self.validation_state['yaml_sequence_state']['yaml_state_name'] = yaml_sequence_forward
            else:
                self.validation_state['log_sequence_state']['last_log_sequence_valid'] = False
                self.validation_state['yaml_sequence_state']['last_yaml_sequence_valid'] = False
                self.validation_state['yaml_sequence_state']['yaml_state_name'] = 'log_sequence_in_process'
        else:
            if self.validation_state['valid'] != 'FAIL':
                self.validation_state['valid'] = 'PASS'
                self.validation_state['validation_end_reason'] = "validated"

    def add_sequence_to_validated_sequence_list(self, sequence, subsequence):
        """
        Adds a sequence to the validate sequence list,
        Arguments:
            sequence: A sequence dictionary.
            subsequence: A subsequence dictionary.
        """
        if subsequence:
            self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict'][sequence['sequence_name']] = sequence.copy(
            )
            self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict'][sequence['sequence_name']
            ]['subsequences_dict'] = {}
            for subsequence_name in sequence['subsequences_dict']:
                subsequence = sequence['subsequences_dict'][subsequence_name]
                if subsequence['validated']:
                    validated_sequence = self.validation_state['yaml_sequence_state'][
                        'validated_yaml_sequence_dict'][sequence['sequence_name']]
                    validated_sequence['subsequences_dict'][subsequence['subsequence_name']] = subsequence
        else:
            self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict'][sequence['sequence_name']] = sequence

    def validate_yaml_sequence(self, next_log_sequence):
        """
        Validatea YAML sequence
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
        Returns:
            yaml_sequence_forward: Weather the YAML sequence validation should forward the validation step to the next one.
        """
        if self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict']:
            if next_log_sequence['sequence_name'] in self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict']:
                if next_log_sequence['in_subsequence']:
                    for started_validated_sequence_name in self.validation_state[
                        'yaml_sequence_state']['validated_yaml_sequence_dict']:
                        started_validated_sequence = self.validation_state['yaml_sequence_state'][
                            'current_yaml_sequence_dict'][started_validated_sequence_name]
                        subsequences_dict = started_validated_sequence['subsequences_dict']
                        for subsequence_name in subsequences_dict:
                            subsequence = subsequences_dict[subsequence_name]
                            if not subsequence['validated']:
                                if subsequence['subsequence_name'] == next_log_sequence['subsequence_name']:
                                    subsequence['validated'] = True
                                    self.add_sequence_to_validated_sequence_list(self.validation_state['yaml_sequence_state']['next_yaml_sequence'], subsequence)
                                    return 'sequence_forward'
                                else:
                                    return 'subsequence_forward'
                    return 'subsequence_forward'
                else:
                    sequence_name = self.validation_state['yaml_sequence_state']['next_yaml_sequence']['sequence_name']
                    if self.validation_state['log_sequence_state']['next_log_sequence']['sequence_name'] == sequence_name:
                        self.add_sequence_to_validated_sequence_list(
                            self.validation_state['yaml_sequence_state']['next_yaml_sequence'], None)
                        return 'sequence_forward'
            else:
                if next_log_sequence['in_subsequence']:
                    first_subsequence = self.validation_state['yaml_sequence_state'][
                        'next_yaml_sequence']['subsequences_dict'][next_log_sequence['subsequence_name']]
                    if self.validation_state['log_sequence_state']['next_log_sequence'][
                        'subsequence_name'] == first_subsequence['subsequence_name']:
                        first_subsequence['validated'] = True
                        self.add_sequence_to_validated_sequence_list(
                            self.validation_state['yaml_sequence_state']['next_yaml_sequence'],
                            first_subsequence)
                        return 'subsequence_forward'
                else:
                    sequence_name = self.validation_state['yaml_sequence_state']['next_yaml_sequence']['sequence_name']
                    if self.validation_state['log_sequence_state']['next_log_sequence']['sequence_name'] == sequence_name:
                        self.add_sequence_to_validated_sequence_list(
                            self.validation_state['yaml_sequence_state']['next_yaml_sequence'], None)
                        return 'sequence_forward'
        else:
            if next_log_sequence['in_subsequence']:
                first_subsequence_name = list(self.validation_state['yaml_sequence_state']['next_yaml_sequence']['subsequences_dict'].keys())[0]
                first_subsequence = self.validation_state['yaml_sequence_state'][
                    'next_yaml_sequence']['subsequences_dict'][first_subsequence_name]
                if self.validation_state['log_sequence_state']['next_log_sequence'][
                    'subsequence_name'] == first_subsequence['subsequence_name']:
                    first_subsequence['validated'] = True
                    self.add_sequence_to_validated_sequence_list(self.validation_state['yaml_sequence_state']['next_yaml_sequence'], first_subsequence)
                    return 'subsequence_forward'
            else:
                sequence_name = self.validation_state['yaml_sequence_state']['next_yaml_sequence']['sequence_name']
                if self.validation_state['log_sequence_state']['next_log_sequence']['sequence_name'] == sequence_name:
                    self.add_sequence_to_validated_sequence_list(
                        self.validation_state['yaml_sequence_state']['next_yaml_sequence'], None)
                    return 'sequence_forward'

    @staticmethod
    def yaml_sub_sequences_completed(next_yaml_sequence):
        """
        Increment a YAML sequence valid count.
        Arguments:
            next_yaml_sequence: The next YAML sequence object.
        """
        next_yaml_sequence['sequence_valid_count'] += 1

    def is_last_yaml_sequence_reached(self, preprocessing, is_last_log_sequence_reached):
        """
        Checks weather the last YAML sequence has been reached.
        Arguments:
            preprocessing: The pre-processing object.
            is_last_log_sequence_reached: Weather to warn if a sequence that was not validated exists.
        Returns:
            is_last_yaml_sequence_reached: Weather the last YAML sequence has been reached.
        """
        validated_yaml_sequence_dict = self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict']
        current_yaml_sequence_dict = self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict']
        current_last_validated_sequence = preprocessing.get_yaml_last_valid_sequence(current_yaml_sequence_dict)
        if current_last_validated_sequence['sequence_name'] in validated_yaml_sequence_dict:
            last_validated_yaml_sequence = preprocessing.get_yaml_last_valid_sequence(validated_yaml_sequence_dict)
            if self.validation_state['yaml_sequence_state']['yaml_final_sequence']['sequence_name'] == last_validated_yaml_sequence['sequence_name']:
                if current_last_validated_sequence['has_subsequence']:
                    subsequence = None
                    for subsequence_name in current_last_validated_sequence['subsequences_dict']:
                        subsequence = current_last_validated_sequence['subsequences_dict'][subsequence_name]
                        if not subsequence['validated']:
                            if is_last_log_sequence_reached:
                                self.do_if_last_yaml_sequence_reached()
                            return False
                else:
                    return True
                self.add_sequence_to_validated_sequence_list(current_last_validated_sequence, subsequence)
                self.add_sequence_to_validated_sequence_list(current_last_validated_sequence, subsequence)
                if is_last_log_sequence_reached:
                    self.do_if_last_yaml_sequence_reached()
                return True
            else:
                return False
        else:
            return False

    def do_if_last_yaml_sequence_reached(self):
        """
        Warn if exists a sequence that was not validated.
        """
        validated_yaml_sequence_dict = self.validation_state['yaml_sequence_state']['validated_yaml_sequence_dict']
        current_yaml_sequence_dict = self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict']
        for yaml_sequence_name in current_yaml_sequence_dict:
            current_yaml_sequence = current_yaml_sequence_dict[yaml_sequence_name]
            if yaml_sequence_name not in validated_yaml_sequence_dict.keys() and \
                    (('log_messages' in current_yaml_sequence)
                     and current_yaml_sequence['log_messages']):
                warning_str = f"There was a sequence that was not validated (maybe it was not found), the sequence name is {yaml_sequence_name}"
                self.validation_state['validation_info']['warning'] = warning_str
                self.validation_state['validation_end_reason'] = "sequence_not_validated"
                self.validation_state['valid'] = 'FAIL'
            else:
                if 'subsequences_dict' in current_yaml_sequence:
                    for subsequence_name in current_yaml_sequence['subsequences_dict']:
                        subsequence = current_yaml_sequence['subsequences_dict'][subsequence_name]
                        if not subsequence['validated']:
                            warning_str = f"There was a subsequence that was not validated (maybe it was not found), the sub sequence name is" \
                                          f" {subsequence['subsequence_name']}"
                            self.validation_state['validation_info']['warning'] = warning_str
                            self.validation_state['validation_end_reason'] = "subsequence_not_validated"
                            self.validation_state['valid'] = 'FAIL'

    def validate_fail_message_sequence_flow(self):
        """
        Validates fail message in sequence flow.
        """
        is_fail_message, fail_message = self.is_fail_message(self.validation_state['log_sequence_state']['next_log_sequence'], self.validation_state['yaml_sequence_state']['yaml_sequence'])
        is_flow_fail_message, flow_fail_message = self.is_config_fail_message(self.validation_state['log_sequence_state']['next_log_sequence'], self.validation_state['flow_configuration'])
        if is_fail_message:
            self.validation_state['fails_sequence_dicts']['flow_fail_message_failed'].append(fail_message)
            self.validation_state['fails_num'] += 1
            self.validation_state['validation_end_reason'] = 'a sequence fail message has been found more then the max allowed.'
            self.create_validation_info_with_fail_message(fail_message)
            self.validation_state['valid'] = 'FAIL'
        if is_flow_fail_message:
            self.validation_state['fails_sequence_dicts']['flow_fail_message_failed'].append(flow_fail_message)
            self.validation_state['fails_num'] += 1
            self.validation_state['validation_end_reason'] = 'a flow fail message has been found more then the max allowed.'
            self.create_validation_info_with_fail_message(flow_fail_message)
            self.validation_state['valid'] = 'FAIL'

    def validate_fail_message_message_flow(self, next_log_sequence, global_fail_messages):
        """
        Validates fail message in message flow.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow (taken from the list of messages from sed)
            sequence_info: The sequence information (taken from the YAML).
        """
        for fail_message in global_fail_messages:
            if fail_message['fail_message_name'] == next_log_sequence['log_message_name']:
                if fail_message['max_repeat'] < fail_message['repeat_num']:
                    self.validation_state['fails_sequence_dicts']['global_fail_message_passed'].pop(next_log_sequence['log_message_name'], None)
                    fail_message['validation_end_reason'] = f"fail_message_fail"
                    fail_message['validation_info_str'] = f"The global fail message {next_log_sequence['log_message_name']} has occurred {fail_message['repeat_num']} times," \
                                                          f" which is more than the allowed max repeat: {fail_message['max_repeat']}."
                    self.validation_state['fails_sequence_dicts']['global_fail_message_failed'][next_log_sequence['log_message_name']] = {}
                    self.validation_state['fails_sequence_dicts']['global_fail_message_failed'][next_log_sequence['log_message_name']]['global_fail_message'] = fail_message
                    self.validation_state['fails_sequence_dicts']['global_fail_message_failed'][next_log_sequence['log_message_name']]['validation_end_reason'] = fail_message['validation_end_reason']
                    self.validation_state['fails_sequence_dicts']['global_fail_message_failed'][next_log_sequence['log_message_name']]['validation_info_str'] = fail_message['validation_info_str']
                    try:
                        self.validation_state['fails_sequence_dicts']['global_fail_message_failed'][next_log_sequence['log_message_name']]['global_fail_message_list'].append(next_log_sequence)
                    except Exception:
                        self.validation_state['fails_sequence_dicts']['global_fail_message_failed'][next_log_sequence['log_message_name']]['global_fail_message_list'] = []
                        self.validation_state['fails_sequence_dicts']['global_fail_message_failed'][next_log_sequence['log_message_name']]['global_fail_message_list'].append(next_log_sequence)
                    self.validation_state['fails_num'] += 1
                    self.validation_state['validation_end_reason'] = 'fail_message_fail'
                    self.validation_state['valid'] = 'FAIL'
                else:
                    fail_message['validation_end_reason'] = f"fail_message_pass."
                    fail_message['validation_info_str'] = f"The following message: {next_log_sequence['message_text']} \nhas occurred {fail_message['repeat_num']} times," \
                                                          f" which is less than the allowed max repeat: {fail_message['max_repeat']}."
                    self.validation_state['fails_sequence_dicts']['global_fail_message_passed'][next_log_sequence['log_message_name']] = {}
                    self.validation_state['fails_sequence_dicts']['global_fail_message_passed'][next_log_sequence['log_message_name']]['global_fail_message'] = fail_message
                    self.validation_state['fails_sequence_dicts']['global_fail_message_passed'][next_log_sequence['log_message_name']]['validation_end_reason'] = fail_message['validation_end_reason']
                    self.validation_state['fails_sequence_dicts']['global_fail_message_passed'][next_log_sequence['log_message_name']]['validation_info_str'] = fail_message['validation_info_str']
                    try:
                        self.validation_state['fails_sequence_dicts']['global_fail_message_passed'][next_log_sequence['log_message_name']]['global_fail_message_list'].append(next_log_sequence)
                    except Exception:
                        self.validation_state['fails_sequence_dicts']['global_fail_message_passed'][next_log_sequence['log_message_name']]['global_fail_message_list'] = []
                        self.validation_state['fails_sequence_dicts']['global_fail_message_passed'][next_log_sequence['log_message_name']]['global_fail_message_list'].append(next_log_sequence)
                    if self.validation_state['valid'] != 'FAIL':
                        self.validation_state['valid'] = 'PASS'

    def update_message_repeat_sequence_flow(self, current_yaml_sequence_dict, next_log_sequence, in_subsequence):
        """
        Updates the message repeat number in current_yaml_sequence_dict.
        Arguments:
            current_yaml_sequence_dict: The current YAML validation sequence.
            next_log_sequence: The next log sequence object in the log flow.
            in_subsequence: A boolean with a value weather the next log sequence in a subsequence.
        """
        try:
            if in_subsequence:
                for sub_sequence_name in current_yaml_sequence_dict[next_log_sequence['sequence_name']]['subsequences_dict']:
                    sub_sequence = current_yaml_sequence_dict[next_log_sequence['sequence_name']]['subsequences_dict'][sub_sequence_name]
                    for log_message in sub_sequence['subsequence_log_messages']:
                        self.update_message_repeat(next_log_sequence, log_message)
            else:
                if current_yaml_sequence_dict[next_log_sequence['sequence_name']
                ]['log_messages']:
                    for log_message in current_yaml_sequence_dict[
                        next_log_sequence['sequence_name']]['log_messages']:
                        self.update_message_repeat(
                            next_log_sequence, log_message)
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'update_message_repeat_sequence_flow error.',
            self.logger.error(frame_info, track_message)

    @staticmethod
    def update_message_repeat(next_log_sequence, log_message):
        """
        Updates the message repeat number in next_log_sequence.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            log_message: The log message dictionary.
        """
        if 'has_regex' in log_message and log_message['has_regex']:
            try:
                if re.search(
                        log_message['compiled_regex'].pattern,
                        next_log_sequence['message_text']).group(0):
                    log_message['repeat_num'] += 1
            except Exception:
                pass
        elif next_log_sequence['message_text'] == log_message['message_text']:
            log_message['repeat_num'] += 1

    def update_message_repeat_message_flow(self, next_log_sequence, sequence_info):
        """
        update message repeat number in current_yaml_sequence_dict for message flow.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
        """
        try:
            for sequence in sequence_info:
                if sequence['fail_message_name'] == next_log_sequence['log_message_name']:
                    sequence['repeat_num'] += 1
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'update_message_repeat_message_flow error.',
            self.logger.error(frame_info, track_message)

    def reset_validation_sequence(self):
        """
        Resets the validation flow sequence
        """
        self.validation_state['log_sequence_state']['current_log_sequence'] = [
        ]
        self.validation_state['yaml_sequence_state']['yaml_sequence_num'] = 0
        self.validation_state['yaml_sequence_state']['yaml_state_name'] = 'last_log_sequence_fail'
        self.validation_state['yaml_sequence_state']['yaml_sequence'] = {
            'sequence_name': 'reset'}
        self.validation_state['yaml_sequence_state']['next_yaml_sequence'] = {
            'sequence_name': 'reset'}

    def forward_log_state_per_sequence_flow(self, preprocessing, sequence_state, sequence_list, device_name):
        """
        Forward the log sequence flow validation state.
        Arguments:
            preprocessing: The pre-processing object.
            sequence_state: The sequence state to forward  (can be a log sequence state or a YAML sequence state).
            sequence_list: The list the next forward step is being taken from.
        """
        if len(sequence_list) > 0:
            self.handle_pre_log_forward_step_actions(sequence_state[f'next_log_sequence'], device_name)
            sequence_state[f'previous_log_sequence'] = sequence_state[f'log_sequence']
            sequence_state[f'log_sequence'] = sequence_state[f'next_log_sequence']
            if 'sequence_name' in sequence_state[f'next_log_sequence'] and \
                    sequence_state[f'next_log_sequence']['sequence_name'] != 'init' and \
                    sequence_state[f'next_log_sequence']['sequence_name'] != 'reset' or \
                    'subsequence_name' in sequence_state[f'next_log_sequence']:
                sequence_state['log_sequence_num'] += 1
                if sequence_state['log_sequence_num'] < sequence_state[f'log_final_sequence_num']:
                    sequence_state[f'log_sequence_num'] = sequence_state['log_sequence_num']
                    sequence_state[f'next_log_sequence'] = sequence_list[sequence_state['log_sequence_num']]
                    sequence_state[f'log_state_name'] = f'log_sequence_in_process'
                    try:
                        self.update_message_repeat_sequence_flow(self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'],
                            sequence_state[f'next_log_sequence'],
                            sequence_state[f'next_log_sequence']['in_subsequence'])
                    except Exception:
                        self.logger.error('update message repeat error ')
                    try:
                        self.handle_post_log_forward_step_actions(sequence_state[f'next_log_sequence'], device_name)
                    except Exception:
                        frame_info = getframeinfo(currentframe())
                        track_message = 'handle_post_log_forward_step_actions error.',
                        self.logger.error(frame_info, track_message)
                else:
                    if self.is_last_yaml_sequence_reached(preprocessing, is_last_log_sequence_reached=True) and self.validation_state['valid'] != 'FAIL':
                        self.validation_state['valid'] = 'PASS'
                        self.validation_state['validation_end'] = True
                        self.validation_state['validation_end_reason'] = "validated"
                        sequence_state[f'log_state_name'] = f'log_sequence_end'
                    else:
                        self.validation_state['valid'] = 'FAIL'
                        self.validation_state['validation_end'] = True
                        self.validation_state['validation_end_reason'] = f'log_final_sequence_num_reached'
                        sequence_state[f'log_state_name'] = f'log_sequence_end'
            else:
                next_sequence_num = 0
                try:
                    sequence_state[f'next_log_sequence'] = sequence_list[next_sequence_num]
                    try:
                        self.update_message_repeat_sequence_flow(
                            self.validation_state['yaml_sequence_state']['current_yaml_sequence_dict'],
                            sequence_state[f'next_log_sequence'],
                            sequence_state[f'next_log_sequence']['in_subsequence'])
                    except Exception:
                        frame_info = getframeinfo(currentframe())
                        track_message = 'update message repeat error.',
                        self.logger.error(frame_info, track_message)
                except Exception:
                    pass
                try:
                    self.handle_post_log_forward_step_actions(sequence_state[f'next_log_sequence'], device_name)
                except Exception:
                    frame_info = getframeinfo(currentframe())
                    track_message = 'handle_post_log_forward_step_actions error.',
                    self.logger.error(frame_info, track_message)
                sequence_state[f'log_state_name'] = f'log_sequence_started'
        else:
            self.validation_state['valid'] = 'FAIL'
            self.validation_state['validation_end'] = True
            self.validation_state['validation_end_reason'] = f'log_sequence_list_empty'
            sequence_state[f'log_state_name'] = f'log_sequence_end'

    def forward_yaml_state_per_sequence_flow(self, sequence_state, sequence_list, is_last_log_sequence_reached):
        """
        Forward the YAML sequence flow validation state.
        Arguments:
            sequence_state: The sequence state to forward  (can be a log sequence state or a YAML sequence state).
            sequence_list: The list the next forward step is being taken from
            is_last_log_sequence_reached: Weather the last log sequence has been reached.
        """
        sequence_state[f'previous_yaml_sequence'] = sequence_state[f'yaml_sequence']
        sequence_state[f'yaml_sequence'] = sequence_state[f'next_yaml_sequence']
        if 'sequence_name' in sequence_state[f'next_yaml_sequence'] and \
                sequence_state[f'next_yaml_sequence']['sequence_name'] != 'init' and \
                sequence_state[f'next_yaml_sequence']['sequence_name'] != 'reset':
            try:
                if sequence_state['yaml_sequence_num'] <= sequence_state[f'yaml_final_sequence_num']:
                    if sequence_list[sequence_state['yaml_sequence_num']]['has_subsequence']:
                        if sequence_state['yaml_subsequence_num'] < sequence_state[f'next_yaml_sequence']['subsequence_final_index']:
                            sequence_state['yaml_subsequence_num'] += 1
                        else:
                            self.yaml_sub_sequences_completed(sequence_state['next_yaml_sequence'])
                            sequence_state['yaml_sequence_num'] += 1
                            sequence_state['yaml_subsequence_num'] = 0
                    else:
                        sequence_state['yaml_sequence_num'] += 1
                        sequence_state['yaml_subsequence_num'] = 0
                else:
                    if sequence_list[sequence_state['yaml_final_sequence_num']]['has_subsequence']:
                        if sequence_state['yaml_subsequence_num'] < sequence_state[f'next_yaml_sequence']['subsequence_final_index']:
                            sequence_state['yaml_subsequence_num'] += 1
                        else:
                            self.yaml_sub_sequences_completed(
                                sequence_state['next_yaml_sequence'])
                            sequence_state['yaml_sequence_num'] += 1
                            sequence_state['yaml_subsequence_num'] = 0
                    else:
                        sequence_state['yaml_sequence_num'] += 1
                        sequence_state['yaml_subsequence_num'] = 0
            except Exception:
                pass
            if sequence_state['yaml_sequence_num'] <= sequence_state[f'yaml_final_sequence_num']:
                sequence_state[f'next_yaml_sequence'] = sequence_list[sequence_state['yaml_sequence_num']]
                sequence_state[f'yaml_state_name'] = f'yaml_sequence_in_process'
            else:
                if not is_last_log_sequence_reached:
                    sequence_state[f'yaml_state_name'] = f'yaml_sequence_in_process'
                else:
                    self.validation_state['validation_end_reason'] = "validated"
                    sequence_state['yaml_state_name'] = 'yaml_sequence_end'
        else:
            sequence_state['next_sequence_num'] = 0
            sequence_state['yaml_subsequence_num'] = 0
            try:
                sequence_state[f'next_yaml_sequence'] = sequence_list[sequence_state['next_sequence_num']]
            except Exception:
                pass
            sequence_state[f'yaml_state_name'] = f'yaml_sequence_started'

    def forward_state_per_message_flow(self, sequence_state, sequence_info, sequence_list, device_name):
        """
        Move a step forward the sequence state
        Arguments:
            sequence_state: The sequence state to forward  (can be a log sequence state or a YAML sequence state).
            sequence_info: The sequence information.
            sequence_list: The list the next forward step is being taken from
        """
        self.handle_pre_log_forward_step_actions(sequence_state[f'next_log_sequence'], device_name)
        sequence_state[f'previous_log_sequence'] = sequence_state[f'log_sequence']
        sequence_state[f'log_sequence'] = sequence_state[f'next_log_sequence']
        if sequence_state[f'next_log_sequence']['sequence_name'] != 'init' and sequence_state[f'next_log_sequence']['sequence_name'] != 'reset':
            next_sequence_num = sequence_state['log_sequence_num'] + 1
            if next_sequence_num < sequence_state[f'log_final_sequence_num']:
                sequence_state[f'log_sequence_num'] = next_sequence_num
                sequence_state[f'next_log_sequence'] = sequence_list[next_sequence_num]
                sequence_state[f'log_state_name'] = f'log_sequence_in_process'
                try:
                    self.update_message_repeat_message_flow(sequence_state[f'next_log_sequence'], sequence_info)
                except Exception:
                    frame_info = getframeinfo(currentframe())
                    track_message = 'update message repeat error.',
                    self.logger.error(frame_info, track_message)
            else:
                self.validation_state['validation_end'] = True
                sequence_state[f'log_state_name'] = f'log_sequence_end'
        else:
            next_sequence_num = 0
            try:
                sequence_state[f'next_log_sequence'] = sequence_list[next_sequence_num]
                try:
                    self.update_message_repeat_message_flow(sequence_state[f'next_log_sequence'], sequence_info)
                except Exception:
                    frame_info = getframeinfo(currentframe())
                    track_message = 'update message repeat error.',
                    self.logger.error(frame_info, track_message)
            except Exception:
                pass
            sequence_state[f'log_state_name'] = f'log_sequence_started'
        try:
            self.handle_post_log_forward_step_actions(sequence_state[f'next_log_sequence'], device_name)
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'handle_post_log_forward_step_actions error.',
            self.logger.error(frame_info, track_message)
        return sequence_state

    def handle_pre_log_forward_step_actions(self, next_log_sequence, device_name):
        """
        Handle pre Log Forward Step Actions.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
        """
        pass

    def handle_post_log_forward_step_actions(self, next_log_sequence, device_name):
        """
        Handle post Log Forward Step Actions.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
        """
        if next_log_sequence['sequence_name'] != 'init':
            if 'actions' in next_log_sequence:
                if 'post_log_forward_step' in next_log_sequence['actions']:
                    for action in next_log_sequence['actions']['post_log_forward_step']:
                        getattr(self, action['action_name'])(next_log_sequence, action, device_name)

    def handle_post_validation_action(self, actions_info, global_validation_info, validation_data):
        """
        Handle post validation Actions.
        Arguments:
            actions_info: An object that holds the actions' info.
            global_validation_info: The global validation information.
        Returns:
            global_validation_info: The global validation information.
        """
        if 'post_validation_action' in actions_info:
            for action_name in actions_info['post_validation_action']:
                action = actions_info['post_validation_action'][action_name]
                global_validation_info = getattr(self, action_name)(validation_data, action, global_validation_info)
                return global_validation_info
        return global_validation_info

    # def verify_sequences_conditions(self, _, action, global_validation_info):
    #     """
    #     Handle post validation Actions.
    #     Arguments:
    #         actions_info: An object that holds the actions' info.
    #         global_validation_info: The global validation information.
    #     Returns:
    #         global_validation_info: The global validation information.
    #     """
    #     action_config = action['action_config']
    #     if 'sequences_conditions' in action_config:
    #         result = self.evaluate_conditions(
    #             action_config['sequences_conditions'])
    #         if result == 'PASS':
    #             global_validation_info['Handover_Result'] = 'Handover successful'
    #         elif result == 'FAIL':
    #             global_validation_info['Handover_Result'] = 'Handover failed'
    #     return global_validation_info

    def get_regex_extraction_summary(self, validation_data, action_info_set, global_validation_info):
        global_validation_info['regex_extraction_summary'] = {}
        for flow_dict in validation_data:
            global_validation_info = self.create_regex_extraction_summary(flow_dict['validation_state']['actions_info'], global_validation_info, flow_dict)
        return global_validation_info


    def create_regex_extraction_summary(self, actions_info, global_validation_info, flow_dict):
        for action_info_name in actions_info:
            actions = actions_info[action_info_name]
            for action_name in actions:
                if action_name == 'extract_regex_from_message':
                    if flow_dict['sequence_flow_name'] not in global_validation_info['regex_extraction_summary']:
                        global_validation_info['regex_extraction_summary'][flow_dict['sequence_flow_name']] = {}
                    global_validation_info['regex_extraction_summary'][flow_dict['sequence_flow_name']]['device_name'] = flow_dict['device_name']
                    action_info = actions_info[action_info_name][action_name]['action_info']
                    global_validation_info['regex_extraction_summary'][flow_dict['sequence_flow_name']][action_info_name] = {}
                    global_validation_info['regex_extraction_summary'][flow_dict['sequence_flow_name']][action_info_name][flow_dict['device_name']] = \
                        action_info[flow_dict['device_name']]
        return global_validation_info

    def get_message_stats_summary(self, validation_data, action_info_set, global_validation_info):
        global_validation_info['message_stats_summary'] = {}
        for flow_dict in validation_data:
            global_validation_info = self.create_message_stats_summary(flow_dict['validation_state']['actions_info'], global_validation_info, flow_dict)
        return global_validation_info

    def create_message_stats_summary(self, actions_info, global_validation_info, flow_dict):
        for action_info_name in actions_info:
            action_info = actions_info[action_info_name]
            for action_name in action_info:
                if action_name == 'get_message_stats':
                    if flow_dict['sequence_flow_name'] not in global_validation_info['message_stats_summary']:
                        global_validation_info['message_stats_summary'][flow_dict['sequence_flow_name']] = {}
                    global_validation_info['message_stats_summary'][flow_dict['sequence_flow_name']]['device_name'] = flow_dict['device_name']
                    global_validation_info['message_stats_summary'][flow_dict['sequence_flow_name']][action_info_name] = action_info['get_message_stats']['action_info']
        return global_validation_info

    def get_sequences_stats(self, _, action_info_set, global_validation_info):
        """
        Gets sequences statistics.
        Arguments:
            _: dummy variable
            action_info_set: A set of an action information.
            global_validation_info: The global validation information.
        Returns:
            global_validation_info: The global validation information.
        """
        for flow_dict in self.validation_data:
            if flow_dict['flow_info']:
                if flow_dict['flow_info']['has_sub_flow']:
                    for sub_flow_name in flow_dict['flow_info']:
                        if sub_flow_name == 'has_sub_flow':
                            continue
                        sequence_dict_list = flow_dict['flow_info'][sub_flow_name]['sequence_dict_list']
                        for sequence in sequence_dict_list:
                            sequence_stats = {
                                'sequence_num': sequence['sequence_num'],
                                'sequence_name': sequence['sequence_name'],
                                'sequence_identifier': sequence['sequence_identifier'],
                                'has_subsequence': sequence['has_subsequence'],
                                'in_sub_flow': sequence['in_sub_flow'],
                                'sub_flow_name': sequence['sub_flow_name'],
                                'sequence_valid_count': sequence['sequence_valid_count'],
                                'log_type': flow_dict['log_type'],
                                'device_id': flow_dict['device_id'],
                                'device_name': flow_dict['device_name'],
                                'log_file_name': flow_dict['log_file_name'],
                                'log_file_path': flow_dict['log_file_path'],
                            }
                            if flow_dict['device_name'] not in action_info_set['action_info']:
                                action_info_set['action_info'][flow_dict['device_name']] = {}
                            action_info_set['action_info'][flow_dict['device_name']][sub_flow_name] = {}
                            action_info_set['action_info'][flow_dict['device_name']][sub_flow_name]['sequences_stats'] = sequence_stats
                else:
                    for sequence in flow_dict['sequence_dict_list']:
                        sequence_stats = {
                            'sequence_num': sequence['sequence_num'],
                            'sequence_name': sequence['sequence_name'],
                            'sequence_identifier': sequence['sequence_identifier'],
                            'has_subsequence': sequence['has_subsequence'],
                            'in_sub_flow': sequence['in_sub_flow'],
                            'sub_flow_name': sequence['sub_flow_name'],
                            'sequence_valid_count': sequence['sequence_valid_count'],
                            'log_type': flow_dict['log_type'],
                            'device_id': flow_dict['device_id'],
                            'device_name': flow_dict['device_name'],
                            'log_file_name': flow_dict['log_file_name'],
                            'log_file_path': flow_dict['log_file_path'],
                        }
                        if flow_dict['device_name'] not in action_info_set['action_info']:
                            action_info_set['action_info'][flow_dict['device_name']] = {}
                        action_info_set['action_info'][flow_dict['device_name']][flow_dict['original_sequence_flow_name']] = {}
                        action_info_set['action_info'][flow_dict['device_name']][flow_dict['original_sequence_flow_name']]['sequences_stats'] = sequence_stats
        global_validation_info['sequence_count_summary'] = self.evaluate_sequence_count_summary(action_info_set['action_info'])
        return global_validation_info

    def evaluate_sequence_count_summary(self, action_info):
        """
        Evaluates the sequences count summary.
        Arguments:
            action_info: An action information object.
        Returns:
            sequence_count_summary: The sequences count summary.
        """
        sequence_count_summary = {}
        arranged_sequence_count_summary = {}
        for device_name in action_info:
            if device_name is None or device_name == 'global_action_info':
                continue
            for sub_flow in action_info[device_name]:
                if action_info[device_name][sub_flow]['sequences_stats']['log_type'] == 'DU_MAC':
                    arranged_sequence_count_summary[f"{device_name}"] = {}
                if f"{device_name}" not in sequence_count_summary:
                    sequence_count_summary[f"{device_name}"] = {}
                sequence_count_summary[f"{device_name}"][action_info[device_name][sub_flow]['sequences_stats']['sequence_identifier']] = \
                    action_info[device_name][sub_flow]['sequences_stats']['sequence_valid_count']
                sequence_count_summary[f"{device_name}"]['device_id'] = action_info[device_name][sub_flow]['sequences_stats']['device_id']
        arranged_sequence_count_summary = self.arrange_sequence_count_summary(sequence_count_summary, arranged_sequence_count_summary)
        return arranged_sequence_count_summary

    def arrange_sequence_count_summary(self, sequence_count_summary, arranged_sequence_count_summary):
        for curr_device_name in arranged_sequence_count_summary.keys():
            curr_device_id = sequence_count_summary[curr_device_name]['device_id']
            arranged_sequence_count_summary = self.get_all_devices_for_id(curr_device_id, curr_device_name, sequence_count_summary, arranged_sequence_count_summary)
        return arranged_sequence_count_summary

    def get_all_devices_for_id(self, curr_device_id, curr_device_name, sequence_count_summary, arranged_sequence_count_summary):
        for device_name in sequence_count_summary:
            if sequence_count_summary[device_name]['device_id'] == curr_device_id:
                for sequence_key in sequence_count_summary[device_name].keys():
                    if sequence_key != 'device_id':
                        arranged_sequence_count_summary[curr_device_name][sequence_key] = sequence_count_summary[device_name][sequence_key]
        return arranged_sequence_count_summary

    # @staticmethod
    # def evaluate_conditions(sequences_conditions):
    #     for sequences_condition_name in sequences_conditions:
    #         condition_valid = eval(
    #             sequences_conditions[sequences_condition_name])
    #         if not condition_valid:
    #             return 'FAIL'
    #     return 'PASS'

    def get_sequence_valid_count(self, sequence_identifier):
        """
        Gets a specific sequence valid count.
        Arguments:
            sequence_identifier: The sequence identifier
        Returns:
            sequence_valid_count: The sequence valid count.
        """
        for sequence_flow in self.validation_data:
            validated_yaml_sequence_dict = sequence_flow['validation_state'][
                'yaml_sequence_state']['validated_yaml_sequence_dict']
            for sequence_name in validated_yaml_sequence_dict:
                sequence = validated_yaml_sequence_dict[sequence_name]
                if sequence['sequence_identifier'] == sequence_identifier:
                    return sequence['sequence_valid_count']

    def get_message_stats(self, next_log_sequence, action, device_name):
        """
        Gets a specific message statistics.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            action: An action.
        """
        if self.validation_state['actions_info'][next_log_sequence['log_message_name']][action['action_name']]['result'] == 'Not Found':
            self.validation_state['actions_info'][next_log_sequence['log_message_name']][action['action_name']]['result'] = 'Found'
        self.validation_state['actions_info'][next_log_sequence['log_message_name']][action['action_name']]['action_info'][device_name].append(next_log_sequence)

    def verify_hex_content(self, next_log_sequence, action, device_name):
        """
        Process of the verify_hex_content action.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            action: An action.
        """
        hex_str = next_log_sequence['next_line_dict']['message_text']
        action['hex_str'] = hex_str
        json_o = self.asn1_parse.parse(hex_str)
        all_values_verified = self.verify_json_expected_value(
            json_o, action['action_config'])
        self.validation_state['actions_info'][next_log_sequence['log_message_name']]['action_info'].append(next_log_sequence)
        if all_values_verified:
            action['result'] = 'PASS'
        else:
            action['result'] = 'FAIL'
        if not all_values_verified:
            self.validation_state['validation_end_reason'] = 'A hex message content verification failed'
            self.create_validation_info()
            self.validation_state['valid'] = 'FAIL'
            self.validation_state['validation_end'] = True

    def verify_json_expected_value(self, json_o, action_config):
        """
        Verify an expected_value in a Json object.
        Arguments:
            json_o: Json Object
            action_config: An action configuration object.
        Returns:
            all_values_verified: Weather all the values has been verified.
        """
        all_values_verified = False
        if len(action_config) > 0:
            for expected_value in action_config:
                values = list(
                    self.asn1_parse.find_all_json_keys(
                        expected_value, json_o))
                all_values_verified = self.verify_json_values(
                    values, action_config[expected_value])
        else:
            self.logger.error(
                'The verify_hex_content action has been used but no action_config has been specified')
        return all_values_verified

    @staticmethod
    def verify_json_values(values, expected_value):
        """
        Verify an expected_value in a values list.
        Arguments:
            values: A values list.
            expected_value: The expected value.
        Returns:
            all_values_verified: Weather all the values has been verified.
        """
        for value in values:
            if value != expected_value:
                return False
        return True

    def extract_regex_from_message(self, next_log_sequence, action, device_name):
        """
        Process of the extract_regex_from_message action.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            action: An action.
        """
        self.validation_state['actions_info'][next_log_sequence['log_message_name']][action['action_name']]['action_info'][device_name].append(next_log_sequence)
        if self.validation_state['validation_type'] == 'per_sequence_flow':
            self.extract_regex_message(next_log_sequence, action, next_log_sequence)
        elif self.validation_state['validation_type'] == 'per_message_flow':
            if 'fail_messages_list' in next_log_sequence:
                for fail_message_dict in next_log_sequence['fail_messages_list']:
                    self.extract_regex_message(next_log_sequence, action, fail_message_dict)

    def extract_regex_message(self, next_log_sequence, action, message_dict):
        """
        Extracts a regex pattern from a message.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            action: An action.
            message_dict: A message dictionary.
        """
        match = self.validation_state['actions_info'][next_log_sequence['log_message_name']][action['action_name']]['regex_obj'].match(message_dict['message_text'])
        if not match:
            frame_info = getframeinfo(currentframe())
            track_message = 'The regex pattern matcher has failed.',
            self.logger.error(frame_info, track_message)
        else:
            match_groups = match.groups()
            message_dict['extracted_by_regex'] = match_groups[0]
            regex_format_pattern = action['action_config']['regex_format_pattern']
            if action['action_config']['regex_type'] == 'datetime':
                message_dict['extracted_by_regex'] = self.extract_datetime_regex(message_dict['extracted_by_regex'], regex_format_pattern)

    @staticmethod
    def extract_datetime_regex(extracted_by_regex, regex_format_pattern):
        """
        Extracts a datetime with regex pattern from a message.
        Arguments:
            extracted_by_regex: The extracted regex.
            regex_format_pattern: The datetime regex format pattern.
        Returns:
            datetime_obj: The extracted datetime object.
        """
        datetime_obj = datetime.datetime.strptime(extracted_by_regex, regex_format_pattern)
        return datetime_obj

    @staticmethod
    def verify_max_repeat(next_log_sequence, action, device_name):
        """
        Process of the verify_repeat action.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            action: An action.
        """
        return

    def verify_max_repeat_global_scope(self, log_message):
        """
        Process of the verify_max_repeat_global_scope action.
        Arguments:
            log_message: The log message dictionary.
        """
        try:
            if 'max_repeat' in self.validation_state['global_configuration']:
                if log_message['repeat_num'] > self.validation_state['global_configuration']['max_repeat']:
                    return 'FAIL'
                else:
                    return 'PASS'
        except Exception:
            frame_info = getframeinfo(currentframe())
            track_message = 'check_fail_on_max_repeat_global_scope error.',
            self.logger.error(frame_info, track_message)

    @staticmethod
    def verify_max_repeat_flow_scope(log_message, flow_configuration):
        """
        Process of the verify_max_repeat_flow_scope action.
        Arguments:
            log_message: The log message dictionary.
            flow_configuration: The configuration of the flow.
        """
        if 'max_repeat' in flow_configuration:
            if log_message['repeat_num'] > flow_configuration['max_repeat']:
                return 'FAIL'
            else:
                return 'PASS'

    def verify_max_repeat_message_scope(self, log_message):
        """
        Process of the verify_max_repeat_message_scope action.
        Arguments:
            log_message: The log message dictionary.
        """
        for action in log_message['actions']['post_log_forward_step']:
            if 'max_repeat' in action['action_config']:
                self.validation_state['actions_info'][log_message['log_message_name']][action['action_name']]['action_info'] = log_message['repeat_num']
                if log_message['repeat_num'] > action['action_config']['max_repeat']:
                    self.validation_state['actions_info'][log_message['log_message_name']
                    ][action['action_name']]['result'] = 'FAIL'
                    return 'FAIL'
                else:
                    self.validation_state['actions_info'][log_message['log_message_name']
                    ][action['action_name']]['result'] = 'PASS'
                    return 'PASS'
        return None

    @staticmethod
    def verify_repeat(next_log_sequence, action, device_name):
        """
        Process of the verify_repeat action.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            action: An action.
        """
        return

    @staticmethod
    def verify_min_repeat(next_log_sequence, action, device_name):
        """
        Process of the verify_repeat action.
        Arguments:
            next_log_sequence: The next log sequence object in the log flow.
            action: An action.
        """
        return

    def process_global_actions(self, preprocessing, validation_data, global_configuration):
        """
        Process of global actions.
        Arguments:
            preprocessing: The pre-processing object.
            validation_data: The validation data object.
            global_configuration: The global configuration object.
        Returns:
            global_validation_info: The global validation information.
        """
        self.validation_data = validation_data
        global_validation_info = {}
        if global_configuration and 'actions' in global_configuration:
            action_flow_position = 'post_validation_action'
            source_item_dict = {
                'global_action_items': {
                    'post_validation_action': {
                        'actions': global_configuration['actions']}}}
            target_item_dict = {
                'global_action_items': {
                    'actions': global_configuration['actions'].copy()}}
            actions_info = {}
            actions_info = preprocessing.get_actions(
                None,
                source_item_dict['global_action_items'],
                action_flow_position,
                target_item_dict['global_action_items'],
                'post_validation_action',
                actions_info)
            global_validation_info = self.handle_post_validation_action(actions_info, global_validation_info, validation_data)
        return global_validation_info
