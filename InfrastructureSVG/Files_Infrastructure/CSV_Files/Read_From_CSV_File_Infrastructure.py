import csv


from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import PathFoldersClass
import logging

""" 
In this py file have 1 class
    - ReadFromCSVFileClass
"""


class ReadFromCSVFileClass:
    """ This class ("ReadFromCSVFileClass") responsible for read data from CSV files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def convert_listoslist_to_list(self, list_of_list_value, index=0):
        try:
            return [value[index] for value in list_of_list_value]
        except Exception:
            self.logger.exception('')

    def read_csv_from_full_path(self, full_path):
        """
        This function responsible for reading data from the CSV file in specific folder and create an array from this
        data

        The function get 1 parameter:
            - "full_path" - parameter need to be the full path location of the file (string type)

        The function return 1 parameters:
            - "list_from_csv_file" - all the data in the CSV file (list type)
        """

        try:
            list_from_csv_file = []
            with open(full_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                list_from_csv_file.extend(iter(csv_reader))
            # print(list_from_csv_file)
            return list_from_csv_file
        except Exception:
            self.logger.exception("Can't read from CSV file")
            return None

    def read_csv_from_pycharm_folder(self, path_in_pycharm):
        """
        This function responsible for reading data from the CSV file in specific Pycharm folder and create an array from
        this data

        The function get 1 parameter: 
            - "path_in_pycharm" - parameter need to be the path location till Pycharm folder (string type)

        The function return 1 parameters:
            - "list_from_csv_file" - all the data in the CSV file (list type)
        """

        try:
            pycharm_root_path = PathFoldersClass().return_to_pycharm_root_path()
            pycharm_root_path = pycharm_root_path + path_in_pycharm
            # print(list_from_csv_file)
            return ReadFromCSVFileClass().read_csv_from_full_path(pycharm_root_path)
        except Exception:
            self.logger.exception("Can't read CSV file from Pycharm folder")
            return None
