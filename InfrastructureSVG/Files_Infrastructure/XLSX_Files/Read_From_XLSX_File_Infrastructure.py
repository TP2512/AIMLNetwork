import xlrd
import logging
import pandas as pd

from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import PathFoldersClass

""" 
In this py file have 1 class
    - ReadFromXLSXFileClass
"""


class ReadFromXLSXFileClass:
    """ This class ("ReadFromXLSXFileClass") responsible for read data from xlsx files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def type_converter_to_int_str(self, type_value):
        """
        This function responsible to convert value type to int-str.

        The function get 1 parameter:
            - "float_value" - Full path location of the file (string type)


        The function return 1 parameters.

        - "int_str_value" - The converted value
        """

        try:
            if type(type_value) != str:
                return str(int(type_value)) if type(type_value) == float else str(type_value)
            else:
                return type_value
        except Exception:
            self.logger.exception("Can't read from xlsx file")
            return None

    def read_xlsx_by_sheet_name_from_full_path(self, full_path, sheet_name=None):
        """
        This function responsible for reading data from the xlsx file in specific folder and create an array from this
        data

        The function get 1 parameter:
            - "full_path" - parameter need to be the full path location of the file (string type)
            - "sheet_name" - The sheet name in the xlsx (string type)

        The function return 1 parameters:
            - "full_list_from_xlsx_file" - all the data in the xlsx file (all sheets) (list type)
        """

        try:
            full_list_from_xlsx_file = []
            config = xlrd.open_workbook(full_path)
            sheet_name = [sheet_name] if sheet_name else config.sheet_names()
            for names in sheet_name:
                list_from_xlsx_file = []
                if type(sheet_name) is list:
                    list_from_xlsx_file.append(names)
                    sheet = config.sheet_by_name(names)
                else:
                    list_from_xlsx_file.append(sheet_name)
                    sheet = config.sheet_by_name(sheet_name)
                sheet.cell_value(0, 0)
                rows = sheet.nrows
                for i in range(rows):
                    r = sheet.row_values(i)
                    list_from_xlsx_file.append(r)
                full_list_from_xlsx_file.append(list_from_xlsx_file)
            # print(list_from_xlsx_file)
            return full_list_from_xlsx_file
        except Exception:
            self.logger.exception("Can't read from xlsx file")
            return None

    def read_xlsx_from_pycharm_folder(self, path_in_pycharm, sheet_name=None):
        """
        This function responsible for reading data from the XLSX file in specific Pycharm folder and create an array
        from this data

        The function get 1 parameter:
            - "path_in_pycharm" - parameter need to be the path location till Pycharm folder (string type)

        The function return 1 parameters:
            - "list_from_xlsx_file" - all the data in the XLSX file (list type)
        """

        try:
            pycharm_root_path = PathFoldersClass().return_to_pycharm_root_path()
            pycharm_root_path = pycharm_root_path + path_in_pycharm
            # print(list_from_xlsx_file)
            return ReadFromXLSXFileClass().read_xlsx_by_sheet_name_from_full_path(pycharm_root_path, sheet_name)

        except Exception:
            self.logger.exception("Can't read XLSX file from Pycharm folder")
            return None

    def read_xlsx_by_sheet_name(self, path_to_file, sheetname):
        """
        This function responsible to read data from excel file and put it as data frame.

        The function doesn't get parameters.
        The function return/update the result into self.
        """

        try:
            return pd.read_excel(path_to_file, sheetname)
        except Exception:
            self.logger.exception("Can't read from xlsx file")
            return None
