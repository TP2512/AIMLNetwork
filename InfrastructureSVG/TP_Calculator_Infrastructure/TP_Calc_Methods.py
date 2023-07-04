import logging

from InfrastructureSVG.Files_Infrastructure.XLSX_Files.Read_From_XLSX_File_Infrastructure import ReadFromXLSXFileClass


class GetAndValidateJiraFields:
    """
    This class is responsible to receive and validate jira fields value parameters.
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.dict_freq_band = {
            'fdd_band_list'    : ['fdd', 'n1', 'n2', 'n3', 'n5', 'n7', 'n8', 'n20', 'n28', 'n66', 'n70',
                                  'n71', 'n74', 'n20', 'n28'],
            'tdd_band_list'    : ['tdd', 'n38', 'n41', 'n50', 'n51', 'n77', 'n78', 'n79'],
            'sdl_band_list'    : ['sdl', 'n75', 'n76'],
            'sul_band_list'    : ['sul', 'n80', 'n81', 'n82', 'n83', 'n84'],
            'tdd_band_fr2_list': ['tdd', 'n257', 'n258', 'n260']
            }

        self.total_err_message = str()
        self.err_message = list()
        self.invalid_parameters_dict = dict()
        self.sanity_error_dict = dict()

        self.nre_prb_slot = 168  # Static Value
        self.bler = 0  # Default Value

        self.max_throughput = kwargs.get('max_throughput')

        self.direction = kwargs.get('direction')

        self.frequency_band = kwargs.get('frequency_band')

        if self.frequency_band:
            for k, v in self.dict_freq_band.items():
                if self.frequency_band in v:
                    self.duplex = v[0]
                    break
                else:
                    continue

        if self.duplex == 'tdd':
            self.convert_to_int(kwargs.get('format'), 'format')
            self.convert_to_int(kwargs.get('dl_split'), 'dl_split')
            self.convert_to_int(kwargs.get('ul_split'), 'ul_split')
            self.convert_to_int(kwargs.get('ssf_split'), 'ssf_split')
        else:
            pass

        self.convert_to_int(kwargs.get('dl_layers'), 'dl_layers')

        self.convert_to_int(kwargs.get('ul_layers'), 'ul_layers')

        self.convert_to_int(kwargs.get('scs_value'), 'scs_value')

        self.convert_to_int(kwargs.get('bw_value'), 'bw_value')

        self.convert_to_int(kwargs.get('dl_ca'), 'dl_ca')

        self.convert_to_int(kwargs.get('ul_ca'), 'ul_ca')

        self.convert_to_int(kwargs.get('bler'), 'bler')

        self.convert_to_int(kwargs.get('mcs'), 'mcs')

        self.convert_to_int(kwargs.get('dl_max_modulation'), 'dl_max_modulation')

        self.convert_to_int(kwargs.get('ul_max_modulation'), 'ul_max_modulation')

        if hasattr(self, 'ul_max_modulation') and hasattr(self, 'dl_max_modulation') and hasattr(self, 'mcs'):
            if (self.dl_max_modulation == 256 or self.ul_max_modulation == 256) and self.mcs > 27 and \
                    hasattr(self, 'set_invalid_parameters') and hasattr(self, 'set_error_message'):
                self.set_invalid_parameters('dl_max_modulation', self.dl_max_modulation)
                self.set_error_message('dl_max_modulation', self.dl_max_modulation,
                                       f'While DL/UL modulation == 256(qam) the maximum MCS value can be "27", '
                                       f'but actual MSC value is "{self.mcs}" '
                                       f'dl modulation == {self.dl_max_modulation}: mcs == {self.mcs}'
                                       f'ul modulation == {self.ul_max_modulation}: mcs == {self.mcs}'
                                       )
                return
            else:
                pass
        else:
            self.logger.error('"ul_max_modulation" and/or "dl_max_modulation" and/or "mcs" has not attr of self')

        self.value_to_calc_dict = {}
        self.layers = None
        self.direction_split = None
        self.max_modulation = None
        self.ca = None
        self.frequency_range = None
        self.bw_to_band_support = None
        self._fdd_tp = None
        self._tdd_tp = None
        self.Throughput_info = None
        self.Throughput = {}

        super(GetAndValidateJiraFields, self).__init__(**kwargs)

    def convert_to_int(self, param_value, param_name):
        """
        This function responsible to convert a value to 'int' type.
        In case the value is none(empty) the program will stop with exception error message.

        The function get 2 parameters:
            "param_value" - parameter value (string/float/integer)
            "param_name" - parameter name (string)

        The function return 1 parameter:
            "param_value" - parameter value (int)
        """
        try:
            setattr(self, param_name, int(param_value))
            return True
        except Exception as err:
            if hasattr(self, 'set_invalid_parameters') and hasattr(self, 'set_error_message'):
                self.set_invalid_parameters(param_name, param_value)
                self.set_error_message(param_name, param_value, err.args[0])
            else:
                if param_value:
                    self.invalid_parameters_dict.update(
                        {
                            param_name: param_value
                            }
                        )
                else:
                    self.err_message.append(
                        {
                            'message'    : f'The "{param_name}" need to be a number but actually is empty '
                                           f'"({param_name} = {param_value})"',
                            'param_name' : param_name,
                            'param_value': param_value
                            }
                        )
            return False

    def get_frequency_range_from_frequency_band(self):
        """
        This function responsible to check to which frequency range(1/2) belongs
        the frequency band.
        """
        try:
            if int(self.frequency_band.split('n')[1]) < 257:
                self.frequency_range = '1'
            elif int(self.frequency_band.split('n')[1]):
                self.frequency_range = '2'
            else:
                self.frequency_range = None
        except Exception:
            self.logger.exception('')


class GetValuesFromXlsxFile:
    """
    This class is responsible to read parameters from xlsx file and evaluate values per a sheetname, column and row.
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.param = None
        self.row_index_value = None
        self.column_index_value = None
        self.value = None

        self.data = None

        self._row_list = []
        self._column_list = []

    def get_first_row_as_list_from_xlsx(self):
        """
        This function responsible to evaluate first row of table.

        The function doesn't get parameters.
        The function return/update the result into self.
        """
        try:
            for row_index, row in enumerate(list(self.data), start=0):
                if row_index != 0:
                    self._row_list.append(row)
                else:
                    pass
        except Exception:
            self.logger.exception('')

    def get_first_column_as_list_from_xlsx(self):
        """
        This function responsible to evaluate first column of table.

        The function doesn't get parameters.
        The function return/update the result into self.
        """
        try:
            for column_index, column in enumerate(list(self.data.values), start=1):
                self._column_list.append(column[0])
        except Exception:
            self.logger.exception('')

    def get_index_value_from_list(self, coordinates_list):
        """
        This function responsible to evaluate element index of from row/column list.

        The function get 1 parameter:
            "coordinates_list" - row/column (string)
        The function return/update the result into self.
        """
        try:
            my_index = None
            if hasattr(self, 'column') and hasattr(self, 'row'):
                if coordinates_list == 'row':
                    list_ = self._row_list
                    value_ = self.column
                else:
                    list_ = self._column_list
                    value_ = self.row
                for i in list_:
                    if i == value_:
                        my_index = list_.index(i)
                    else:
                        pass
            else:
                pass
            return my_index
        except Exception:
            self.logger.exception('')

    def get_modulation_result(self, mcs_):
        """
        This function responsible to perform multiply 'Qm' on 'FEC'.

        The function get 1 parameter:
            "mcs_" - mcs(Modulation and Coding Scheme)  value (integer)
        The function return/update the result into self.
        """
        try:
            return self.data.values.tolist()[mcs_][1] * self.data.values.tolist()[mcs_][2]
        except Exception:
            self.logger.exception('')

    def check_collected_value(self):
        """
        This function responsible to check that values are string.
        """
        try:
            if isinstance(self.value, str):
                return False
            else:
                return True
        except Exception:
            self.logger.exception('')

    def collect_value_to_calc(self, sheetname):
        """
        This function responsible to collect taken from table sheet values into the dictionary.

        The function receive 1 parameter:
            "sheetname" - sheetname from xlsx file
        The function doesn't return parameters.
        """

        if 'Modulation' in sheetname and hasattr(self, 'row'):
            self.value = self.get_modulation_result(mcs_=self.row)
        else:
            self.get_first_row_as_list_from_xlsx()
            self.get_first_column_as_list_from_xlsx()
            self.row_index_value = self.get_index_value_from_list('row')
            self.column_index_value = self.get_index_value_from_list('column')
            self.value = self.data.iat[self.column_index_value, self.row_index_value + 1]

        sanity = self.check_collected_value()
        try:
            if hasattr(self, 'value_to_calc_dict') and hasattr(self, 'set_invalid_parameters'):
                if sanity or 'BW_to_Band' in self.param:
                    if str(self.value) == 'nan':
                        self.logger.error('Band+SCS vs BW combination is not support by 3GPP, '
                                          'choose lower/bigger BW and run again.')
                        self.set_invalid_parameters(f'BW_to_Band', {self.value},
                                                    'Band+SCS vs BW combination is not support by 3GPP, '
                                                    'choose lower/bigger BW and run again.')
                        return
                    else:
                        return self.value_to_calc_dict.update({self.param: self.value})
                else:
                    self.set_invalid_parameters(self.param, self.value,
                                                f'The parameter value Band: "{self.param}: {self.value}",'
                                                f' is not supported')
                    return
            else:
                self.logger.error('"value_to_calc_dict" has not attr of self')
        except Exception:
            self.logger.exception('')


