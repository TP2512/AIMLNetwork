import logging
from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import PathFoldersClass

""" 
In this py file have 1 class
    - ReadFromTXTFileClass
"""


class ReadFromTXTFileClass:
    """ This class ("ReadFromTXTFileClass") responsible for read data from txt files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def read_txt_from_full_path(self, full_path):
        """
        This function responsible for reading data from the txt file in specific folder and create an array from this
        data

        The function get 1 parameter:
            - "full_path" - parameter need to be the full path location of the file (string type)

        The function return 1 parameters:
            - "results_from_txt" - all the data in the txt file (list type)
        """
        try:
            # file = open("Exported.txt", "w")
            # file.write("Text to write to file")
            # file.close()  # This close() is important
            #
            # print(full_path)
            with open(full_path, 'r') as file:
                results_from_txt = file.read()
                file.close()
            return results_from_txt
        except Exception:
            self.logger.exception('')
            return None

    def read_txt_from_pycharm_folder(self, path_in_pycharm):
        """
        This function responsible for reading data from the txt file in specific Pycharm folder and create an array from
        this data

        The function get 1 parameter:
            - "path_in_pycharm" - parameter need to be the path location till Pycharm folder (string type)

        The function return 1 parameters:
            - "results_from_txt" - all the data in the txt file (list type)
        """

        try:
            pycharm_root_path = PathFoldersClass().return_to_pycharm_root_path()
            pycharm_root_path = pycharm_root_path + path_in_pycharm
            return ReadFromTXTFileClass().read_txt_from_full_path(pycharm_root_path)
        except Exception:
            self.logger.exception('')
            return None

    def read_file(self, path):
        """
            This function responsible for reading data from the txt file an array from
            this data

            The function get 1 parameter:
                - "file" - parameter need to be the path location (string type)

            The function return 1 parameters:
                - "results_from_txt" - all the data in the txt file (list type)
        """
        try:
            with open(path) as f:
                full_log = f.read()
                lines = full_log.splitlines()

            return lines
        except Exception:
            self.logger.exception('')
            return None
