import openpyxl
from openpyxl import Workbook
import logging


class WriteToXLSXFileClass:
    """ This class ("WriteToXLSXFileClass") responsible for write data into xlsx files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def write_result_to_excel_xlsx(self, full_path, sheet_name, cell_index, values_to_set, t_f=False):

        """
        This function responsible for write data(values) into xlsx file in specific folder(full path) and sheet name

        The function get 4 parameter:
            - "full_path" - Full path location of the file (string type)
            - "sheet_name" - The sheet name in the xlsx (string type)
            - "cell_index" - The cell index(example: 'A3') in mentioned sheet name (string type)
            - "values_to_set" - The value to write into mentioned cell index (string type)

        The function doesn't return parameters.

        """

        # print(full_path)
        try:
            xfile = openpyxl.load_workbook(full_path)
            sheet = xfile.get_sheet_by_name(sheet_name)
            sheet[cell_index] = values_to_set  # set new value
            xfile.save(full_path)
            if t_f:
                return True
        except Exception:
            self.logger.exception('')
            return None

    def write_to_excel_xlsx(self, full_path, sheet_name, values_to_set, t_f=False):

        """
        This function responsible for create  xlsx file in specific folder(full path) and sheet name and write
        to it row by row

        The function get 4 parameter:
            - "full_path" - Full path location of the file (string type)
            - "sheet_name" - The sheet name in the xlsx (string type - that created)
            - "values_to_set" - list of rows to write

        The function return true if success .

        """

        # print(full_path)
        try:
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = sheet_name
            letter_to_start = "A"
            for number_to_start, row in enumerate(values_to_set, start=1):
                letter = letter_to_start
                for cell in row:
                    self.logger.info(str(letter) + str(number_to_start))
                    worksheet[str(letter) + str(number_to_start)] = cell
                    letter = chr(ord(letter) + 1)
            workbook.save(full_path)
            if t_f:
                return True
        except Exception:
            self.logger.exception('')
            return None