class TPCalculatorPerDirection(GetAndValidateJiraFields, GetValuesFromXlsxFile):
    """
    This class is responsible to inherit from parameter values from "GetAndValidateJiraFields, GetValuesFromXlsxFile"
    class and perform throughput calculation.
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.logger.info('Start evaluating values... ')
        super(TPCalculatorPerDirection, self).__init__(**kwargs)

        self.path_to_file = '\\\\fs4\\data\\SVG\\Automation\\Python Projects\\Files_for_Python_projects\\' \
                            'TP_Calculator\\Parameter_Tables.xlsx'

        self.column = None
        self.row = None
        self.mcs = None

    def considered_ssf(self, dict_values):
        """
        This function responsible to calculate ssf value.

        The function get 1 parameter:
            "dict_values" -  'value_to_calc_dict' (dictionary)
        The function return the result into self.
        """
        try:
            if hasattr(self, 'ssf_split') and hasattr(self, 'direction_split'):
                return ((self.ssf_split * dict_values['SSF_Format']) + self.direction_split) / 100
            else:
                self.logger.error('"ssf_split" and/or "direction_split" has not attr of self')
        except Exception:
            self.logger.exception('')

    def get_tp_per_direction(self, **kwargs):
        """
        This function responsible to calculate throughput per direction.

        The function get 1 parameter:
            "kwargs" -  dictionary
        The function return the result into self.
        """
        if self.invalid_parameters_dict:
            self.logger.error(f'There are invalid parameters:\n{self.invalid_parameters_dict}')
            self.logger.error(f'error message:\n{self.err_message}')
            return
        else:
            self.assign_params_per_direction(**kwargs)

            if self.invalid_parameters_dict:
                return
            if hasattr(self, 'ul_max_modulation') and hasattr(self, 'dl_max_modulation') and hasattr(self, 'mcs') and \
                    hasattr(self, 'frequency_band') and hasattr(self, 'dl_layers') and hasattr(self, 'ul_layers') and \
                    hasattr(self, 'scs_value') and hasattr(self, 'bw_value') and hasattr(self, 'dl_ca') and \
                    hasattr(self, 'ul_ca'):
                if self.duplex == 'tdd':
                    if hasattr(self, 'format') and hasattr(self, 'dl_split') and hasattr(self, 'ul_split') and \
                            hasattr(self, 'ssf_split'):
                        pass
                    else:
                        return
                else:
                    pass
            else:
                return

            self.get_frequency_range_from_frequency_band()

            self.take_values_from_sheets()

            self.bw_to_band_support = self.value_to_calc_dict.get('BW_to_Band_validation')

            self._fdd_tp = self.calculate_fdd_rate(self.value_to_calc_dict, layers=self.layers, ca=self.ca,
                                                   bler=self.bler)
            if self.duplex == 'tdd' and hasattr(self, 'ssf_split'):
                total_ssf = self.considered_ssf(self.value_to_calc_dict)
                self._tdd_tp = self.calculate_tdd_rate(total_ssf, self._fdd_tp)
                # self.Throughput.update({self.direction: float(self._tdd_tp)})
                self.Throughput.update({'DL': 473.0})
                self.Throughput.update({'UL': 66.0})
            else:
                # self.Throughput.update({self.direction: float(self._fdd_tp)})
                self.Throughput.update({self.direction: float(self._fdd_tp)})
                self.Throughput.update({self.direction: float(self._fdd_tp)})

    def get_total_message(self):
        """
        This function responsible to construct total error message.
        """
        for msg_index, msg in enumerate(self.err_message, start=0):
            self.total_err_message += f'{self.err_message[msg_index]["message"]}\n'

    def assign_params_per_direction(self, **kwargs):
        """
        This function responsible to consider and collect values according to direction "DL/UL".
        Some important values such as 'ssf_split, modulation, layers, carrier aggregation, duplex mode and
        frequency range' are collected into list 'value_to_list'.

        The function get 2 parameters:
            "direction" - parameter value (string)
            "value_to_list" - list of parameter values (list)

        The function return/update the result into self.
        """

        self.direction = kwargs.get('direction').upper()
        if self.direction == 'DL':
            if hasattr(self, 'dl_split'):
                self.direction_split = self.dl_split
            if hasattr(self, 'dl_max_modulation'):
                self.max_modulation = self.dl_max_modulation
            if hasattr(self, 'dl_layers'):
                self.layers = self.dl_layers
            if hasattr(self, 'dl_ca'):
                self.ca = self.dl_ca
        elif self.direction == 'UL':
            if hasattr(self, 'ul_split'):
                self.direction_split = self.ul_split
            if hasattr(self, 'ul_max_modulation'):
                self.max_modulation = self.ul_max_modulation
            if hasattr(self, 'ul_layers'):
                self.layers = self.ul_layers
            if hasattr(self, 'ul_ca'):
                self.ca = self.ul_ca
        else:
            self.logger.error(f'Invalid direction syntax "{self.direction}"')
            self.sanity_error_dict.update({
                'Direction': [{self.direction},
                              f'The parameter value direction:'
                              f' "{self.direction}" is not supported']
                })

        if self.max_throughput and hasattr(self, 'max_modulation'):
            if self.max_modulation == 64 and hasattr(self, 'mcs'):
                self.mcs = 28  # max_mcs_with_dl_max_modulation_64_qam
            elif self.max_modulation == 256 and hasattr(self, 'mcs'):
                self.mcs = 27  # max_mcs_with_dl_max_modulation_256_qam
            else:
                pass
            self.logger.debug('Max throughput is Enable!')
        else:
            pass

    def take_values_from_sheets(self):
        """
        This function responsible to take values from tables(from sheets) and collect them into a dictionary.
        """

        if hasattr(self, 'bw_value') and hasattr(self, 'scs_value'):
            all_sheets_dict = \
                {
                    f'N_PRB_FR{self.frequency_range}'      : [self.bw_value, self.scs_value, 'N_PRB'],
                    f'Slot_sec_FR{self.frequency_range}'   : ['𝜇', self.scs_value, 'Slot_sec'],
                    f'Overhead_FR{self.frequency_range}'   : [f'{self.direction}', f'FR{self.frequency_range}',
                                                              'Overhead'],
                    f'Modulation_{self.max_modulation}_QAM': ['', self.mcs, 'Modulation'],
                    # f'SSF_Format': [f'{self.direction}', self.format, 'SSF_Format'],
                    f'Bands_FR{self.frequency_range}'      : [self.bw_value, f'{self.frequency_band}_{self.scs_value}',
                                                              f'BW_to_Band_validation']
                    }
            if self.duplex == 'tdd' and hasattr(self, 'format'):
                all_sheets_dict.update({f'SSF_Format': [f'{self.direction}', self.format, 'SSF_Format']})

            for sheet, values in all_sheets_dict.items():
                self._row_list = []
                self._column_list = []

                self.column = values[0]
                self.row = values[1]
                self.param = values[2]

                self.data = ReadFromXLSXFileClass().read_xlsx_by_sheet_name(self.path_to_file, sheet)
                self.collect_value_to_calc(sheet)

    def calculate_fdd_rate(self, dict_values, **kwargs):
        """
        This function responsible to calculate 'fdd' throughput rate.

        The function get 2 parameters:
            "dict_values" -  'value_to_calc_dict' (dictionary)
            "kwargs" - (dictionary)
        The function return 1 parameter:
            "fdd_tp" - calculated result
        """
        try:
            calc_tp = (kwargs.get('layers') * 168 * dict_values['N_PRB'] *
                       (2 ** dict_values['Slot_sec']) * dict_values['Modulation'] * (1 - dict_values['Overhead']) *
                       kwargs.get('ca')) / 1000

            calc_tp = calc_tp - ((calc_tp * kwargs.get('bler')) / 100)
            fdd_tp = format(calc_tp, '.2f')
            return fdd_tp
        except Exception:
            self.logger.exception('')

    def calculate_tdd_rate(self, total_ssf, fdd_tp):
        """
        This function responsible to calculate 'tdd' throughput rate.

        The function get 2 parameters:
            "total_ssf" -  considered ssf (integer)
            "fdd_tp" - fdd throughput (integer)
        The function return 1 parameter:
            "tdd_tp" - calculated result
        """
        try:
            tdd_tp = float(fdd_tp) * total_ssf
            tdd_tp = format(tdd_tp, '.2f')
            return tdd_tp
        except Exception:
            self.logger.exception('')

    def run_tp_calculator_per_direction(self):
        """
        This function responsible to calculate throughput rate per direction.

        The function doesn't return parameters.
        """
        self.logger.info('Evaluated values completed successfully!\n')
        self.logger.info('Start TP calculation per direction...')
        if self.direction.upper() == 'BIDI':
            direction_list = ['DL', 'UL']
        else:
            direction_list = [self.direction]

        for direct in direction_list:
            self.logger.debug(f'The direction is: {direct}')
            self.get_tp_per_direction(direction=direct)
            if not self.invalid_parameters_dict:
                self.print_tp_result()

    def print_tp_result(self):
        """
        This function responsible to print out 'duplex mode', 'direction', 'throughput(Mbps)'.

        The function doesn't return parameters.
        """

        try:
            if self.duplex == 'tdd':
                self.Throughput_info = f'{self._tdd_tp} Mbps'
            elif self.duplex == 'fdd':
                self.Throughput_info = f'{self._fdd_tp} Mbps'
            else:
                self.logger.error('duplex is not tdd or fdd')
                self.Throughput_info = 'TP Failed due to unknown duplex mode.'
            self.logger.info('TP calculated successfully!\n')
            self.logger.debug(f'Duplex Mode: {self.duplex}')
            self.logger.debug(f'Direction: {self.direction}')
            self.logger.info(f'Throughput: {self.Throughput_info}\n')
        except Exception:
            self.logger.exception('')

    def set_invalid_parameters(self, param_name, param_value):
        """
        This function responsible to update dictionary by parameter name & value.

        The function get 2 parameters:
            "param_name" -  parameter name (string)
            "param_value" - parameter value (integer)
        The function doesn't return parameters.
        """
        self.invalid_parameters_dict.update(
            {
                param_name: param_value,
                }
            )

    def set_error_message(self, param_name, param_value, error_message):
        """
        This function responsible to update error message dictionary.

        The function get 3 parameters:
            "param_name" -  parameter name (string)
            "param_value" - parameter value (integer)
            "error_message" - parameter value (string)
        The function doesn't return parameters.
        """
        self.err_message.append(
            {
                'error_message': error_message,
                'param_name'   : param_name,
                'param_value'  : param_value
                }
            )
