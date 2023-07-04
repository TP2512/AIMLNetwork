import json
import logging
import yaml
from pandasticsearch import Select
from elasticsearch_dsl import Search

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging, print_before_logger


class Helper:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_yaml_dict_test(self, yaml_path):
        yaml_ = None
        try:
            with open(yaml_path) as yaml_file:
                yaml_ = yaml.load(yaml_file, Loader=yaml.FullLoader)
        except Exception as err:
            self.logger.error(err)
        return yaml_

    def get_data_from_elasticsearch(self, gnb_bundle):
        try:
            client = ElasticSearchConnection().connect_to_svg_elasticsearch()
            s = Search(using=client)

            response = s.filter('match_phrase', _index='robotautomationresults')
            for key_version, value_version in gnb_bundle.items():
                if value_version:
                    response = response.filter('match_phrase', **{key_version: value_version})
            return response.extra(size=5000).execute()
        except Exception:
            self.logger.exception('')

    def get_full_dataframe_per_bundle(self, gnb_bundle):
        try:
            response = self.get_data_from_elasticsearch(gnb_bundle)
            return Select.from_dict(response.to_dict()).to_pandas()
        except Exception:
            self.logger.exception('')


def main(project_name, site, dashboard_class):
    print_before_logger(project_name=project_name, site=site)
    logger = ProjectsLogging(project_name).project_logging(timestamp=True)

    helper = Helper()

    file_name = 'DashboardVersions.yaml'
    gnb_versions = helper.get_yaml_dict_test(yaml_path=r'\\fs4\DATA\SVG\Tools\Python Projects' + f'\\{file_name}')
    logger.debug(f'{file_name} is: \n'
                 f'{json.dumps(gnb_versions, indent=4, separators=(", ", " = "))}')

    for gnb_bundle_key, gnb_bundle_value in gnb_versions.items():
        if not gnb_bundle_value['Create Dashboard']:
            logger.debug(f'"Create Dashboard" on "{gnb_bundle_key}" is False => Continue')
            continue
        else:
            logger.debug(f'"Create Dashboard" on "{gnb_bundle_key}" is True => Start Running')
            logger.info(f'"{gnb_bundle_key}" is: \n'
                        f'{json.dumps(gnb_bundle_value, indent=4, separators=(", ", " = "))}')

        dataframe_org = helper.get_full_dataframe_per_bundle(gnb_bundle=gnb_bundle_value['Versions'])

        for dashboard in dashboard_class:
            try:
                dashboard(dataframe=dataframe_org).run_dashboard_main()
            except Exception:
                logger.exception('')
            print()
        print()
    print()
