import contextlib
import logging
from typing import Union

import requests
import json
import re
from bs4 import BeautifulSoup


class ACPInfra:
    def __init__(self, acp_name: str, username: str, password: str, use_ssl: bool = False):
        self.logger = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)

        self.username = username
        self.password = password

        self.acp_name = acp_name

        self.url_api = f'https://{self.acp_name}'
        self.url_swagger_api = f'{self.url_api}/swagger/index.html'

        self.use_ssl = use_ssl
        self.header = {'Content-Type': 'application/json-patch+json'}

        self.acp_token = None
        self.sr_version = None

        self.get_acp_token()
        self.get_sr_version()

    def get_acp_token(self):
        """
        This function responsible provide token key for ACP REST API
        """
        try:
            url = f'https://{self.acp_name}/api/authenticate'
            body = '{' + f'"username": "{self.username}", "password": "{self.password}"' + '}'
            rest_method_response = requests.post(url, data=body, headers=self.header, verify=self.use_ssl)

            self.acp_token = rest_method_response.text
            if self.acp_token:
                # self.header = {'x-Authorization': self.acp_token, 'Content-Type': 'Content-Type = application/json'}
                self.header = {"X-Authorization": self.acp_token, "Content-Type": "application/json-patch+json"}
            else:
                raise Exception('ACP token is None')
        except Exception as e:
            raise Exception('ACP token is None') from e

    def get_sr_version(self):
        try:
            response = requests.get(self.url_swagger_api, headers=self.header, verify=False)

            object_response = response.text
            soup = BeautifulSoup(object_response, features="html.parser")
            rest_version_list_ = re.findall('(?<=swagger/)(.*?)(?=/swagger.json)', soup.prettify())
            rest_version_list = []
            for ver in rest_version_list_:
                with contextlib.suppress(ValueError):
                    float(ver)
                    rest_version_list.append(ver)
            self.sr_version = max(rest_version_list, default=None)
            if not self.sr_version:
                raise Exception('SR version is None')
        except Exception as e:
            raise Exception('SR version is None') from e

    def get_gnb_details(self, gnb_name: str) -> Union[dict, None]:
        response = requests.get(f'https://{self.acp_name}/api/{self.sr_version}/gnb?name={gnb_name}', headers=self.header, verify=self.use_ssl)
        if response.status_code == 200:
            gnb_response = json.loads(response.text)[0]
            entities_data = {'gnb_name': gnb_response['nodeProperties']['name']}
            for k, v in gnb_response['associateNetworkFunctions'].items():
                if k == 'gnbCuCp':
                    for i in range(len(v)):
                        entities_data[k] = {
                            'managedElementId': v[i]['cuCpProperties']['managedElementId'],
                            'ip_address': v[i]['netconfProperties']['ipAddress'],
                            'productType': v[i]['cuCpProperties']['productType'],
                            'productCode': v[i]['cuCpProperties']['productCode'],
                        }
                elif k == 'gnbCuUp':
                    for i in range(len(v)):
                        entities_data[k] = {
                            'managedElementId': v[i]['cuUpProperties']['managedElementId'],
                            'ip_address': v[i]['netconfProperties']['ipAddress'],
                            'productType': v[i]['cuUpProperties']['productType'],
                            'productCode': v[i]['cuUpProperties']['productCode'],
                        }
                elif k == 'gnbDu':
                    for i in range(len(v)):
                        entities_data[k] = {
                            'managedElementId': v[i]['duProperties']['managedElementId'],
                            'ip_address': v[i]['netconfProperties']['ipAddress'],
                            'productType': v[i]['duProperties']['productType'],
                            'productCode': v[i]['duProperties']['productCode'],
                        }
                elif k == 'gnbRu':
                    for i in range(len(v)):
                        entities_data[k] = {
                            'managedElementId': v[i]['ruProperties']['managedElementId'],
                            'ip_address': v[i]['ruNetconfProperties']['ipAddress'],
                            'productType': v[i]['ruProperties']['productType'],
                            'productCode': v[i]['ruProperties']['productCode'],
                        }

                elif k == 'gnbXpu':
                    entities_data[k] = {
                        'managedElementId': v['xpuProperties']['managedElementId'],
                        'ip_address': v['netconfProperties']['ipAddress'],
                        'productType': v['xpuProperties']['productType'],
                        'productCode': v['xpuProperties']['productCode'],
                    }
            return entities_data
