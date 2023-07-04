import logging
import os
from datetime import datetime, timezone

from InfrastructureSVG.Files_Infrastructure.Actions_On_Files_And_Folders.Active_actions_files_and_folders import GeneralActionClass
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Tenable_Infrastructure.Tenable import Tenable, ExtractDetailsFromWeb
from InfrastructureSVG.Projects.General.TenableScanAndReport.TenableDefect import OpenOrUpdateDefect


def create_folder(folder_path, sub_folder):
    check_if_directory_exist_t_f_ = GeneralActionClass().check_if_directory_exist(f'{folder_path}\\{sub_folder}')
    folder_path = f'{folder_path}\\{sub_folder}'
    if not check_if_directory_exist_t_f_:
        os.system(f'mkdir {folder_path}')


class TenableProcess:
    def __init__(self):
        self.logger = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)

    def tenable_process(self, node_name, ip_address, site, tenable_scanner_name, username, password, credential_type, folder_path='\\\\192.168.127.247\\TenableScans',
                        severity=None, defect_parameters_dict=None, scan_id=None):
        if not severity:
            severity = ['Critical', 'High', 'Medium', 'Low', 'Info']

        current_date = datetime.strftime(datetime.today(), "%Y_%m_%d")
        create_folder(folder_path=folder_path, sub_folder=current_date)

        folder_node_name = node_name.replace(' ', '_').replace('.', '_').replace(':', '_')
        create_folder(folder_path=folder_path, sub_folder=f"{current_date}\\{folder_node_name}")

        download_to_path_pdf = f'{folder_path}\\{current_date}\\{folder_node_name}\\{folder_node_name}.pdf'
        download_to_path_csv = f'{folder_path}\\{current_date}\\{folder_node_name}\\{folder_node_name}.csv'
        download_to_path_html = f'{folder_path}\\{current_date}\\{folder_node_name}\\{folder_node_name}.html'

        tenable_client = Tenable()

        # Start connection
        tenable_client.tenable_connection()

        if not scan_id:
            # Build and start the scan
            scan_id = tenable_client.build_and_start_scan(
                node_name=node_name,
                ip_address=ip_address,
                tenable_scanner_name=tenable_scanner_name,
                username=username,
                password=password,
                credential_type=credential_type
            )
        self.logger.info(f'The scan_id is: {scan_id}')
        tenable_client.wait_until_scan_finish(scan_id=scan_id, hour_time_to_wait=10)  # 0.001 for 3.6 sec ; 10 for 10 hours

        tenable_client.download_report_as_pdf(scan_id=scan_id, download_to_path=download_to_path_pdf)
        tenable_client.download_report_as_csv(scan_id=scan_id, download_to_path=download_to_path_csv)
        tenable_client.download_report_as_html(scan_id=scan_id, download_to_path=download_to_path_html)

        scan_details = tenable_client.get_scan_details(scan_id)

        severity_list = ['critical', 'high', 'medium', 'low', 'info']
        severity_details = {severity_name: 0 for severity_name in severity_list}
        for vulnerability in scan_details.vulnerabilities:
            for severity_name in severity_list:
                if tenable_client.get_severity_name_by_id(vulnerability['severity']).lower() == severity_name:
                    severity_details[severity_name] += 1

        plugin_id_to_defect = {}
        defects_dict = {'new_defects_list': [], 'existing_defects_list': []}
        for severity_obj in scan_details.vulnerabilities:
            plugin_name = severity_obj['plugin_name']
            plugin_id = severity_obj['plugin_id']
            severity_id = severity_obj['severity']
            severity_name = tenable_client.get_severity_name_by_id(severity_id=severity_id)
            if severity_name not in severity:
                continue

            extract_details_from_web_output = ExtractDetailsFromWeb()
            extract_details_from_web_output.process(node_name=node_name, severity_name=severity_name, plugin_id=plugin_id, plugin_name=plugin_name)
            description = f'URL: https://www.tenable.com/plugins/nessus/{plugin_id}\n{extract_details_from_web_output.output}'

            # open defect
            open_defect = OpenOrUpdateDefect(
                summary=plugin_name,
                label=plugin_id,
                site=site,
                severity=severity_name,
                description=description,
                folder_path=download_to_path_pdf,
                defect_parameters_dict=defect_parameters_dict
            )
            defect = open_defect.found_or_create_defect()
            defects_dict[f'{list(defect.keys())[0]}s_list'].append(defect.get(list(defect.keys())[0]))

            plugin_id_to_defect[plugin_id] = defect.get(list(defect.keys())[0])

        return defects_dict, download_to_path_pdf, download_to_path_csv, severity_details, plugin_id_to_defect

    def link_def_to_testsir_and_testplan(self, test_plan_id, test_sir, defects_dict):
        jira_client = JiraActions()
        for k, v in defects_dict.items():
            for def_number in v:
                try:
                    jira_client.create_issue_link(project='created', link_from_issue=test_plan_id, link_to_issue=def_number)
                    self.logger.info(f'link test_plan_id: {test_plan_id} to def_number: {def_number} was successful')
                except Exception as err:
                    self.logger.exception('')
                    self.logger.info(f'link test_plan_id: {test_plan_id} to def_number: {def_number} was not successful')

                try:
                    jira_client.create_issue_link(project='created', link_from_issue=test_sir, link_to_issue=def_number)
                    self.logger.info(f'link test_sir: {test_sir} to def_number: {def_number} was successful')
                except Exception as err:
                    self.logger.exception('')
                    self.logger.info(f'link test_sir: {test_sir} to def_number: {def_number} was not successful')
