import logging
from copy import deepcopy, copy
from elasticsearch import helpers
from datetime import datetime, timezone
import asyncio

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchHelper


class ELKClassError(Exception):
    pass


class ELKReporter:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.elk_client = None
        self.list_of_docs: list = []
        self.index_name: dict = {}

    def get_elk_client(self, debug: bool) -> None:
        if debug:
            self.elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch_dev()
        else:
            self.elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch()

    @staticmethod
    def generate_doc_id(test_results_object: dict = None) -> str:
        if not test_results_object:
            return datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%m')

        build_id = f"{test_results_object['test_info']['build_id']}"
        test_sir_id = f"{test_results_object['test_info']['test_sir_id']}"
        scenario_end_time = test_results_object['test_info']['scenario_end_time'].replace('-', '').replace(' ', '').replace(':', '')
        return f"{scenario_end_time}{build_id}{test_sir_id.replace('SIR-', '')}"

    def fill_list_of_docs(self, index_name: str, doc: dict) -> None:
        self.list_of_docs.append(
            {
                "_index": index_name,
                "_source": copy(doc)
            }
        )

    def fill_list_of_docs_as_deepcopy(self, index_name: str, doc: dict) -> None:
        self.list_of_docs.append(
            {
                "_index": index_name,
                "_source": deepcopy(doc)
            }
        )

    def set_list_of_docs(self) -> None:
        self.logger.info('Start "set_list_of_docs" function')
        if self.list_of_docs:
            self.logger.info('Start to report the documents to ELK')
            ElasticSearchHelper().change_elasticsearch_logger()
            helpers.bulk(self.elk_client, self.list_of_docs)
        else:
            self.logger.error('list_of_docs is empty')


class ReportToELKHelper:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        if self.__class__.__name__ != 'ReportToELK':
            raise ELKClassError('Cannot call constructor, use the "ReportToELK" Class')


