import logging
import os
import json
import shutil
import jira
import re

from InfrastructureSVG.Files_Infrastructure.Actions_On_Files_And_Folders.Active_actions_files_and_folders import GeneralActionClass
from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import GeneralFolderActionClass
from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import get_basic_field_list
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX


class DeletePerCloseDefect:
    def __init__(self, app_credentials: str = 'TestspanAuto'):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = JiraActions(app_credentials=app_credentials)
        self.create_object_on_jira = CreateObjectOnJira(jira_client=self.jira_client)

    def get_defects_dict(self, defect: [str, jira.resources.Issue]):
        defects_dict = {'defects_open': [], 'all_defects_dict': {}, 'defects_list': []}
        if type(defect) == str:
            defects_dict = self.create_object_on_jira.get_open_defects_include_links(defect_str=defect, defects_dict=defects_dict)
        else:
            defects_dict = self.create_object_on_jira.get_open_defects_include_links(defect_str=defect.key, defects_dict=defects_dict)

        json_to_print = {"defects_open": defects_dict["defects_open"], "all_defects_dict": list(defects_dict["all_defects_dict"].keys())}
        self.logger.info(f'defects_dict is: \n{json.dumps(json_to_print, sort_keys=True, indent=4, separators=(",", ": "))}')

        return defects_dict

    @staticmethod
    def get_defects_list_from_defects_folder(path):
        r""" Defects folder: \\192.168.127.231\Defects """

        folders = os.walk(path).__next__()[1]
        return [folder for folder in folders if 'DEF' in folder.upper()]

    def delete_defects_from_defects_folder(self, path='\\\\192.168.127.231\\Defects', debug=True):
        defects_list = self.get_defects_list_from_defects_folder(path=path)
        self.logger.info(f'Len defects_list is: {len(defects_list)}')
        self.logger.info(f'def_folders_list is: {defects_list}')

        # regex = r'^DEF-(\d+)'
        # match = re.search(regex, defect_str)
        regex = r'^DEF-\d+$'
        for defect_str in defects_list:
            match = re.search(regex, defect_str)
            if not match:
                self.logger.error(f'DEF-number not match to standard. defect_str is: {defect_str}')
                continue

            try:
                defects_dict = self.get_defects_dict(defect=defect_str)
                if defects_dict['defects_open']:
                    continue

                for folder in list(defects_dict["all_defects_dict"].keys()):
                    full_path_folder = f'{path}\\{folder}'
                    if GeneralActionClass().check_if_directory_exist(full_path_folder):
                        if not debug:
                            try:
                                shutil.rmtree(full_path_folder)
                            except PermissionError:
                                self.logger.error('PermissionError')
                                continue

                        self.logger.info(f'Delete {full_path_folder}')
                    else:
                        self.logger.debug(f'{full_path_folder} not exist')
            except Exception:
                self.logger.exception('')
                continue

    def delete_cores_from_core_server(self, debug=True):
        open_status_str = f"(status = {' and status != '.join(DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX)})"
        close_status_str = f"(status != {' and status != '.join(DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX)})"

        defects_list = self.jira_client.search_by_filter(f'project = DEF AND reporter in (CoreCare-5G) and {close_status_str}', fields=get_basic_field_list('customfield_12600'))
        self.logger.info(f'Len defects_list is: {len(defects_list)}')
        self.logger.info(f'defects_list is: {defects_list}')

        for defect_obj in defects_list:
            try:
                defects_dict = self.get_defects_dict(defect=defect_obj)
                if defects_dict['defects_open']:
                    continue

                for defect_object in list(defects_dict["all_defects_dict"].keys()):
                    inward_issue_list = [i.inwardIssue.key for i in defects_dict["all_defects_dict"][defect_object].fields.issuelinks if hasattr(i, 'inwardIssue')]
                    outward_issue_list = [i.outwardIssue.key for i in defects_dict["all_defects_dict"][defect_object].fields.issuelinks if hasattr(i, 'outwardIssue')]
                    epic_list = [i for i in inward_issue_list+outward_issue_list if 'core' in i.lower()]
                    if not epic_list or self.jira_client.search_by_filter(f"issue in linkedissues({epic_list[0]}) and {open_status_str}", fields=get_basic_field_list('customfield_12600')):
                        continue
                    cores_list = self.jira_client.search_by_filter(f'project = CoreCare AND issuetype = Core AND "Epic Link" = {epic_list[0]}', fields=get_basic_field_list('customfield_12600'))
                    for core in cores_list:
                        if GeneralFolderActionClass().check_path_exist(core.fields.customfield_12600):
                            if not debug:
                                try:
                                    os.remove(core.fields.customfield_12600)
                                except PermissionError:
                                    self.logger.error('PermissionError')
                                    continue
                            self.logger.info(f'Delete {core.fields.customfield_12600}')
                        else:
                            self.logger.debug(f'{core.fields.customfield_12600} not exist')
            except Exception:
                self.logger.exception('')
                continue
