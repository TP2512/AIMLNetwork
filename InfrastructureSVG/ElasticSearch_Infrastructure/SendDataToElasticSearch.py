import logging
from datetime import datetime, timezone
import copy
import json
import os

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection


class CreateDocument:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.doc = {}
        self.client = ElasticSearchConnection().connect_to_svg_elasticsearch()
        # self.client = ElasticSearchConnection().connect_to_svg_elasticsearch_dev()
        self.env_config_key = None
        self.bs_hardwares_type_list_of_dicts = []
        self.bs_hardwares_type_list = []
        self.feature_name = None
        self.group_name = None
        self.sub_task = None
        self.kwargs = kwargs

    @staticmethod
    def _get_fields_from_test_obj(field, param_to_return='value'):
        return getattr(field, param_to_return) if field else None

    def get_feature_name(self):
        self.feature_name = self.kwargs['environment_objs'].test_sir_obj.fields.customfield_11801[0]

    def get_groups(self):
        self.group_name = self.kwargs['environment_objs'].test_sir_obj.fields.customfield_19601

    def get_ho_results(self, mode_index):
        if not self.kwargs['results_and_status_obj'].HO_RESULTS:
            return
        if self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index].get('test_status'):
            self.kwargs['results_and_status_obj'].TEST_STATUS = self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index]['test_status']
        if self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index].get('ho_rate'):
            self.kwargs['results_and_status_obj'].HO_SUCCESS_RATE = self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index].get('ho_rate')
        if self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index].get('failure_reason'):
            self.kwargs['results_and_status_obj'].AUTOMATION_ERROR_MESSAGE = self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index].get('failure_reason')
        if self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index].get('actual_results'):
            self.kwargs['results_and_status_obj'].ACTUAL_RESULT = self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index].get('actual_results')
        if self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index].get('execution_key'):
            self.kwargs['EXECUTION_KEY'] = self.kwargs['results_and_status_obj'].HO_RESULTS[mode_index].get('execution_key')

    def get_mtbf_results(self, mode_index):
        if self.kwargs['results_and_status_obj'].MTBF.get(mode_index):
            self.kwargs['results_and_status_obj'].CORE_OCCURRENCE_COUNT = self.kwargs['results_and_status_obj'].MTBF[mode_index].CORE_OCCURRENCE_COUNT
            self.kwargs['results_and_status_obj'].MTBF_CORE_OCCURRENCE_COUNT = self.kwargs['results_and_status_obj'].MTBF[mode_index].MTBF_CORE_OCCURRENCE_COUNT
            self.kwargs['results_and_status_obj'].TIME_TO_FIRST_CRASH = self.kwargs['results_and_status_obj'].MTBF[mode_index].TIME_TO_FIRST_CRASH
            self.kwargs['results_and_status_obj'].MIN_RUN_TIME = self.kwargs['results_and_status_obj'].MTBF[mode_index].MIN_RUN_TIME
            self.kwargs['results_and_status_obj'].MAX_RUN_TIME = self.kwargs['results_and_status_obj'].MTBF[mode_index].MAX_RUN_TIME

    def get_cores(self, mode_index):
        self.kwargs['results_and_status_obj'].CORE_FILES_NAME = self.kwargs['results_and_status_obj'].CORE_FILES[mode_index] if self.kwargs['results_and_status_obj'].CORE_FILES else []

    @staticmethod
    def version_iterator(version_dict):
        for _, version in version_dict.items():
            return version

    def extract_versions(self, version_type):
        for hw_type, version_dict in self.kwargs.get('versions').items():
            if hw_type == version_type:
                return self.version_iterator(version_dict)

    def extract_previous_versions(self, version_type):
        if hasattr(self.kwargs['results_and_status_obj'], 'PREVIOUS_VERSION'):
            for hw_type, version_dict in self.kwargs['results_and_status_obj'].PREVIOUS_VERSION.items():
                if hw_type == version_type:
                    return self.version_iterator(version_dict)
        else:
            self.logger.error('extract_previous_versions not working')
            self.logger.error(f'"version_type" is: {version_type}')

    def get_env_config(self):
        try:
            return [i.inwardIssue.key for i in self.kwargs['environment_objs'].test_plan_obj.fields.issuelinks if hasattr(i, 'inwardIssue') and 'SVGA' in i.inwardIssue.key][0]
        except IndexError:
            return [i.outwardIssue.key for i in self.kwargs['environment_objs'].test_plan_obj.fields.issuelinks if hasattr(i, 'outwardIssue') and 'SVGA' in i.outwardIssue.key][0]

    def prepare_doc_global_information_body(self):
        timestamp = datetime.now(tz=timezone.utc)

        return {
            'timestamp': timestamp,

            'Slave Name': self.kwargs['environment_objs'].jenkins_args.get('slave_name'),
            'Test Plan': self.kwargs['environment_objs'].jenkins_args.get('test_plan_id'),
            'Test Set': self.kwargs['environment_objs'].jenkins_args.get('test_set_id'),
            'Test SIR': self.kwargs['environment_objs'].jenkins_args.get('test_sir'),
            'Jenkins Build ID': self.kwargs['environment_objs'].jenkins_args.get('build_id'),
            'Execution Summary': self.kwargs['environment_objs'].jenkins_args.get('test_summary'),
            'Builder Name': self.kwargs['environment_objs'].jenkins_args.get('BUILDER_NAME'),
            'UR Version': self.kwargs['environment_objs'].jenkins_args.get('UR_VERSION'),

            'Run Test In Loop': self.kwargs['environment_objs'].jenkins_args.get('RUN_TEST_IN_LOOP'),
            'Loop Count': self.kwargs['environment_objs'].jenkins_args.get('LOOP_COUNT'),

            'Environment Config': self.get_env_config(),

            'Jenkins Link': self.kwargs.get('REPORT_LINK'),
            'Scenario Run Time': self.kwargs['mtbf_results_obj'].SCENARIO_RUN_TIME,
            'Labels': self.kwargs.get('labels'),
            'Link': self.kwargs.get('Link'),

            'Feature Name': self.feature_name,
            'Group Name': self.group_name,

            'Test Run Time': self.kwargs.get('run_time') or self.kwargs['environment_objs'].test_sir_obj.fields.customfield_12623,
            'Number Of Ues': self.kwargs['environment_objs'].test_sir_obj.fields.customfield_13716,

            'Traffic Transport Layer Protocol': self._get_fields_from_test_obj(self.kwargs['environment_objs'].test_sir_obj.fields.customfield_13816),
            'Automation Traffic Direction': self._get_fields_from_test_obj(self.kwargs['environment_objs'].test_sir_obj.fields.customfield_13834),
            'Traffic Testing tool': self._get_fields_from_test_obj(self.kwargs['environment_objs'].test_sir_obj.fields.customfield_13900),
            'Window Size': self._get_fields_from_test_obj(self.kwargs['environment_objs'].test_sir_obj.fields.customfield_14300),
            'Frame Size': self._get_fields_from_test_obj(self.kwargs['environment_objs'].test_sir_obj.fields.customfield_12607),
            'HO Type': self._get_fields_from_test_obj(self.kwargs['environment_objs'].test_sir_obj.fields.customfield_13821),

            'Threshold UL': self.kwargs['results_and_status_obj'].EXPECTED_UL,
            'Threshold DL': self.kwargs['results_and_status_obj'].EXPECTED_DL,
            'Threshold': self.kwargs.get('THRESHOLD'),
            'UL AVG': self.kwargs['results_and_status_obj'].UL,
            'DL AVG': self.kwargs['results_and_status_obj'].DL,
            'MAX UL': self.kwargs['results_and_status_obj'].MAX_UL,
            'MAX DL': self.kwargs['results_and_status_obj'].MAX_DL,

            'Expected DL ': self.kwargs['results_and_status_obj'].EXPECTED_DL,
            'Expected UL ': self.kwargs['results_and_status_obj'].EXPECTED_UL,

            'Defects List': self.kwargs['results_and_status_obj'].DEFECTS_LIST,
        }

    def prepare_doc_body(self, gnb):
        timestamp = datetime.now(tz=timezone.utc)
        if self.kwargs.get('EXECUTION_KEY') and type(self.kwargs.get('EXECUTION_KEY')) is str:
            execution = self.kwargs.get('EXECUTION_KEY')
        elif self.kwargs.get('EXECUTION_KEY'):
            execution = self.kwargs.get('EXECUTION_KEY').key
        else:
            execution = None

        return {
            'timestamp': timestamp,

            'GNB Object': gnb,

            'GNB Name': gnb['name'],
            'GNB ID': gnb['id'],
            'GNB Type': gnb['hardware_type']['name'],
            'GNB ACP NAME': gnb['acp_name'],
            'BS Hardware Type': self.sub_task.customfield_10800[0].value,
            'Chipset': self._get_fields_from_test_obj(self.sub_task.customfield_10510) or None,
            'Format(SSF)': self.sub_task.customfield_17300[0].value,
            'Numerology(SCS)': self.sub_task.customfield_16900[0].value,
            'DL Layers': self.sub_task.customfield_17301[0].value,
            'UL Layers': self.sub_task.customfield_17302[0].value,
            'Band': self.sub_task.customfield_10511.value,
            'Bandwidth': self.sub_task.customfield_10513.value,
            'CUCP_Ver': self.extract_versions('cucps_under_test_versions'),
            'CUUP_Ver': self.extract_versions('cuups_under_test_versions'),
            'DU_Ver': self.extract_versions('dus_under_test_versions'),
            'RU_Ver': self.extract_versions('rus_under_test_versions'),
            'AIO_Ver': self.extract_versions('aio_pack_vers_under_test_versions'),
            'XPU_Ver': self.extract_versions('xpus_under_test_versions'),
            'Previous_CUCP_Ver': self.extract_previous_versions('cucps_under_test_versions'),
            'Previous_CUUP_Ver': self.extract_previous_versions('cuups_under_test_versions'),
            'Previous_DU_Ver': self.extract_previous_versions('dus_under_test_versions'),
            'Previous_RU_Ver': self.extract_previous_versions('rus_under_test_versions'),
            'Previous_AIO_Ver': self.extract_previous_versions('aio_pack_vers_under_test_versions'),
            'Previous_XPU_Ver': self.extract_previous_versions('xpus_under_test_versions'),
            'ACP Version': self.kwargs.get('ACP_VERSION'),
            'Previous ACP Version': self.kwargs['results_and_status_obj'].PREVIOUS_ACP_VERSION,
            'Path': self.kwargs.get('Path'),
            'DL Throughput (Mbps)': self.kwargs['results_and_status_obj'].DL,
            'UL Throughput (Mbps)': self.kwargs['results_and_status_obj'].UL,

            'Execution Key': execution,

            'Fix Versions': self.kwargs.get('FIX_VERSIONS'),
            'Test Status': self.kwargs['results_and_status_obj'].TEST_STATUS,
            'Core SystemUpTime (min)': self.kwargs.get('Core SystemUpTime (min)'),
            'HO Success Rate': self.kwargs['results_and_status_obj'].HO_SUCCESS_RATE if self.kwargs['results_and_status_obj'].HO_SUCCESS_RATE is not None else None,
            'Ping Avg Latency': self.kwargs['results_and_status_obj'].PING_AVG_LATENCY,
            'Ping Loss': self.kwargs['results_and_status_obj'].PING_LOSS,
            'Log Path': self.kwargs['results_and_status_obj'].LOGS_PATH,
            'Actual Results': self.kwargs['results_and_status_obj'].ACTUAL_RESULT,
            'Test Results': self.kwargs['results_and_status_obj'].TEST_RESULTS,
            'KPI': self.kwargs['results_and_status_obj'].KPI,

            'SCENARIO RUN TIME': self.kwargs['mtbf_results_obj'].SCENARIO_RUN_TIME,

            'Core Occurrence Count': self.kwargs['results_and_status_obj'].CORE_OCCURRENCE_COUNT,
            'MTBF Core Occurrence Count': self.kwargs['results_and_status_obj'].MTBF_CORE_OCCURRENCE_COUNT,
            'Time To First Crash': self.kwargs['results_and_status_obj'].TIME_TO_FIRST_CRASH,
            'Minimum Run Time': self.kwargs['results_and_status_obj'].MIN_RUN_TIME,
            'Maximum Run Time': self.kwargs['results_and_status_obj'].MAX_RUN_TIME,
            'Core Files Name': self.kwargs['results_and_status_obj'].CORE_FILES_NAME,
            # 'Core SystemUpTime:': self.kwargs['results_and_status_obj'].CORE_SYSTEM_UP_TIME,

            'UE_STATISTICS': self.kwargs['results_and_status_obj'].UE_STATISTICS,
            'UE_RESULTS': self.kwargs['results_and_status_obj'].UE_RESULTS,

            'SYSTEM_RECOVERY_TIME': self.kwargs['results_and_status_obj'].SYSTEM_RECOVERY_TIME,

            "Automation Error Message": self.kwargs['results_and_status_obj'].AUTOMATION_ERROR_MESSAGE,
        }

    @staticmethod
    def index_in_list(a_list, index):
        return index < len(a_list) if a_list else False

    @staticmethod
    def validate_tp_result_dict(body, ue):
        if not body.get('TP_Results'):
            body['TP_Results'] = {}
        if not body['TP_Results'].get(ue):
            body['TP_Results'][ue] = {}
        return body

    def update_ue_dict(self, ue_values, index, ue, body):
        body = self.validate_tp_result_dict(body, ue)

        if ue_values.get('DL') and self.index_in_list(ue_values.get('DL'), index):
            body['TP_Results'][ue].update({"DL": ue_values.get('DL')[index] if ue_values.get('DL') is not None and self.index_in_list(ue_values.get('DL'), index) else 0})

        if ue_values.get('UL') and self.index_in_list(ue_values.get('UL'), index):
            body['TP_Results'][ue].update({"UL": ue_values.get('UL')[index] if ue_values.get('UL') is not None and self.index_in_list(ue_values.get('UL'), index) else 0})

        if (self.index_in_list(ue_values.get('DL'), index) or self.index_in_list(ue_values.get('UL'), index)) and self.kwargs['results_and_status_obj'].UE_STATISTICS.get(ue) and body['TP_Results'].get(ue):
            for i in list(self.kwargs['results_and_status_obj'].UE_STATISTICS[ue].keys()):
                if self.kwargs['results_and_status_obj'].UE_STATISTICS[ue].get(i):
                    body['TP_Results'][ue].update({i: self.kwargs['results_and_status_obj'].UE_STATISTICS[ue][i][index] if self.index_in_list(
                        self.kwargs['results_and_status_obj'].UE_STATISTICS[ue][i], index) and self.kwargs['results_and_status_obj'].UE_STATISTICS[ue][i][index] is not None else 0})

        return body

    def get_total(self, body):
        _body = copy.deepcopy(body)
        body['Total_DL_TP'] = 0
        body['Total_UL_TP'] = 0
        for k, v in _body.items():
            if 'UE' in k:
                if self.kwargs['environment_objs'].test_sir_obj.fields.customfield_13834.value == 'DL':
                    body['Total_DL_TP'] += v['DL']
                elif self.kwargs['environment_objs'].test_sir_obj.fields.customfield_13834.value == 'UL':
                    body['Total_UL_TP'] += v['UL']
                else:
                    body['Total_DL_TP'] += v['DL']
                    body['Total_UL_TP'] += v['UL']
        return body

    def normalize_data(self):
        self.logger.info('Normalizing data')
        for key, value in self.kwargs['results_and_status_obj'].UE_STATISTICS.items():
            for stat_name, stat_values in value.items():
                if isinstance(stat_values, str):
                    continue
                last_index = 0
                for _ in range(int(self.kwargs['environment_objs'].test_sir_obj.fields.customfield_12623)):
                    if int(self.kwargs['environment_objs'].test_sir_obj.fields.customfield_12623) == len(stat_values):
                        break

                    if isinstance(stat_values, list):
                        stat_values.insert(last_index, stat_values[last_index])
                        if last_index + 2 <= len(stat_values) - 1:
                            last_index += 2
                        else:
                            last_index = 0
                # self.logger.info(len(stat_values))
                # self.logger.info(stat_values)

    @staticmethod
    def _clean_none_fields(body):
        _body = copy.deepcopy(body)
        for k in list(body.keys()):
            if _body.get(k) is None:
                _body.pop(k)
        return _body

    @staticmethod
    def dump_to_json(result_object, path, file_name):
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f"{path}\\{file_name}.json", 'w') as fp:
            json.dump(result_object, fp, indent=4)

    def create_execution(self):
        self.get_feature_name()
        self.get_groups()
        list_of_docs = []
        body = ''
        global_information_body = self.prepare_doc_global_information_body()

        if self.kwargs['results_and_status_obj'].MULTIPLE_EXECUTION:
            if self.kwargs['environment_objs'].test_sir_obj.fields.customfield_13821 and 'XN' in self.kwargs['environment_objs'].test_sir_obj.fields.customfield_13821.value:
                for mode_index, gnb in enumerate(self.kwargs['environment_objs'].setup_obj['gnodeb_setup'], start=1):
                    self.get_subtask(mode_index, gnb)
                    self.get_ho_results(mode_index=mode_index)
                    self.get_mtbf_results(mode_index=mode_index)
                    self.get_cores(mode_index=mode_index)
                    body = self.prepare_doc_body(gnb=gnb)
                    list_of_docs.append(body)
            else:
                for mode_index, (ru_index, ru_params) in enumerate(self.kwargs['environment_objs'].tree['rus_under_test'].items(), start=1):
                    self.sub_task = ru_params['subtask'].fields
                    self.get_ho_results(mode_index=mode_index)
                    self.get_mtbf_results(mode_index=mode_index)
                    self.get_cores(mode_index=mode_index)
                    if gnb := [gnb for gnb in self.kwargs['environment_objs'].setup_obj['gnodeb_setup'] if gnb['name'] == ru_params['gnodeb'][0]]:
                        body = self.prepare_doc_body(gnb=gnb[0])
                    else:
                        self.logger.error('Failed to get gnb name')
                    list_of_docs.append(body)

        else:
            gnb = [gnb for gnb in self.kwargs['environment_objs'].setup_obj['gnodeb_setup'] if gnb['name'] == self.extract_gnb_name()['gnodeb'][0]]
            self.get_subtask(1)
            self.get_mtbf_results(mode_index=1)
            self.get_cores(mode_index=1)
            if gnb:
                list_of_docs.append(self.prepare_doc_body(gnb=gnb[0]))
            else:
                self.logger.error('Failed to get GNB')
        return global_information_body, list_of_docs

    def extract_gnb_name(self):
        for index, du in self.kwargs['environment_objs'].tree['dus_under_test'].items():
            return du

    def extract_ru_from_gnb(self, name):
        return next((value for index, (key, value) in enumerate(self.kwargs['environment_objs'].tree['rus_under_test'].items(), start=1) if value['acp_name'] == name), None)

    def get_subtask(self, index, gnb=None):
        if gnb:
            if gnb['hardware_type']['name'] == 'AIO':
                ru = self.extract_ru_from_gnb(gnb['ru_gnodeb'][0]['acp_name'])
            else:
                ru = self.extract_ru_from_gnb(gnb['ru_gnodeb'][index - 1]['acp_name'])
            self.sub_task = ru['subtask'].fields
        else:
            self.sub_task = self.kwargs['environment_objs'].tree['rus_under_test'][index]['subtask'].fields
