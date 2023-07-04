import csv
import logging

from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import PathFoldersClass

""" 
In this py file have 1 class
    - WriteToCSVFileClass
"""


class WriteToCSVFileClass:
    """ This class ("WriteToCSVFileClass") responsible for write data to CSV files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def write_to_csv_full_path(self, full_path, list_to_csv, return_t_f=False):
        """
        This function responsible for writing into the CSV file in specific folder and create an array from this data

        The function get 2 parameter:
            - "full_path" - parameter need to be the full path location of the file (string type)
            - "list_to_csv" - all the data for insert to the CSV file (list type)
                * list_to_csv = each index in the list = row
                * list_to_csv = each string in the list[i] = column

        The function return 0 parameters
        """

        try:
            with open(full_path, 'w', newline='') as my_file:
                wr = csv.writer(my_file, quoting=csv.QUOTE_ALL)
                for word in list_to_csv:
                    wr.writerow(word)
            if return_t_f:
                return True
        except Exception:
            self.logger.exception("Can't write to CSV file")
            return None

    def write_to_csv_pycharm_folder(self, path_in_pycharm, list_to_csv, return_t_f=False):
        """
        This function responsible for writing into the CSV file in specific Pycharm folder and create an array from this
        data

        The function get 2 parameter:
            - "path_in_pycharm" - parameter need to be the path location till Pycharm folder (string type)
            - "list_to_csv" - all the data for insert to the CSV file (list type)
                * list_to_csv = each index in the list = row
                * list_to_csv = each string in the list[i] = column

        The function return 0 parameters
        """

        try:
            pycharm_root_path = PathFoldersClass().return_to_pycharm_root_path()
            pycharm_root_path = pycharm_root_path + path_in_pycharm
            #
            WriteToCSVFileClass().write_to_csv_full_path(pycharm_root_path, list_to_csv)
            if return_t_f:
                return True
        except Exception:
            self.logger.exception("Can't write to CSV file from Pycharm folder")
            return None
