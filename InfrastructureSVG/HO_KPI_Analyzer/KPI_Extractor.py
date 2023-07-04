import logging
import os
import numpy as np
import pandas as pd
from typing import List, Dict

from InfrastructureSVG.Converters.Converter import Converter


class KpiAnalyzer:
    def __init__(self, files_list: list, path: str):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.files_list = files_list
        self.path = path

    def xml_to_dict(self) -> List[Dict]:
        converter = Converter(self.files_list, self.path)
        return converter.xml_to_dict_converter()

    @staticmethod
    def get_counters_from_dict(xml_dicts: List[Dict], kpi_list: List) -> pd.DataFrame:
        flag = False
        df_list = []
        for index, xml_dict in enumerate(xml_dicts, start=1):
            if isinstance(xml_dict['measDataFile']['measData']['measInfo'], list):
                counters_names = xml_dict['measDataFile']['measData']['measInfo'][0]['measTypes'].split(' ')
                cells = xml_dict['measDataFile']['measData']['measInfo'][0]['measValue']
            else:
                counters_names = xml_dict['measDataFile']['measData']['measInfo']['measTypes'].split(' ')
                cells = xml_dict['measDataFile']['measData']['measInfo']['measValue']
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            data_frame = pd.DataFrame(columns=kpi_list)
            for cell_index, cell in enumerate(cells, start=1):
                if type(cell) != str:
                    cell_counters = cell.get('measResults').split(' ') if cell.get('measResults') else None
                else:
                    try:
                        cell_counters = xml_dict['measDataFile']['measData']['measInfo']['measValue'].get('measResults').split(' ') or None
                    except TypeError:
                        cell_counters = xml_dict['measDataFile']['measData']['measInfo'][0]['measValue'].get('measResults').split(' ') or None
                    flag = True
                if cell_counters:
                    cell_counters = [int(i) for i in cell_counters]
                    kpi_names_values_dict = dict(zip(counters_names, cell_counters))
                    values_list = [kpi_names_values_dict[i] for i in kpi_list]
                    data_frame = pd.concat([data_frame, pd.DataFrame([values_list], columns=kpi_list)])
                    if flag:
                        break

            data_frame.index = np.arange(1, len(data_frame) + 1)
            df_list.append(data_frame)

        df = pd.concat(df_list).groupby(level=0).sum()

        for column in df.columns:
            df[f'Total_{column}'] = df[column].sum()
        return df


if __name__ == '__main__':
    file_names = os.listdir('C:\\temp')
    analyzer_obj = KpiAnalyzer(file_names, 'C:\\temp')
    xml_list = analyzer_obj.xml_to_dict()
    kpis_list = ['MM.HoPrepIntraReq', 'MM.HoExeIntraReq', 'MM.HoExeIntraSucc', 'MM.HoPrepIntraSucc']
    kpi_data_frame = analyzer_obj.get_counters_from_dict(xml_list, kpis_list)
    print(f"Cell 1 HoPrepIntraReq: {kpi_data_frame['MM.HoPrepIntraReq'][1]}")
    print(f"Cell 1 HoExeIntraReq: {kpi_data_frame['MM.HoExeIntraReq'][1]}")
    print(f"Cell 1 HoExeIntraSucc: {kpi_data_frame['MM.HoExeIntraSucc'][1]}")
    print(f"Cell 1 HoPrepIntraSucc: {kpi_data_frame['MM.HoPrepIntraSucc'][1]}")
    print(f"Cell 2 HoExeIntraReq: {kpi_data_frame['MM.HoExeIntraReq'][2]}")
    print(f"Cell 2 HoPrepIntraReq: {kpi_data_frame['MM.HoPrepIntraReq'][2]}")
    print(f"Cell 2 HoExeIntraSucc: {kpi_data_frame['MM.HoExeIntraSucc'][2]}")
    print(f"Cell 2 HoPrepIntraSucc: {kpi_data_frame['MM.HoPrepIntraSucc'][2]}")
    print(f"Total_HoPrepIntraSucc: {kpi_data_frame['Total_MM.HoPrepIntraSucc'][2]}")
    print(f"Total_HoPrepIntraSucc: {kpi_data_frame['Total_MM.HoPrepIntraSucc'][2]}")
    print(f"Total_HoPrepIntraSucc: {kpi_data_frame['Total_MM.HoPrepIntraSucc'][2]}")
    print(f"Total_HoPrepIntraSucc: {kpi_data_frame['Total_MM.HoPrepIntraSucc'][2]}")
    print()
