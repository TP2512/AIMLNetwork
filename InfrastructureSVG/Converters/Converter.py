import logging
import xmltodict
import pandas as pd
from typing import List, Dict


class Converter:
    def __init__(self, files_list: list, path: str):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.files_list = files_list
        self.path = path

    def xml_to_dict_converter(self) -> List[Dict]:
        counters_dict = []
        for index, file in enumerate(self.files_list, start=1):
            self.logger.info(f'{index}, {file}')
            with open(f'{self.path}\\{file}', 'r') as f:
                counters_dict.append(xmltodict.parse(f.read(), xml_attribs=False))
        return counters_dict

    def csv_to_dict_converter(self):
        by_raw_list = []
        by_column_list = []
        for index, file in enumerate(self.files_list, start=1):
            df = pd.read_csv(f'{self.path}\\{file}')
            by_raw_list.append(df.T.to_dict())
            by_column_list.append(df.to_dict())
        return by_raw_list, by_column_list


if __name__ == '__main__':
    converter = Converter(['CU-UPExport_20221108_1542.csv'], 'C:\\tmp')
    x = converter.csv_to_dict_converter()




