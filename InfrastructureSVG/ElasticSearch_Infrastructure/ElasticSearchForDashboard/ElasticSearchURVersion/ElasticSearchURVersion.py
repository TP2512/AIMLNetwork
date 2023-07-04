import logging
from copy import deepcopy
from datetime import datetime, timezone
from elasticsearch import helpers
from elasticsearch_dsl import Search

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchHelper
from InfrastructureSVG.Jira_Infrastructure.GetTestListPerURVersion import GetTestListPerURVersion


class ElasticSearchURVersion:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch()
        # self.elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch_dev()

    @staticmethod
    def fill_list_of_docs(list_of_docs, index_name, doc):
        list_of_docs.append(
            {
                "_index": index_name,
                "_source": deepcopy(doc)
            }
        )

    @staticmethod
    def fill_details_doc_old(test_plan_key, test_key, automation_manual, ur_version):
        return {
            "timestamp": datetime.now(timezone.utc),

            "automation_manual": automation_manual,
            "ur_version": ur_version,

            "test_plan_key_per_ur_version": test_plan_key,
            "test_key_per_ur_version": test_key,

            "scenario_status": ['PASS', 'FAIL', 'AUTOMATION_FAIL'],
            "gnb_test_execution_status": ['PASS', 'FAIL', 'AUTOMATION_FAIL'],

            "test_plan": None,
            "test_sir": None,

            "test_plan_2": f'{test_plan_key}',
            "test_sir_2": f'{test_key}',
            "test_plan_and_test_sir_2": f'{test_plan_key} + {test_key}',

            "test_plan_and_test_sir_per_ur_version": f'{test_plan_key} + {test_key}',

            "test_run_time": 1
        }

    @staticmethod
    def fill_details_doc(automation_manual, ur_version, env_config_obj, test_obj, test_set_list, test_plan_list, slave_name_list, test_execute):
        return {
            "timestamp": datetime.now(timezone.utc),

            "automation_manual": automation_manual,
            "ur_version": ur_version,

            "environment_config_per_ur_version": env_config_obj.key,
            "environment_config_per_ur_version_summary": env_config_obj.fields.summary,
            "test_per_ur_version": test_obj.key,
            "test_per_ur_version_summary": test_obj.fields.summary,
            "environment_config_and_test_sir_per_ur_version": f'{env_config_obj.key} - {test_obj.key}',
            "environment_config_and_test_per_ur_version_summary": f'{env_config_obj.fields.summary} - {test_obj.fields.summary}',
            "feature_name": test_obj.fields.customfield_11801,
            "feature_group_name": test_obj.fields.customfield_19601,

            "test_set_per_ur_version_list": test_set_list,
            "test_plan_list_per_ur_version": test_plan_list,
            "slave_name_list_per_ur_version": slave_name_list,
            "slave_name": slave_name_list,

            "scenario_status": ['PASS', 'FAIL', 'AUTOMATION_FAIL'],
            "gnb_test_execution_status": ['PASS', 'FAIL', 'AUTOMATION_FAIL'],

            "test_plan": None,
            "test_sir": None,

            "test_run_time": 1,
            "test_execute": test_execute,
        }

    def build_new_ur_version_on_elk(self, ur_version, manual=False, set_list_of_existing_docs=None):
        get_ur_versions_ins = GetTestListPerURVersion(ur_version=ur_version)
        get_ur_versions_ins.get_automation_test_list_per_ur_versions_per_env_config()
        if manual:
            get_ur_versions_ins.get_manual_test_list_per_ur_versions()
            automation_manual_name_list = ['automation_test_list', 'manual_test_list']
        else:
            automation_manual_name_list = ['automation_test_list']

        for name in automation_manual_name_list:
            count = 0
            list_of_docs_ = []
            for env_config_k, env_config_v in get_ur_versions_ins.test_list[name].items():
                if not env_config_v:
                    continue

                for test_obj in env_config_v['SIR']:
                    # if f"{env_config_v['environment_config'].key} - {test_obj.key}" not in set_list_of_existing_docs or f"None - {test_obj.key}" not in set_list_of_existing_docs:
                    #     print()

                    count += 1
                    self.fill_list_of_docs(
                        list_of_docs=list_of_docs_,
                        index_name='new_dashboard_results_ur_versions_production_ng',
                        doc=self.fill_details_doc(
                            # test_plan_key=test_plan_k.key,
                            # test_key=test_k,
                            automation_manual=name.split('_')[0].title(),
                            ur_version=ur_version.replace('.', '_'),
                            env_config_obj=env_config_v['environment_config'],
                            test_obj=test_obj,
                            test_set_list=[test_set.key for test_set in env_config_v['TEST-SET'][test_obj.key]],
                            test_plan_list=[test_plan.key for test_plan in env_config_v['test_plan_obj'][test_obj.key]],
                            slave_name_list=list(env_config_v['slave_name_per_test_set'][test_obj.key]),
                            # test_execute=f"{env_config_v['environment_config'].key} - {test_obj.key}" in set_list_of_existing_docs,
                            test_execute=f"{env_config_v['environment_config'].key} - {test_obj.key}" in set_list_of_existing_docs or f"None - {test_obj.key}" in set_list_of_existing_docs,
                        )
                    )

            self.logger.info(f'The count for {name} is: {count}')
            if list_of_docs_:
                self.logger.info('Start to report the documents to ELK')
                ElasticSearchHelper().change_elasticsearch_logger()
                helpers.bulk(self.elk_client, list_of_docs_)

    def search_for_test_plan(self, ur_version, test_plan):
        try:
            s = Search(index='new_dashboard_results_feature_details_production_ng', using=self.elk_client)
            return s.filter('match', ur_version=ur_version).extra(size=10000).query('match', test_plan=test_plan).extra(size=1000).execute()
        except Exception:
            self.logger.exception('')

    def search_by_automation_manual_and_ur_version(self, automation_manual, ur_version):
        try:
            s = Search(index='new_dashboard_results_ur_versions_production_ng', using=self.elk_client)
            return s.filter('match', ur_version=ur_version).extra(size=10000).query('match', automation_manual=automation_manual).extra(size=1000).execute()
        except Exception:
            self.logger.exception('')

    def delete_by_automation_manual_and_ur_version(self, automation_manual, ur_version):
        try:
            s = Search(index='new_dashboard_results_ur_versions_production_ng', using=self.elk_client)
            # s = Search(index='new_dashboard_results_*_production_ng', using=self.elk_client)
            return s.filter('match', ur_version=ur_version).extra(size=10000).query('match', automation_manual=automation_manual).extra(size=1000).delete()
        except Exception:
            self.logger.exception('')

    def delete_automation_ur_version(self, ur_version):
        self.delete_by_automation_manual_and_ur_version(automation_manual='Automation', ur_version=ur_version)

    def delete_manual_ur_version(self, ur_version):
        self.delete_by_automation_manual_and_ur_version(automation_manual='Manual', ur_version=ur_version)

    def delete_automation_and_manual_ur_version(self, ur_version):
        self.delete_automation_ur_version(ur_version=ur_version)
        self.delete_manual_ur_version(ur_version=ur_version)

    def get_existing_docs(self, ur_version, automation_manual='Automation'):
        try:
            s = Search(index='new_dashboard_results_*_production_ng', using=self.elk_client)
            # s = Search(index='new_dashboard_results_*_production_ng', using=self.elk_client)
            return s.filter('match', ur_version=ur_version).extra(size=10000).query('exists', field='execute_environment_config_and_test_sir').extra(size=1000).execute()
        except Exception:
            self.logger.exception('')
