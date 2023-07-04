import contextlib
import logging
import os

import xlwings as xw
import re


class Tpcalc:

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.protocol = kwargs.get("protocol") or "5g"
        # self.file_location = \
        #     kwargs.get('file_location') if kwargs.get(
        #         'file_location') else '\\\\fs4\\data\\SVG\\Automation\\Python Projects\\Files_for_Python_projects' \
        #                               '\\TP_Calculator\\TP_calculator.xlsx'

        if self.protocol == "4g":
            self.file_location = kwargs.get(
                'file_location') or f'{os.path.dirname(__file__)}\\TP_calculator_4g.xlsx'
            self.properties_range = kwargs.get('properties_range') or "B2:B11"
            self.tp_per_mcs_table_range = kwargs.get('tp_per_mcs_table_range') or "B34:B62"
        else:
            self.file_location = kwargs.get(
                'file_location') or f'{os.path.dirname(__file__)}\\TP_calculator.xlsx'
            self.properties_range = kwargs.get('properties_range') or "B3:B21"
            self.tp_per_mcs_table_range = kwargs.get('tp_per_mcs_table_range') or "B35:B63"
        self.input_sheet_name = kwargs.get('input_sheet_name') or "inputs"
        self.data_sheet_name = kwargs.get('data_sheet_name') or "DATA"
        self.max_tp_table_range = kwargs.get('max_tp_table_range') or "E2:E3"
        self.mcs = None
        self.Throughput = None
        self.errors = None
        self.data = {}
        self.app = xw.apps.add()
        self.app.visible = False
        try:
            self.workbook = self.app.books.open(self.file_location)
            self.inputs_sheet = self.workbook.sheets(self.input_sheet_name)
            self.data_sheet = self.workbook.sheets(self.data_sheet_name)
        except Exception as err:
            self.logger.error(err)
        self.properties_dict = self.get_table_properties_with_insert_cell(self.properties_range)
        self.max_tp_per_mcs = self.get_table_properties_with_insert_cell(self.tp_per_mcs_table_range)
        self.dict_of_values_per_property = None
        self.input_from_user = self.init_properties()

    def get_next_column_range(self, range_, num_forward):
        try:
            splitted_cells = range_.split(":")
            edit_info_column, properties_names_row_start = self.get_next_column_single(splitted_cells[0], num_forward)
            properties_names_row_end = int(splitted_cells[1][1:])
            return edit_info_column, properties_names_row_start, properties_names_row_end
        except Exception as err:
            self.logger.exception(err)

    def get_next_column_single(self, column, num_forward):
        try:
            column_letter = chr(ord(column[0]) + num_forward)
            column_num = int(column[1:])
            return column_letter, column_num
        except Exception as err:
            self.logger.exception(err)

    def get_table_properties_with_insert_cell(self, properties_range):
        try:
            edit_info_column, properties_names_row_start, properties_names_row_end = self. \
                get_next_column_range(properties_range, 1)
            table_properties_list = self.inputs_sheet.range(properties_range).value
            properties_dict = {}
            for property_ in table_properties_list:
                prop = self.convert_properties_names(property_)
                properties_dict[prop] = edit_info_column + str(properties_names_row_start)
                properties_names_row_start += 1
            return properties_dict
        except Exception as err:
            self.logger.exception(err)

    def extract_data_validation_fields(self):
        try:
            # range_pattern = '(?<=\!).+(?<=\d)'
            range_pattern = '(?<=\!)\$[A-Z]+\$\d+\:\$[A-Z]+\$\d+(?<=\d)'
            dict_of_values_per_property = {}
            for key, value in self.properties_dict.items():
                try:
                    data_validation_formula = self.inputs_sheet.range(value).api.Validation.Formula1
                    new_key = self.convert_properties_names(key)
                    if "$" in data_validation_formula:  # its range of cells --> needc to extract the range
                        if data_validation_range := re.findall(range_pattern, data_validation_formula):
                            tmp_list = []
                            for range_ in data_validation_range:
                                pure_range = range_.replace("$", "")
                                tmp_list += self.data_sheet.range(pure_range).value
                            dict_of_values_per_property[new_key] = tmp_list
                    else:  # its list of values --> just split it
                        regular_list_of_values = data_validation_formula.split(",")
                        dict_of_values_per_property[new_key] = regular_list_of_values
                except Exception:  # used to handle xlwings errors when no formula in cell
                    continue
            return dict_of_values_per_property
        except Exception as err:
            self.logger.exception(err)

    def init_properties(self):
        try:
            properties_copy = {}
            for key in self.properties_dict.keys():
                value = self.convert_properties_names(key)
                properties_copy[value] = ""
            return properties_copy
        except Exception as err:
            self.logger.exception(err)

    def convert_properties_names(self, excel_name):
        try:

            if type(excel_name) is str:
                if (
                        'TDD Split ( %' in excel_name
                        or "%" not in excel_name
                        and "(" in excel_name
                        and "(CA)" not in excel_name
                ):
                    value = excel_name.split(" (")[0]
                elif "%" in excel_name:
                    value = excel_name.split(" %")[0]
                elif "[" in excel_name:
                    value = excel_name.split(" [")[0]
                else:
                    value = excel_name
                value = value.replace(" ", "_").lower()
            else:
                value = excel_name
            return value
        except Exception as err:
            self.logger.exception(err)

    def validate_got_all_data_from_user(self, **kwargs):
        try:
            if not (kwargs.get('frequency_band')):
                self.logger.error("frequency band must be specified")
            if not (kwargs.get('cyclic_prefix')):
                self.logger.error("cyclic prefix band must be specified")
            # if not (kwargs.get('sub_carrier_spacing')):
            #     self.logger.error("sub carrier spacing band must be specified")
            if not (kwargs.get('bw')):
                self.logger.error("bw band must be specified")
            if not (kwargs.get('dl_max_modulation')):
                self.logger.error("dl max modulation band must be specified")
            if not (kwargs.get('ul_max_modulation')):
                self.logger.error("dl max modulation band must be specified")
            if not (kwargs.get('dl_layers')):
                self.logger.error("dl layers band must be specified")
            if not (kwargs.get('ul_layers')):
                self.logger.error("ul layers band must be specified")
            if not (kwargs.get('packet_size')):
                self.logger.error("packet_size must be specified")
            elif kwargs.get('mcs'):
                if 0 > int(kwargs.get('mcs')) < 28:
                    self.logger.error("mcs must be specified in allowed range 0-28")
                else:
                    self.mcs = int(kwargs.get('mcs'))
            # iterate over self.input_from_user to avoid "unknown key" if user will input by mistake
            # key that not exist in table
            for key, value in self.input_from_user.items():
                self.input_from_user[key] = kwargs.get(key)
        except Exception as err:
            self.logger.exception(err)

    def validate_got_all_data_from_user_4g(self, **kwargs):
        try:
            if not (kwargs.get('channel_bandwidth')):
                self.logger.error("channel_bandwidth must be specified")
            # if not (kwargs.get('sub_carrier_spacing')):
            #     self.logger.error("sub carrier spacing band must be specified")
            if not (kwargs.get('max_dl_qam')):
                self.logger.error("max_dl_qam modulation band must be specified")
            if not (kwargs.get('max_ul_qam')):
                self.logger.error("max_ul_qam modulation band must be specified")
            if not (kwargs.get('duplex')):
                self.logger.error("duplex band must be specified")
            if not (kwargs.get('frame_split')):
                self.logger.error("frame_split band must be specified")
            if not (kwargs.get("nb._dl_carriers_(ca)")):
                self.logger.error("nb._dl_carriers (ca) band must be specified")
            # if not (kwargs.get('packet_size')):
            #     self.logger.error("packet_size must be specified")
            elif kwargs.get('mcs'):
                if 0 > int(kwargs.get('mcs')) < 28:
                    self.logger.error("mcs must be specified in allowed range 0-28")
                else:
                    self.mcs = int(kwargs.get('mcs'))
            # iterate over self.input_from_user to avoid "unknown key" if user will input by mistake
            # key that not exist in table
            for key, value in self.input_from_user.items():
                self.input_from_user[key] = kwargs.get(key)
        except Exception as err:
            self.logger.exception(err)

    def parse_str_from_jira(self, attr_name):
        try:
            value = self.input_from_user[attr_name]
            if attr_name == "sub_carrier_spacing":
                extract_number_scs_pattern = '(?<=)\\d+(?=k|K)'
                pure_number = re.findall(extract_number_scs_pattern, value)
            else:
                extract_numbers_regular_pattern = '\\d+'
                pure_number = re.findall(extract_numbers_regular_pattern, value)
            if pure_number:
                self.input_from_user[attr_name] = pure_number[0]
        except Exception as err:
            self.logger.exception(err)

    def align_string_from_jira_with_excel_data_validation_names(self, attr_name, split_char=""):
        try:
            if split_char:
                value = self.input_from_user[attr_name].split(split_char)[0].lower()
            else:
                value = self.input_from_user[attr_name].lower()
            for excel_str in self.dict_of_values_per_property[attr_name]:
                if value in str(excel_str).lower():
                    self.input_from_user[attr_name] = excel_str
                    return
            raise KeyError(f'cant find {value} in {attr_name}')
        except Exception as err:
            self.logger.exception(err)

    def get_key(self, val, dict_):
        try:
            for key, value in dict_.items():
                if val == value:
                    return key
        except Exception as err:
            self.logger.exception(err)

    def validate_user_data_in_excel_data_validation_list(self):
        try:
            if self.protocol == "4g":
                self.align_string_from_jira_with_excel_data_validation_names("channel_bandwidth")
            else:
                self.align_string_from_jira_with_excel_data_validation_names("frequency_band")
            # self.align_string_from_jira_with_excel_data_validation_names("slot_format", "-")
            self.input_from_user = {k: v for k, v in self.input_from_user.items() if v}
            for key, value in self.input_from_user.items():
                if key in self.dict_of_values_per_property.keys():  # if the property has data validation list
                    # compare the value twice as it might be in different type, first compare AS IS (str)
                    # second compare is type casted to int
                    if value not in self.dict_of_values_per_property[key]:
                        with contextlib.suppress(Exception):
                            value = int(value)
                    if value not in self.dict_of_values_per_property[key]:
                        with contextlib.suppress(Exception):
                            value = str(value)
                    if value not in self.dict_of_values_per_property[key]:
                        self.logger.exception(
                            f'{value} is not allowed value for {key}, allowed values is {str(self.dict_of_values_per_property[key])}')
        except Exception as err:
            self.logger.exception(err)

    def parse_str_to_specific_fields(self):
        try:
            if self.protocol == '5g':
                self.jira_field_parser(
                    "dl_max_modulation", "ul_max_modulation", "bw"
                )
            else:
                self.jira_field_parser(
                    "max_dl_qam", "max_ul_qam", "channel_bandwidth"
                )
        except Exception as err:
            self.logger.exception(err)

    def jira_field_parser(self, dl_quam, ul_quam, bw):
        self.parse_str_from_jira(dl_quam)
        self.parse_str_from_jira(ul_quam)
        self.parse_str_from_jira(bw)

    def insert_data_to_excel(self):
        try:
            self.properties_dict = {k: v for k, v in self.properties_dict.items() if k not in ['dl_split', 'ul_split', 'ssf_split', 'sub_carrier_spacing', 'slot_format', 'special_subframe_', 'max_dl_ri', 'nb._ul_carriers_(ca)']}
            for property_, cell_number in self.properties_dict.items():
                self.inputs_sheet.range(cell_number).value = self.input_from_user[property_]
        except Exception as err:
            self.logger.exception(err)

    def monitor_errors_in_excel(self):
        try:
            errors_column, errors_row_start, errors_row_end = self.get_next_column_range(self.properties_range, 2)
            error_range = f'{errors_column}{errors_row_start}:{errors_column}{errors_row_end}'
            errors_list = list(dict.fromkeys(self.inputs_sheet.range(error_range).value))  # remove duplicates --> None / ""
            return "".join(error + "\n" for error in errors_list if error != "" and (error is not None and 'default' not in error))

        except Exception as err:
            self.logger.exception(err)

    def max_tp(self):
        # go to regular result
        max_tp_column, max_tp_start, max_tp_end = self.get_next_column_range(self.max_tp_table_range, 1)
        dl = self.inputs_sheet.range(f'{max_tp_column}{max_tp_start}').value
        ul = self.inputs_sheet.range(f'{max_tp_column}{max_tp_end}').value
        return dl, ul

    def mcs_tp(self, traffic_direction=None):
        # go to mcs table
        ul = ""
        dl = ""
        for mcs, cell in self.max_tp_per_mcs.items():
            if mcs == self.mcs:
                if traffic_direction and traffic_direction == 'DL':
                    dl = self.inputs_sheet.range(cell).value
                elif traffic_direction and traffic_direction == 'UL':
                    ul_column, ul_row = self.get_next_column_single(cell, 1)
                    ul = self.inputs_sheet.range(f'{ul_column}{ul_row}').value
                else:
                    ul_column, ul_row = self.get_next_column_single(cell, 1)
                    ul = self.inputs_sheet.range(f'{ul_column}{ul_row}').value
                    dl = self.inputs_sheet.range(cell).value
                break
        if not ul and not dl:
            self.errors += f'cant get TP from calculator, mcs {self.mcs} not found in table'
        return dl, ul

    def get_tp_result(self, max_tp=True, traffic_direction=None, **kwargs):
        try:
            if self.protocol == "4g":
                self.validate_got_all_data_from_user_4g(**kwargs)
            else:
                self.validate_got_all_data_from_user(**kwargs)
            if not max_tp and not kwargs.get('mcs'):
                self.logger.error("max tp flag is false -> mcs must be specified")
            self.parse_str_to_specific_fields()
            # first insert the sub carrier spacing as it change the values in Format SSF, then get all validation
            # fields and insert rest of the data
            # self.inputs_sheet.range(self.properties_dict['sub_carrier_spacing']).value = \
            #     self.input_from_user['sub_carrier_spacing']
            self.dict_of_values_per_property = self.extract_data_validation_fields()
            self.validate_user_data_in_excel_data_validation_list()
            self.insert_data_to_excel()
            error_str = self.monitor_errors_in_excel()
            self.errors = error_str
            tp_dict = {}

            dl, ul = self.max_tp() if max_tp else self.mcs_tp(traffic_direction)
            if ul:
                tp_dict["UL"] = float("%.1f" % float(ul))
            if dl:
                tp_dict["DL"] = float("%.1f" % float(dl))
            self.logger.info(str(tp_dict))
            self.Throughput = tp_dict
            app = xw.apps.active
            app.kill()
        except Exception as err:
            self.logger.exception(err)
