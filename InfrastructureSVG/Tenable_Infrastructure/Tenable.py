import logging
import time
import requests
from bs4 import BeautifulSoup

from tenable_io.client import TenableIOClient
from tenable_io.api.credentials import CredentialPermission, CredentialRequest
from tenable_io.api.scans import ScanSettings, ScanCreateRequest, ScanCredentials, ScanExportRequest, ScanConfigureRequest
# from tenable_io.api.policies import PolicyCreateRequest, PolicyCreateRequest, PolicyCredentials


class Tenable:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.client = None

    def tenable_connection(
            self,
            access_key='ea9762885c0bd275c61c5f45decf366b516c2e7410b7f0ad39142724c27d2889',
            secret_key='0756cbd8ec03f1d27df7b7a7648938eca166a74dbd55ab7e93fea0752870ffbf'
    ):
        self.client = TenableIOClient(
            access_key=access_key,
            secret_key=secret_key
        )

    def get_scanner_id_by_name(self, tenable_scanner_name):
        scanners = {scanner.name: scanner.id for scanner in self.client.scanners_api.list().scanners}
        scanner = self.client.scanners_api.details(scanner_id=scanners[tenable_scanner_name])
        return scanner

    def get_template(self, template_name=None):
        if not template_name:
            template_name = 'advanced'
        return self.client.scan_helper.template(name=template_name)

    def get_policy(self, policy_name=None):
        if not policy_name:
            policy_name = 'SVG_5G_Full_TCP_UDP_AuditTrail'
        try:
            policy = [i for i in self.client.policies_api.list().policies if i.name == policy_name][0]
            return policy.id
        except Exception:
            return '1179'

    @staticmethod
    def get_ssh_credential_permission(user_permission, username, password):
        return CredentialRequest(
            name='Lab SSH',
            description='SSH Credentials for Lab',
            type_='SSH',
            settings={
                'auth_method': 'password',
                'elevate_privileges_with': 'Nothing',
                'username': username,
                'password': password
            },
            permissions=[user_permission]
        )

    def get_credential_permission(self, username, password, credential_type='SSH'):
        user = self.client.users_api.list().users[0]  # user with prev 64 (sem)
        user_permission = CredentialPermission(
            grantee_uuid=user.uuid,
            type=CredentialPermission.USER_TYPE,
            permissions=CredentialPermission.CAN_EDIT,
            name=user.username,
            isPending=True
        )

        if credential_type == 'SSH':
            credential_request = self.get_ssh_credential_permission(user_permission=user_permission, username=username, password=password)
        else:
            return None
        credential_uuid = self.client.credentials_api.create(credential_request)
        credential_detail = self.client.credentials_api.details(credential_uuid)
        return ScanCredentials(add=[credential_detail])

    def create_new_scan_name(self, node_name, ip_address, tenable_scanner_name, template_name=None, credentials=None):
        try:
            template = self.get_template(template_name)
            policy_id = self.get_policy()
            # policy_obj = self.client.policies_api.details(policy_id)

            settings = ScanSettings(
                name=node_name,
                text_targets=ip_address,
                scanner_id=self.get_scanner_id_by_name(tenable_scanner_name).id,
                policy_id=policy_id
            )
            scan_create_request = ScanCreateRequest(
                uuid=template.uuid,
                settings=settings,
                credentials=credentials
            )
            scan_id = self.client.scans_api.create(scan_create_request)
            # self.client.scans_api.configure(scan_id, ScanConfigureRequest(template.uuid, ScanSettings(
            #     name='test_2022_04_12__x',
            #     text_targets=ip_address,
            #     scanner_id=self.get_scanner_id_by_name(tenable_scanner_name).id,
            #     policy_id=policy_id)))
            self.client.scans_api.configure(
                scan_id, ScanCreateRequest(
                    uuid=template.uuid,
                    settings=settings,
                    credentials=credentials
                )
            )

            return scan_id
        except Exception:
            self.logger.exception('')

    def start_launch_existed_scan_name(self, scan_id, node_name):
        """This function starts Launch existing Scan names"""
        try:
            scan = self.client.scan_helper.id(scan_id)
            self.logger.info(f'Launch the candidate {node_name} is started!\n')
            scan.launch()
        except Exception:
            self.logger.exception('')

    def build_and_start_scan(self, node_name, ip_address, tenable_scanner_name, username=None, password=None, credential_type='SSH'):
        # Build credentials
        if username and password and credential_type:
            credentials = self.get_credential_permission(username=username, password=password, credential_type=credential_type)
        else:
            credentials = None

        # Build the scan
        scan_id = self.create_new_scan_name(
            node_name=node_name,
            ip_address=ip_address,
            tenable_scanner_name=tenable_scanner_name,
            credentials=credentials
        )

        # Start the scan
        self.start_launch_existed_scan_name(
            scan_id=scan_id,
            node_name=node_name
        )

        return scan_id

    def wait_until_scan_finish(self, scan_id, running_status=None, hour_time_to_wait=10):
        if not running_status:
            running_status = ['pending', 'running', 'resuming', 'processing', 'initializing']

        timeout = time.time() + 60 * 60 * hour_time_to_wait  # sec * min * hour

        self.logger.info('Waiting for the scan to complete')
        while self.client.scan_helper.id(scan_id).status() in running_status and time.time() < timeout:
            time.sleep(600)
            self.logger.info('Still waiting for the scan to complete')

    def download_report_as_pdf(self, scan_id, download_to_path):
        scan = self.client.scan_helper.id(scan_id)
        scan.download(download_to_path)

    def download_report_as_csv(self, scan_id, download_to_path):
        scan = self.client.scan_helper.id(scan_id)
        scan.download(download_to_path, format=ScanExportRequest.FORMAT_CSV)

    def download_report_as_html(self, scan_id, download_to_path):
        scan = self.client.scan_helper.id(scan_id)
        scan.download(download_to_path, format=ScanExportRequest.FORMAT_HTML)

    def get_scan_details(self, scan_id):
        scan = self.client.scan_helper.id(scan_id)
        return scan.details()

    @staticmethod
    def get_severity_name_by_id(severity_id):
        if severity_id == 0:
            return 'Info'
        elif severity_id == 1:
            return 'Low'
        elif severity_id == 2:
            return 'Medium'
        elif severity_id == 3:
            return 'High'
        elif severity_id == 4:
            return 'Critical'
        else:
            return 'NotFound'


