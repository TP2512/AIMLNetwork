import logging
import random
from datetime import datetime, timezone
from copy import deepcopy
from elasticsearch import helpers
import asyncio

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchHelper


class SendDataForDashboard:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.gnb_flag = True
        self.ue_flag = True

    @staticmethod
    def generate_doc_id():
        return datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%m')

    @staticmethod
    def fill_list_of_docs(list_of_docs, index_name, doc):
        list_of_docs.append(
            {
                "_index": index_name,
                "_source": deepcopy(doc)
            }
        )

    def change_dot_to_underscore(self):
        pass

    def set_list_of_docs(self, elk_client, list_of_docs):
        self.logger.info('Start "set_list_of_docs" function')
        if list_of_docs:
            self.logger.info('Start to report the documents to ELK')
            ElasticSearchHelper().change_elasticsearch_logger()
            helpers.bulk(elk_client, list_of_docs)
            # print()
        else:
            self.logger.error('list_of_docs is empty')

    @staticmethod
    def fill_feature_global_information_doc(automation_manual, global_information_body, gnb_data_list, feature_doc_id, scenario_status, test_run_time):
        # sourcery skip: low-code-quality, or-if-exp-identity
        return {
            "automation_manual": automation_manual,

            "doc_id": feature_doc_id,
            "feature_doc_id": feature_doc_id,
            "ezlife_builder_id": global_information_body.get('Builder ID', 'null'),
            "ezlife_builder_name": global_information_body.get('Builder Name', 'null'),
            "jenkins_build_number": f"Build #{global_information_body.get('Jenkins Build ID', 'null')}",
            "slave_name": global_information_body.get('Slave Name', 'null'),

            "ur_version": global_information_body.get('UR Version', 'null').replace(".", "_"),

            "environment_config": global_information_body.get('Environment Config', 'null'),
            "execute_environment_config_and_test_per_ur_version":
                f"{global_information_body.get('Environment Config', 'null')} - {global_information_body.get('Test SIR', 'null')}",

            "test_set": global_information_body.get('Test Set', 'null'),
            "execute_environment_config_and_test_set":
                f"{global_information_body.get('Environment Config', 'null')} - {global_information_body.get('Test Set', 'null')}",

            "test_plan": global_information_body.get('Test Plan', 'null'),
            "test_sir": global_information_body.get('Test SIR', 'null'),
            "feature_name": global_information_body.get('Feature Name', 'null'),
            "feature_group_name": global_information_body.get('Group Name', 'null'),
            "test_execution_list": [gnb_data.get('Execution Key') for gnb_data in gnb_data_list],
            "test_execution_list_str": ', '.join([gnb_data.get('Execution Key') for gnb_data in gnb_data_list]),

            "test_plan_2": f'{global_information_body.get("Test Plan")}',
            "test_sir_2": f'{global_information_body.get("Test SIR")}',
            "test_plan_and_test_sir_2": f'{global_information_body.get("Test Plan")} + {global_information_body.get("Test SIR")}',

            "scenario_run_time": global_information_body.get('Scenario Run Time', -1),
            "scenario_status": scenario_status,

            "test_run_time": test_run_time,
            "gnb_test_status_list": [gnb_data.get('Test Status', 'null') for gnb_data in gnb_data_list],

            "run_test_in_loop": global_information_body.get('Run Test In Loop', 'null'),
            "loop_count": global_information_body.get('Run Test In Loop', 'null'),

            "gnb_type_list": [gnb_data['GNB Type'] for gnb_data in gnb_data_list],
            "gnb_type_list_str": ', '.join([gnb_data['GNB Type'] for gnb_data in gnb_data_list]),

            "fix_version_list": list(
                set(
                    [gnb_data['CUCP_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list] +
                    [gnb_data['CUUP_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list] +
                    [gnb_data['DU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list] +
                    [gnb_data['RU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list] +
                    [gnb_data['XPU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('XPU_Ver')]
                )
            ),
            "fix_version_list_str": ', '.join(
                list(
                    set(
                        [gnb_data['CUCP_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list] +
                        [gnb_data['CUUP_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list] +
                        [gnb_data['DU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list] +
                        [gnb_data['RU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list] +
                        [gnb_data['XPU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('XPU_Ver')]
                    )
                )
            ),

            "cucp_fix_version_list": sorted(list({gnb_data['CUCP_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list})),
            "cucp_version_list": sorted(list({gnb_data['CUCP_Ver'].replace(".", "_") for gnb_data in gnb_data_list})),
            "cucp_version_list_str": ', '.join(sorted(list({gnb_data['CUCP_Ver'].replace(".", "_") for gnb_data in gnb_data_list}))),

            "cuup_fix_version_list": sorted(list({gnb_data['CUUP_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list})),
            "cuup_version_list": sorted(list({gnb_data['CUUP_Ver'].replace(".", "_") for gnb_data in gnb_data_list})),
            "cuup_version_list_str": ', '.join(sorted(list({gnb_data['CUUP_Ver'].replace(".", "_") for gnb_data in gnb_data_list}))),

            "du_fix_version_list": sorted(list({gnb_data['DU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list})),
            "du_version_list": sorted(list({gnb_data['DU_Ver'].replace(".", "_") for gnb_data in gnb_data_list})),
            "du_version_list_str": ', '.join(sorted(list({gnb_data['DU_Ver'].replace(".", "_") for gnb_data in gnb_data_list}))),

            "ru_fix_version_list": sorted(list({gnb_data['RU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list})),
            "ru_version_list": sorted(list({gnb_data['RU_Ver'].replace(".", "_") for gnb_data in gnb_data_list})),
            "ru_version_list_str": ', '.join(sorted(list({gnb_data['RU_Ver'].replace(".", "_") for gnb_data in gnb_data_list}))),

            "aio_fix_version_list": sorted(list({gnb_data['AIO_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('AIO_Ver')})),
            "aio_version_list": sorted(list({gnb_data['AIO_Ver'].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('AIO_Ver')})),
            "aio_version_list_str": ', '.join(sorted(list({gnb_data['AIO_Ver'].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('AIO_Ver')}))),

            "xpu_fix_version_list": sorted(list({gnb_data['XPU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('XPU_Ver')})),
            "xpu_version_list": sorted(list({gnb_data['XPU_Ver'].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('XPU_Ver')})),
            "xpu_version_list_str": ', '.join(sorted(list({gnb_data['XPU_Ver'].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('XPU_Ver')}))),

            "ems_fix_version_list": sorted(list({gnb_data['ACP Version'].split('-', 1)[0].replace(".", "_") if gnb_data['ACP Version'] else 'N/A' for gnb_data in gnb_data_list})),
            "ems_version_list": sorted(list({gnb_data['ACP Version'].replace(".", "_") for gnb_data in gnb_data_list})),
            "ems_version_list_str": ', '.join(sorted(list({gnb_data['ACP Version'].replace(".", "_") for gnb_data in gnb_data_list}))),

            # "vran_fix_version_list": sorted(list({gnb_data['AIO_Ver'].split('-', 1)[0] for gnb_data in gnb_data_list if gnb_data.get('AIO_Ver')})),
            # "vran_version_list": sorted(list({gnb_data['AIO_Ver'] for gnb_data in gnb_data_list if gnb_data.get('AIO_Ver')})),
            # "vran_version_list_str": ', '.join(sorted(list({gnb_data['AIO_Ver'] for gnb_data in gnb_data_list if gnb_data.get('AIO_Ver')}))),

            "previous_cucp_fix_version_list": sorted(list({gnb_data['Previous_CUCP_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list
                                                           if gnb_data.get('Previous_CUCP_Ver', 'null')})),
            "previous_cucp_version_list": sorted(list({gnb_data['Previous_CUCP_Ver'].replace(".", "_") for gnb_data in gnb_data_list
                                                       if gnb_data.get('Previous_CUCP_Ver', 'null')})),
            "previous_cucp_version_list_str": ', '.join(sorted(list({gnb_data['Previous_CUCP_Ver'].replace(".", "_") for gnb_data in gnb_data_list
                                                                     if gnb_data.get('Previous_CUCP_Ver', 'null')}))),

            "previous_cuup_fix_version_list": sorted(list({gnb_data['Previous_CUUP_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list
                                                           if gnb_data.get('Previous_CUUP_Ver', 'null')})),
            "previous_cuup_version_list": sorted(list({gnb_data['Previous_CUUP_Ver'].replace(".", "_") for gnb_data in gnb_data_list
                                                       if gnb_data.get('Previous_CUUP_Ver', 'null')})),
            "previous_cuup_version_list_str": ', '.join(sorted(list({gnb_data['Previous_CUUP_Ver'].replace(".", "_") for gnb_data in gnb_data_list
                                                                     if gnb_data.get('Previous_CUUP_Ver', 'null')}))),

            "previous_du_fix_version_list": sorted(list({gnb_data['Previous_DU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list
                                                         if gnb_data.get('Previous_DU_Ver', 'null')})),
            "previous_du_version_list": sorted(list({gnb_data['Previous_DU_Ver'].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('Previous_DU_Ver', 'null')})),
            "previous_du_version_list_str": ', '.join(sorted(list({gnb_data['Previous_DU_Ver'].replace(".", "_") for gnb_data in gnb_data_list
                                                                   if gnb_data.get('Previous_DU_Ver', 'null')}))),

            "previous_ru_fix_version_list": sorted(list({gnb_data['Previous_RU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list
                                                         if gnb_data.get('Previous_RU_Ver', 'null')})),
            "previous_ru_version_list": sorted(list({gnb_data['Previous_RU_Ver'].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('Previous_RU_Ver', 'null')})),
            "previous_ru_version_list_str": ', '.join(sorted(list({gnb_data['Previous_RU_Ver'].replace(".", "_") for gnb_data in gnb_data_list
                                                                   if gnb_data.get('Previous_RU_Ver', 'null')}))),

            "previous_aio_fix_version_list": sorted(list({gnb_data['Previous_AIO_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list
                                                          if gnb_data.get('Previous_AIO_Ver', 'null')})),
            "previous_aio_version_list": sorted(list({gnb_data['Previous_AIO_Ver'].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('Previous_AIO_Ver', 'null')})),
            "previous_aio_version_list_str": ', '.join(sorted(list({gnb_data['Previous_AIO_Ver'].replace(".", "_") for gnb_data in gnb_data_list
                                                                    if gnb_data.get('Previous_AIO_Ver', 'null')}))),

            "previous_xpu_fix_version_list": sorted(list({gnb_data['Previous_XPU_Ver'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list
                                                          if gnb_data.get('Previous_XPU_Ver', 'null')})),
            "previous_xpu_version_list": sorted(list({gnb_data['Previous_XPU_Ver'].replace(".", "_") for gnb_data in gnb_data_list if gnb_data.get('Previous_XPU_Ver', 'null')})),
            "previous_xpu_version_list_str": ', '.join(sorted(list({gnb_data['Previous_XPU_Ver'].replace(".", "_") for gnb_data in gnb_data_list
                                                                    if gnb_data.get('Previous_XPU_Ver', 'null')}))),

            "previous_ems_fix_version_list": sorted(list({gnb_data['Previous ACP Version'].split('-', 1)[0].replace(".", "_") for gnb_data in gnb_data_list
                                                          if gnb_data.get('Previous ACP Version', 'null')})),
            "previous_ems_version_list": sorted(list({gnb_data['Previous ACP Version'].replace(".", "_") for gnb_data in gnb_data_list
                                                      if gnb_data.get('Previous ACP Version', 'null')})),
            "previous_ems_version_list_str": ', '.join(sorted(list({gnb_data['Previous ACP Version'].replace(".", "_")for gnb_data in gnb_data_list
                                                                    if gnb_data.get('Previous ACP Version', 'null')}))),

            "number_of_ues": len([ue_name for gnb_data in gnb_data_list for ue_name in gnb_data['UE_STATISTICS']]),

            # "automation_error_message": global_information_body.get('Automation Error Message'),

            'core_files_name_list': sorted(list({core_files_name for gnb_data in gnb_data_list for core_files_name in gnb_data.get('Core Files Name', 'null') if core_files_name})),
            'core_files_name_list_str': ', '.join(sorted(list({core_files_name if core_files_name else 'N/A'
                                                               for gnb_data in gnb_data_list for core_files_name in gnb_data.get('Core Files Name')}))),

            "defects_list": global_information_body.get('Defects List') if global_information_body.get('Defects List') else 'N/A',
            "defects_list_str": ', '.join(global_information_body.get('Defects List') if global_information_body.get('Defects List') else ['N/A']),

            # ----- Need to add more thresholds -----

            # ##### Throughput #####
            "traffic_transport_layer_protocol": global_information_body.get('Traffic Transport Layer Protocol', 'null'),
            "automation_traffic_direction": global_information_body.get('Automation Traffic Direction', 'null'),
            "traffic_testing_tool": global_information_body.get('Traffic Testing tool', 'null'),
            "window_size": global_information_body.get('Window Size', 'null'),
            "frame_size": global_information_body.get('Frame Size', 'null'),

            "threshold": float(global_information_body['Threshold']) if global_information_body.get('Threshold') is not None else -1.0,  # in percent
            "dl_threshold": float(global_information_body['Threshold DL']) if global_information_body.get('Threshold DL') is not None else -1.0,
            "ul_threshold": float(global_information_body['Threshold UL']) if global_information_body.get('Threshold UL') is not None else -1.0,

            "ul_avg": float(global_information_body['UL AVG']) if global_information_body.get('UL AVG') is not None else -1.0,
            "dl_avg": float(global_information_body['DL AVG']) if global_information_body.get('DL AVG') is not None else -1.0,
            "max_ul": float(global_information_body['MAX UL']) if global_information_body.get('MAX UL') is not None else -1.0,
            "max_dl": float(global_information_body['MAX DL']) if global_information_body.get('MAX DL') is not None else -1.0,

            "expected_dl": float(global_information_body['Expected DL']) if global_information_body.get('Expected DL') is not None else None,
            "expected_ul": float(global_information_body['Expected UL']) if global_information_body.get('Expected UL') is not None else None,

            # ##### HandOver #####
            "ho_type": global_information_body.get('HO Type', 'null'),
        }

    @staticmethod
    def fill_feature_details_dict(timestamp):
        return {
            "timestamp": timestamp,
        }

    def fill_feature_details_doc(self, list_of_docs, index_name, timestamp, feature_global_information_doc):
        feature_details_doc = self.fill_feature_details_dict(
            timestamp=timestamp,
        )
        feature_details_doc |= feature_global_information_doc
        self.fill_list_of_docs(list_of_docs, index_name, feature_details_doc)

    # @staticmethod
    def fill_gnb_dict(self, timestamp, gnb_data, time_number):
        # sourcery skip: or-if-exp-identity
        # self.logger.info(f"Previous ACP Version is: {gnb_data.get('Previous ACP Version')}")
        # self.logger.info(f"Type of Previous ACP Version is: {type(gnb_data.get('Previous ACP Version'))}")
        # if type(gnb_data.get('Previous ACP Version')) != str:
        #     previous_ems_version = None
        # else:
        #     previous_ems_version = gnb_data.get('Previous ACP Version', 'null')
        return {
            "timestamp": timestamp,

            "gnb_name": gnb_data.get("GNB Name", 'null'),
            "gnb_number": gnb_data.get("GNB ID", 'null'),
            "gnb_name_by_number": f'gNB_{gnb_data.get("GNB ID", "null")}',
            "gnb_serial_number": f'{gnb_data.get("GNB SERIAL NUMBER", "null")}',
            "time": time_number,

            "gnb_type_name": gnb_data.get('GNB Type', 'null'),

            "hardware_type": gnb_data.get('BS Hardware Type', 'null'),
            "band": gnb_data.get('Band', 'null'),
            "bandwidth": gnb_data.get('Bandwidth', 'null'),
            "numerology": gnb_data.get('Numerology(SCS)', 'null'),
            "chipset": gnb_data.get('Chipset', 'null'),
            "format_ssf": gnb_data.get('Format(SSF)', 'null'),
            # "scs": gnb_data['scs'],

            "cucp_version": gnb_data.get('CUCP_Ver', 'null').replace(".", "_"),
            "cuup_version": gnb_data.get('CUUP_Ver', 'null').replace(".", "_"),
            "du_version": gnb_data.get('DU_Ver', 'null').replace(".", "_"),
            "ru_version": gnb_data.get('RU_Ver', 'null').replace(".", "_"),
            "aio_version": gnb_data.get('AIO_Ver', 'null').replace(".", "_"),
            "xpu_version": gnb_data.get('XPU_Ver', 'null').replace(".", "_"),
            "ems_version": gnb_data.get('ACP Version', 'null').replace(".", "_"),

            'previous_cucp_version': gnb_data.get('Previous_CUCP_Ver').replace(".", "_") if gnb_data.get('Previous_CUCP_Ver') else 'null',
            'previous_cuup_version': gnb_data.get('Previous_CUUP_Ver').replace(".", "_") if gnb_data.get('Previous_CUUP_Ver') else 'null',
            'previous_du_version': gnb_data.get('Previous_DU_Ver').replace(".", "_") if gnb_data.get('Previous_DU_Ver') else 'null',
            'previous_ru_version': gnb_data.get('Previous_RU_Ver').replace(".", "_") if gnb_data.get('Previous_RU_Ver') else 'null',
            'previous_aio_version': gnb_data.get('Previous_AIO_Ver').replace(".", "_") if gnb_data.get('Previous_AIO_Ver') else 'null',
            'previous_xpu_version': gnb_data.get('Previous_XPU_Ver').replace(".", "_") if gnb_data.get('Previous_XPU_Ver') else 'null',
            "previous_ems__version": gnb_data.get('Previous ACP Version').replace(".", "_") if gnb_data.get('Previous ACP Version') else 'null',

            "gnb_test_execution": gnb_data.get('Execution Key', 'null'),
            "gnb_test_execution_status": gnb_data.get('Test Status', 'null'),
            "gnb_test_status": gnb_data.get('Test Status', 'null'),

            "number_of_ues_per_gnb": len(gnb_data['UE_STATISTICS']) if gnb_data.get('UE_STATISTICS') is not None else 0,

            # "expected_results": feature_data['Status'][gnb_data['Test Status']]['expected_results'],
            "gnb_actual_results": gnb_data.get('Actual Results') if gnb_data.get('Actual Results') else 'N/A',

            "gnb_configuration": f"{gnb_data.get('Band')}, {gnb_data.get('Bandwidth')}, {gnb_data.get('Numerology(SCS)')}",

            # f"{gnb_data['BS Hardware Type']}, {gnb_data['Band']}, {gnb_data['Bandwidth']}, {gnb_data['Numerology(SCS)']}":
            #     f"Expected Results: {feature_data['Status'][gnb_data['Test Status']]['expected_results']}, Actual Results: {gnb_data['Actual Results']}",

            'gnb_core_files_name_list': gnb_data.get('Core Files Name') if gnb_data.get('Core Files Name') else [],
            'gnb_core_system_up_time_min': gnb_data.get('Core SystemUpTime (min)'),
            'gnb_core_occurrence_count': gnb_data.get('Core Occurrence Count') if gnb_data.get('Core Occurrence Count') else 0,
            'gnb_mtbf_core_occurrence_count': gnb_data.get('MTBF Core Occurrence Count') if gnb_data.get('MTBF Core Occurrence Count') else 0,
            'gnb_time_to_first_crash': gnb_data.get('Time To First Crash', -1),
            'gnb_minimum_run_time': gnb_data.get('Minimum Run Time', -1),
            'gnb_maximum_run_time': gnb_data.get('Maximum Run Time', -1),

            "system_recovery_time": gnb_data.get('SYSTEM_RECOVERY_TIME') if gnb_data.get('SYSTEM_RECOVERY_TIME') else 0,
            'kpi': gnb_data.get('KPI') if gnb_data.get('KPI') else 'N/A',

            "gnb_automation_error_message": gnb_data.get('Automation Error Message') if gnb_data.get('Automation Error Message') else 'N/A',
            'test_results': gnb_data.get('Test Results') if gnb_data.get('Test Results') else 'N/A',
            'log_path': gnb_data.get('Log Path', 'null'),

            # ----- Need to add more thresholds -----

            # ##### HandOver #####
            'ho_success_rate': gnb_data.get('HO Success Rate', -1),

            # ##### Ping Latency #####
            'ping_latency_avg': gnb_data.get('Ping Avg Latency', -1.0),

            # ##### Ping Loss #####
            'ping_loss': gnb_data.get('Ping Loss', -1.0),
        }

    async def fill_gnbs_docs(self, list_of_docs, index_name, feature_global_information_doc, time_number, gnbs_data):
        for index, gnb_data in enumerate(gnbs_data, start=0):
            gnbs_docs = self.fill_gnb_dict(
                timestamp=datetime.now(timezone.utc),
                gnb_data=gnb_data,
                time_number=time_number
            )
            gnbs_docs |= feature_global_information_doc
            self.fill_list_of_docs(list_of_docs, index_name['dashboard_results_gnbs'], gnbs_docs)
            if self.gnb_flag:
                self.gnb_flag = False
                self.logger.info(f'first gnbs_docs_information_doc is: {gnbs_docs}')

    @staticmethod
    def fill_ue_dict(timestamp, ue_statistics_data, ue_results_data, ue_name, time_number):  # sourcery skip: low-code-quality
        return {
            "timestamp": timestamp,
            "full_ue_name": ue_name,
            "ue_number": int(ue_name.split('_')[1]) if ue_name.split('_')[1] else None,
            "ue_name": ue_name.upper(),
            "time": time_number,

            "dl_tpt_results_mb": float(ue_results_data.get('DL')[time_number]) if ue_results_data and ue_results_data.get('DL') and ue_results_data['DL'][0] is not None else -1.0,
            "ul_tpt_results_mb": float(ue_results_data.get('UL')[time_number]) if ue_results_data and ue_results_data.get('UL') and ue_results_data['UL'][0] is not None else -1.0,

            "imsi": f"{ue_statistics_data.get('IMSI')[time_number] if ue_statistics_data.get('IMSI') is not None else 'null'}",
            "rnti": f"{ue_statistics_data.get('RNTI')[time_number] if ue_statistics_data.get('RNTI') is not None else 'null'}",
            "ue_id": f"{ue_statistics_data.get('UE-ID')[time_number] if ue_statistics_data.get('UE-ID') is not None else 'null'}",
            "cell_id": f"{ue_statistics_data.get('CELL-ID')[time_number] if ue_statistics_data.get('CELL-ID') is not None else 'null'}",
            "pcell_id": f"{ue_statistics_data.get('PCELL-ID')[time_number] if ue_statistics_data.get('PCELL-ID') is not None else 'null'}",
            "connected_time_min": f"{ue_statistics_data.get('Connected Time(Min)')[time_number] if ue_statistics_data.get('Connected Time(Min)') is not None else 'null'}",
            "256qam_actv": f"{ue_statistics_data.get('256QAM ACTV')[time_number] if ue_statistics_data.get('256QAM ACTV') is not None else 'null'}",
            "256qam_alloc": f"{ue_statistics_data.get('256QAM Alloc')[time_number] if ue_statistics_data.get('256QAM Alloc') is not None else 'null'}",
            "meas_gap_active": f"{ue_statistics_data.get('MEAS GAP ACTIVE')[time_number] if ue_statistics_data.get('MEAS GAP ACTIVE') is not None else 'null'}",
            "dl_tpt_mb": float(ue_statistics_data.get('DL-TPT (Mb)')[time_number]) if ue_statistics_data.get('DL-TPT (Mb)') is not None else -1.0,
            "ul_tpt_mb": float(ue_statistics_data.get('UL-TPT (Mb)')[time_number]) if ue_statistics_data.get('UL-TPT (Mb)') is not None else -1.0,
            "dl_bler_cw_0": float(ue_statistics_data.get('DL-BLER %CW-0')[time_number]) if ue_statistics_data.get('DL-BLER %CW-0') is not None else None,
            "dl_bler_cw_1": float(ue_statistics_data.get('DL-BLER %CW-1')[time_number]) if ue_statistics_data.get('DL-BLER %CW-1') is not None else None,
            "ul_bler_crc_per": float(ue_statistics_data.get('UL-BLER-CRC %PER')[time_number]) if ue_statistics_data.get('UL-BLER-CRC %PER') is not None else None,
            "ri_rx": float(ue_statistics_data.get('RI RX')[time_number]) if ue_statistics_data.get('RI RX') is not None else None,
            "ri_ul": float(ue_statistics_data.get('RI UL')[time_number]) if ue_statistics_data.get('RI UL') is not None else None,
            "ri_dl": float(ue_statistics_data.get('RI DL')[time_number]) if ue_statistics_data.get('RI DL') is not None else None,
            "dl_cqi_cw_0": float(ue_statistics_data.get('DL-CQI CW-0')[time_number]) if ue_statistics_data.get('DL-CQI CW-0') is not None else None,
            "dl_cqi_cw_1": float(ue_statistics_data.get('DL-CQI CW-1')[time_number]) if ue_statistics_data.get('DL-CQI CW-1') is not None else None,
            "ul_cqi_cw_0": float(ue_statistics_data.get('UL-CQI CW-0')[time_number]) if ue_statistics_data.get('UL-CQI CW-0') is not None else None,
            "ul_cqi_cw_1": float(ue_statistics_data.get('UL-CQI CW-1')[time_number]) if ue_statistics_data.get('UL-CQI CW-1') is not None else None,
            "dl_mcs_cw_0": float(ue_statistics_data.get('DL-MCS CW-0')[time_number]) if ue_statistics_data.get('DL-MCS CW-0') is not None else None,
            "dl_mcs_cw_1": float(ue_statistics_data.get('DL-MCS CW-1')[time_number]) if ue_statistics_data.get('DL-MCS CW-1') is not None else None,
            "ul_mcs_cw_0": float(ue_statistics_data.get('UL-MCS CW-0')[time_number]) if ue_statistics_data.get('UL-MCS CW-0') is not None else None,
            "ul_mcs_cw_1": float(ue_statistics_data.get('UL-MCS CW-1')[time_number]) if ue_statistics_data.get('UL-MCS CW-1') is not None else None,
            "dl_cuup_pdcp_mbps": float(ue_statistics_data.get('DL_CUUP_PDCP(Mbps)')[time_number]) if ue_statistics_data.get('DL_CUUP_PDCP(Mbps)') is not None else None,
            "ul_cuup_pdcp_mbps": float(ue_statistics_data.get('UL_CUUP_PDCP(Mbps)')[time_number]) if ue_statistics_data.get('UL_CUUP_PDCP(Mbps)') is not None else None,
            "c2i": float(ue_statistics_data.get('C2I')[time_number]) if ue_statistics_data.get('C2I') is not None else None,
            "dl_pkt_rx": float(ue_statistics_data.get('DL-PKT-RX')[time_number]) if ue_statistics_data.get('DL-PKT-RX') is not None else None,
            "ul_pkt_tx": float(ue_statistics_data.get('UL-PKT-TX')[time_number]) if ue_statistics_data.get('UL-PKT-TX') is not None else None,
            "rlc_dl_tpt_mb": float(ue_statistics_data.get('RLC-DL-TPT (Mb)')[time_number]) if ue_statistics_data.get('RLC-DL-TPT (Mb)') is not None else None,
            "rlc_ul_tpt_mb": float(ue_statistics_data.get('RLC-UL-TPT (Mb)')[time_number]) if ue_statistics_data.get('RLC-UL-TPT (Mb)') is not None else None,
            "mac_dl_tpt_mb": float(ue_statistics_data.get('MAC-DL-TPT (Mb)')[time_number]) if ue_statistics_data.get('MAC-DL-TPT (Mb)') is not None else None,
            "mac_ul_tpt_mb": float(ue_statistics_data.get('MAC-UL-TPT (Mb)')[time_number]) if ue_statistics_data.get('MAC-UL-TPT (Mb)') is not None else None,
            "cl_dl_tpt_mb": float(ue_statistics_data.get('CL-DL-TPT (Mb)')[time_number]) if ue_statistics_data.get('CL-DL-TPT (Mb)') is not None else None,
            "cl_ul_tpt_mb": float(ue_statistics_data.get('CL-UL-TPT (Mb)')[time_number]) if ue_statistics_data.get('CL-UL-TPT (Mb)') is not None else None,
            "num_sr": float(ue_statistics_data.get('NUM-SR')[time_number]) if ue_statistics_data.get('NUM-SR') is not None else None,
            "rsrp": float(ue_statistics_data.get('RSRP')[time_number]) if ue_statistics_data.get('RSRP') is not None else None,
            "rssi": float(ue_statistics_data.get('RSSI')[time_number]) if ue_statistics_data.get('RSSI') is not None else None,
            "rsrq": float(ue_statistics_data.get('RSRQ')[time_number]) if ue_statistics_data.get('RSRQ') is not None else None,
            "snr": float(ue_statistics_data.get('SNR')[time_number]) if ue_statistics_data.get('SNR') is not None else None,

            "static_to_ru": f"{ue_statistics_data.get('static_to_ru', 'null')}",
            "cuup_ue_id": f"{ue_statistics_data.get('CUUP_UE_ID')[time_number] if ue_statistics_data.get('CUUP_UE_ID') else 'null'}",
            "cuup_bearer_id": f"{ue_statistics_data.get('CUUP_BEARER')[time_number] if ue_statistics_data.get('CUUP_BEARER') else 'null'}",
            "cucp_ue_id": f"{ue_statistics_data.get('CUCP_UE_Id')[time_number] if ue_statistics_data.get('CUCP_UE_Id') else 'null'}",
            "cucp_rnti": f"{ue_statistics_data.get('CUCP_rnti')[time_number] if ue_statistics_data.get('CUCP_rnti') else 'null'}",
            "cucp_amf_id": f"{ue_statistics_data.get('CUCP_amfId')[time_number] if ue_statistics_data.get('CUCP_amfId') else 'null'}",
        }

    async def fill_ues_docs(self, list_of_docs, index_name, feature_global_information_doc, time_number, ue_statistics_data, ue_results_data, ue_name):
        ues_docs = self.fill_ue_dict(
            timestamp=datetime.now(timezone.utc),
            ue_statistics_data=ue_statistics_data,
            ue_results_data=ue_results_data,
            ue_name=ue_name,
            time_number=time_number,
        )
        ues_docs |= feature_global_information_doc
        self.fill_list_of_docs(list_of_docs, index_name['dashboard_results_ues'], ues_docs)
        if self.ue_flag:
            self.ue_flag = False
            self.logger.info(f'first ues_docs_information_doc is: {ues_docs}')

    @staticmethod
    def fill_error_and_warning_dict(timestamp, warning_int, error_int):
        return {
            "timestamp": timestamp,

            "warning_message_int": warning_int,
            "warning_message": f'warning {warning_int}',

            "error_message_int": error_int,
            "error_message": f'error {error_int}',
        }

    def fill_error_and_warning_list(self, list_of_docs, index_name, feature_global_information_doc):
        for _ in range(20):
            warning_int = random.randint(0, 100)
            error_int = random.randint(0, 100)

            error_and_warning_list = self.fill_error_and_warning_dict(
                timestamp=datetime.now(timezone.utc),
                warning_int=warning_int,
                error_int=error_int
            )
            error_and_warning_list |= feature_global_information_doc
            self.fill_list_of_docs(list_of_docs, index_name['dashboard_results_error_and_warning_list'], error_and_warning_list)

    async def process(self, elk_client, index_name, global_information_body, list_of_data, run_time, automation_manual='Automation') -> None:
        self.logger.info('Start ELK Process')
        list_of_docs = []
        feature_doc_id = self.generate_doc_id()
        self.logger.info(f'feature_doc_id is: {feature_doc_id}')
        self.logger.info('Start "global_information_body" function')  # -------------------------------
        scenario_status = global_information_body['Scenario Status']

        self.logger.info('Start "feature_global_information_doc" function')  # -------------------------------
        feature_global_information_doc = self.fill_feature_global_information_doc(
            automation_manual=automation_manual,

            global_information_body=global_information_body,
            gnb_data_list=list_of_data,
            feature_doc_id=feature_doc_id,

            scenario_status=scenario_status,
            test_run_time=run_time,
        )
        self.logger.info(f'feature_global_information_doc is: {feature_global_information_doc}')

        self.logger.info('Start "fill_feature_details_doc" function')  # -------------------------------
        self.fill_feature_details_doc(
            list_of_docs=list_of_docs,
            index_name=index_name['dashboard_results_feature_details'],
            timestamp=datetime.now(timezone.utc),
            feature_global_information_doc=feature_global_information_doc,
        )

        self.logger.info(f'Start "fill_gnbs_docs" functions at {datetime.now(tz=timezone.utc)}')
        gnb_functions = [
            self.fill_gnbs_docs(
                list_of_docs=list_of_docs,
                index_name=index_name,
                feature_global_information_doc=feature_global_information_doc,

                time_number=time_number,
                gnbs_data=list_of_data,
            )
            for time_number in range(run_time)
        ]

        await asyncio.gather(*list(gnb_functions))
        self.logger.info(f'Stop "fill_gnbs_docs" functions at {datetime.now(tz=timezone.utc)}')

        self.logger.info(f'Start "fill_ues_docs" functions at {datetime.now(tz=timezone.utc)}')
        ue_functions = [
            self.fill_ues_docs(
                list_of_docs=list_of_docs,
                index_name=index_name,
                feature_global_information_doc=feature_global_information_doc,
                time_number=time_number,
                ue_statistics_data=ue_statistics_data,
                ue_name=ue_name.replace(' ', '_'),
                ue_results_data=gnb_data['UE_RESULTS'][list(gnb_data['UE_RESULTS'].keys())[index]] if len(list(gnb_data['UE_RESULTS'].keys())) > index else None
            ) for time_number in range(run_time) for gnb_data in list_of_data for index, (ue_name, ue_statistics_data) in enumerate(gnb_data['UE_STATISTICS'].items(), start=0)
        ]
        await asyncio.gather(*list(ue_functions))
        self.logger.info(f'Stop "fill_ues_docs" functions at {datetime.now(tz=timezone.utc)}')

        self.set_list_of_docs(elk_client, list_of_docs)

        # await asyncio.gather(
        #     *[
        #         self.fill_gnbs_docs(
        #             list_of_docs=list_of_docs,
        #             index_name=index_name,
        #             feature_global_information_doc=feature_global_information_doc,
        #
        #             time_number=time_number,
        #             gnbs_data=list_of_data,
        #         )
        #         for time_number in range(run_time)
        #     ]
        # )
        #
        # self.logger.info('Start "fill_ues_docs" functions')
        # await asyncio.gather(
        #     *[
        #         await self.fill_ues_docs(
        #             list_of_docs=list_of_docs,
        #             index_name=index_name,
        #             feature_global_information_doc=feature_global_information_doc,
        #
        #             time_number=time_number,
        #             gnb_data_list=list_of_data,
        #         ) for time_number in range(run_time)
        #     ]
        # )
        # self.set_list_of_docs(elk_client, list_of_docs)

        # for time_number in range(run_time):
        #     await asyncio.gather(
        #         self.fill_gnbs_docs(
        #             list_of_docs=list_of_docs,
        #             index_name=index_name,
        #             feature_global_information_doc=feature_global_information_doc,
        #
        #             time_number=time_number,
        #             gnbs_data=list_of_data,
        #         ),
        #
        #         self.fill_ues_docs(
        #             list_of_docs=list_of_docs,
        #             index_name=index_name,
        #             feature_global_information_doc=feature_global_information_doc,
        #
        #             time_number=time_number,
        #             gnb_data_list=list_of_data,
        #         )
        #     )
        #
        #     # fill_error_and_warning_list(
        #     #     list_of_docs=list_of_docs,
        #     #     index_name=index_name,
        #     #     feature_global_information_doc=feature_global_information_doc,
        #     # )
        #     self.set_list_of_docs(elk_client, list_of_docs)

        self.set_list_of_docs(elk_client, list_of_docs)
