import logging
from InfrastructureSVG.Files_Infrastructure.txt_Files.Read_From_txt_File_Infrastructure import ReadFromTXTFileClass
from InfrastructureSVG.Files_Infrastructure.XLSX_Files.Read_From_XLSX_File_Infrastructure import ReadFromXLSXFileClass


class CreateTemplate:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def create_txt_by_template_and_xlsx(self, template_full_path, parameter_for_replace_full_path):
        """
        This function responsible to fill template by relevant parameters.

        The function get 1 parameter:
            - "template_full_path" - parameter need to be the full path location of the template file (string type)
            - "parameter_for_replace_full_path" - parameter need to be the full path location of the xlsx file - fill
             the parameters to replace (string type)


        The function return 1 parameters.
        - "template" - the template after the replace parameters
        """

        try:
            template = ReadFromTXTFileClass().read_txt_from_full_path(template_full_path)
            # print(template)

            parameter_for_replace = ReadFromXLSXFileClass().\
                read_xlsx_by_sheet_name_from_full_path(parameter_for_replace_full_path, 'Sheet1')
            # print(parameter_for_replace)

            for index, row_list in enumerate(parameter_for_replace[0], start=0):
                if index > 0:
                    # print(row_list)
                    template = template.replace(ReadFromXLSXFileClass().type_converter_to_int_str(row_list[0]),
                                                ReadFromXLSXFileClass().type_converter_to_int_str(row_list[1]))

            return template
        except Exception:
            self.logger.exception('Can\'t read from xlsx file')
            return None
