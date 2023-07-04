import os
import time
import logging
import win32com.client as com

""" 
In this py file have 2 class
    - PathFoldersClass
    - GeneralFolderActionClass
"""


class GeneralFolderActionClass:
    """ This class ("GeneralFolderActionClass") responsible to do actions on folder """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def check_path_exist(self, folder_path: str):
        try:
            return bool(os.path.exists(folder_path))
        except Exception:
            self.logger.exception('')

    def check_path_exist_and_create(self, folder_path: str):
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                self.logger.info(f"created path: {folder_path}")
        except Exception:
            self.logger.exception('')

    def get_folder_size(self, folder_path: str):
        try:
            total_size = 0
            for dir_path, dir_names, file_names in os.walk(folder_path):
                for file_ in file_names:
                    fp = os.path.join(dir_path, file_)
                    total_size += os.path.getsize(fp)
            return total_size
        except Exception:
            self.logger.exception('')

    @staticmethod
    def get_drive_free_space(folder_path):
        """ Return the FreeSpace of a shared drive [GB]"""
        try:
            fso = com.Dispatch("Scripting.FileSystemObject")
            drv = fso.GetDrive(os.path.splitdrive(folder_path)[0])
            return drv.FreeSpace / 2 ** 30
        except Exception:
            return 0

    def get_folder(self, path: str):
        for dir_path, dir_names, file_names in os.walk(path):
            self.logger.info(f'The folders are: {dir_names}')
            if dir_names:
                for dir_name in dir_names:
                    if dir_name:
                        self.logger.info(dir_name)
                        return dir_name

        return None


class PathFoldersClass:
    """ This class ("PathFoldersClass") responsible for Folders related actions """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def return_to_username_path(self):
        """
        This function responsible to find the username path

        The function get 0 parameter:

        The function return 1 parameters:
            - "user_path" - the full path location (string type) till username folder
              (by user name),
                * for example: C:\\Users\\username
        """

        try:
            current_path = os.path.dirname(__file__)
            time.sleep(0.5)
            current_path = current_path.split('/')
            if len(current_path) < 2:
                current_path = os.path.dirname(__file__)
                time.sleep(0.5)
                current_path = str(current_path).split('\\')
            len_current_path = len(current_path) - 1
            user_path = ''
            for i in range(len_current_path):
                user_path = user_path + str(current_path[i]) + '\\'
                if 'Users' in user_path:
                    user_path = user_path + str(current_path[i + 1])
                    break
            return user_path if 'Users' in user_path else None
        except Exception:
            self.logger.exception('')
            return None

    def return_to_pycharm_root_path(self):
        """
        This function responsible to find the pycharm root path

        The function get 0 parameter: 

        The function return 1 parameters:
            - "pycharm_root_path" - the full path location (string type) till Pycharm folder
              (by user name),
                * for example: C:\\Users\\username\\PycharmProjects
        """

        try:
            current_path = os.path.dirname(__file__)
            time.sleep(0.5)
            current_path = current_path.split('/')
            if len(current_path) < 2:
                current_path = os.path.dirname(__file__)
                time.sleep(0.5)
                current_path = str(current_path).split('\\')
            len_current_path = len(current_path) - 1
            pycharm_root_path = ''
            for i in range(len_current_path):
                pycharm_root_path = pycharm_root_path + str(current_path[i]) + '\\'
                if 'Pycharm' in pycharm_root_path:
                    break
            return pycharm_root_path if 'Pycharm' in pycharm_root_path else None
        except Exception:
            self.logger.exception('')
            return None

    def delete_all_files_in_folder(self, path: str):
        try:
            files_to_remove = [os.path.join(path, f) for f in os.listdir(path)]
            for f in files_to_remove:
                os.remove(f)
        except Exception:
            self.logger.exception('')
