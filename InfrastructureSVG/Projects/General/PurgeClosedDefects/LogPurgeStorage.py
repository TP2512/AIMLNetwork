import logging
from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import GeneralFolderActionClass
from InfrastructureSVG.Network_Infrastructure.Send_Outlook_Mail_Infrastructure import SendOutlookMailClass
import datetime
import pandas as pd
import win32api
import win32con
import os



class LogPurgeStorage:
    def __init__(self, debug_flag, purge_folder_path_list, MAIL_RECIPIENTS):
        self.logger = \
            logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)

        self.purge_folder_path_list = purge_folder_path_list
        self.purge_folder_dict_list = []
        self.KB_to_GB = 1 / 1024 / 1024 / 1024
        self.KB_to_MB = 1 / 1024 / 1024
        for purged_folder_path in purge_folder_path_list:
            purge_folder_dict = {
                'purged_folder_path': purged_folder_path,
                'folder_size_before_purge': GeneralFolderActionClass().get_folder_size(purged_folder_path),
                'free_space_before_purge': GeneralFolderActionClass().get_drive_free_space(purged_folder_path),
                'free_space_after_purge': None
            }
            self.purge_folder_dict_list.append(purge_folder_dict)
            self.average_defect_storage_size = None
        self.percent_oversize = 50
        self.sendOutlookMailClass = SendOutlookMailClass()
        self.smtp_server_name = "mail.airspan.com"
        self.sender = "Automation_Dev_SVG@airspan.com"
        if debug_flag:
            self.receives = ['rblumberg@airspan.com']
        else:
            self.receives = MAIL_RECIPIENTS
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.mail_subject = f"This is a run summary from the PurgeClosedDefects script that was run at {now_str}"
        self.mail_body = ""
        self.mail_body_1 = ""
        self.mail_body_2 = ""
        self.mail_body_3 = ""
        self.mail_body_4 = ""
        self.mail_body_5 = ""
        self.mail_body_6 = ""
        self.excel_purge_log_file_path = r'\\fs4\PRT_Attachments\PurgeClosedDefectsScript-PurgeLog\purge_excel_log.xlsx'

    def log_disk_usage(self):
        """ log amount of space freed
        """
        message = ''
        for purge_folder_dict in self.purge_folder_dict_list:
            message += f"________________________________________\n"
            message += f"summary for folder {purge_folder_dict['purged_folder_path']}:\n"
            purge_folder_dict['folder_size_after_purge'] = GeneralFolderActionClass().get_folder_size(purge_folder_dict['purged_folder_path'])
            purge_folder_dict['free_space_after_purge'] = GeneralFolderActionClass().get_drive_free_space(purge_folder_dict['purged_folder_path'])
            space_freed = round((purge_folder_dict['folder_size_before_purge'] - purge_folder_dict['folder_size_after_purge']), 2)
            if space_freed > 0:
                message += f"Disk space freed for the folder is: {round(space_freed * self.KB_to_GB, 2)} GB.\n"
            else:
                message += f"No Disk space freed for the folder.\n"
            message += f"Currently free space for the drive of the folder is: {round(purge_folder_dict['free_space_after_purge'], 2)} GB."
            message += '\n'
        self.mail_body_2 += f'{message}'
        self.logger.info(message)

    def calculate_average_defect_storage_size(self, purged_folder_chunks_list):
        num_of_defects = 0
        total_storage_size = 0
        for purged_folder_chunk_list in purged_folder_chunks_list:
            for defect_dict in purged_folder_chunk_list:
                total_storage_size += defect_dict['defect_dir_storage_size']
                num_of_defects += 1
        self.average_defect_storage_size = total_storage_size/num_of_defects

    def get_oversized_defect_folders(self, purged_folder_chunks_list):
        oversized_defect_folders = []
        oversized_storage_size = self.average_defect_storage_size * ((100 + self.percent_oversize) / 100)
        for purged_folder_chunk_list in purged_folder_chunks_list:
            for defect_dict in purged_folder_chunk_list:
                if defect_dict['defect_dir_storage_size'] > oversized_storage_size:
                    oversized_defect_folders.append(defect_dict)
        return oversized_defect_folders

    def log_oversized_defect_folders(self, purged_folder_chunks_list):
        oversized_defect_folders = self.get_oversized_defect_folders(purged_folder_chunks_list)
        oversized_defect_folders_path_str = ""
        for defect_dict in oversized_defect_folders:
            oversized_defect_folders_path_str += f"\t - {defect_dict['defect_dir_path']}\n"

        if oversized_defect_folders_path_str:
            message = "________________________________________\n"
            if oversized_defect_folders_path_str != '':
                message += f"\nThe following folders are oversized by {self.percent_oversize} percent from the average defect size of " \
                          f"{round(self.average_defect_storage_size * self.KB_to_MB, 2)} MB:\n{oversized_defect_folders_path_str}"
            else:
                message += "There are no oversized folders."
            self.logger.info(message)
            self.mail_body_5 += message
        else:
            message = f'There are no oversized folders larger then {self.percent_oversize} percent from average defect size of ' \
                      f'{round(self.average_defect_storage_size * self.KB_to_MB, 2)} MB.\n'
            self.logger.info(message)
            self.mail_body_5 += message

    def log_delete_errors(self, error_list):
        error_str = "________________________________________\n"
        error_str += "The following folders haven't been deleted due to an error:\n"
        for error_dict in error_list:
            error_str += f"\t - {error_dict['purged_folder']}, error reason: {error_dict['purged_reason']}\n"
            self.logger.info(error_str)
            self.mail_body_6 += error_str

    def purge_operation_output(self, purged_folder_chunks_list,
                               removed_empty_folders_list,
                               removed_closed_old_defect_folders_list,
                               error_list):
        self.log_disk_usage()
        self.log_oversized_defect_folders(purged_folder_chunks_list)
        self.log_delete_errors(error_list)
        self.save_to_excel(removed_empty_folders_list, removed_closed_old_defect_folders_list, error_list)

    def save_to_excel(self, removed_empty_folders_list, removed_closed_old_defect_folders_list, error_list):
        if GeneralFolderActionClass().check_path_exist(self.excel_purge_log_file_path):
            win32api.SetFileAttributes(self.excel_purge_log_file_path, win32con.FILE_ATTRIBUTE_NORMAL)
            current_dataframe = pd.read_excel(self.excel_purge_log_file_path)
            current_dataframe.drop(columns=['id'], inplace=True)
            removed_empty_folders_list_df = pd.DataFrame(removed_empty_folders_list)
            removed_closed_old_defect_folders_list_df = pd.DataFrame(removed_closed_old_defect_folders_list)
            error_list_df = pd.DataFrame(error_list)
            df = pd.concat([current_dataframe, removed_empty_folders_list_df, removed_closed_old_defect_folders_list_df, error_list_df], ignore_index=True)
            df.index.name = 'id'
            df.index += 1
            df.to_excel(self.excel_purge_log_file_path, header=True)
            win32api.SetFileAttributes(self.excel_purge_log_file_path, win32con.FILE_ATTRIBUTE_READONLY)
        else:
            removed_empty_folders_list_df = pd.DataFrame(removed_empty_folders_list)
            removed_closed_old_defect_folders_list_df = pd.DataFrame(removed_closed_old_defect_folders_list)
            df = pd.concat([removed_empty_folders_list_df, removed_closed_old_defect_folders_list_df], ignore_index=True)
            df.index.name = 'id'
            df.index += 1
            df.to_excel(self.excel_purge_log_file_path, header=True)
            win32api.SetFileAttributes(self.excel_purge_log_file_path, win32con.FILE_ATTRIBUTE_READONLY)

    # def save_excel_log(self, removed_empty_folders_list, removed_closed_old_defect_folders_list):
    #     try:
    #         workbook = load_workbook(self.excel_purge_log_file_path)
    #         start_row = workbook['Sheet1'].max_row
    #         workbook.close()
    #         excel_writer = pd.ExcelWriter(self.excel_purge_log_file_path, engine='openpyxl')
    #         if len(removed_empty_folders_list):
    #             removed_empty_folders_list_df = pd.DataFrame(removed_empty_folders_list)
    #             removed_empty_folders_list_df.to_excel(excel_writer, sheet_name='Sheet1', startrow=start_row, index=False, header=False)
    #         if len(removed_closed_old_defect_folders_list):
    #             removed_closed_old_defect_folders_list_df = pd.DataFrame(removed_closed_old_defect_folders_list)
    #             removed_closed_old_defect_folders_list_df.to_excel(excel_writer, sheet_name='Sheet1', startrow=start_row, index=False, header=False)
    #         workbook.close()
    #     except Exception:
    #         self.logger.exception('unable to write to excel file')

    def send_run_summary_mail(self, debug_flag):
        self.mail_body_3 = f"________________________________________\n"
        if debug_flag:
            if self.mail_body_4 != '':
                self.mail_body_3 += f'This is a test run, in a production run the following folders would have been removed:\n'
            else:
                self.mail_body_3 += f'No folders have been removed.\n'
        else:
            if self.mail_body_4 != '':
                self.mail_body_3 += f'The following folders have been removed:\n'
            else:
                self.mail_body_3 += f'No folders have been removed.\n'
        self.mail_body = f'{self.mail_body_1}{self.mail_body_2}{self.mail_body_3}{self.mail_body_4}{self.mail_body_5}{self.mail_body_6}'
        self.sendOutlookMailClass.send_outlook_mail(self.smtp_server_name, None, None, self.sender, self.receives, self.mail_subject, self.mail_body)
        self.logger.info("A summary mail message have been sent")