class ReportToELK:  # BuildDocsFromRobotFrameworkObject
    def __init__(self, test_results_object: dict, debug: bool = False) -> None:
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.debug = debug
        self.elk_reporter = ELKReporter()

        self.dut = None
        self.test_results_object = test_results_object
        self.feature_global_information_doc = None
        self.shortest_time = None
        self.ue_shortest_time = None
        self.qci_shortest_time = None

        self.gnb_flag = True
        self.ue_flag = True

        self.elk_reporter.get_elk_client(debug=debug)
        self.get_index_name()

    def get_index_name(self) -> None:
        if self.debug:
            self.elk_reporter.index_name = {
                'dashboard_results_feature_details': 'new_dashboard_results_feature_details_production_ng_1',
                'dashboard_results_gnbs': 'new_dashboard_results_gnbs_production_ng_1',
                'dashboard_results_gnb_cells': 'new_dashboard_results_gnb_cell_details_production_ng_1',
                'dashboard_results_gnb_cell_ues': 'new_dashboard_results_gnb_cell_ue_details_production_ng_1',
                'dashboard_results_gnb_cell_ue_qcis': 'new_dashboard_results_gnb_cell_ue_qci_details_production_ng_1',
            }
        else:
            self.elk_reporter.index_name = {
                'dashboard_results_feature_details': 'new_dashboard_results_feature_details_production_ng',
                'dashboard_results_gnbs': 'new_dashboard_results_gnbs_production_ng',
                'dashboard_results_gnb_cells': 'new_dashboard_results_gnb_cell_details_production_ng',
                'dashboard_results_gnb_cell_ues': 'new_dashboard_results_gnb_cell_ue_details_production_ng',
                'dashboard_results_gnb_cell_ue_qcis': 'new_dashboard_results_gnb_cell_ue_qci_details_production_ng',

                # 'dashboard_results_setup': 'new_dashboard_results_setup_production',
                # 'dashboard_results_ues': 'new_dashboard_results_ues_production',
                # 'dashboard_results_execution': 'new_dashboard_results_execution_production',
                # 'dashboard_results_error_and_warning_list': 'new_dashboard_results_error_and_warning_list_production',
            }

    def update_run_time(self) -> None:
        if all(
                test_tag not in ['throughput', 'link_adaptation']
                for test_tag in self.test_results_object['test_info']['labels']
        ):
            self.test_results_object['test_info']['run_time'] = 1

    def add_test_run_time_by_shortest_list(self) -> None:
        len_list = []
        ue_list = []
        qci_list = []
        for dut_k, dut_v in self.test_results_object[self.dut].items():
            for cells_k, cells_v in dut_v['cells'].items():
                for ues_k, ues_v in cells_v['ues'].items():
                    for value in ues_v.keys():
                        if type(ues_v.get(value)) is not list and value != 'qcis':
                            continue
                        elif value != 'qcis':
                            ue_list.append(len(ues_v.get(value)))
                            len_list.append(len(ues_v.get(value)))
                        else:
                            for qcis_k, qcis_v in ues_v['qcis'].items():
                                qci_list.extend(len(qcis_v.get(value)) for value in qcis_v.keys() if value != 'tp_results' and type(qcis_v.get(value)) is list)
                                len_list.extend(len(qcis_v.get(value)) for value in qcis_v.keys() if value != 'tp_results' and type(qcis_v.get(value)) is list)
        self.ue_shortest_time = sorted(ue_list)[0] if ue_list else 1
        self.qci_shortest_time = sorted(qci_list)[0] if qci_list else 1
        self.shortest_time = sorted(len_list)[0] if len_list else 1

    def add_scenario_run_time(self) -> None:
        if scenario_run_time := [v['mtbf']['scenario_run_time'] for k, v in self.test_results_object['gnb'].items()][0]:
            self.test_results_object['test_info']['scenario_run_time'] = scenario_run_time
        else:
            self.test_results_object['test_info']['scenario_run_time'] = None

    def add_scenario_status(self) -> None:
        status_list = [f"{v['test_status']}".upper() for k, v in self.test_results_object[self.dut].items()]
        if 'ABORTED' in status_list:
            self.logger.info("scenario_status == ABORTED, doesn't need to report this scenario to ELK")
            self.test_results_object['test_info']['scenario_status'] = 'ABORTED'
        elif set(status_list) == {'PASS'}:
            self.test_results_object['test_info']['scenario_status'] = 'PASS'
        elif 'AUTOMATION_FAIL' in status_list:
            self.test_results_object['test_info']['scenario_status'] = 'AUTOMATION_FAIL'
        elif 'FAIL' in status_list:
            self.test_results_object['test_info']['scenario_status'] = 'FAIL'
        else:
            self.test_results_object['test_info']['scenario_status'] = 'FAIL_TO_GENERATE_STATUS'

    def add_and_update_data(self) -> None:
        self.update_run_time()
        self.add_test_run_time_by_shortest_list()
        # self.add_scenario_run_time()
        self.add_scenario_status()

    def get_scenario_status_number(self) -> int:
        if self.test_results_object['test_info']['scenario_status'].upper() == 'PASS':
            return 10
        elif self.test_results_object['test_info']['scenario_status'].upper() == 'FAIL':
            return 5
        elif self.test_results_object['test_info']['scenario_status'].upper() == 'AUTOMATION_FAIL':
            return 0
        elif self.test_results_object['test_info']['scenario_status'].upper() == 'FAIL_TO_GENERATE_STATUS':
            return -1

    def get_throughput_results_list_str(self, traffic_direction: list[str] = None) -> list:
        if not traffic_direction:
            traffic_direction = ['DL', 'UL']

        throughput_results_list_per_gnb = []
        for k, v in self.test_results_object[self.dut].items():
            l_dl = []
            l_ul = []
            for kk, vv in v['tp_results'].items():
                if 'DL' in kk and 'DL' in traffic_direction:
                    l_dl.append(f'{kk}: {vv}')
                elif 'UL' in kk and 'UL' in traffic_direction:
                    l_ul.append(f'{kk}: {vv}')

            if l_dl and l_ul:
                throughput_results_list_per_gnb.append(f'{k} - [{", ".join(l_dl)} ; {", ".join(l_ul)}]')
            elif l_dl:
                throughput_results_list_per_gnb.append(f'{k} - [{", ".join(l_dl)}]')
            elif l_ul:
                throughput_results_list_per_gnb.append(f'{k} - [{", ".join(l_ul)}]')
            else:
                throughput_results_list_per_gnb.append(f'{k} - [N/A]')

        return throughput_results_list_per_gnb

    def get_sub_tasks_list(self, key_list: list[str] = None) -> list:
        if not key_list:
            if '5g' in self.test_results_object['test_info']['protocol']:
                key_list = ['cucp', 'cuup', 'du', 'ru']
            if '4g' in self.test_results_object['test_info']['protocol']:
                key_list = ['enb']

        all_sub_task_list = []
        for k, v in self.test_results_object[self.dut].items():
            sub_task_list = [
                f"{key.upper()}: {', '.join(sorted(v['sub_tasks'][f'{key}_sub_task']))}"
                for key in key_list
            ]
            all_sub_task_list.append(f"[{', '.join(sub_task_list)}]")
        return all_sub_task_list

    def create_feature_global_information_dict(self, automation_manual: str, jira_test_run_time: str) -> dict:
        # sourcery skip: low-code-quality
        self.logger.debug('starting "fill_feature_global_information_doc" function')

        return_dict = {
            "automation_manual": automation_manual,

            "doc_id": self.test_results_object['test_info']['feature_doc_id'],
            "feature_doc_id": self.test_results_object['test_info']['feature_doc_id'],
            "protocol": self.test_results_object['test_info']['protocol'],
            "automation_version": self.test_results_object['test_info'].get('automation_version', 'null'),
            "ezlife_builder_id": int(self.test_results_object['test_info']['builder_id']),
            "ezlife_builder_name": self.test_results_object['test_info']['builder_name'],
            "jenkins_version": self.test_results_object['test_info']['jenkins_version'],
            "jenkins_job_name": self.test_results_object['test_info']['job_name'],
            "jenkins_build_number_int": self.test_results_object['test_info']['build_id'],
            "jenkins_build_number": f"Build #{self.test_results_object['test_info']['build_id']}",
            "slave_name": self.test_results_object['test_info']['slave_name'],
            "setup_type": self.test_results_object['test_info']['setup_type'],
            "ur_version_cycle_str": self.test_results_object['test_info']['ur_version_cycle'] if self.test_results_object['test_info'].get('ur_version_cycle') is not None else '0',
            "ur_version_cycle_int": int(self.test_results_object['test_info']['ur_version_cycle']) if self.test_results_object['test_info'].get('ur_version_cycle') is not None else 0,

            "ur_version": self.test_results_object['test_info']['ur_version'].replace(".", "_"),

            "feature_name": self.test_results_object['test_info']['feature_name'],
            "feature_group_name": self.test_results_object['test_info']['group_name'],

            "environment_config": self.test_results_object['test_info']['environment_config'],
            "test_plan": self.test_results_object['test_info']['test_plan_id'],
            "test_set": self.test_results_object['test_info']['test_set_id'],
            "test_sir": self.test_results_object['test_info']['test_sir_id'],

            "test_sir_per_all_sub_tasks":
                f"{self.test_results_object['test_info']['test_sir_id']} - "
                " ; ".join(sorted(set(self.get_sub_tasks_list()), reverse=True)),

            # ### need to check / change

            "execute_environment_config_per_test_sir_per_all_sub_tasks":
                f"{self.test_results_object['test_info']['environment_config']} - "
                f"{self.test_results_object['test_info']['test_sir_id']} - "
                " ; ".join(sorted(set(self.get_sub_tasks_list()), reverse=True)),

            #

            "execute_environment_config_and_test_sir":
                f"{self.test_results_object['test_info']['environment_config']} - {self.test_results_object['test_info']['test_sir_id']}",

            "execute_environment_config_and_test_per_ur_version":
                f"{self.test_results_object['test_info']['environment_config']} - {self.test_results_object['test_info']['test_sir_id']}",
            "environment_config_and_test_per_ur_version":
                f"{self.test_results_object['test_info']['environment_config']} - {self.test_results_object['test_info']['test_sir_id']}",
            "test_plan_2": self.test_results_object['test_info']['test_plan_id'],
            "test_sir_2": self.test_results_object['test_info']['test_sir_id'],
            "test_plan_and_test_sir_2": f"{self.test_results_object['test_info']['test_plan_id']} + {self.test_results_object['test_info']['test_sir_id']}",

            # ###

            # "scenario_run_time": self.test_results_object['test_info']['scenario_run_time'],
            "scenario_status": self.test_results_object['test_info']['scenario_status'],
            "scenario_status_number": self.get_scenario_status_number(),

            "jira_test_run_time": int(jira_test_run_time),
            "shortest_time": int(self.shortest_time),
            "ue_shortest_time": int(self.ue_shortest_time),
            "qci_shortest_time": int(self.qci_shortest_time),
            "number_of_ues": int(self.test_results_object['test_info'].get('number_of_ues', 0)),
            "run_test_in_loops": self.test_results_object['test_info'].get('run_test_in_loop', False),
            "loops_count": self.test_results_object['test_info'].get('loop_count', 0),

            "ems_fix_version_list": [self.test_results_object['test_info']['acp_version']],
            "ems_version_list": [self.test_results_object['test_info']['acp_version']],
            "ems_version_list_str": ', '.join([self.test_results_object['test_info']['acp_version']]),

            "previous_ems_fix_version_list": sorted([self.test_results_object['test_info']['previous_acp_version']]),
            "previous_ems_version_list": sorted([self.test_results_object['test_info']['previous_acp_version']]),
            "previous_ems_version_list_str": ', '.join(sorted([self.test_results_object['test_info']['previous_acp_version']])),

            # Configurations
            # "all_execution_key_list": [v['execution_key'] for k, v in self.test_results_object[self.dut].items()],
            "all_actual_results_list": list({vv for k, v in self.test_results_object[self.dut].items() for vv in v['actual_results']}),
            "all_failure_reason_list": list({vv for k, v in self.test_results_object[self.dut].items() for vv in v['failure_reason']}),
            "all_failure_reason_id_list": list({vv for k, v in self.test_results_object[self.dut].items() for vv in v['failure_reason_id']}),
            "all_configuration_list": sorted([', '.join(v['config'].values()) for k, v in self.test_results_object[self.dut].items()]),
            "all_configuration_list_min": sorted({', '.join(v['config'].values()) for k, v in self.test_results_object[self.dut].items()}),
            "all_configuration_list_str": '   +   '.join(sorted([', '.join(v['config'].values()) for k, v in self.test_results_object[self.dut].items()])),
            "all_configuration_list_min_str": '   +   '.join(sorted({', '.join(v['config'].values()) for k, v in self.test_results_object[self.dut].items()})),

            "hardware_type_list": sorted({v['config']['hw_type'] for k, v in self.test_results_object[self.dut].items()}),
            "hardware_type_list_str": ', '.join(sorted({v['config']['hw_type'] for k, v in self.test_results_object[self.dut].items()})),

            "band_list": sorted({v['config']['band'] for k, v in self.test_results_object[self.dut].items()}),
            "band_list_str": ', '.join(sorted({v['config']['band'] for k, v in self.test_results_object[self.dut].items()})),

            "bandwidth_list": sorted({v['config']['bandwidth'] for k, v in self.test_results_object[self.dut].items()}),
            "bandwidth_list_str": ', '.join(sorted({v['config']['bandwidth'] for k, v in self.test_results_object[self.dut].items()})),

            "chipset_list": sorted({v['config']['chipset'] for k, v in self.test_results_object[self.dut].items()}),
            "chipset_list_str": ', '.join(sorted({v['config']['chipset'] for k, v in self.test_results_object[self.dut].items()})),

            "cell_carrier_list": sorted({v['config']['cell_carrier'] for k, v in self.test_results_object[self.dut].items()}),
            "cell_carrier_list_str": ', '.join(sorted({v['config']['cell_carrier'] for k, v in self.test_results_object[self.dut].items()})),

            "defects_list": sorted({defect for k, v in self.test_results_object[self.dut].items() for defect in v.get('defects_list', ['N/A'])}),
            "defects_list_str": ', '.join(sorted({defect for k, v in self.test_results_object[self.dut].items() for defect in v.get('defects_list', ['N/A'])})),

            'core_files_name_list': sorted({vv for k, v in self.test_results_object[self.dut].items() for vv in v['mtbf'].get('core_file_names', [])}),
            'core_files_name_list_str': ', '.join(sorted({vv for k, v in self.test_results_object[self.dut].items() for vv in v['mtbf'].get('core_file_names', [])})),

            # ##### Data Per gNB #####
            "all_sub_task_list": sorted(set(self.get_sub_tasks_list()), reverse=True),
            "all_sub_task_list_str": ' ; '.join(sorted(set(self.get_sub_tasks_list()), reverse=True)),

            # ##### Current Version Per DUT #####
            "test_execution_list": [v.get('execution_key') for k, v in self.test_results_object[self.dut].items()],
            # "test_execution_list_str": ', '.join([v.get('execution_key') for k, v in self.test_results_object[self.dut].items()]),
            "dut_test_status_list": sorted({v.get('test_status', 'null') for k, v in self.test_results_object[self.dut].items()}),

            "pack_version_list": sorted({version.replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                                         for kk, version in v['current_version']['pack_vers_under_test_versions'].items()}),
            "pack_version_list_str": ', '.join(sorted({version.replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                                                       for kk, version in v['current_version']['pack_vers_under_test_versions'].items()})),

            # ##### Throughput #####
            "all_throughput_results_list": [f'{k} - {kk}: {vv}' for k, v in self.test_results_object[self.dut].items() for kk, vv in v['tp_results'].items()],
            # "all_throughput_results_list_str": ', '.join([f'{k} - {kk}: {vv}' for k, v in self.test_results_object[self.dut].items() for kk, vv in v['tp_results'].items()]),
            "all_throughput_results_list_str": self.get_throughput_results_list_str(),

            "all_dl_throughput_results_list": [f'{k} - {kk}: {vv}' for k, v in self.test_results_object[self.dut].items() for kk, vv in v['tp_results'].items() if 'DL' in kk],
            # "all_dl_throughput_results_list_str": ', '.join([f'{k} - {kk}: {vv}' for k, v in self.test_results_object[self.dut].items() for kk, vv in v['tp_results'].items() if 'DL' in kk]),
            "all_dl_throughput_results_list_str": self.get_throughput_results_list_str(traffic_direction=['DL']),

            "all_ul_throughput_results_list": [f'{k} - {kk}: {vv}' for k, v in self.test_results_object[self.dut].items() for kk, vv in v['tp_results'].items() if 'UL' in kk],
            # "all_ul_throughput_results_list_str": ', '.join([f'{k} - {kk}: {vv}' for k, v in self.test_results_object[self.dut].items() for kk, vv in v['tp_results'].items() if 'UL' in kk]),
            "all_ul_throughput_results_list_str": self.get_throughput_results_list_str(traffic_direction=['UL']),

        }

        if '5g' in self.test_results_object['test_info']['protocol']:
            return_dict |= {
                "test_sir_per_ru_sub_task": f"{self.test_results_object['test_info']['test_sir_id']} - {' ; '.join(sorted(set(self.get_sub_tasks_list(key_list=['ru']))))}",

                "format_list": sorted({v['config']['format'] for k, v in self.test_results_object[self.dut].items()}),
                "format_list_str": ', '.join(sorted({v['config']['format'] for k, v in self.test_results_object[self.dut].items()})),

                "numerology_list": list({v['config']['numerology'] for k, v in self.test_results_object[self.dut].items()}),
                "numerology_list_str": ', '.join(list({v['config']['numerology'] for k, v in self.test_results_object[self.dut].items()})),

                "tdd_split_list": sorted({v['config']['tdd_split'] for k, v in self.test_results_object[self.dut].items()}),
                "tdd_split_list_str": ', '.join(sorted({v['config']['tdd_split'] for k, v in self.test_results_object[self.dut].items()})),

                "product_support_list": sorted({v['config']['product_support'] for k, v in self.test_results_object[self.dut].items()}),
                "product_support_list_str": ', '.join(sorted({v['config']['product_support'] for k, v in self.test_results_object[self.dut].items()})),

                "cucp_sub_task_list": sorted(set(self.get_sub_tasks_list(key_list=['cucp']))),
                "cucp_sub_task_list_str": ' ; '.join(sorted(set(self.get_sub_tasks_list(key_list=['cucp'])))),

                "cuup_sub_task_list": sorted(set(self.get_sub_tasks_list(key_list=['cuup']))),
                "cuup_sub_task_list_str": ' ; '.join(sorted(set(self.get_sub_tasks_list(key_list=['cuup'])))),

                "du_sub_task_list": sorted(set(self.get_sub_tasks_list(key_list=['du']))),
                "du_sub_task_list_str": ' ; '.join(sorted(set(self.get_sub_tasks_list(key_list=['du'])))),

                "ru_sub_task_list": sorted(set(self.get_sub_tasks_list(key_list=['ru']))),
                "ru_sub_task_list_str": ' ; '.join(sorted(set(self.get_sub_tasks_list(key_list=['ru'])))),

                # ##### Data Per gNB #####
                # ##### Current Version Per gNB #####
                "gnb_ran_mode_list": sorted({v.get('ran_mode') for k, v in self.test_results_object['gnb'].items()}),
                "gnb_type_list": sorted({v['ran_mode'] for k, v in self.test_results_object['gnb'].items()}),
                "gnb_type_list_str": ', '.join(sorted({v['ran_mode'] for k, v in self.test_results_object['gnb'].items()})),

                "fix_version_list": sorted(
                    set(
                        [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                         for kk, version in v['current_version']['cucps_under_test_versions'].items()] +
                        [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                         for kk, version in v['current_version']['cuups_under_test_versions'].items()] +
                        [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                         for kk, version in v['current_version']['dus_under_test_versions'].items()] +
                        [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                         for kk, version in v['current_version']['rus_under_test_versions'].items()] +
                        [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                         for kk, version in v['current_version'].get('xpus_under_test_versions', {}).items()]
                    )
                ),

                "fix_version_list_str": ', '.join(
                    sorted(
                        set(
                            [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                             for kk, version in v['current_version']['cucps_under_test_versions'].items()] +
                            [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                             for kk, version in v['current_version']['cuups_under_test_versions'].items()] +
                            [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                             for kk, version in v['current_version']['dus_under_test_versions'].items()] +
                            [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                             for kk, version in v['current_version']['rus_under_test_versions'].items()] +
                            [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                             for kk, version in v['current_version'].get('xpus_under_test_versions', {}).items()]
                        )
                    )
                ),

                "cucp_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                                 for kk, version in v['current_version']['cucps_under_test_versions'].items()}),
                "cucp_version_list": sorted({version.replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                             for kk, version in v['current_version']['cucps_under_test_versions'].items()}),
                "cucp_version_list_str": ', '.join(sorted({version.replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                                           for kk, version in v['current_version']['cucps_under_test_versions'].items()})),

                "cuup_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                                 for kk, version in v['current_version']['cuups_under_test_versions'].items()}),
                "cuup_version_list": sorted({version.replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                             for kk, version in v['current_version']['cuups_under_test_versions'].items()}),
                "cuup_version_list_str": ', '.join(sorted({version.replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                                           for kk, version in v['current_version']['cuups_under_test_versions'].items()})),

                "du_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                               for kk, version in v['current_version']['dus_under_test_versions'].items()}),
                "du_version_list": sorted({version.replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                           for kk, version in v['current_version']['dus_under_test_versions'].items()}),
                "du_version_list_str": ', '.join(sorted({version.replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                                         for kk, version in v['current_version']['dus_under_test_versions'].items()})),

                "ru_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                               for kk, version in v['current_version']['rus_under_test_versions'].items()}),
                "ru_version_list": sorted({version.replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                           for kk, version in v['current_version']['rus_under_test_versions'].items()}),
                "ru_version_list_str": ', '.join(sorted({version.replace(".", "_") for k, v in self.test_results_object['gnb'].items()
                                                         for kk, version in v['current_version']['rus_under_test_versions'].items()})),

                "xpu_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                for kk, version in v['current_version'].get('xpus_under_test_versions', {}).items()}),
                "xpu_version_list": sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                            for kk, version in v['current_version'].get('xpus_under_test_versions', {}).items()}),
                "xpu_version_list_str": ', '.join(sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                          for kk, version in v['current_version'].get('xpus_under_test_versions', {}).items()})),

                # ##### Previous Version Per gNB #####
                "previous_cucp_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                          for kk, version in v['previous_version']['cucps_under_test_versions'].items()}),
                "previous_cucp_version_list": sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                      for kk, version in v['previous_version']['cucps_under_test_versions'].items()}),
                "previous_cucp_version_list_str": ', '.join(sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                                    for kk, version in v['previous_version']['cucps_under_test_versions'].items()})),

                "previous_cuup_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                          for kk, version in v['previous_version']['cuups_under_test_versions'].items()}),
                "previous_cuup_version_list": sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                      for kk, version in v['previous_version']['cuups_under_test_versions'].items()}),
                "previous_cuup_version_list_str": ', '.join(sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                                    for kk, version in v['previous_version']['cuups_under_test_versions'].items()})),

                "previous_du_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                        for kk, version in v['previous_version']['dus_under_test_versions'].items()}),
                "previous_du_version_list": sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                    for kk, version in v['previous_version']['dus_under_test_versions'].items()}),
                "previous_du_version_list_str": ', '.join(sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                                  for kk, version in v['previous_version']['dus_under_test_versions'].items()})),

                "previous_ru_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                        for kk, version in v['previous_version']['rus_under_test_versions'].items()}),
                "previous_ru_version_list": sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                    for kk, version in v['previous_version']['rus_under_test_versions'].items()}),
                "previous_ru_version_list_str": ', '.join(sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                                  for kk, version in v['previous_version']['rus_under_test_versions'].items()})),

                "previous_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                     for kk, version in v['previous_version']['pack_vers_under_test_versions'].items()}),
                "previous_pack_version_list": sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                      for kk, version in v['previous_version']['pack_vers_under_test_versions'].items()}),
                "previous_pack_version_list_str": ', '.join(sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                                    for kk, version in v['previous_version']['pack_vers_under_test_versions'].items()})),

                "previous_xpu_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                         for kk, version in v['previous_version'].get('xpus_under_test_versions', {}).items()}),
                "previous_xpu_version_list": sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                     for kk, version in v['previous_version'].get('xpus_under_test_versions', {}).items()}),
                "previous_xpu_version_list_str": ', '.join(sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object['gnb'].items()
                                                                   for kk, version in v['previous_version'].get('xpus_under_test_versions', {}).items()})),

                # 'dl_min_rx_rate_mbps_list': [f"{k} - {v['tp_results'].get('DLMinRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                              if v['tp_results'].get('DLMinRxRate(Mbps)')],
                # 'dl_min_rx_rate_mbps_list_str': ', '.join([f"{k} - {v['tp_results'].get('DLMinRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                                            if v['tp_results'].get('DLMinRxRate(Mbps)')]),
                #
                # 'dl_avg_rx_rate_mbps_list': [f"{k} - {v['tp_results'].get('DLAvgRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                              if v['tp_results'].get('DLAvgRxRate(Mbps)')],
                # 'dl_avg_rx_rate_mbps_list_str': ', '.join([f"{k} - {v['tp_results'].get('DLAvgRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                                            if v['tp_results'].get('DLAvgRxRate(Mbps)')]),
                #
                # 'dl_avg_max_rate_mbps_list': [f"{k} - {v['tp_results'].get('DLMaxRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                               if v['tp_results'].get('DLMaxRxRate(Mbps)')],
                # 'dl_avg_max_rate_mbps_list_str': ', '.join([f"{k} - {v['tp_results'].get('DLMaxRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                                             if v['tp_results'].get('DLMaxRxRate(Mbps)')]),
                #
                # 'ul_min_rx_rate_mbps_list': [f"{k} - {v['tp_results'].get('ULMinRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                              if v['tp_results'].get('ULMinRxRate(Mbps)')],
                # 'ul_min_rx_rate_mbps_list_str': ', '.join([f"{k} - {v['tp_results'].get('ULMinRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                                            if v['tp_results'].get('ULMinRxRate(Mbps)')]),
                #
                # 'ul_avg_rx_rate_mbps_list': [f"{k} - {v['tp_results'].get('ULAvgRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                              if v['tp_results'].get('ULAvgRxRate(Mbps)')],
                # 'ul_avg_rx_rate_mbps_list_str': ', '.join([f"{k} - {v['tp_results'].get('ULAvgRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                                            if v['tp_results'].get('ULAvgRxRate(Mbps)')]),
                #
                # 'ul_avg_max_rate_mbps_list': [f"{k} - {v['tp_results'].get('ULMaxRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                               if v['tp_results'].get('ULMaxRxRate(Mbps)')],
                # 'ul_avg_max_rate_mbps_list_str': ', '.join([f"{k} - {v['tp_results'].get('ULMaxRxRate(Mbps)')}" for k, v in self.test_results_object['gnb'].items()
                #                                             if v['tp_results'].get('ULMaxRxRate(Mbps)')]),

                # # ##### HO #####
                # "kpi_list": [v['kpi'] if v.get('kpi') else 'N/A' for k, v in self.test_results_object['gnb'].items()],
                # "kpi_list_str": ', '.join(sorted({f"{v['kpi']}" if v.get('kpi') else ['N/A'] for k, v in self.test_results_object['gnb'].items()})),
                #
                # "ho_rate_list": [v['ho_rate'] for k, v in self.test_results_object['gnb'].items() if v.get('ho_rate')],
                # "ho_rate_list_str": ', '.join(sorted({v['ho_rate'] for k, v in self.test_results_object['gnb'].items()})),

                # ----- thresholds -----
                # ----- Need to add more thresholds -----

                # # ##### Throughput #####
                # "threshold": float(self.test_results_object['test_info']['Threshold']) if self.test_results_object['test_info'].get('Threshold') is not None else -1.0,  # in percent
                # "dl_threshold": float(self.test_results_object['test_info']['Threshold DL']) if self.test_results_object['test_info'].get('Threshold DL') is not None else -1.0,
                # "ul_threshold": float(self.test_results_object['test_info']['Threshold UL']) if self.test_results_object['test_info'].get('Threshold UL') is not None else -1.0,
                #
                # "ul_avg": float(self.test_results_object['test_info']['UL AVG']) if self.test_results_object['test_info'].get('UL AVG') is not None else -1.0,
                # "dl_avg": float(self.test_results_object['test_info']['DL AVG']) if self.test_results_object['test_info'].get('DL AVG') is not None else -1.0,
                # "max_ul": float(self.test_results_object['test_info']['MAX UL']) if self.test_results_object['test_info'].get('MAX UL') is not None else -1.0,
                # "max_dl": float(self.test_results_object['test_info']['MAX DL']) if self.test_results_object['test_info'].get('MAX DL') is not None else -1.0,
                #
                # "expected_dl": float(self.test_results_object['test_info']['Expected DL']) if self.test_results_object['test_info'].get('Expected DL') is not None else None,
                # "expected_ul": float(self.test_results_object['test_info']['Expected UL']) if self.test_results_object['test_info'].get('Expected UL') is not None else None,

                #
            }

        if '4g' in self.test_results_object['test_info']['protocol']:
            return_dict |= {
                "enb_sub_task_list": sorted(set(self.get_sub_tasks_list(key_list=['enb']))),
                "enb_sub_task_list_str": ' ; '.join(sorted(set(self.get_sub_tasks_list(key_list=['enb'])))),

                # ##### Data Per gNB #####
                # ##### Current Version Per gNB #####
                "fix_version_list": sorted(
                    set(
                        [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                         for kk, version in v['current_version']['pack_vers_under_test_versions'].items()] +
                        [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                         for kk, version in v['current_version']['relay_version'].items() if version]
                    )
                ),
                "fix_version_list_str": ', '.join(
                    sorted(
                        set(
                            [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                             for kk, version in v['current_version']['pack_vers_under_test_versions'].items()] +
                            [version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                             for kk, version in v['current_version']['relay_version'].items() if version]
                        )
                    )
                ),

                "enb_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                                                for kk, version in v['current_version']['pack_vers_under_test_versions'].items()}),
                "enb_version_list": sorted({version.replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                                            for kk, version in v['current_version']['pack_vers_under_test_versions'].items()}),
                "enb_version_list_str": ', '.join(sorted({version.replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                                                          for kk, version in v['current_version']['pack_vers_under_test_versions'].items()})),

                "relay_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                                                  for kk, version in v['current_version']['relay_version'].items() if version}),
                "relay_version_list": sorted({version.replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                                              for kk, version in v['current_version']['relay_version'].items() if version}),
                "relay_version_list_str": ', '.join(sorted({version.replace(".", "_") for k, v in self.test_results_object[self.dut].items()
                                                            for kk, version in v['current_version']['relay_version'].items() if version})),

                # ##### Previous Version Per gNB #####
                "previous_enb_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") if version else 'null' for k, v in self.test_results_object[self.dut].items()
                                                         for kk, version in v['previous_version']['pack_vers_under_test_versions'].items()}),
                "previous_enb_version_list": sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object[self.dut].items()
                                                     for kk, version in v['previous_version']['pack_vers_under_test_versions'].items()}),
                "previous_enb_version_list_str": ', '.join(sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object[self.dut].items()
                                                                   for kk, version in v['previous_version']['pack_vers_under_test_versions'].items()})),

                "previous_relay_fix_version_list": sorted({version.split('-', 1)[0].replace(".", "_") if version else 'null' for k, v in self.test_results_object[self.dut].items()
                                                           for kk, version in v['previous_version']['relay_version'].items() if version}),
                "previous_relay_version_list": sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object[self.dut].items()
                                                       for kk, version in v['previous_version']['relay_version'].items() if version}),
                "previous_relay_version_list_str": ', '.join(sorted({version.replace(".", "_") if version else 'null' for k, v in self.test_results_object[self.dut].items()
                                                                     for kk, version in v['previous_version']['relay_version'].items() if version})),
            }

        # ##### Feature Information #####

        # ##### Throughput #####
        if self.test_results_object['test_info'].get('traffic_transport_layer'):
            return_dict |= {
                "traffic_transport_layer_protocol": self.test_results_object['test_info'].get('traffic_transport_layer', 'null'),
                "automation_traffic_direction": self.test_results_object['test_info'].get('traffic_direction', 'null'),
                "traffic_testing_tool": self.test_results_object['test_info'].get('traffic_testing_tool', 'null'),
                "window_size": self.test_results_object['test_info'].get('tcp_window_size', 'null'),
                "frame_size": self.test_results_object['test_info'].get('frame_size', 'null'),
            }

        # ##### HandOver #####
        if self.test_results_object['test_info'].get('ho_type'):
            return_dict["ho_type"] = self.test_results_object['test_info'].get('ho_type', 'null')

        return return_dict

    def create_feature_details_dict(self, timestamp: datetime) -> dict:
        self.logger.debug('starting "fill_feature_details_dict" function')

        return {
            "timestamp": timestamp,
        }

    def fill_feature_details_doc(self) -> None:
        feature_details_doc = self.create_feature_details_dict(
            timestamp=datetime.now(timezone.utc),
        )
        feature_details_doc |= self.feature_global_information_doc
        self.elk_reporter.fill_list_of_docs(index_name=self.elk_reporter.index_name['dashboard_results_feature_details'], doc=feature_details_doc)

    def create_global_dut_data_dict(self, timestamp: datetime, dut_data: dict) -> dict:
        self.logger.debug('starting "fill_global_gnb_data_dict" function')

        return_dict = {
            "timestamp": timestamp,
            "dut_acp_name": dut_data['acp_name'],
            # "gnb_serial_number": gnb_data['serial_number'],
            "dut_test_status": dut_data['test_status'],
            # "gnb_execution_key": gnb_data['execution_key'],
            "dut_failure_reason_id": dut_data['failure_reason_id'],
            "dut_failure_reason": dut_data['failure_reason'],
            "dut_actual_results": dut_data['actual_results'],

            "all_configuration_list": ', '.join(dut_data['config'].values()),
            "dut_hardware_type": dut_data['config']['hw_type'],
            "dut_band": dut_data['config']['band'],
            "dut_bandwidth": dut_data['config']['bandwidth'],
            "dut_chipset": dut_data['config']['chipset'],
            "dut_cell_carrier": dut_data['config']['cell_carrier'],
            # "scs": gnb_data['config']['scs'],
            "dut_dl_layers": dut_data['config'].get('dl_layers'),
            "dut_ul_layers": dut_data['config'].get('ul_layers'),
        }

        if '5g' in self.test_results_object['test_info']['protocol']:
            return_dict |= {
                "gnb_ran_mode": dut_data['ran_mode'],
                "gnb_type_name": dut_data['ran_mode'],

                "dut_numerology": dut_data['config']['numerology'],
                "dut_format_ssf": dut_data['config']['format'],

                "gnb_cucp_version": list({v.replace(".", "_") for k, v in dut_data['current_version']['cucps_under_test_versions'].items()}),
                "gnb_cuup_version": list({v.replace(".", "_") for k, v in dut_data['current_version']['cuups_under_test_versions'].items()}),
                "gnb_du_version": list({v.replace(".", "_") for k, v in dut_data['current_version']['dus_under_test_versions'].items()}),
                "gnb_ru_version": list({v.replace(".", "_") for k, v in dut_data['current_version']['rus_under_test_versions'].items()}),
                "gnb_pack_version": list({v.replace(".", "_") for k, v in dut_data['current_version']['pack_vers_under_test_versions'].items()}),
                "gnb_xpu_version": list({v.replace(".", "_") for k, v in dut_data['current_version']['xpus_under_test_versions'].items()}),
                "gnb_helm_version": list({v.replace(".", "_") for k, v in dut_data['current_version']['helms_under_test_versions'].items()}),

                "previous_gnb_cucp_version": list({v.replace(".", "_") for k, v in dut_data['previous_version']['cucps_under_test_versions'].items()}),
                "previous_gnb_cuup_version": list({v.replace(".", "_") for k, v in dut_data['previous_version']['cuups_under_test_versions'].items()}),
                "previous_gnb_du_version": list({v.replace(".", "_") for k, v in dut_data['previous_version']['dus_under_test_versions'].items()}),
                "previous_gnb_ru_version": list({v.replace(".", "_") for k, v in dut_data['previous_version']['rus_under_test_versions'].items()}),
                "previous_gnb_pack_version": list({v.replace(".", "_") for k, v in dut_data['previous_version']['pack_vers_under_test_versions'].items()}),
                "previous_gnb_xpu_version": list({v.replace(".", "_") for k, v in dut_data['previous_version']['xpus_under_test_versions'].items()}),
                "previous_gnb_helm_version": list({v.replace(".", "_") for k, v in dut_data['previous_version']['helms_under_test_versions'].items()}),

                "gnb_core_occurrence_count": dut_data['mtbf'].get('core_occurrence_count', 0),
                "gnb_mtbf_core_occurrence_count": dut_data['mtbf'].get('mtbf_core_occurrence_count', 0),
                "gnb_mtbf": dut_data['mtbf'].get('mtbf', -1),
                "gnb_core_system_up_time": dut_data['mtbf'].get('core_system_up_time', -1),
                "gnb_minimum_run_time": dut_data['mtbf'].get('min_run_time', -1),
                "gnb_maximum_run_time": dut_data['mtbf'].get('max_run_time', -1),
                "gnb_time_to_first_crash": dut_data['mtbf'].get('time_to_first_crash', -1),

                # Missing
                "gnb_core_files_name_list": dut_data['mtbf'].get('gnb_core_files_name_list', []),
                "gnb_core_system_up_time_min": dut_data['mtbf'].get('gnb_core_system_up_time_min', -1),

                "gnb_expected_throughput_dl": dut_data.get('expected_throughput', {}).get('DL', -1.0),
                "gnb_expected_throughput_ul": dut_data.get('expected_throughput', {}).get('UL', -1.0),
                "gnb_expected_throughput_by_threshold_dl": dut_data.get('expected_throughput_by_threshold', {}).get('DL', -1.0),
                "gnb_expected_throughput_by_threshold_ul": dut_data.get('expected_throughput_by_threshold', {}).get('UL', -1.0),

                # 'memory'
                'memory__gnb_du__ssi_mem_cli_exec__virt': copy(dut_data['memory'].get('gnb_du -f ../config/ssi_mem_cli_exec -s 64').get('VIRT', [])),
                'memory__gnb_du__ssi_mem_cli_exec__res': copy(dut_data['memory'].get('gnb_du -f ../config/ssi_mem_cli_exec -s 64').get('RES', [])),

                'memory__gnb_du__ssi_mem__virt': copy(dut_data['memory'].get('gnb_du -f ../config/ssi_mem').get('VIRT', [])),
                'memory__gnb_du__ssi_mem__res': copy(dut_data['memory'].get('gnb_du -f ../config/ssi_mem').get('RES', [])),

                'memory__gnb_cu_up_gcli__virt': copy(dut_data['memory'].get('gnb_cu_up_gcli').get('VIRT', [])),
                'memory__gnb_cu_up_gcli__res': copy(dut_data['memory'].get('gnb_cu_up_gcli').get('RES', [])),

                'memory__gnb_cu_up__virt': copy(dut_data['memory'].get('gnb_cu_up').get('VIRT', [])),
                'memory__gnb_cu_up__res': copy(dut_data['memory'].get('gnb_cu_up').get('RES', [])),

                'memory__gnb_cu_pd__virt': copy(dut_data['memory'].get('gnb_cu_pd').get('VIRT', [])),
                'memory__gnb_cu_pd__res': copy(dut_data['memory'].get('gnb_cu_pd').get('RES', [])),

                'memory__gnb_cu_dl_1__virt': copy(dut_data['memory'].get('gnb_cu_dl 1').get('VIRT', [])),
                'memory__gnb_cu_dl_1__res': copy(dut_data['memory'].get('gnb_cu_dl 1').get('RES', [])),

                'memory__gnb_cu_dl_2__virt': copy(dut_data['memory'].get('gnb_cu_dl 2').get('VIRT', [])),
                'memory__gnb_cu_dl_2__res': copy(dut_data['memory'].get('gnb_cu_dl 2').get('RES', [])),

                'memory__gnb_cu_ul__virt': copy(dut_data['memory'].get('gnb_cu_ul').get('VIRT', [])),
                'memory__gnb_cu_ul__res': copy(dut_data['memory'].get('gnb_cu_ul').get('RES', [])),

                'memory__gnb_cu_cp_gcli__virt': copy(dut_data['memory'].get('gnb_cu_cp_gcli').get('VIRT', [])),
                'memory__gnb_cu_cp_gcli__res': copy(dut_data['memory'].get('gnb_cu_cp_gcli').get('RES', [])),

                'memory__gnb_cu_cp_sctp_e1_s__virt': copy(dut_data['memory'].get('gnb_cu_cp_sctp E1_S').get('VIRT', [])),
                'memory__gnb_cu_cp_sctp_e1_s__res': copy(dut_data['memory'].get('gnb_cu_cp_sctp E1_S').get('RES', [])),

                'memory__gnb_cu_cp_sctp_f1_s__virt': copy(dut_data['memory'].get('gnb_cu_cp_sctp F1_S').get('VIRT', [])),
                'memory__gnb_cu_cp_sctp_f1_s__res': copy(dut_data['memory'].get('gnb_cu_cp_sctp F1_S').get('RES', [])),

                'memory__gnb_cu_cp_sctp_ng_c__virt': copy(dut_data['memory'].get('gnb_cu_cp_sctp NG_C').get('VIRT', [])),
                'memory__gnb_cu_cp_sctp_ng_c__res': copy(dut_data['memory'].get('gnb_cu_cp_sctp NG_C').get('RES', [])),

                'memory__gnb_cu_cp_sctp_xn_c_s__virt': copy(dut_data['memory'].get('gnb_cu_cp_sctp XN_C_S').get('VIRT', [])),
                'memory__gnb_cu_cp_sctp_xn_c_s__res': copy(dut_data['memory'].get('gnb_cu_cp_sctp XN_C_S').get('RES', [])),

                'memory__gnb_cu_cp__virt': copy(dut_data['memory'].get('gnb_cu_cp').get('VIRT', [])),
                'memory__gnb_cu_cp__res': copy(dut_data['memory'].get('gnb_cu_cp').get('RES', [])),
            }

        if '4g' in self.test_results_object['test_info']['protocol'].lower():
            return_dict |= {
                "enb_version": list({v.replace(".", "_") for k, v in dut_data['current_version']['pack_vers_under_test_versions'].items()}),
                "relay_version": list({v.replace(".", "_") for k, v in dut_data['current_version']['relay_version'].items() if v}),

                "previous_enb_version": list({v.replace(".", "_") for k, v in dut_data['previous_version']['pack_vers_under_test_versions'].items()}),
                "previous_relay_version": list({v.replace(".", "_") for k, v in dut_data['previous_version']['relay_version'].items() if v}),
            }

        # ##### HandOver #####
        if self.test_results_object['test_info'].get('ho_type'):
            return_dict["ho_rate"] = dut_data.get('ho_rate')

        return return_dict

    def fill_dut_docs(self, dut_data: dict) -> dict:
        dut_docs = self.create_global_dut_data_dict(
            timestamp=datetime.now(timezone.utc),
            dut_data=dut_data,
        )
        dut_docs |= self.feature_global_information_doc

        self.elk_reporter.fill_list_of_docs(index_name=self.elk_reporter.index_name['dashboard_results_gnbs'], doc=dut_docs)
        if self.gnb_flag:
            self.gnb_flag = False
            self.logger.info(f'first gnbs_docs_information_doc is: {dut_docs}')

        return dut_docs

    def create_dut_cell_data_dict(self, timestamp: datetime, dut_cell_key: str, dut_cell_data: dict) -> dict:
        self.logger.debug('starting "fill_gnb_cell_data_dict" function')

        return_dict = {
            "timestamp": timestamp,
            "dut_cell_key": dut_cell_key,
            "dut_cell_name": f'gnb_{dut_cell_key}',
        }

        # ##### Throughput #####
        if self.test_results_object['test_info'].get('traffic_transport_layer'):
            return_dict |= {
                "cell_expected_throughput_dl": dut_cell_data.get('expected_throughput', {}).get('DL', -1.0),
                "cell_expected_throughput_ul": dut_cell_data.get('expected_throughput', {}).get('UL', -1.0),
                "cell_expected_throughput_by_threshold_dl": dut_cell_data.get('expected_throughput_by_threshold', {}).get('DL', -1.0),
                "cell_expected_throughput_by_threshold_ul": dut_cell_data.get('expected_throughput_by_threshold', {}).get('UL', -1.0),

                "cell_dl_min_rx_rate": dut_cell_data.get('tp_results', {}).get('DLMinRxRate(Mbps)', -1.0),
                "cell_dl_avg_rx_rate": dut_cell_data.get('tp_results', {}).get('DLAvgRxRate(Mbps)', -1.0),
                "cell_dl_max_rx_rate": dut_cell_data.get('tp_results', {}).get('DLMaxRxRate(Mbps)', -1.0),
            }

        # ##### HandOver #####

        return return_dict

    def create_dut_cell_ue_data_dict(self, timestamp: datetime, ue_ezlife_key: str, dut_cell_ue_data: dict, current_time: int) -> dict:
        # sourcery skip: low-code-quality
        self.logger.debug('starting "create_dut_cell_ue_data_dict" function')
        if current_time > self.ue_shortest_time - 1:
            return {}

        return_dict = {
            "timestamp": timestamp,

            "ue_ezlife_key": ue_ezlife_key,
            "ue_name": dut_cell_ue_data['ue_name']
        }

        if '5g' in self.test_results_object['test_info']['protocol'].lower():
            return_dict |= {
                # "ue_id": list(set(dut_cell_ue_data.get('UE-ID'))) if dut_cell_ue_data.get('UE-ID') else None,  # <class 'list'>
                # "pcell_id": dut_cell_ue_data.get('PCELL-ID')[current_time] if dut_cell_ue_data.get('PCELL-ID') and len(dut_cell_ue_data['PCELL-ID']) > current_time else None,  # <class 'list'>
                "cell_id": dut_cell_ue_data.get('CELL-ID')[current_time] if dut_cell_ue_data.get('CELL-ID') and len(dut_cell_ue_data['CELL-ID']) > current_time else None,  # <class 'list'>
                "ue_static_to_ru": dut_cell_ue_data['static_to_ru'],

                "connected_time_min": dut_cell_ue_data.get('Connected Time(Min)')[current_time] if dut_cell_ue_data.get('Connected Time(Min)') and len(dut_cell_ue_data['Connected Time(Min)']) > current_time else None,  # <class 'list'>

                # UE #
                "rsrp": dut_cell_ue_data.get('RSRP')[current_time] if dut_cell_ue_data.get('RSRP') and len(dut_cell_ue_data['RSRP']) > current_time else -1,
                "rsrq": dut_cell_ue_data.get('RSRQ')[current_time] if dut_cell_ue_data.get('RSRQ') and len(dut_cell_ue_data['RSRQ']) > current_time else -1,
                "rssi": dut_cell_ue_data.get('RSSI')[current_time] if dut_cell_ue_data.get('RSSI') and len(dut_cell_ue_data['RSSI']) > current_time else -1,
                "snr": dut_cell_ue_data.get('SNR')[current_time] if dut_cell_ue_data.get('SNR') and len(dut_cell_ue_data['SNR']) > current_time else -1,

                # DUT #
                "rnti": dut_cell_ue_data['gnb_statistics'].get('RNTI')[current_time]['value'] if dut_cell_ue_data.get('RNTI') and len(dut_cell_ue_data['RNTI']) > current_time else -1,
                "rnti_timestamp": dut_cell_ue_data['gnb_statistics'].get('RNTI')[current_time]['timestamp'] if dut_cell_ue_data.get('RNTI') and len(dut_cell_ue_data['RNTI']) > current_time else -1,
                "rnti_second": dut_cell_ue_data['gnb_statistics'].get('RNTI')[current_time]['second'] if dut_cell_ue_data.get('RNTI') and len(dut_cell_ue_data['RNTI']) > current_time else -1,

                "dl_mcs_cw_0": dut_cell_ue_data['gnb_statistics']['DL-MCS CW-0'][current_time]['value'] if dut_cell_ue_data.get('DL-MCS CW-0') and len(dut_cell_ue_data['DL-MCS CW-0']) > current_time else -1,
                "dl_mcs_cw_0_timestamp": dut_cell_ue_data['gnb_statistics']['DL-MCS CW-0'][current_time]['timestamp'] if dut_cell_ue_data.get('DL-MCS CW-0') and len(dut_cell_ue_data['DL-MCS CW-0']) > current_time else -1,
                "dl_mcs_cw_0_second": dut_cell_ue_data['gnb_statistics']['DL-MCS CW-0'][current_time]['second'] if dut_cell_ue_data.get('DL-MCS CW-0') and len(dut_cell_ue_data['DL-MCS CW-0']) > current_time else -1,

                "dl_mcs_cw_1": dut_cell_ue_data['gnb_statistics']['DL-MCS CW-1'][current_time]['value'] if dut_cell_ue_data.get('DL-MCS CW-1') and len(dut_cell_ue_data['DL-MCS CW-1']) > current_time else -1,
                "dl_mcs_cw_1_timestamp": dut_cell_ue_data['gnb_statistics']['DL-MCS CW-1'][current_time]['timestamp'] if dut_cell_ue_data.get('DL-MCS CW-1') and len(dut_cell_ue_data['DL-MCS CW-1']) > current_time else -1,
                "dl_mcs_cw_1_second": dut_cell_ue_data['gnb_statistics']['DL-MCS CW-1'][current_time]['second'] if dut_cell_ue_data.get('DL-MCS CW-1') and len(dut_cell_ue_data['DL-MCS CW-1']) > current_time else -1,

                "dl_tpt_mb": dut_cell_ue_data['gnb_statistics']['DL-TPT (Mb)'][current_time]['value'] if dut_cell_ue_data.get('DL-TPT (Mb)') and len(dut_cell_ue_data['DL-TPT (Mb)']) > current_time else -1,
                "dl_tpt_mb_timestamp": dut_cell_ue_data['gnb_statistics']['DL-TPT (Mb)'][current_time]['timestamp'] if dut_cell_ue_data.get('DL-TPT (Mb)') and len(dut_cell_ue_data['DL-TPT (Mb)']) > current_time else -1,
                "dl_tpt_mb_second": dut_cell_ue_data['gnb_statistics']['DL-TPT (Mb)'][current_time]['second'] if dut_cell_ue_data.get('DL-TPT (Mb)') and len(dut_cell_ue_data['DL-TPT (Mb)']) > current_time else -1,

                "mac_dl_tpt_mb": dut_cell_ue_data['gnb_statistics']['MAC-DL-TPT (Mb)'][current_time]['value'] if dut_cell_ue_data.get('MAC-DL-TPT (Mb)') and len(dut_cell_ue_data['MAC-DL-TPT (Mb)']) > current_time else -1,
                "mac_dl_tpt_mb_timestamp": dut_cell_ue_data['gnb_statistics']['MAC-DL-TPT (Mb)'][current_time]['timestamp'] if dut_cell_ue_data.get('MAC-DL-TPT (Mb)') and len(dut_cell_ue_data['MAC-DL-TPT (Mb)']) > current_time else -1,
                "mac_dl_tpt_mb_second": dut_cell_ue_data['gnb_statistics']['MAC-DL-TPT (Mb)'][current_time]['second'] if dut_cell_ue_data.get('MAC-DL-TPT (Mb)') and len(dut_cell_ue_data['MAC-DL-TPT (Mb)']) > current_time else -1,

                "cl_dl_tpt_mb": dut_cell_ue_data['gnb_statistics']['CL-DL-TPT (Mb)'][current_time]['value'] if dut_cell_ue_data.get('CL-DL-TPT (Mb)') and len(dut_cell_ue_data['CL-DL-TPT (Mb)']) > current_time else -1,
                "cl_dl_tpt_mb_timestamp": dut_cell_ue_data['gnb_statistics']['CL-DL-TPT (Mb)'][current_time]['timestamp'] if dut_cell_ue_data.get('CL-DL-TPT (Mb)') and len(dut_cell_ue_data['CL-DL-TPT (Mb)']) > current_time else -1,
                "cl_dl_tpt_mb_second": dut_cell_ue_data['gnb_statistics']['CL-DL-TPT (Mb)'][current_time]['second'] if dut_cell_ue_data.get('CL-DL-TPT (Mb)') and len(dut_cell_ue_data['CL-DL-TPT (Mb)']) > current_time else -1,

                "rlc_dl_tpt_mb": dut_cell_ue_data['gnb_statistics']['RLC-DL-TPT (Mb)'][current_time]['value'] if dut_cell_ue_data.get('RLC-DL-TPT (Mb)') and len(dut_cell_ue_data['RLC-DL-TPT (Mb)']) > current_time else -1,
                "rlc_dl_tpt_mb_timestamp": dut_cell_ue_data['gnb_statistics']['RLC-DL-TPT (Mb)'][current_time]['timestamp'] if dut_cell_ue_data.get('RLC-DL-TPT (Mb)') and len(dut_cell_ue_data['RLC-DL-TPT (Mb)']) > current_time else -1,
                "rlc_dl_tpt_mb_second": dut_cell_ue_data['gnb_statistics']['RLC-DL-TPT (Mb)'][current_time]['second'] if dut_cell_ue_data.get('RLC-DL-TPT (Mb)') and len(dut_cell_ue_data['RLC-DL-TPT (Mb)']) > current_time else -1,

                "ul_mcs_cw_0": dut_cell_ue_data['gnb_statistics']['UL-MCS CW-0'][current_time]['value'] if dut_cell_ue_data.get('UL-MCS CW-0') and len(dut_cell_ue_data['UL-MCS CW-0']) > current_time else -1,
                "ul_mcs_cw_0_timestamp": dut_cell_ue_data['gnb_statistics']['UL-MCS CW-0'][current_time]['timestamp'] if dut_cell_ue_data.get('UL-MCS CW-0') and len(dut_cell_ue_data['UL-MCS CW-0']) > current_time else -1,
                "ul_mcs_cw_0_second": dut_cell_ue_data['gnb_statistics']['UL-MCS CW-0'][current_time]['second'] if dut_cell_ue_data.get('UL-MCS CW-0') and len(dut_cell_ue_data['UL-MCS CW-0']) > current_time else -1,

                "ul_mcs_cw_1": dut_cell_ue_data['gnb_statistics']['UL-MCS CW-1'][current_time]['value'] if dut_cell_ue_data.get('UL-MCS CW-1') and len(dut_cell_ue_data['UL-MCS CW-1']) > current_time else -1,
                "ul_mcs_cw_1_timestamp": dut_cell_ue_data['gnb_statistics']['UL-MCS CW-1'][current_time]['timestamp'] if dut_cell_ue_data.get('UL-MCS CW-1') and len(dut_cell_ue_data['UL-MCS CW-1']) > current_time else -1,
                "ul_mcs_cw_1_second": dut_cell_ue_data['gnb_statistics']['UL-MCS CW-1'][current_time]['second'] if dut_cell_ue_data.get('UL-MCS CW-1') and len(dut_cell_ue_data['UL-MCS CW-1']) > current_time else -1,

                "ul_tpt_mb": dut_cell_ue_data['gnb_statistics']['UL-TPT (Mb)'][current_time]['value'] if dut_cell_ue_data.get('UL-TPT (Mb)') and len(dut_cell_ue_data['UL-TPT (Mb)']) > current_time else -1,
                "ul_tpt_mb_timestamp": dut_cell_ue_data['gnb_statistics']['UL-TPT (Mb)'][current_time]['timestamp'] if dut_cell_ue_data.get('UL-TPT (Mb)') and len(dut_cell_ue_data['UL-TPT (Mb)']) > current_time else -1,
                "ul_tpt_mb_second": dut_cell_ue_data['gnb_statistics']['UL-TPT (Mb)'][current_time]['second'] if dut_cell_ue_data.get('UL-TPT (Mb)') and len(dut_cell_ue_data['UL-TPT (Mb)']) > current_time else -1,

                "mac_ul_tpt_mb": dut_cell_ue_data['gnb_statistics']['MAC-UL-TPT (Mb)'][current_time]['value'] if dut_cell_ue_data.get('MAC-UL-TPT (Mb)') and len(dut_cell_ue_data['MAC-UL-TPT (Mb)']) > current_time else -1,
                "mac_ul_tpt_mb_timestamp": dut_cell_ue_data['gnb_statistics']['MAC-UL-TPT (Mb)'][current_time]['timestamp'] if dut_cell_ue_data.get('MAC-UL-TPT (Mb)') and len(dut_cell_ue_data['MAC-UL-TPT (Mb)']) > current_time else -1,
                "mac_ul_tpt_mb_second": dut_cell_ue_data['gnb_statistics']['MAC-UL-TPT (Mb)'][current_time]['second'] if dut_cell_ue_data.get('MAC-UL-TPT (Mb)') and len(dut_cell_ue_data['MAC-UL-TPT (Mb)']) > current_time else -1,

                "cl_ul_tpt_mb": dut_cell_ue_data['gnb_statistics']['CL-UL-TPT (Mb)'][current_time]['value'] if dut_cell_ue_data.get('CL-UL-TPT (Mb)') and len(dut_cell_ue_data['CL-UL-TPT (Mb)']) > current_time else -1,
                "cl_ul_tpt_mb_timestamp": dut_cell_ue_data['gnb_statistics']['CL-UL-TPT (Mb)'][current_time]['timestamp'] if dut_cell_ue_data.get('CL-UL-TPT (Mb)') and len(dut_cell_ue_data['CL-UL-TPT (Mb)']) > current_time else -1,
                "cl_ul_tpt_mb_second": dut_cell_ue_data['gnb_statistics']['CL-UL-TPT (Mb)'][current_time]['second'] if dut_cell_ue_data.get('CL-UL-TPT (Mb)') and len(dut_cell_ue_data['CL-UL-TPT (Mb)']) > current_time else -1,

                "rlc_ul_tpt_mb": dut_cell_ue_data['gnb_statistics']['RLC-UL-TPT (Mb)'][current_time]['value'] if dut_cell_ue_data.get('RLC-UL-TPT (Mb)') and len(dut_cell_ue_data['RLC-UL-TPT (Mb)']) > current_time else -1,
                "rlc_ul_tpt_mb_timestamp": dut_cell_ue_data['gnb_statistics']['RLC-UL-TPT (Mb)'][current_time]['timestamp'] if dut_cell_ue_data.get('RLC-UL-TPT (Mb)') and len(dut_cell_ue_data['RLC-UL-TPT (Mb)']) > current_time else -1,
                "rlc_ul_tpt_mb_second": dut_cell_ue_data['gnb_statistics']['RLC-UL-TPT (Mb)'][current_time]['second'] if dut_cell_ue_data.get('RLC-UL-TPT (Mb)') and len(dut_cell_ue_data['RLC-UL-TPT (Mb)']) > current_time else -1,

                "256qam_actv": dut_cell_ue_data['gnb_statistics'].get('256QAM ACTV')[current_time]['value'] if dut_cell_ue_data.get('256QAM ACTV') and len(dut_cell_ue_data['256QAM ACTV']) > current_time else -1,
                "256qam_actv_timestamp": dut_cell_ue_data['gnb_statistics'].get('256QAM ACTV')[current_time]['timestamp'] if dut_cell_ue_data.get('256QAM ACTV') and len(dut_cell_ue_data['256QAM ACTV']) > current_time else -1,
                "256qam_actv_second": dut_cell_ue_data['gnb_statistics'].get('256QAM ACTV')[current_time]['second'] if dut_cell_ue_data.get('256QAM ACTV') and len(dut_cell_ue_data['256QAM ACTV']) > current_time else -1,

                "256qam_alloc": dut_cell_ue_data['gnb_statistics'].get('256QAM Alloc')[current_time]['value'] if dut_cell_ue_data.get('256QAM Alloc') and len(dut_cell_ue_data['256QAM Alloc']) > current_time else -1,
                "256qam_alloc_timestamp": dut_cell_ue_data['gnb_statistics'].get('256QAM Alloc')[current_time]['timestamp'] if dut_cell_ue_data.get('256QAM Alloc') and len(dut_cell_ue_data['256QAM Alloc']) > current_time else -1,
                "256qam_alloc_second": dut_cell_ue_data['gnb_statistics'].get('256QAM Alloc')[current_time]['second'] if dut_cell_ue_data.get('256QAM Alloc') and len(dut_cell_ue_data['256QAM Alloc']) > current_time else -1,

                "c2i": dut_cell_ue_data['gnb_statistics'].get('C2I')[current_time]['value'] if dut_cell_ue_data.get('C2I') and len(dut_cell_ue_data['C2I']) > current_time else -1,
                "c2i_timestamp": dut_cell_ue_data['gnb_statistics'].get('C2I')[current_time]['timestamp'] if dut_cell_ue_data.get('C2I') and len(dut_cell_ue_data['C2I']) > current_time else -1,
                "c2i_second": dut_cell_ue_data['gnb_statistics'].get('C2I')[current_time]['second'] if dut_cell_ue_data.get('C2I') and len(dut_cell_ue_data['C2I']) > current_time else -1,

                "ca_mode": dut_cell_ue_data['gnb_statistics'].get('CA MODE')[current_time]['value'] if dut_cell_ue_data.get('CA MODE') and len(dut_cell_ue_data['CA MODE']) > current_time else -1,
                "ca_mode_timestamp": dut_cell_ue_data['gnb_statistics'].get('CA MODE')[current_time]['timestamp'] if dut_cell_ue_data.get('CA MODE') and len(dut_cell_ue_data['CA MODE']) > current_time else -1,
                "ca_mode_second": dut_cell_ue_data['gnb_statistics'].get('CA MODE')[current_time]['second'] if dut_cell_ue_data.get('CA MODE') and len(dut_cell_ue_data['CA MODE']) > current_time else -1,

                "meas_gap_active": dut_cell_ue_data['gnb_statistics'].get('MEAS GAP ACTIVE')[current_time]['value'] if dut_cell_ue_data.get('MEAS GAP ACTIVE') and len(dut_cell_ue_data['MEAS GAP ACTIVE']) > current_time else -1,
                "meas_gap_active_timestamp": dut_cell_ue_data['gnb_statistics'].get('MEAS GAP ACTIVE')[current_time]['timestamp'] if dut_cell_ue_data.get('MEAS GAP ACTIVE') and len(dut_cell_ue_data['MEAS GAP ACTIVE']) > current_time else -1,
                "meas_gap_active_second": dut_cell_ue_data['gnb_statistics'].get('MEAS GAP ACTIVE')[current_time]['second'] if dut_cell_ue_data.get('MEAS GAP ACTIVE') and len(dut_cell_ue_data['MEAS GAP ACTIVE']) > current_time else -1,

                "num_sr": dut_cell_ue_data['gnb_statistics'].get('NUM-SR')[current_time]['value'] if dut_cell_ue_data.get('NUM-SR') and len(dut_cell_ue_data['NUM-SR']) > current_time else -1,
                "num_sr_timestamp": dut_cell_ue_data['gnb_statistics'].get('NUM-SR')[current_time]['timestamp'] if dut_cell_ue_data.get('NUM-SR') and len(dut_cell_ue_data['NUM-SR']) > current_time else -1,
                "num_sr_second": dut_cell_ue_data['gnb_statistics'].get('NUM-SR')[current_time]['second'] if dut_cell_ue_data.get('NUM-SR') and len(dut_cell_ue_data['NUM-SR']) > current_time else -1,

                "small_alloc": dut_cell_ue_data['gnb_statistics'].get('SMALL ALLOC')[current_time]['value'] if dut_cell_ue_data.get('SMALL ALLOC') and len(dut_cell_ue_data['SMALL ALLOC']) > current_time else -1,
                "small_alloc_timestamp": dut_cell_ue_data['gnb_statistics'].get('SMALL ALLOC')[current_time]['timestamp'] if dut_cell_ue_data.get('SMALL ALLOC') and len(dut_cell_ue_data['SMALL ALLOC']) > current_time else -1,
                "small_alloc_second": dut_cell_ue_data['gnb_statistics'].get('SMALL ALLOC')[current_time]['second'] if dut_cell_ue_data.get('SMALL ALLOC') and len(dut_cell_ue_data['SMALL ALLOC']) > current_time else -1,

                "dl_bler_crc_per": dut_cell_ue_data['gnb_statistics'].get('DL-BLER-CRC %PER')[current_time]['value'] if dut_cell_ue_data.get('DL-BLER-CRC %PER') and len(dut_cell_ue_data['DL-BLER-CRC %PER']) > current_time else -1,
                "dl_bler_crc_per_timestamp": dut_cell_ue_data['gnb_statistics'].get('DL-BLER-CRC %PER')[current_time]['timestamp'] if dut_cell_ue_data.get('DL-BLER-CRC %PER') and len(dut_cell_ue_data['DL-BLER-CRC %PER']) > current_time else -1,
                "dl_bler_crc_per_second": dut_cell_ue_data['gnb_statistics'].get('DL-BLER-CRC %PER')[current_time]['second'] if dut_cell_ue_data.get('DL-BLER-CRC %PER') and len(dut_cell_ue_data['DL-BLER-CRC %PER']) > current_time else -1,

                "dl_bler_cw_0": dut_cell_ue_data['gnb_statistics'].get('DL-BLER %CW-0')[current_time]['value'] if dut_cell_ue_data.get('DL-BLER %CW-0') and len(dut_cell_ue_data['DL-BLER %CW-0']) > current_time else -1,
                "dl_bler_cw_0_timestamp": dut_cell_ue_data['gnb_statistics'].get('DL-BLER %CW-0')[current_time]['timestamp'] if dut_cell_ue_data.get('DL-BLER %CW-0') and len(dut_cell_ue_data['DL-BLER %CW-0']) > current_time else -1,
                "dl_bler_cw_0_second": dut_cell_ue_data['gnb_statistics'].get('DL-BLER %CW-0')[current_time]['second'] if dut_cell_ue_data.get('DL-BLER %CW-0') and len(dut_cell_ue_data['DL-BLER %CW-0']) > current_time else -1,

                "dl_bler_cw_1": dut_cell_ue_data['gnb_statistics'].get('DL-BLER %CW-1')[current_time]['value'] if dut_cell_ue_data.get('DL-BLER %CW-1') and len(dut_cell_ue_data['DL-BLER %CW-1']) > current_time else -1,
                "dl_bler_cw_1_timestamp": dut_cell_ue_data['gnb_statistics'].get('DL-BLER %CW-1')[current_time]['timestamp'] if dut_cell_ue_data.get('DL-BLER %CW-1') and len(dut_cell_ue_data['DL-BLER %CW-1']) > current_time else -1,
                "dl_bler_cw_1_second": dut_cell_ue_data['gnb_statistics'].get('DL-BLER %CW-1')[current_time]['second'] if dut_cell_ue_data.get('DL-BLER %CW-1') and len(dut_cell_ue_data['DL-BLER %CW-1']) > current_time else -1,

                "dl_cqi_cw_0": dut_cell_ue_data['gnb_statistics'].get('DL-CQI CW-0')[current_time]['value'] if dut_cell_ue_data.get('DL-CQI CW-0') and len(dut_cell_ue_data['DL-CQI CW-0']) > current_time else -1,
                "dl_cqi_cw_0_timestamp": dut_cell_ue_data['gnb_statistics'].get('DL-CQI CW-0')[current_time]['timestamp'] if dut_cell_ue_data.get('DL-CQI CW-0') and len(dut_cell_ue_data['DL-CQI CW-0']) > current_time else -1,
                "dl_cqi_cw_0_second": dut_cell_ue_data['gnb_statistics'].get('DL-CQI CW-0')[current_time]['second'] if dut_cell_ue_data.get('DL-CQI CW-0') and len(dut_cell_ue_data['DL-CQI CW-0']) > current_time else -1,

                "dl_cqi_cw_1": dut_cell_ue_data['gnb_statistics'].get('DL-CQI CW-1')[current_time]['value'] if dut_cell_ue_data.get('DL-CQI CW-1') and len(dut_cell_ue_data['DL-CQI CW-1']) > current_time else -1,
                "dl_cqi_cw_1_timestamp": dut_cell_ue_data['gnb_statistics'].get('DL-CQI CW-1')[current_time]['timestamp'] if dut_cell_ue_data.get('DL-CQI CW-1') and len(dut_cell_ue_data['DL-CQI CW-1']) > current_time else -1,
                "dl_cqi_cw_1_second": dut_cell_ue_data['gnb_statistics'].get('DL-CQI CW-1')[current_time]['second'] if dut_cell_ue_data.get('DL-CQI CW-1') and len(dut_cell_ue_data['DL-CQI CW-1']) > current_time else -1,

                "dl_pkt_rx": dut_cell_ue_data['gnb_statistics'].get('DL-PKT-RX')[current_time]['value'] if dut_cell_ue_data.get('DL-PKT-RX') and len(dut_cell_ue_data['DL-PKT-RX']) > current_time else -1,
                "dl_pkt_rx_timestamp": dut_cell_ue_data['gnb_statistics'].get('DL-PKT-RX')[current_time]['timestamp'] if dut_cell_ue_data.get('DL-PKT-RX') and len(dut_cell_ue_data['DL-PKT-RX']) > current_time else -1,
                "dl_pkt_rx_second": dut_cell_ue_data['gnb_statistics'].get('DL-PKT-RX')[current_time]['second'] if dut_cell_ue_data.get('DL-PKT-RX') and len(dut_cell_ue_data['DL-PKT-RX']) > current_time else -1,

                "ri_dl": dut_cell_ue_data['gnb_statistics'].get('RI DL')[current_time]['value'] if dut_cell_ue_data.get('RI DL') and len(dut_cell_ue_data['RI DL']) > current_time else -1,
                "ri_dl_timestamp": dut_cell_ue_data['gnb_statistics'].get('RI DL')[current_time]['timestamp'] if dut_cell_ue_data.get('RI DL') and len(dut_cell_ue_data['RI DL']) > current_time else -1,
                "ri_dl_second": dut_cell_ue_data['gnb_statistics'].get('RI DL')[current_time]['second'] if dut_cell_ue_data.get('RI DL') and len(dut_cell_ue_data['RI DL']) > current_time else -1,

                "ri_rx": dut_cell_ue_data['gnb_statistics'].get('RI RX')[current_time]['value'] if dut_cell_ue_data.get('RI RX') and len(dut_cell_ue_data['RI RX']) > current_time else -1,
                "ri_rx_timestamp": dut_cell_ue_data['gnb_statistics'].get('RI RX')[current_time]['timestamp'] if dut_cell_ue_data.get('RI RX') and len(dut_cell_ue_data['RI RX']) > current_time else -1,
                "ri_rx_second": dut_cell_ue_data['gnb_statistics'].get('RI RX')[current_time]['second'] if dut_cell_ue_data.get('RI RX') and len(dut_cell_ue_data['RI RX']) > current_time else -1,

                "ri_ul": dut_cell_ue_data['gnb_statistics'].get('RI UL')[current_time]['value'] if dut_cell_ue_data.get('RI UL') and len(dut_cell_ue_data['RI UL']) > current_time else -1,
                "ri_ul_timestamp": dut_cell_ue_data['gnb_statistics'].get('RI UL')[current_time]['timestamp'] if dut_cell_ue_data.get('RI UL') and len(dut_cell_ue_data['RI UL']) > current_time else -1,
                "ri_ul_second": dut_cell_ue_data['gnb_statistics'].get('RI UL')[current_time]['second'] if dut_cell_ue_data.get('RI UL') and len(dut_cell_ue_data['RI UL']) > current_time else -1,

                "ul_bler_crc_per": dut_cell_ue_data['gnb_statistics'].get('UL-BLER-CRC %PER')[current_time]['value'] if dut_cell_ue_data.get('UL-BLER-CRC `%PER') and len(dut_cell_ue_data['UL-BLER-CRC %PER']) > current_time else -1,
                "ul_bler_crc_per_timestamp": dut_cell_ue_data['gnb_statistics'].get('UL-BLER-CRC %PER')[current_time]['timestamp'] if dut_cell_ue_data.get('UL-BLER-CRC `%PER') and len(dut_cell_ue_data['UL-BLER-CRC %PER']) > current_time else -1,
                "ul_bler_crc_per_second": dut_cell_ue_data['gnb_statistics'].get('UL-BLER-CRC %PER')[current_time]['second'] if dut_cell_ue_data.get('UL-BLER-CRC `%PER') and len(dut_cell_ue_data['UL-BLER-CRC %PER']) > current_time else -1,

                "ul_bler_cw_0": dut_cell_ue_data['gnb_statistics'].get('UL-BLER %CW-0')[current_time]['value'] if dut_cell_ue_data.get('UL-BLER %CW-0') and len(dut_cell_ue_data['UL-BLER %CW-0']) > current_time else -1,
                "ul_bler_cw_0_timestamp": dut_cell_ue_data['gnb_statistics'].get('UL-BLER %CW-0')[current_time]['timestamp'] if dut_cell_ue_data.get('UL-BLER %CW-0') and len(dut_cell_ue_data['UL-BLER %CW-0']) > current_time else -1,
                "ul_bler_cw_0_second": dut_cell_ue_data['gnb_statistics'].get('UL-BLER %CW-0')[current_time]['second'] if dut_cell_ue_data.get('UL-BLER %CW-0') and len(dut_cell_ue_data['UL-BLER %CW-0']) > current_time else -1,

                "ul_bler_cw_1": dut_cell_ue_data['gnb_statistics'].get('UL-BLER %CW-1')[current_time]['value'] if dut_cell_ue_data.get('UL-BLER %CW-1') and len(dut_cell_ue_data['UL-BLER %CW-1']) > current_time else -1,
                "ul_bler_cw_1_timestamp": dut_cell_ue_data['gnb_statistics'].get('UL-BLER %CW-1')[current_time]['timestamp'] if dut_cell_ue_data.get('UL-BLER %CW-1') and len(dut_cell_ue_data['UL-BLER %CW-1']) > current_time else -1,
                "ul_bler_cw_1_second": dut_cell_ue_data['gnb_statistics'].get('UL-BLER %CW-1')[current_time]['second'] if dut_cell_ue_data.get('UL-BLER %CW-1') and len(dut_cell_ue_data['UL-BLER %CW-1']) > current_time else -1,

                "ul_cqi_cw_0": dut_cell_ue_data['gnb_statistics'].get('UL-CQI CW-0')[current_time]['value'] if dut_cell_ue_data.get('UL-CQI CW-0') and len(dut_cell_ue_data['UL-CQI CW-0']) > current_time else -1,
                "ul_cqi_cw_0_timestamp": dut_cell_ue_data['gnb_statistics'].get('UL-CQI CW-0')[current_time]['timestamp'] if dut_cell_ue_data.get('UL-CQI CW-0') and len(dut_cell_ue_data['UL-CQI CW-0']) > current_time else -1,
                "ul_cqi_cw_0_second": dut_cell_ue_data['gnb_statistics'].get('UL-CQI CW-0')[current_time]['second'] if dut_cell_ue_data.get('UL-CQI CW-0') and len(dut_cell_ue_data['UL-CQI CW-0']) > current_time else -1,

                "ul_cqi_cw_1": dut_cell_ue_data['gnb_statistics'].get('UL-CQI CW-1')[current_time]['value'] if dut_cell_ue_data.get('UL-CQI CW-1') and len(dut_cell_ue_data['UL-CQI CW-1']) > current_time else -1,
                "ul_cqi_cw_1_timestamp": dut_cell_ue_data['gnb_statistics'].get('UL-CQI CW-1')[current_time]['timestamp'] if dut_cell_ue_data.get('UL-CQI CW-1') and len(dut_cell_ue_data['UL-CQI CW-1']) > current_time else -1,
                "ul_cqi_cw_1_second": dut_cell_ue_data['gnb_statistics'].get('UL-CQI CW-1')[current_time]['second'] if dut_cell_ue_data.get('UL-CQI CW-1') and len(dut_cell_ue_data['UL-CQI CW-1']) > current_time else -1,

                "ul_pkt_tx": dut_cell_ue_data['gnb_statistics'].get('UL-PKT-TX')[current_time]['value'] if dut_cell_ue_data.get('UL-PKT-TX') and len(dut_cell_ue_data['UL-PKT-TX']) > current_time else -1,
                "ul_pkt_tx_timestamp": dut_cell_ue_data['gnb_statistics'].get('UL-PKT-TX')[current_time]['timestamp'] if dut_cell_ue_data.get('UL-PKT-TX') and len(dut_cell_ue_data['UL-PKT-TX']) > current_time else -1,
                "ul_pkt_tx_second": dut_cell_ue_data['gnb_statistics'].get('UL-PKT-TX')[current_time]['second'] if dut_cell_ue_data.get('UL-PKT-TX') and len(dut_cell_ue_data['UL-PKT-TX']) > current_time else -1,
            }

        if '4g' in self.test_results_object['test_info']['protocol'].lower():
            return_dict |= {
                "ue_static_to_enb": dut_cell_ue_data['static_to_enb'],
            }

        return return_dict

    async def async_fill_dut_cell_ue_data_dict(self, dut_cell_docs: dict, ue_key: str, ue_data: dict, time_number: int):
        dut_cell_ue_docs = self.create_dut_cell_ue_data_dict(
            timestamp=datetime.now(timezone.utc),
            ue_ezlife_key=ue_key,
            dut_cell_ue_data=ue_data,
            current_time=time_number
        )

        dut_cell_ue_docs |= dut_cell_docs
        self.elk_reporter.fill_list_of_docs(index_name=self.elk_reporter.index_name['dashboard_results_gnb_cell_ues'], doc=dut_cell_ue_docs)

    def create_dut_cell_ue_qci_data_dict(self, timestamp: datetime, ue_key: str, ue_data: dict, dut_cell_ue_qci_key: str, dut_cell_ue_qci_data: dict, current_time: int = 0) -> dict:
        # sourcery skip: low-code-quality
        self.logger.debug('starting "fill_gnb_cell_ue_qci_data_dict" function')

        return_dict = {
            "timestamp": timestamp,
            "ue_ezlife_key": ue_key,
            "ue_name": ue_data['ue_name'],

            "dut_cell_ue_qci_key": dut_cell_ue_qci_key,
        }

        if '5g' in self.test_results_object['test_info']['protocol'].lower():
            return_dict |= {
                "ue_static_to_ru": ue_data['static_to_ru'],
            }

        if '4g' in self.test_results_object['test_info']['protocol'].lower():
            return_dict |= {
                "ue_static_to_enb": ue_data['static_to_enb'],
            }

        # # ##### Feature Information #####

        # ##### Throughput #####
        if dut_cell_ue_qci_data.get('tp_results'):
            return_dict |= {
                "tp_timestamp": dut_cell_ue_qci_data['DL_with_timestamp'][current_time]['timestamp'] if dut_cell_ue_qci_data.get('DL_with_timestamp') else
                dut_cell_ue_qci_data['UL_with_timestamp'][current_time]['timestamp'] if dut_cell_ue_qci_data.get('UL_with_timestamp') else None,
                "tp_second": dut_cell_ue_qci_data['UL_with_timestamp'][current_time]['second'] if dut_cell_ue_qci_data.get('UL_with_timestamp') else
                dut_cell_ue_qci_data['DL_with_timestamp'][current_time]['second'] if dut_cell_ue_qci_data.get('DL_with_timestamp') else None,

                "dl_mbs_traffic_generator": dut_cell_ue_qci_data['DL_with_timestamp'][current_time]['value'] if dut_cell_ue_qci_data.get('DL_with_timestamp') else None,
                "dl_mbs_traffic_generator_timestamp": dut_cell_ue_qci_data['DL_with_timestamp'][current_time]['timestamp'] if dut_cell_ue_qci_data.get('DL_with_timestamp') else None,
                "dl_mbs_traffic_generator_second": dut_cell_ue_qci_data['DL_with_timestamp'][current_time]['second'] if dut_cell_ue_qci_data.get('DL_with_timestamp') else None,

                "ul_mbs_traffic_generator": dut_cell_ue_qci_data['UL_with_timestamp'][current_time]['value'] if dut_cell_ue_qci_data.get('UL_with_timestamp') else None,
                "ul_mbs_traffic_generator_timestamp": dut_cell_ue_qci_data['UL_with_timestamp'][current_time]['timestamp'] if dut_cell_ue_qci_data.get('UL_with_timestamp') else None,
                "ul_mbs_traffic_generator_second": dut_cell_ue_qci_data['UL_with_timestamp'][current_time]['second'] if dut_cell_ue_qci_data.get('UL_with_timestamp') else None,

                "qci_ul_min_rx_rate_mbs": dut_cell_ue_qci_data['tp_results']['ULMinRxRate(Mbps)'] if dut_cell_ue_qci_data['tp_results'].get('ULMinRxRate(Mbps)') is not None else None,
                "qci_ul_avg_rx_rate_mbs": dut_cell_ue_qci_data['tp_results']['ULAvgRxRate(Mbps)'] if dut_cell_ue_qci_data['tp_results'].get('ULAvgRxRate(Mbps)') is not None else None,
                "qci_ul_max_rx_rate_mbs": dut_cell_ue_qci_data['tp_results']['ULMaxRxRate(Mbps)'] if dut_cell_ue_qci_data['tp_results'].get('ULMaxRxRate(Mbps)') is not None else None,
                "qci_dl_min_rx_rate_mbs": dut_cell_ue_qci_data['tp_results']['DLMinRxRate(Mbps)'] if dut_cell_ue_qci_data['tp_results'].get('DLMinRxRate(Mbps)') is not None else None,
                "qci_dl_avg_rx_rate_mbs": dut_cell_ue_qci_data['tp_results']['DLAvgRxRate(Mbps)'] if dut_cell_ue_qci_data['tp_results'].get('DLAvgRxRate(Mbps)') is not None else None,
                "qci_dl_max_rx_rate_mbs": dut_cell_ue_qci_data['tp_results']['DLMaxRxRate(Mbps)'] if dut_cell_ue_qci_data['tp_results'].get('DLMaxRxRate(Mbps)') is not None else None,
            }

        # ##### HandOver #####

        return return_dict

    async def async_fill_dut_cell_ue_qci_data_dict(self, dut_cell_docs: dict, ue_key: str, ue_data: dict, qci_key: str, qci_data: dict, time_number: int):
        dut_cell_ue_qci_docs = self.create_dut_cell_ue_qci_data_dict(
            timestamp=datetime.now(timezone.utc),
            ue_data=ue_data,
            dut_cell_ue_qci_key=qci_key,
            dut_cell_ue_qci_data=qci_data,
            current_time=time_number,
            ue_key=ue_key,
        )
        dut_cell_ue_qci_docs |= dut_cell_docs
        self.elk_reporter.fill_list_of_docs(index_name=self.elk_reporter.index_name['dashboard_results_gnb_cell_ue_qcis'], doc=dut_cell_ue_qci_docs)

    async def fill_gnb_cell_docs(self, dut_docs: dict, dut_data: dict) -> None:
        for cell_key, cell_data in dut_data['cells'].items():
            self.logger.debug('1!')
            dut_cell_docs = self.create_dut_cell_data_dict(
                timestamp=datetime.now(timezone.utc),
                dut_cell_key=cell_key,
                dut_cell_data=cell_data,
            )
            dut_cell_docs |= self.feature_global_information_doc
            dut_cell_docs |= dut_docs
            self.elk_reporter.fill_list_of_docs(index_name=self.elk_reporter.index_name['dashboard_results_gnb_cells'], doc=dut_cell_docs)

            for ue_key, ue_data in cell_data['ues'].items():
                self.logger.debug('2!')
                await asyncio.gather(
                    *[
                        self.async_fill_dut_cell_ue_data_dict(
                            dut_cell_docs=dut_cell_docs,
                            ue_key=ue_key,
                            ue_data=ue_data,
                            time_number=time_number
                        )
                        for time_number in range(self.feature_global_information_doc['ue_shortest_time'])
                    ]
                )

                for qci_key, qci_data in ue_data['qcis'].items():
                    self.logger.debug('3!')
                    gnb_cell_ue_qci_data_dict_functions = [
                        self.async_fill_dut_cell_ue_qci_data_dict(
                            dut_cell_docs=dut_cell_docs,
                            ue_key=ue_key,
                            ue_data=ue_data,
                            qci_key=qci_key,
                            qci_data=qci_data,
                            time_number=time_number
                        )
                        for time_number in range(self.feature_global_information_doc['qci_shortest_time'])
                    ]
                    chunk_size = 1000
                    for i in range(0, 50000, chunk_size):
                        chunk = gnb_cell_ue_qci_data_dict_functions[i:i + chunk_size]
                        await asyncio.gather(*chunk)

                    # await asyncio.gather(
                    #     *[
                    #         self.async_fill_gnb_cell_ue_qci_data_dict(
                    #             gnb_cell_docs=gnb_cell_docs,
                    #             ue_key=ue_key,
                    #             ue_data=ue_data,
                    #             qci_key=qci_key,
                    #             qci_data=qci_data,
                    #             time_number=time_number
                    #         )
                    #         for time_number in range(self.feature_global_information_doc['qci_shortest_time'])
                    #     ]
                    # )
                    # await asyncio.sleep(3)
        print()

    def process(self, deep_analysis: bool = False, jira_test_run_time: int = None, automation_manual: str = 'Automation') -> None:
        self.dut = 'gnb' if '5g' in self.test_results_object['test_info']['protocol'].lower() else 'enb'

        self.add_and_update_data()
        if self.test_results_object['test_info']['scenario_status'] == 'ABORTED':
            return

        self.test_results_object['test_info']['feature_doc_id'] = self.elk_reporter.generate_doc_id(self.test_results_object)
        self.logger.info(f"feature_doc_id is: {self.test_results_object['test_info']['feature_doc_id']}")

        self.logger.info('Start ELK Process "fill_feature_details_docs_process" function')
        if not jira_test_run_time:
            jira_test_run_time = self.test_results_object['test_info']['run_time']

        start_process_run_time = datetime.now(timezone.utc)

        self.logger.info('Start "feature_global_information_doc" function')
        self.feature_global_information_doc = self.create_feature_global_information_dict(
            automation_manual=automation_manual,
            jira_test_run_time=jira_test_run_time,
        )
        self.logger.info('Stop "feature_global_information_doc" function')
        self.logger.info(f'feature_global_information_doc is: {self.feature_global_information_doc}')

        if not deep_analysis:
            self.logger.info('deep_analysis == False')

            self.logger.info('Start "fill_feature_details_doc" function')
            self.fill_feature_details_doc()
            self.logger.info('Stop "fill_feature_details_doc" function')

            # Temporary block waiting for Deep Analysis VMs splitting
            if any([True for i in self.feature_global_information_doc['feature_name'] if 'Link_Adaptation' in i]) or self.debug:  # Temporary block
                # sourcery skip: comprehension-to-generator, extract-method
                self.logger.info('Temporary block')
                for dut_name, dut_data in self.test_results_object[self.dut].items():
                    dut_docs = self.fill_dut_docs(dut_data)
                    # await self.fill_gnb_cell_docs(gnbs_docs, gnb_data)
                    asyncio.run(self.fill_gnb_cell_docs(dut_docs, dut_data))
        else:
            self.logger.info('deep_analysis == True')
            for gnb_name, gnb_data in self.test_results_object[self.dut].items():
                gnbs_docs = self.fill_dut_docs(gnb_data)
                asyncio.run(self.fill_gnb_cell_docs(gnbs_docs, gnb_data))
        self.logger.info(f'Total time to build the list of documents is: {datetime.now(timezone.utc) - start_process_run_time}')

        start_report_time = datetime.now(timezone.utc)
        self.elk_reporter.set_list_of_docs()
        self.logger.info(f'Total time to report the list of documents is: {datetime.now(timezone.utc) - start_report_time}')

        self.logger.info(f'Total time to run the ELK reporter is: {datetime.now(timezone.utc) - start_process_run_time}')


