import os
import random
import datetime
import logging
import re

from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import PathFoldersClass
from InfrastructureSVG.Files_Infrastructure.Actions_On_Files_And_Folders.Active_actions_files_and_folders \
    import GeneralActionClass

""" 
In this py file have 1 class
    - WriteToTXTFileClass
"""


class WriteToTXTFileClass:
    """ This class ("WriteToTXTFileClassoldersClass().) responsible for write data to txt files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def write_to_txt_full_path(self, full_path, wr_to_txt):
        """
        This function responsible for writing into the txt file in specific folder and create an array from this data

        The function get 2 parameter:
            - "full_path" - parameter need to be the full path location of the file (include file name) (string type)
            - "wr_to_txt" - all the data for insert to the txt file (list type)

        The function return 0 parameters
        """

        try:
            # file = open("Exported.txt", "w")
            # file.write("Text to write to file")
            # file.close()  # This close() is important
            #
            with open(full_path, 'w') as file:
                file.write(wr_to_txt)
                file.close()
            return
        except Exception:
            print()
            self.logger.exception("Can't write to txt file")
            return None

    def append_to_txt_full_path(self, full_path, wr_to_txt):
        """
        This function responsible for writing into the txt file in specific folder and create an array from this data

        The function get 2 parameter:
            - "full_path" - parameter need to be the full path location of the file (include file name) (string type)
            - "wr_to_txt" - all the data for insert to the txt file (list type)

        The function return 0 parameters
        """

        try:
            with open(full_path, 'a', newline="") as file:
                file.write(wr_to_txt)
                file.close()
            return
        except UnicodeEncodeError:
            with open(full_path, 'a', newline="") as file:
                file.write(re.sub(r"\ufffd", "", wr_to_txt))
                file.close()
            return
        except Exception:
            self.logger.exception("Can't write to txt file")
            return None

    def write_to_txt_pycharm_folder(self, path_in_pycharm, wr_to_txt):
        """
        This function responsible for writing into the txt file in specific Pycharm folder and create an array from this
        data

        The function get 2 parameter:
            - "path_in_pycharm" - parameter need to be the path location till Pycharm folder (string type)
            - "wr_to_txt" - all the data for insert to the txt file (list type)

        The function return 0 parameters
        """

        try:
            pycharm_root_path = PathFoldersClass().return_to_pycharm_root_path()
            pycharm_root_path = pycharm_root_path + path_in_pycharm
            #
            WriteToTXTFileClass().write_to_txt_full_path(pycharm_root_path, wr_to_txt)
            return
        except Exception:
            self.logger.exception("Can't write to txt file in Pycharm folder")
            return None

    def write_to_log_file(self, path, str_log, project_name, unique_identification, phase_name):
        """
        func to save outputs of func as logs txt file
        :param path: path for file output
        :param str_log: string to save into log file (str)
        :param project_name: name of the project example: eNBanalyzer (str)
        :param unique_identification: for example: name of the test plan: SVG1-XXXXX (str)
        :param phase_name:  phase of the log output example : get testplan from jira (str)
        :return:
        """
        try:
            if str_log is None:
                str_log = ''
            exist_check = GeneralActionClass().check_if_directory_exist(path)
            time_ = datetime.datetime.now(datetime.timezone.utc)
            if not exist_check:
                # create the folder
                try:
                    os.makedirs(path)
                except Exception:
                    self.logger.exception('')

            if phase_name == '' or phase_name:
                now = str(datetime.datetime.now(datetime.timezone.utc))
                started_phase = "\n============================= phase " + phase_name + " started at: " + \
                                now + " =======================\n"
                ended_phase = "\n============================= phase " + phase_name + " ended =======================\n"
            else:
                started_phase = '\n'
                ended_phase = '\n'
            file_name = f"{project_name}_{str(time_.day)}_{str(time_.month)}_{str(time_.year)}_{str(unique_identification)}.log"

            full_path = path + file_name
            with open(full_path, "a") as file:
                file.write(started_phase)
                file.write(str(str_log))
                file.write(ended_phase)
        except Exception:
            self.logger.exception('')

    def check_if_file_exist(self, path, file_name_or_part_name):
        try:
            file_list = os.listdir(path)
            for file in file_list:
                if f"{file_name_or_part_name}.log" in file:
                    random_num = random.randint(1, 500)
                    return f"{file_name_or_part_name}_{str(random_num)}"
            return file_name_or_part_name

        except Exception:
            self.logger.exception('')
