import logging
import json
from elasticsearch_dsl import Search

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchForDashboard.ELKDashboardFillData.SendDataToDashboard import ELKReporter


class XXX:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch()
        # self.elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch_dev()
        self.path = 'C:\\Users\\azaguri\\Desktop\\ELK_json'

    @staticmethod
    def change_key_name(data_dict, old_key, new_key):
        data_dict[new_key] = data_dict[old_key]
        del data_dict[old_key]
        return data_dict

    @staticmethod
    def get_scenario_status_number(data_scenario_status):
        if data_scenario_status.upper() == 'PASS':
            return 10
        elif data_scenario_status.upper() == 'FAIL':
            return 5
        elif data_scenario_status.upper() == 'AUTOMATION_FAIL':
            return 0
        elif data_scenario_status.upper() == 'FAIL_TO_GENERATE_STATUS':
            return -1

    def replacement(self, index, len_ur, ur_version: str, data: dict) -> object:
        print(f'{ur_version} - {index} / {len_ur}')
        if not data.get('feature_doc_id') and not data.get('doc_id'):
            self.logger.error(f'There is no "doc_id" for {ur_version} UR version')
            return

        if type(data.get('feature_group_name')) is list and len(data.get('feature_group_name')) > 1:
            if 'Throughput_Stability' in data['feature_group_name']:
                data['feature_group_name'] = 'Throughput_Stability'
            elif 'HO_Stability' in data['feature_group_name']:
                data['feature_group_name'] = 'HO_Stability'
            elif 'gNB_SW_Upgrade' in data['feature_group_name']:
                data['feature_group_name'] = 'gNB_SW_Upgrade'
            else:
                print()

        new_data = {}
        if ur_version == 'SR19.00_UR7.2':
            if [True for k in list(data.keys()) if 'config' in k and 'env' not in k]:
                print()

            if data['test_execution_list'] if data.get('test_execution_list') else [data['test_execution']] == [None]:
                data['test_execution_list'] = []
            elif type(data.get('test_execution')) is str:
                data['test_execution_list'] = [data.get('test_execution')]

            print()
        elif ur_version == 'SR19.50_GA_AT2200':
            if data['test_execution_list'] if data.get('test_execution_list') else [data['test_execution']] == [None]:
                data['test_execution_list'] = []
            elif type(data.get('test_execution')) is str:
                data['test_execution_list'] = [data.get('test_execution')]

            if 'gnb_type_list' in list(data.keys()) and not data.get('gnb_type_list'):
                data['gnb_type_list'] = []
            elif data.get('gnb_type'):
                data['gnb_type_list'] = data.get('gnb_type')

                print()
        elif ur_version == 'SR19.50_UR1':
            if [True for k in list(data.keys()) if 'config' in k and 'env' not in k]:
                print()

            if data['test_execution_list'] if data.get('test_execution_list') else [data['test_execution']] == [None]:
                data['test_execution_list'] = []
            elif type(data.get('test_execution')) is str:
                data['test_execution_list'] = [data.get('test_execution')]

            if 'gnb_type_list' in list(data.keys()) and not data.get('gnb_type_list'):
                data['gnb_type_list'] = []
            elif data.get('gnb_type'):
                data['gnb_type_list'] = data.get('gnb_type')

                print()
        elif ur_version in {
            'SR19_50_UR1',
            'SR20.00 GA',
            'SR20_00 GA',
            'SVG_SR19.50_GA',
            'SVG_SR19.50_ROW',
            'SVG_SR19.50_UR1',
            'SVG_SR19_50_ROW',
            'SVG_SR19_50_UR1',
            'SVG_SR20.00 GA',
            'SVG_SR20_00 GA',
        }:
            if [True for k in list(data.keys()) if 'config' in k and 'env' not in k]:
                print()

        try:
            new_data |= {
                "timestamp": data['timestamp'],
                "automation_manual": data.get('automation_manual', 'Automation'),
                "doc_id": data['feature_doc_id'],
                "feature_doc_id": data['feature_doc_id'],
                "automation_version": data.get('automation_version', 'null').replace('.', '_'),
                "ezlife_builder_id": data['jenkins_build_number'].split('Build #')[1] if data.get('jenkins_build_number') else 'N/A',
                "ezlife_builder_name": data.get('ezlife_builder_name', 'null'),
                "jenkins_version": data.get('jenkins_version', 'null').replace('.', '_'),
                "jenkins_job_name": data.get('job_name', 'null'),
                "jenkins_build_number_int": data.get('job_name', 0),
                "jenkins_build_number": data.get('build_id', 'null'),
                "slave_name": data['slave_name'],
                "ur_version": data['ur_version'].replace('.', '_'),
                "feature_name": data['feature_name'],
                "feature_group_name": data['feature_group_name'],
                "environment_config": data.get('environment_config', 'null'),
                "test_plan": data['test_plan'],
                "test_set": data['test_set'],
                "test_sir": data['test_sir'],
                "execute_environment_config_and_test_sir": f"{data['environment_config']} - {data['test_sir']}",
                "execute_environment_config_and_test_set": f"{data['environment_config']} - {data['test_set']}",
                "execute_environment_config_and_test_per_ur_version": f"{data['environment_config']} - {data['test_sir']}",
                "environment_config_and_test_per_ur_version": f"{data['environment_config']} - {data['test_sir']}",
                "test_plan_2": data['test_plan'],
                "test_sir_2": data['test_sir'],
                "test_plan_and_test_sir_2": f"{data['test_plan']} + {data['test_sir']}",
                "scenario_run_time": data['scenario_run_time'],
                "scenario_status": data['scenario_status'],
                "scenario_status_number": self.get_scenario_status_number(data['scenario_status']),
                "jira_test_run_time": int(data['test_run_time'])
                if data.get('test_run_time')
                else data['jira_test_run_time'],
                # "actual_test_run_time": int(self.actual_test_run_time),
                "number_of_ues": int(data['number_of_ues']) if data.get('number_of_ues') else -1,
                "gnb_ran_mode_list": data['gnb_type_list'],
                "gnb_type_list": data['gnb_type_list'],
                "gnb_type_list_str": ', '.join(data['gnb_type_list']) if data.get('gnb_type_list') else [],
                "test_execution_list": data['test_execution_list'],
                "test_execution_list_str": ', '.join(data['test_execution_list']),
                "gnb_test_status_list": data['test_execution_list'],
                "all_execution_key_list": data['test_execution_list'],

                # ##### Feature Information #####
                # ##### Throughput #####
                "traffic_transport_layer_protocol": data.get('traffic_transport_layer_protocol'),
                "automation_traffic_direction": data.get('automation_traffic_direction'),
                "traffic_testing_tool": data.get('traffic_testing_tool'),
                "window_size": data.get('window_size'),
                "frame_size": data.get('frame_size'),

                # ##### HandOver #####
                "ho_type": data.get('ho_type'),

                # ##### SW Update #####
                # "run_test_in_loop": data.get('run_test_in_loop'),
                # "loop_count": data.get('loop_count'),

                # ##### Data Per gNB #####
                # ##### Current Version Per gNB #####
                "pack_version_list": data['aio_version_list'] if data.get('aio_version_list') else data.get('aio_versions'),
                "pack_version_list_str": ', '.join(data['aio_version_list'] if data.get('aio_version_list') else data.get('aio_versions', [])).replace('.', '_'),
                "fix_version_list": data['fix_version_list'] if data.get('fix_version_list') else data.get('fix_versions'),
                "fix_version_list_str": ', '.join(data['fix_version_list'] if data.get('fix_version_list') else data.get('fix_versions', [])).replace('.', '_'),
                "cucp_fix_version_list": data['cucp_fix_version_list'] if data.get('cucp_fix_version_list') else data.get('cucp_fix_versions', []),
                "cucp_version_list": data['cucp_version_list'] if data.get('cucp_version_list') else data.get('cucp_versions'),
                "cucp_version_list_str": ', '.join(data['cucp_version_list'] if data.get('cucp_version_list') else data.get('cucp_versions', [])).replace('.', '_'),
                "cuup_fix_version_list": data['cuup_fix_version_list'] if data.get('cuup_fix_version_list') else data.get('cuup_fix_versions', []),
                "cuup_version_list": data['cuup_version_list'] if data.get('cuup_version_list') else data.get('cuup_versions'),
                "cuup_version_list_str": ', '.join(data['cuup_version_list'] if data.get('cuup_version_list') else data.get('cuup_versions', [])).replace('.', '_'),
                "du_fix_version_list": data['du_fix_version_list'] if data.get('du_fix_version_list') else data.get('du_fix_versions', []),
                "du_version_list": data['du_version_list'] if data.get('du_version_list') else data.get('du_versions'),
                "du_version_list_str": ', '.join(data['du_version_list'] if data.get('du_version_list') else data.get('du_versions', [])).replace('.', '_'),
                "ru_fix_version_list": data['ru_fix_version_list'] if data.get('ru_fix_version_list') else data.get('ru_fix_versions', []),
                "ru_version_list": data['ru_version_list'] if data.get('ru_version_list') else data.get('ru_versions'),
                "ru_version_list_str": ', '.join(data['ru_version_list'] if data.get('ru_version_list') else data.get('ru_versions', [])).replace('.', '_'),
                "xpu_fix_version_list": data['xpu_fix_version_list'] if data.get('xpu_fix_version_list') else data.get('xpu_fix_versions', []),
                "xpu_version_list": data['xpu_version_list'] if data.get('xpu_version_list') else data.get('xpu_versions'),
                "xpu_version_list_str": ', '.join(data['xpu_version_list'] if data.get('xpu_version_list') else data.get('xpu_versions', [])).replace('.', '_'),
                "ems_fix_version_list": data['ems_fix_version_list'] if data.get('ems_fix_version_list') else data.get('ems_fix_versions', []),
                "ems_version_list": data['ems_version_list'] if data.get('ems_version_list') else data.get('ems_versions'),
                "ems_version_list_str": ', '.join(data['ems_version_list'] if data.get('ems_version_list') else data.get('ems_versions', [])).replace('.', '_'),

                # ##### Previous Version Per gNB #####
                "previous_cucp_fix_version_list": data.get('previous_cucp_fix_version_list', []),
                "previous_cucp_version_list": data.get('previous_cucp_version_list', []),
                "previous_cucp_version_list_str": ', '.join(data.get('previous_cucp_version_list', [])).replace('.', '_'),
                "previous_cuup_fix_version_list": data.get('previous_cuup_fix_version_list', []),
                "previous_cuup_version_list": data.get('previous_cuup_version_list', []),
                "previous_cuup_version_list_str": ', '.join(data.get('previous_cuup_version_list', [])).replace('.', '_'),
                "previous_du_fix_version_list": data.get('previous_du_fix_version_list', []),
                "previous_du_version_list": data.get('previous_du_version_list', []),
                "previous_du_version_list_str": ', '.join(data.get('previous_du_version_list', [])).replace('.', '_'),
                "previous_ru_fix_version_list": data.get('previous_ru_fix_version_list', []),
                "previous_ru_version_list": data.get('previous_ru_version_list', []),
                "previous_ru_version_list_str": ', '.join(data.get('previous_ru_version_list', [])).replace('.', '_'),
                "previous_xpu_fix_version_list": data.get('previous_xpu_fix_version_list', []),
                "previous_xpu_version_list": data.get('previous_xpu_version_list', []),
                "previous_xpu_version_list_str": ', '.join(data.get('previous_xpu_version_list', [])).replace('.', '_'),
                "previous_ems_fix_version_list": data.get('previous_ems_fix_version_list', []),
                "previous_ems_version_list": data.get('previous_ems_version_list', []),
                "previous_ems_version_list_str": ', '.join(data.get('previous_ems_version_list', [])).replace('.', '_'),

                #

                "all_actual_results_list": data.get('actual_results', 'N/A'),
                "all_failure_reason_list": data.get('failure_reason', 'N/A'),
                "all_failure_reason_id_list": data.get('failure_reason_id', 'N/A'),
                "all_configuration_list": data.get('all_configuration_list', 'N/A'),
                "all_configuration_list_min": data.get('all_configuration_list_min', 'N/A'),
                "all_configuration_list_str": data.get('all_configuration_list_str', 'N/A'),
                "all_configuration_list_min_str": data.get('all_configuration_list_min_str', 'N/A'),
                "defects_list": data.get('defects_list', 'N/A'),
                "defects_list_str": ', '.join(data.get('defects_list', [])),
                'core_files_name_list': data.get('core_files_name', 'N/A'),
                'core_files_name_list_str': ', '.join(data.get('core_files_name_list', [])),

                # # ##### Throughput #####
                "all_throughput_results_list": data.get('all_throughput_results_list', 'N/A'),
                "all_throughput_results_list_str": ', '.join(data.get('all_throughput_results_list', [])),
                "all_dl_throughput_results_list": data.get('all_dl_throughput_results_list', 'N/A'),
                "all_dl_throughput_results_list_str": ', '.join(data.get('all_dl_throughput_results_list', [])),
                "all_ul_throughput_results_list": data.get('all_ul_throughput_results_list', 'N/A'),
                "all_ul_throughput_results_list_str": ', '.join(data.get('all_ul_throughput_results_list', [])),
            }
        except Exception:
            self.logger.exception(f'{ur_version}:')
            print()
        return new_data

    def search_by_ur_version(self, ur_version):
        list_of_docs = []
        s = Search(index='new_dashboard_results_feature_details_production').using(self.elk_client).extra(size=10000).query("match", ur_version=ur_version)
        response = s.execute()
        for index, hit in enumerate(response, start=1):
            hit_d = hit.__dict__
            list_of_docs.append(self.replacement(index=index, len_ur=response.hits.total.value, data=hit_d['_d_'], ur_version=ur_version))
        return list_of_docs

    def wr_to_file(self, file_name, list_of_docs):
        with open(f'{self.path}\\{file_name}', "w") as f:
            f.write(json.dumps(list_of_docs, sort_keys=True, indent=4, separators=(",", ": ")))

    def read_from_file(self, ur_version):
        print(ur_version)
        with open(f'{self.path}\\{ur_version}.json', "r") as f:
            file_str = f.read()
        return {ur_version: json.loads(file_str)}