class RebootCareReportToELK:  # BuildDocsFromRebootCareObject
    def __init__(self, debug: bool = False) -> None:
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.debug = debug
        self.elk_reporter = ELKReporter()

        self.elk_reporter.get_elk_client(debug=debug)
        self.get_index_name()

    def get_index_name(self) -> None:
        if self.debug:
            self.elk_reporter.index_name = {
                'dashboard_reboot_care': 'dashboard_reboot_care_1',
            }
        else:
            self.elk_reporter.index_name = {
                'dashboard_reboot_care': 'dashboard_reboot_care',
            }

    def fill_reboot_care_details_dict(self, timestamp: datetime, doc_id: str, data_dict: dict, file_name: str) -> dict:
        self.logger.debug('starting "fill_reboot_care_details_dict" function')

        return {
            "timestamp": timestamp,
            "doc_id": doc_id,
            "file_name": file_name,

            "bs_hardware_type": data_dict['Bs_hardware_type'].upper(),
            "entity_type_reboot": data_dict['entity_type_reboot'].upper(),
            "reboot_triggered_by_entity_type": data_dict['reboot_triggered_by_entity_type'].upper(),
            "platform": data_dict['Platform'].upper(),
            "detailed_info": data_dict['detailed_info'],
            "entity_version": data_dict['entity_SW'],
            "reboot_expected": data_dict['expected'],
            "reboot_expected_str": f"{data_dict['expected']}".title(),
            "reboot_reason": data_dict['reboot_reason'],
            "pack_version": data_dict['pack_SW'].split('airspan_aio_')[1],  # -----
            "reboot_reason_id": data_dict['reboot_reason_id'],
            "reboot_reason_id_str": f"{data_dict['reboot_reason_id']}",
            "serial_number": data_dict['serial'].upper(),
            "entity_timestamp": data_dict['timestamp']
        }

    def fill_reboot_care_details_doc(self, data_dict, file_name: str) -> None:
        reboot_care_details_doc = self.fill_reboot_care_details_dict(
            timestamp=datetime.now(timezone.utc),
            doc_id=self.elk_reporter.generate_doc_id(),
            data_dict=data_dict,
            file_name=file_name
        )
        self.elk_reporter.fill_list_of_docs(
            index_name=self.elk_reporter.index_name['dashboard_reboot_care'],
            doc=reboot_care_details_doc
        )

    def process(self, data_dict, file_name) -> None:
        self.logger.info('Start "feature_global_information_doc" function')
        self.logger.info(f'feature_global_information_doc is: {self.fill_reboot_care_details_doc(data_dict=data_dict, file_name=file_name)}')
        self.logger.info('Stop "feature_global_information_doc" function')

        self.elk_reporter.set_list_of_docs()
        print()


