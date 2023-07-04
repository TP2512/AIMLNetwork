import yaml

from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import PathFoldersClass
import logging

""" 
In this py file have 1 class
    - ReadFromYAMLFileClass
"""


class ReadFromYAMLFileClass:
    """ This class ("ReadFromYAMLFileClass") responsible for read data from YAML files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def read_yaml_from_full_path(self, full_path):
        """
        This function responsible for reading data from the YAML file in specific folder and create an array from this
        data

        The function get 1 parameter:
            - "full_path" - parameter need to be the full path location of the file (string type)

        The function return 1 parameters:
            - "yaml_dict" - all the data in the YAML file (dict type)
        """

        try:
            with open(full_path) as yaml_file:
                return yaml.load(yaml_file, Loader=yaml.FullLoader)
        except Exception:
            self.logger.exception("Can't read from yaml file")
            return None

    def read_yaml_from_pycharm_folder(self, path_in_pycharm):
        """
        This function responsible for reading data from the YAML file in specific Pycharm folder and create an array from
        this data

        The function get 1 parameter: 
            - "path_in_pycharm" - parameter need to be the path location till Pycharm folder (string type)

        The function return 1 parameters:
            - "yaml_dict" - all the data in the YAML file (dict type)
        """

        try:
            pycharm_root_path = PathFoldersClass().return_to_pycharm_root_path()
            pycharm_root_path = pycharm_root_path + path_in_pycharm
            # print(yaml_dict)
            return self.read_yaml_from_full_path(pycharm_root_path)
        except Exception:
            self.logger.exception("Can't read YAML file from Pycharm folder")
            return None