def main_1():
    x = XXX()

    ur_version_list = [
        "SR19.00_UR7.2",
        "SR19.50_GA_AT2200",
        "SR19.50_UR1",
        "SR19_50_UR1",
        "SR20.00 GA",
        "SR20_00 GA",
        "SVG_SR19.50_GA",
        "SVG_SR19.50_ROW",
        "SVG_SR19.50_UR1",
        "SVG_SR19_50_ROW",
        "SVG_SR19_50_UR1",
        "SVG_SR20.00 GA",
        "SVG_SR20_00 GA"
    ]

    # d = {}
    # for _ur_version in ur_version_list:
    #     d |= x.read_from_file(ur_version=_ur_version)
    # print()

    for _ur_version in ur_version_list:
        if _list_of_docs := x.search_by_ur_version(ur_version=_ur_version):
            x.wr_to_file(file_name=f'{_ur_version}.json', list_of_docs=_list_of_docs)
            print()
    print()


def main_2():
    x = XXX()
    elk_reporter = ELKReporter()
    elk_reporter.elk_client = x.elk_client

    ur_version_list = [
        "SR19.00_UR7.2",
        "SR19.50_GA_AT2200",
        "SR19.50_UR1",
        "SR19_50_UR1",
        "SR20.00 GA",
        "SR20_00 GA",
        "SVG_SR19.50_GA",
        "SVG_SR19.50_ROW",
        "SVG_SR19.50_UR1",
        "SVG_SR19_50_ROW",
        "SVG_SR19_50_UR1",
        "SVG_SR20.00 GA",
        "SVG_SR20_00 GA"
    ]

    d = {}
    for _ur_version in ur_version_list:
        d |= x.read_from_file(ur_version=_ur_version)

    for k, v in d.items():
        for doc in v:
            elk_reporter.fill_list_of_docs(
                index_name='new_dashboard_results_feature_test_details_production_ng',
                doc=doc
            )

    elk_reporter.set_list_of_docs()
    print()


if __name__ == '__main__':
    main_1()
    main_2()