class ExtractDetailsFromWeb:
    # def __init__(self, tenable_url, _key_terms, _extract_pdf_details):
    def __init__(self, tenable_url='https://www.tenable.com/plugins/nessus', _key_terms=r"Plugin Id"):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.tenable_url = tenable_url
        self.key_terms = _key_terms

        self.output = ''

    def get_beautiful_soup_list(self, plugin_id):
        html_response = requests.get(f'{self.tenable_url}/{plugin_id}')
        try:
            b_soup = BeautifulSoup(html_response.content, 'html.parser')
            try:
                b_soup_synopsis = b_soup("section", attrs={"class": "mb-3"})[0]  # Synopsis
            except Exception:
                self.logger.exception('')
                b_soup_synopsis = ''
            try:
                b_soup_description = b_soup("section", attrs={"class": "mb-3"})[1]  # Description
            except Exception:
                self.logger.exception('')
                b_soup_description = ''
            try:
                b_soup_solution = b_soup("section", attrs={"class": "mb-3"})[2]  # Solution
            except Exception:
                self.logger.exception('')
                b_soup_solution = ''
            return [b_soup_synopsis, b_soup_description, b_soup_solution]
        except Exception:
            self.logger.exception('')
            return []

    def process(self, node_name, severity_name, plugin_id, plugin_name):
        try:
            beautiful_soup_list = self.get_beautiful_soup_list(plugin_id)
            self.output = f'\n\n{plugin_id} - {plugin_name}:\n'
            for beautiful_soup_obj in beautiful_soup_list:
                if not beautiful_soup_obj:
                    continue
                self.output += f'{beautiful_soup_obj.contents[0].text}: \n' + '\n'.join(x.text for x in beautiful_soup_obj.find_all("span")) + '\n'
        except Exception:
            self.logger.exception(
                f"Severity is: {severity_name}\n"
                f"Plugin Id is: {plugin_id}\n"
                f"Name is: {node_name}\n"
            )
