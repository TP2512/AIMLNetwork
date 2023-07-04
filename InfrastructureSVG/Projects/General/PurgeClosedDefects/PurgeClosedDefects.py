import os
import shutil
from LogPurgeStorage import LogPurgeStorage
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import GeneralFolderActionClass
from datetime import datetime, timezone
from datetime import timedelta
import pathlib
import logging


class PurgeClosedDefects:

    def __init__(self, purged_folders_path_list, MAIL_RECIPIENTS):
        self.logger = \
            logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)
        self.debug_flag = False
        self.purged_folders_path_list = purged_folders_path_list
        self.validate_purged_folders_exist(self.purged_folders_path_list)
        self.defects_chunk_size = 50
        self.jira_client = JiraActions()
        self.logStorage = LogPurgeStorage(self.debug_flag, purged_folders_path_list, MAIL_RECIPIENTS)
        purged_folders_path_list_str = ""
        for purged_folder_path in purged_folders_path_list:
            purged_folders_path_list_str += f'\t - {purged_folder_path} \n'
        message = f"The following folder paths are about to be purged:\n{purged_folders_path_list_str}"
        self.logStorage.mail_body_1 = f'{message}\n'
        self.logger.info(message)
        now_datetime = datetime.now(timezone.utc)
        two_weeks_ago_date = now_datetime - timedelta(days=14)
        self.two_weeks_ago_date = two_weeks_ago_date
        self.two_weeks_ago_date_str = two_weeks_ago_date.strftime('%Y-%m-%d')

    def validate_purged_folders_exist(self, purged_folders_path_list):
        for purged_folders_path in purged_folders_path_list:
            if not os.path.exists(purged_folders_path):
                self.logger.error("One of the purged folder doesn't exist")
                raise OSError("One of the purged folder doesn't exist")

    def get_defect_chunks(self, operation_start_time):
        removed_empty_folders_list = []
        purged_folder_chunks_list = []
        for purged_folder_path in self.purged_folders_path_list:
            defects_chunk_list = []
            for dir_path in os.listdir(purged_folder_path):
                defect_dir_path = os.path.join(purged_folder_path, dir_path)
                if os.path.isdir(defect_dir_path):
                    defect_dir_storage_size = GeneralFolderActionClass().get_folder_size(defect_dir_path)
                    if defect_dir_storage_size != 0:
                        if dir_path.upper().startswith('DEF-'):
                            if len(defects_chunk_list) < 50:
                                defect_dict = {'defect_name': dir_path,
                                               'defect_dir_path': defect_dir_path,
                                               'defect_dir_storage_size': defect_dir_storage_size,
                                               'purged_folder_path': purged_folder_path
                                               }
                                defects_chunk_list.append(defect_dict)
                            else:
                                purged_folder_chunks_list.append(defects_chunk_list)
                                defects_chunk_list = []
                    else:
                        pathlib_defect_dir_path = pathlib.Path(defect_dir_path)
                        last_modified_date = datetime.fromtimestamp(pathlib_defect_dir_path.stat().st_mtime)
                        if last_modified_date < self.two_weeks_ago_date:
                            if dir_path != 'Thumbs.db':
                                self.remove_defect_folder(defect_dir_path)
                                removed_empty_folders_list.append({'purged_folder': defect_dir_path,
                                                                   'purged_reason': "empty folder that hasn't been modified in the last two weeks",
                                                                   'operation_start_date': operation_start_time.date().strftime('%Y-%m-%d'),
                                                                   'operation_start_time': operation_start_time.time().strftime('%H:%M:%S')})
            purged_folder_chunks_list.append(defects_chunk_list)
        return purged_folder_chunks_list, removed_empty_folders_list

    def filter_and_delete_folder_by_chunk_by_status_closed(self, purged_folders_chunks_list, operation_start_time):
        removed_closed_old_defect_folders_list = []
        error_list = []
        filtered_defects_chunks_list = []
        for defects_chunk_list in purged_folders_chunks_list:
            defects_str = ""
            for defect_dict in defects_chunk_list:
                defects_str += defect_dict['defect_name'] + ','
            defects_str = defects_str[0:-1]
            filter_str = f"project = DEF AND issuetype = Defect AND status = Closed AND updated < {self.two_weeks_ago_date_str} AND Issuekey in ({defects_str})"
            filtered_defects = self.jira_client.search_by_filter(filter_str)
            if filtered_defects is not None:
                for filtered_defect in filtered_defects:
                    # if filtered_defect.key == 'DEF-36053':
                    defect_dict = self.find_defect_dict(defects_chunk_list, filtered_defect)
                    if defect_dict:
                        delete_success, exception_name = self.remove_defect_folder(defect_dict['defect_dir_path'])
                        if delete_success:
                            removed_closed_old_defect_folders_list.append({'purged_folder': defect_dict['defect_dir_path'],
                                                                           'purged_reason': 'closed defect with update date older than two weeks',
                                                                           'operation_start_date': operation_start_time.date().strftime('%Y-%m-%d'),
                                                                           'operation_start_time': operation_start_time.time().strftime('%H:%M:%S')})
                        else:
                            if exception_name == 'PermissionError':
                                error_list.append({'purged_folder': defect_dict['defect_dir_path'],
                                                   'purged_reason': f'A Permission Error has occurred',
                                                   'operation_start_date': operation_start_time.date().strftime('%Y-%m-%d'),
                                                   'operation_start_time': operation_start_time.time().strftime('%H:%M:%S')})
                            else:
                                error_list.append({
                                                      'purged_folder'       : defect_dict['defect_dir_path'],
                                                      'purged_reason'       : f'An Input output Error has occurred (A file might have been opened.',
                                                      'operation_start_date': operation_start_time.date().strftime('%Y-%m-%d'),
                                                      'operation_start_time': operation_start_time.time().strftime('%H:%M:%S')
                                                      })
        return filtered_defects_chunks_list, removed_closed_old_defect_folders_list, error_list

    @staticmethod
    def find_defect_dict(defects_chunk_list, filtered_defect):
        for defect_dict in defects_chunk_list:
            if defect_dict['defect_name'] == filtered_defect.key:
                return defect_dict

    def remove_defect_folder(self, folder):
        message = f'\t\t - {folder}'
        self.logger.info(message)
        if self.debug_flag:
            pass
        else:
            try:
                shutil.rmtree(folder)
                self.logStorage.mail_body_4 += f'{message}\n'
                return True, None
            except PermissionError:
                self.logger.warning(f"unable to delete folder: {folder}, PermissionError")
                return False, 'PermissionError'
            except IOError:
                self.logger.warning(f"unable to delete folder: {folder}, IOError")
                return False, 'IOError'

