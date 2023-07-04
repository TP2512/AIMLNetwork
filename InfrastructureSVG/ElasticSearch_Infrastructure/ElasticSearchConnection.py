import warnings
warnings.simplefilter("ignore", UserWarning)

from elasticsearch_dsl import connections
import time
import logging

from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials


class ElasticSearchArgumentMissing(Exception):
    pass


class ElasticSearchHelper:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    @staticmethod
    def change_elasticsearch_logger():
        tracer = logging.getLogger('elasticsearch')
        tracer.setLevel(logging.CRITICAL)  # or desired level
        # tracer.addHandler(logging.FileHandler('indexer.log'))


class ElasticSearchConnection:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.ELK_hostname = None
        self.elasticsearch_port = None
        self.kibana_port = None
        self.elasticsearch_url = None

    def _connect_to_elasticsearch(self, app_credentials=None):
        """
           This function responsible for creating a connection client to elasticSearch database

           The function return elasticSearch client
        """

        if not self.elasticsearch_url or not self.elasticsearch_port:
            raise ElasticSearchArgumentMissing('elasticsearch_url or elasticsearch_port is missing')

        c = 0
        while True:
            try:
                c = c + 1  # count
                if not app_credentials:
                    return connections.create_connection(hosts=[f'{self.elasticsearch_url}:{self.elasticsearch_port}'], timeout=20)
                username, password = Credentials().credentials_per_app(app_credentials)
                return connections.create_connection(hosts=[f'{self.elasticsearch_url}:{self.elasticsearch_port}'], http_auth=f'{username}:{password}', timeout=20, verify_certs=False) \
                    if 'https' in f'{self.elasticsearch_url}' else \
                    connections.create_connection(hosts=[f'{self.elasticsearch_url}:{self.elasticsearch_port}'], http_auth=f'{username}:{password}', timeout=20)

            except Exception:
                self.logger.exception('')
                if c > 10:
                    time.sleep(1800)
                time.sleep(20)

    def connect_to_testspan_elasticsearch(self):
        self.ELK_hostname = 'asil-svg-testspan'
        self.elasticsearch_port = 9200
        self.kibana_port = 5602
        self.elasticsearch_url = f'http://{self.ELK_hostname}'
        return self._connect_to_elasticsearch()

    def connect_to_svg_elasticsearch(self, elk_hostname=None):
        self.ELK_hostname = elk_hostname or '192.168.126.186'
        # self.ELK_hostname = elk_hostname or '172.20.63.186'
        self.elasticsearch_port = 9200
        self.kibana_port = 5601
        self.elasticsearch_url = f'https://{self.ELK_hostname}'
        return self._connect_to_elasticsearch(app_credentials='elasticsearch_production')

    def connect_to_svg_elasticsearch_dev(self, elk_hostname=None):
        self.ELK_hostname = elk_hostname or '192.168.126.187'
        # self.ELK_hostname = elk_hostname or '172.20.63.187'
        self.elasticsearch_port = 9200
        self.kibana_port = 5601
        self.elasticsearch_url = f'https://{self.ELK_hostname}'
        return self._connect_to_elasticsearch(app_credentials='elasticsearch_dev')