if __name__ == '__main__':
    import json
    import msgpack

    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger

    project_name = 'ReportGlobalInformationToELK'
    site = None
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    # path = 'C:\\tmp\\ue_statistics\\final_result_object_4g.json'
    # path = 'C:\\tmp\\ue_statistics\\final_result_object_5g.json'
    path = 'C:\\tmp\\ue_statistics\\final_result_object_5g_2.json'
    # path = 'C:\\tmp\\ue_statistics\\final_result_object.json'
    # path = 'C:\\tmp\\ue_statistics\\final_result_object_1h.json'
    # path = 'C:\\tmp\\ue_statistics\\final_result_object_12h.json'

    try:
        with open(path, "r") as json_file:
            _test_results_object = json.load(json_file)
    except Exception:
        with open(path, "rb") as json_file:
            _test_results_object = msgpack.unpackb(json_file.read(), strict_map_key=False)

    print()
    # _test_results_object['test_info']['builder_name'] = ''
    # _test_results_object['enb']['Cyclone_AV1500T']['sub_tasks']['enb_sub_task'] = _test_results_object['enb']['Cyclone_AV1500T']['sub_tasks']['enb']

    global_information_reporter = ReportToELK(
        test_results_object=_test_results_object,
        debug=True
    )
    global_information_reporter.process(
        # jira_test_run_time=30,
        # deep_analysis=True,
    )
