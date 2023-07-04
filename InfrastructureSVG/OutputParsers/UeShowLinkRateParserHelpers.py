import contextlib
import logging
import re
import os
import pandas as pd
from typing import Union, List


class ParserHelper:
    def __init__(self, protocol: str):
        self.logger = logging.getLogger(
            f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}'
        )
        self.link_table_list = []
        self.rate_table_list = []
        self.original_table = None
        self.cell1_ues = 0
        self.cell2_ues = 0
        self.total_connected_ues = 0
        self.df = None
        self.protocol = protocol
        self.link_pattern = '(?s)(\\| (RN.*?))(Total)'
        self.rate_pattern = '(?s)(\\|(UE-ID.*?))(Total)'
        self.total_rate_pattern = r'(?s)(Total:(.*?)(DL-TPT.*?)Connected UEs: \d{1,4})'
        self.connected_pattern = r'Connected UEs: (\d{1,4})'
        self.cu_connected_pattern = r'Total UE connected: (\d{1,4})'

    def get_table(self, **kwargs):

        if kwargs.get('output'):
            self.original_table = kwargs['output'] if kwargs.get('output') else self.logger.info('')
        elif kwargs.get('file') and os.path.isfile(kwargs.get('file')):
            with open(kwargs['file'], 'r') as f:
                self.original_table = f.read()
        elif kwargs.get('path') and os.path.isdir(kwargs.get('path')):
            for dir_path, dir_names, file_names in os.walk(kwargs.get('path')):
                for folder in dir_names:
                    if folder == kwargs.get('gnb'):
                        self.get_table(path=f"{kwargs.get('path')}\\{folder}", host=kwargs.get('host'), gnb=kwargs.get('gnb'))
                        if self.original_table:
                            return
                    elif kwargs.get('host').lower() in folder.lower() and 'ue_show' in folder.lower():
                        if filelist := os.listdir(f"{kwargs.get('path')}\\{folder}"):
                            with open(f"{kwargs.get('path')}\\{folder}\\{filelist[0]}", 'r') as f:
                                self.original_table = f.read()
                            return

    @staticmethod
    def clean_table(table: List):
        first_clean = [i.replace('\t', '') for i in table if '--' not in i and '==' not in i]
        return [i for i in first_clean if i]

    def extract_table_with_regex(self, table: str, pattern: str, group: int, table_name: str, find_all: bool = False) -> Union[list, None]:
        if find_all:
            return re.findall(pattern, table, re.DOTALL)
        if re.search(pattern, table):
            return re.search(pattern, table)[group].replace('ue show link', '').replace('ue show rate', '').replace('Nr_cli:>>', '').split('\n')

        self.logger.warning(f'{table_name} table is not found')

        return None

    def extract_rate_table_with_regex(self, table: str, traffic_direction):
        pattern = r'(\*\*\*UL TP statistics\*\*\*)(.*?)(Total)' if traffic_direction == 'UL' else r'(\*\*\*DL TP statistics\*\*\*)(.*?)(Total)'
        # matches = re.finditer(r'(\*\*\*UL TP statistics\*\*\*)(.*?)(\*\*\*DL TP statistics\*\*\*)', table, re.DOTALL)
        if re.search(pattern, table, re.DOTALL):
            matches = re.findall(pattern, table, re.DOTALL)[2]
            cleaned_list = [i.replace('\r', '') for i in self.clean_table(matches.split('\n')) if i.replace('\r', '') and i.replace('\r', '') != ' ' and 'ue' not in i and 'cli' not in i]
            if len(cleaned_list) > 1:
                return self.get_data_frame(cleaned_list, rate=True)
        return None

    def parse_cucp_link_table(self, table):
        unsorted_ues = [i.replace('\n', '') for i in table]
        ue_id = {}
        key = None
        value = None
        for ue in unsorted_ues:
            if rnti := re.search(r'(rnti):(\d{1,20})', ue):
                if not ue_id.get(rnti[1]):
                    ue_id[rnti[1]] = []
                    key = 'rnti'
                    value = rnti[2]
            elif ueid := re.search(r'(UE Id):(\d{1,20})', ue):
                if not ue_id.get(ueid[1]):
                    ue_id[ueid[1]] = []
                    key = 'UE Id'
                    value = ueid[2]
            elif amf_id := re.search(r'(amfId):(\d{1,20})', ue):
                if not ue_id.get(amf_id[1]):
                    ue_id[amf_id[1]] = []
                    key = 'amfId'
                    value = amf_id[2]
            if key and value:
                ue_id[key].append(value)
                key, value = None, None
            else:
                return pd.DataFrame()

        try:
            return pd.DataFrame(ue_id)
        except ValueError:
            self.logger.info(ue_id)
            return None

    def parse_cuup_rate_table(self, table, traffic_direction):
        return self.extract_rate_table_with_regex(table, traffic_direction)

    @staticmethod
    def get_total_connected_ues(table, string_name, all_ues=False):
        if not all_ues and re.search(string_name, table):
            return int(re.search(string_name, table)[1])
        elif re.findall(string_name, table):
            return any(int(i) for i in re.findall(string_name, table))
        # self.logger.warning(f'{string_name} string is not found')
        return None

    def get_connected_ues_per_cell(self, df):
        self.cell1_ues = \
            int(df.value_counts().get(1 if self.protocol == '5g' else 0)) if df.value_counts().get(1 if self.protocol == '5g' else 0) is not None else 0

        self.cell2_ues = \
            int(df.value_counts().get(2 if self.protocol == '5g' else 1)) if df.value_counts().get(2 if self.protocol == '5g' else 1) is not None else 0

    def link_5g_table_iterator(self, clean_link_table):
        headers = []
        link_header = []
        line1 = None
        for index, line in enumerate(clean_link_table):
            if index == 0:
                line1 = line.replace(' ', '').split('|')[:-1]
                headers = [[i for i in line1 if i not in ['', '\n', '-']]]
            elif index == 1:
                line2 = line.split('|')[:-1][1:]
                if len(line2) != len(line1):
                    line2.insert(8, '')
                # line2.insert(8, '')
                for index_item, item in enumerate(line2):
                    line2[index_item] = item.rstrip().lstrip()
                line2 = [i for i in line2 if i not in ['\n']]
                # line2.insert(-3, '')
                headers.append(line2)

        for index1, j in enumerate(headers[0]):
            if headers[1][index1]:
                link_header.append(f'{j} {headers[1][index1]}')
            else:
                link_header.append(j)

        return link_header, self.extract_lines_from_table(clean_link_table)

    @staticmethod
    def rate_5g_table_iterator(table):
        table_for_df = []
        rate_header = []
        for index, line in enumerate(table):
            if index == 0:
                rate_header = line.rstrip('|\r').split('|')
                rate_header = [x.rstrip() for x in rate_header if x]
            elif line and '--' not in line or '==' not in line:
                row = line.rstrip('|\r').lstrip('|').replace('|', '').split(' ')
                row = [x.rstrip().lstrip() for x in row if x]
                # row = list(filter(None, row))
                table_for_df.append(row)

        return rate_header, table_for_df

    @staticmethod
    def validate_rx_ul_dl_field(df):
        return int(df[0].split('/')[2]) if len(df[0].split('/')) == 3 else 1

    def link_5g_column_parser(self, df, single=False):
        # df['Total_Connected UEs'] = self.get_total_connected_ues(orig_table, r'Connected UEs: (\d{1,4})')
        df['CELL-ID'] = df['CELL-ID'].apply(lambda x: int(x))
        df['DL-MCS CW-0'] = df['DL-MCS CW-0/1'].apply(lambda x: int(x.split('/')[0]))
        df['DL-MCS CW-1'] = df['DL-MCS CW-0/1'].apply(lambda x: int(x.split('/')[1]))
        df['UL-MCS CW-0'] = df['UL-MCS CW-0/1'].apply(lambda x: int(x.split('/')[0]))
        df['UL-MCS CW-1'] = df['UL-MCS CW-0/1'].apply(lambda x: int(x.split('/')[1]))
        df['C2I'] = df['C2I'].apply(lambda x: float(x))
        df['RI RX'] = df['RI RX/UL/DL'].apply(lambda x: int(x.split('/')[0]))
        df['RI UL'] = df['RI RX/UL/DL'].apply(lambda x: int(x.split('/')[1]))
        df['RI DL'] = df['RI RX/UL/DL'].apply(lambda x: self.validate_rx_ul_dl_field(df['RI RX/UL/DL']))
        df['DL-BLER %CW-0'] = df['DL-BLER %CW-0/1'].apply(lambda x: int(x.split('/')[0]))
        df['DL-BLER %CW-1'] = df['DL-BLER %CW-0/1'].apply(lambda x: int(x.split('/')[1]))
        df['UL-CQI CW-0'] = df['UL-CQI CW-0/1'].apply(lambda x: int(x.split('/')[0]))
        df['UL-CQI CW-1'] = df['UL-CQI CW-0/1'].apply(lambda x: int(x.split('/')[1]))
        if 'UL-BLER-CRC %%PER' in df.columns:
            df['UL-BLER-CRC %%PER'] = df['UL-BLER-CRC %%PER'].apply(lambda x: int(x))
        if 'UL-BLER-CRC %PER' in df.columns:
            df['UL-BLER-CRC %PER'] = df['UL-BLER-CRC %PER'].apply(lambda x: int(x))
        df['DL-CQI CW-0'] = df['DL-CQI CW-0/1'].apply(lambda x: int(x.split('/')[0]))
        df['DL-CQI CW-1'] = df['DL-CQI CW-0/1'].apply(lambda x: int(x.split('/')[1]))
        df['MEAS GAP ACTIVE'] = df['MEASGAP ACTIVE'].apply(lambda x: int(x.replace('-', '-1').replace('V', '1'))).astype(int)
        df['256QAM Alloc'] = df['256QAM Alloc'].apply(lambda x: int(x.replace('-', '0').replace('V', '1'))).astype(int)
        df['256QAM ACTV'] = df['256QAM ACTV'].apply(lambda x: int(x.replace('V', '1').replace('-', '0'))).astype(int)
        if 'SMALL ALLOC' in df.columns:
            df['SMALL ALLOC'] = df['SMALL ALLOC'].apply(lambda x: int(x.replace('V', '1').replace('-', '0'))).astype(int)
        if 'CA MODE' in df.columns:
            df['CA MODE'] = df['CA MODE'].apply(lambda x: int(x.replace('V', '1').replace('-', '0'))).astype(int)
        df.drop(['UL-MCS CW-0/1', 'DL-MCS CW-0/1', 'RI RX/UL/DL', 'DL-BLER %CW-0/1', 'UL-CQI CW-0/1', 'MEASGAP ACTIVE', 'DL-CQI CW-0/1'], axis=1, inplace=True)
        if single:
            return df
        self.link_table_list.append(df)

    def link_4g_column_parser(self, df, single=False):
        # df['Total_Connected UEs'] = self.get_total_connected_ues(orig_table, r'Connected UEs: (\d{1,4})')
        df['CELL-ID'] = df['CELL-ID'].apply(lambda x: int(x))
        df['RNTI'] = df['RNTI'].apply(lambda x: int(x))
        df['DL-CQI CW-0'] = df['DL-CQI CW 0/1'].apply(lambda x: int(x.split('/')[0]))
        df['DL-CQI CW-1'] = df['DL-CQI CW 0/1'].apply(lambda x: int(x.split('/')[1]))
        df['DL-MCS CW-0'] = df['DL-MCS CW 0/1'].apply(lambda x: int(x.split('/')[0]))
        df['DL-MCS CW-1'] = df['DL-MCS CW 0/1'].apply(lambda x: int(x.split('/')[1]))
        df['256QAM Alloc'] = df['256QAM Alloc'].apply(lambda x: int(x.replace('-', '0').replace('V', '1'))).astype(int)
        df['DL %PER'] = df['DL %PER'].apply(lambda x: int(x))
        df['NACKS'] = df['NACKS'].apply(lambda x: int(x))
        df['RI Rx'] = df['RI Rx/Tx'].apply(lambda x: int(x.split('/')[0]))
        df['RI Tx'] = df['RI Rx/Tx'].apply(lambda x: int(x.split('/')[1]))
        df['UL PHY-CRC'] = df['UL PHY-CRC'].apply(lambda x: int(x))
        df['UL %CRC'] = df['UL %CRC'].apply(lambda x: int(x))
        df['UL MCS'] = df['UL MCS'].apply(lambda x: int(x))
        df['C2I'] = df['C2I'].apply(lambda x: float(x))
        df['RSSI'] = df['RSSI'].apply(lambda x: int(x))
        df['Tim Off'] = df['Tim Off'].apply(lambda x: int(x))
        df['UL Agr'] = df['UL Agr'].apply(lambda x: int(x))
        df['DL Agr'] = df['DL Agr'].apply(lambda x: int(x))
        df['MeasGap Off'] = df['MeasGap Off'].apply(lambda x: int(x.replace('NA', '-1').replace('V', '1'))).astype(int)
        df['UL-PHY CW-1'] = df['DL-CQI CW 0/1'].apply(lambda x: int(x.split('/')[1]))
        df['256QAM ACTV'] = df['256QAM ACTV'].apply(lambda x: int(x.replace('V', '1').replace('-', '0'))).astype(int)
        df['DRX ?'] = df['DRX ?'].apply(lambda x: int(x.replace('V', '1').replace('-', '0'))).astype(int)
        df.drop(['DL-MCS CW 0/1', 'RI Rx/Tx', 'DL-CQI CW 0/1'], axis=1, inplace=True)
        if single:
            return df
        self.link_table_list.append(df)

    def parse_link_columns(self, df, single=False):
        if self.protocol == '5g':
            return self.link_5g_column_parser(df, single)
        elif self.protocol == '4g':
            return self.link_4g_column_parser(df, single)

    def parse_cu_link_columns(self, df, single=False):
        if df is None or df.empty:
            return None
        try:
            df['CUCP_UE_Id'] = df['UE Id'].astype(int)
            df['CUCP_rnti'] = df['rnti'].astype(int)
            df['CUCP_amfId'] = df['amfId'].astype(int)
            df.drop(['UE Id', 'rnti', 'amfId'], axis=1, inplace=True)
            if single:
                return df
            self.link_table_list.append(df)
        except Exception:
            if single:
                return pd.DataFrame()

    @staticmethod
    def parse_cu_rate_columns(df_list):
        # df['Total_Connected UEs'] = self.get_total_connected_ues(orig_table, r'Connected UEs: (\d{1,4})')
        new_df = pd.DataFrame()
        for index, df in enumerate(df_list):
            with contextlib.suppress(Exception):
                if df is not None:
                    if 'CUUP_UE_ID' not in new_df.columns or 'BEARER ID' in new_df.columns:
                        new_df['CUUP_UE_ID'] = df['UE_ID'].mask(df['UE_ID'].eq('')).dropna().astype(int)
                        new_df['CUUP_BEARER ID'] = df['BEARER ID'].mask(df['BEARER ID'].eq('')).dropna().astype(int)
                    if index == 0:
                        new_df['UL_CUUP_PDCP(Mbps)'] = df['PDCP(Mbps)'].mask(df['PDCP(Mbps)'].eq('')).dropna().astype(float)
                        new_df['UL_CUUP_EGTP(Mbps)'] = df['EGTP(Mbps)'].mask(df['EGTP(Mbps)'].eq('')).dropna().astype(float)
                    elif index == 1:
                        new_df['DL_CUUP_PDCP(Mbps)'] = df['PDCP(Mbps)'].mask(df['PDCP(Mbps)'].eq('')).dropna().astype(float)
                        new_df['DL_CUUP_EGTP(Mbps)'] = df['EGTP(Mbps)'].mask(df['EGTP(Mbps)'].eq('')).dropna().astype(float)
        return new_df

    @staticmethod
    def parse_5g_rate_columns(df):
        # df['Total_Connected UEs'] = self.get_total_connected_ues(orig_table, r'Connected UEs: (\d{1,4})')
        df['UE-ID'] = df['UE-ID'].apply(lambda x: int(x))
        df['PCELL-ID'] = df['PCELL-ID'].apply(lambda x: int(x))
        df['DL-TPT (Mb)'] = df['DL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['UL-TPT (Mb)'] = df['UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['DL-PKT-RX'] = df['DL-PKT-RX'].apply(lambda x: int(x))
        df['RLC-DL-TPT (Mb)'] = df['RLC-DL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['RLC-UL-TPT (Mb)'] = df['RLC-UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['MAC-DL-TPT (Mb)'] = df['MAC-DL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['MAC-UL-TPT (Mb)'] = df['MAC-UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['CL-DL-TPT (Mb)'] = df['MAC-UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['CL-UL-TPT (Mb)'] = df['CL-UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['UL-PKT-TX'] = df['UL-PKT-TX'].apply(lambda x: int(x))
        df['NUM-SR'] = df['NUM-SR'].apply(lambda x: int(x))

        return df

    @staticmethod
    def parse_4g_rate_columns(df):
        # df['Total_Connected UEs'] = self.get_total_connected_ues(orig_table, r'Connected UEs: (\d{1,4})')
        df['RNTI'] = df['RNTI'].apply(lambda x: int(x))
        df['PDCP-UL'] = df['PDCP-UL'].apply(lambda x: float("%.2f" % float(x)))
        df['RB-UL'] = df['RB-UL'].apply(lambda x: int(x.replace('K|M', '')))
        df['PHY-UL'] = df['PHY-UL'].apply(lambda x: float("%.2f" % float(x)))
        df['PHY-UL RETX'] = df['PHY-UL RETX'].apply(lambda x: int(x))
        df['EGTP-DL'] = df['EGTP-DL'].apply(lambda x: float("%.2f" % float(x)))
        df['PDCP-DL'] = df['PDCP-DL'].apply(lambda x: float("%.2f" % float(x)))
        df['RLC-DL'] = df['RLC-DL'].apply(lambda x: float("%.2f" % float(x)))
        df['RLC-DL RETX-BYTE'] = df['RLC-DL RETX-BYTE'].apply(lambda x: int(x))
        df['MAC-DL'] = df['MAC-DL'].apply(lambda x: float("%.2f" % float(x)))
        df['PHY-DL'] = df['PHY-DL'].apply(lambda x: float("%.2f" % float(x)))
        df['PHY-DL RETX'] = df['PHY-DL RETX'].apply(lambda x: int(x))
        df['PDCP-PPS'] = df['PDCP-PPS'].apply(lambda x: int(x))
        df['PHY-TBPS'] = df['PHY-TBPS'].apply(lambda x: int(x))
        df['EGTP-DL PPS'] = df['EGTP-DL PPS'].apply(lambda x: int(x))
        df['EGTP-UL PPS'] = df['EGTP-UL PPS'].apply(lambda x: int(x))
        df['UL-ALLOC'] = df['UL-ALLOC'].apply(lambda x: float("%.2f" % float(x)))
        df['LATE'] = df['LATE'].apply(lambda x: int(x))

        return df

    def parse_rate_columns(self, df):
        if self.protocol == '5g':
            return self.parse_5g_rate_columns(df)
        elif self.protocol == '4g':
            return self.parse_4g_rate_columns(df)

    def parse_total_rate_columns(self, df, total_df, orig_table):
        df['Total_Connected UEs'] = self.get_total_connected_ues(orig_table, r'Connected UEs: (\d{1,4})')
        df['Total_DL-TPT (Mb)'] = total_df['DL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['Total_UL-TPT (Mb)'] = total_df['UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['Total_DL-PKT-RX'] = total_df['DL-PKT-RX'].apply(lambda x: int(x))
        df['Total_RLC-DL-TPT (Mb)'] = total_df['RLC-DL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['Total_RLC-UL-TPT (Mb)'] = total_df['RLC-UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['Total_MAC-DL-TPT (Mb)'] = total_df['MAC-DL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['Total_MAC-UL-TPT (Mb)'] = total_df['MAC-UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['Total_CL-DL-TPT (Mb)'] = total_df['MAC-UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['Total_CL-UL-TPT (Mb)'] = total_df['CL-UL-TPT (Mb)'].apply(lambda x: float("%.2f" % float(x)))
        df['Total_UL-PKT-TX'] = total_df['UL-PKT-TX'].apply(lambda x: int(x))
        df['Total_NUM-SR'] = total_df['NUM-SR'].apply(lambda x: int(x))
        return df

    def data_frame_5g_parser(self, table, rate, link, total):
        if link:
            headers, rows = self.link_5g_table_iterator(self.clean_table(table))
            return self.table_to_df(headers, rows)

        if rate:
            headers, rows = self.rate_5g_table_iterator(self.clean_table(table))
            return self.table_to_df(headers, rows)

        if total:
            total_headers, total_rows = self.rate_5g_table_iterator(self.clean_table(table))
            return self.table_to_df(total_headers, total_rows)

    @staticmethod
    def combine_link_lists(list1, list2, list3):
        combined_list = []
        for i, (item1, item2, item3) in enumerate(zip(list1, list2, list3)):
            if not list2[i]:
                combined_list.append(item1)
            elif list1[i] and list2[i] and not list3[i]:
                combined_list.append(f'{item1} {list2[i]}')
            if list3[i]:
                combined_list.append(f'{item1} {list2[i]} {list3[i]}')

        return combined_list

    @staticmethod
    def combine_rate_lists(list1, list2):
        combined_list = []
        for i, (item1, item2) in enumerate(zip(list1, list2)):
            if not list2[i]:
                combined_list.append(item1)
            elif list1[i] and list2[i]:
                combined_list.append(f'{item1} {list2[i]}')

        return combined_list

    def extract_headers(self, table, link=False, rate=False):
        rows = table[1].split("\n")
        headers_1 = [i.rstrip().lstrip() for i in rows[2].split('|')[2:][:-1]]
        headers_2 = [None if s.strip() == '' else s.rstrip().lstrip() for s in rows[3].split('|')[2:][:-1]]
        headers_3 = [None if s.strip() == '' else s.rstrip().lstrip() for s in rows[4].split('|')[2:][:-1]]
        return self.combine_link_lists(headers_1, headers_2, headers_3) if link else self.combine_rate_lists(headers_1, headers_2)

    def link_4g_table_iterator(self, tables, pattern, rate=False, link=False):
        dataframes = []
        for table in tables:
            for index, cell in enumerate(re.findall(pattern, table), start=1):
                cell_index = index if link else int(re.search('Cell (\\d)', cell[0])[1])
                headers = self.extract_headers(cell, link, rate)
                headers.append('CELL-ID')
                table_index = 5 if rate else 6
                table_to_parse = cell[1].split("\n")[table_index:]
                rows = self.extract_lines_from_table4g(table_to_parse, cell_index, rate)
                dataframes.append(self.table_to_df(headers, rows))
        return pd.concat(dataframes, ignore_index=True)

    def data_frame_4g_parser(self, tables, rate, link):
        if link:
            return self.link_4g_table_iterator(tables, '(Cell \\d+) =+([\\s\\S]*?)=+', rate, link)
        if rate:
            return self.link_4g_table_iterator(tables, '(Cell \\d+)([\\s\\S]*?)(?=\n=)', rate, link)

    def get_data_frame(self, table: List[List], rate=False, link=False, total=False) -> pd.DataFrame:
        if self.protocol == '5g':
            return self.data_frame_5g_parser(table, rate, link, total)
        elif self.protocol == '4g':
            return self.data_frame_4g_parser(table, rate, link)

    def get_ue_show_link_rate_df_lists(self, **kwargs):
        self.get_table(**kwargs)
        tables = self.original_table.split('Nr_cli:>>')
        rate_table_df = None
        for table in tables:
            rate_table = self.extract_table_with_regex(table, self.rate_pattern, 2, 'Ue Show Rate')
            total_rate_table = self.extract_table_with_regex(table, self.total_rate_pattern, 3, 'Ue Show Rate')
            link_table = self.extract_table_with_regex(table, self.link_pattern, 2, 'Ue Show Link')
            if rate_table:
                rate_table_df = self.parse_rate_columns(self.get_data_frame(rate_table, rate=True))
            if total_rate_table:
                total_rate_table_df = self.get_data_frame(rate_table, total=True)
                self.rate_table_list.append(self.parse_total_rate_columns(rate_table_df, total_rate_table_df, "".join(table)))
            if link_table:
                self.parse_link_columns(self.get_data_frame(link_table, link=True))

    def get_total_table(self):
        table = ''.join(self.original_table)
        total_table_header = ''
        total_table_for_df = ''
        total_table = table.split('Total:')[1].split('\n')
        total_table = [i.replace('\t', '') for i in total_table if i not in '' and '=' not in i and 'Connected' not in i]
        for index1, line1 in enumerate(total_table):
            if index1 == 0:
                total_table_header = line1.split('|')[1:][:-1]
                total_table_header[0] = total_table_header[0].replace(' ', '')
                total_table_header[1] = total_table_header[1].replace(' ', '')
            else:
                total_table_for_df = [line1.replace(' ', '').split('|')[1:][:-1]]

        return total_table_header, total_table_for_df

    @staticmethod
    def extract_lines_from_table(table):
        table_for_df = []
        for table_index, line in enumerate(table):
            if table_index in [0, 1] or '--' in line:
                continue
            line = line.split()
            for index, param in enumerate(line):
                if index != 0 and index != len(line) - 1 and param == "|" and line[index + 1] == "|":
                    line.insert(index + 1, "-")
            line = "".join(line)
            line3 = line.replace(' ', '').replace('\t', '').split('|')
            if line3 := [i for i in line3 if i not in ['', '\n', '\r']]:
                table_for_df.append(line3)

        return table_for_df

    @staticmethod
    def extract_lines_from_table4g(table, cell_index, rate=False):
        table_for_df = []
        for index, line in enumerate(table):
            if '--' in line or 'Total' in line:
                continue
            line = (
                [
                    re.sub('[KM]', '', value.strip())
                    if value.strip() != ''
                    else 'N/A'
                    for value in line.strip().split('|')[2:]
                ]
                if rate
                else [
                    value.strip() if value.strip() != '' else 'N/A'
                    for value in line.strip().split('|')[2:-1]
                ]
            )
            if line:
                line.append(f'{cell_index + 1 if cell_index == 0 else cell_index}')
                table_for_df.append(line)

        return table_for_df

    @staticmethod
    def table_to_df(header, table, total_table_header=None):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        df = pd.DataFrame(table, columns=header)
        return (df, pd.DataFrame(table, columns=header)) if total_table_header else df

    @staticmethod
    def calculate_fields(df):
        COLUMNS = [
            'RNTI',
            'DL-MCS CW-0',
            'DL-MCS CW-1',
            'UL-MCS CW-0',
            'UL-MCS CW-1',
            'C2I',
            'RI RX',
            'RI UL',
            'RI DL',
            'DL-BLER %CW-0',
            'DL-BLER %CW-1',
            'UL-CQI CW-0',
            'UL-CQI CW-1',
            'UL-BLER-CRC %%PER',
            'DL-CQI CW-0',
            'DL-CQI CW-1',
        ]
        new_df = pd.DataFrame(columns=COLUMNS)
        for rnti in df['RNTI'].unique():
            ue = df.loc[df['RNTI'] == rnti]

            if 'UL-BLER-CRC %%PER' in df.columns:
                bler = ue['UL-BLER-CRC %%PER'].mean()
            elif 'UL-BLER-CRC %PER' in df.columns:
                bler = ue['UL-BLER-CRC %PER'].mean()
            else:
                bler = 0
            row = [
                rnti,
                ue['DL-MCS CW-0'].mean(),
                ue['DL-MCS CW-1'].mean(),
                ue['UL-MCS CW-0'].mean(),
                ue['UL-MCS CW-1'].mean(),
                ue['C2I'].mean(),
                ue['RI RX'].mean(),
                ue['RI UL'].mean(),
                ue['RI DL'].mean(),
                ue['DL-BLER %CW-0'].mean(),
                ue['DL-BLER %CW-1'].mean(),
                ue['UL-CQI CW-0'].mean(),
                ue['UL-CQI CW-1'].mean(),
                bler,
                ue['DL-CQI CW-0'].mean(),
                ue['DL-CQI CW-1'].mean(),
            ]
            new_row = pd.DataFrame([row], columns=COLUMNS)
            new_df = pd.concat([new_df, new_row], ignore_index=True)

        return new_df
