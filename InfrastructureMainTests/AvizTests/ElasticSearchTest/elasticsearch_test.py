import logging
from copy import deepcopy
from datetime import datetime, timezone
from elasticsearch import helpers
from elasticsearch_dsl import Search

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchHelper
from InfrastructureSVG.Jira_Infrastructure.GetTestListPerURVersion import GetTestListPerURVersion


class FillURVersionOnELK:
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
    def fill_details_doc(test_key, automation_manual):
        return {
            "timestamp": datetime.now(timezone.utc),
            "ur_version": 'SR19.00_UR7.2',

            "automation_manual": automation_manual,
            "test_key_per_ur_version": test_key,
        }

    def build_new_ur_version_on_elk(self):
        get_ur_versions_ins = GetTestListPerURVersion()
        get_ur_versions_ins.get_automation_test_list_per_ur_versions()
        get_ur_versions_ins.get_manual_test_list_per_ur_versions()

        for name in ['automation_test_list', 'manual_test_list']:
            list_of_docs_ = []
            for test_key_ in get_ur_versions_ins.test_list[name]:
                self.fill_list_of_docs(
                    list_of_docs_,
                    'new_dashboard_results_ur_versions_production',
                    self.fill_details_doc(
                        test_key=test_key_,
                        automation_manual=name.split('_')[0].title()
                    )
                )

            if list_of_docs_:
                logger.info('Start to report the documents to ELK')
                ElasticSearchHelper().change_elasticsearch_logger()
                helpers.bulk(self.elk_client, list_of_docs_)

    def search_by_automation_manual_and_ur_version(self, client, automation_manual, ur_version):
        try:
            s = Search(index='new_dashboard_results_ur_versions_production', using=client)
            return s.filter('match', ur_version=ur_version).extra(size=10000).query('match', automation_manual=automation_manual).extra(size=1000).execute()
        except Exception:
            self.logger.exception('')

    def delete_by_automation_manual_and_ur_version(self, automation_manual, ur_version):
        try:
            s = Search(index='new_dashboard_results_ur_versions_production', using=self.elk_client)
            return s.filter('match', ur_version=ur_version).extra(size=10000).query('match', automation_manual=automation_manual).extra(size=1000).delete()
        except Exception:
            self.logger.exception('')

    @staticmethod
    def delete_automation_ur_version(ur_version):
        fill_ur_version_on_elk.delete_by_automation_manual_and_ur_version(automation_manual='Automation', ur_version=ur_version)

    @staticmethod
    def delete_manual_ur_version(ur_version):
        fill_ur_version_on_elk.delete_by_automation_manual_and_ur_version(automation_manual='Manual', ur_version=ur_version)

    def delete_automation_and_manual_ur_version(self, ur_version):
        self.delete_automation_ur_version(ur_version=ur_version)
        self.delete_manual_ur_version(ur_version=ur_version)


if __name__ == '__main__':
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger

    PROJECT_NAME = 'ELK Test'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    fill_ur_version_on_elk = FillURVersionOnELK()

    fill_ur_version_on_elk.build_new_ur_version_on_elk()

    print()

    fill_ur_version_on_elk.delete_automation_ur_version(ur_version='SR19.00_UR7.2')
    fill_ur_version_on_elk.delete_manual_ur_version(ur_version='SR19.00_UR7.2')

    print()

    fill_ur_version_on_elk.delete_automation_and_manual_ur_version(ur_version='SR19.00_UR7.2')

    print()
