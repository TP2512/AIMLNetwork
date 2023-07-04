import logging
from itertools import islice
from InfrastructureSVG.Rate_Converter.Rate_Converter import RateConverter
import csv


class IperfCsvAnalyzer(RateConverter):
    def __init__(self, file, path, traffic_direction, dl_threshold, ul_threshold):
        super().__init__()
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.tp_ue1 = []
        self.tp_ue2 = []
        self.tp_ue_tot = []
        self.dl_threshold_list = []
        self.ul_threshold_list = []
        self.column_list = []
        self.list_for_check = []
        self.file = file
        self.path = path
        self.dl_threshold = dl_threshold
        self.ul_threshold = ul_threshold
        self.traffic_direction = traffic_direction
        self.csv_analyzer()
        self.build_graph_data(self.dl_threshold, self.ul_threshold)

    def get_line(self, index, start_line, string_name):
        return next((j for j, row in enumerate(self.file, start=1) if row != [] and j == start_line and string_name in row[index]), None)

    def get_line_(self, start_line):
        line = None
        if self.file:
            for j, row in enumerate(self.file, start=1):
                if row != [] and j == start_line:
                    line = j
                    break
        else:
            self.logger.warning('file parameter is empty')

        return line

    def get_column(self, line):
        bw = []
        try:
            if line:
                with open(self.path) as fd:
                    for row in islice(csv.reader(fd), line, None):
                        if row:
                            bw.append(row[8])
                        else:
                            break
            else:
                self.logger.warning('line parameter is empty')
            self.logger.info(f"len bw_ is:{len(bw)}")
            tp_list = bw[:len(bw)-5]
            self.logger.info(f"len tp_list is:{len(tp_list)}")
            return tp_list
        except IndexError:
            self.logger.debug(f"len bw_ is:{len(bw)}")
            tp_list = bw[:len(bw) - 5]
            self.logger.debug(f"len tp_list is:{len(tp_list)}")
            return tp_list

    def csv_analyzer(self):
        index_for_append = 0
        old_row_ul_dl = None
        old_row_timestamp = None
        if self.file:
            if 'UL' in self.traffic_direction:
                ul_dl = 'Up link Raw Data'
            else:
                ul_dl = 'Down link Raw Data'
            string_name = 'Session Name:Iperf_Session_UE'
            tmp = []
            for j, row in enumerate(self.file, start=1):
                if row:
                    if string_name in row[0]:
                        line_number = self.get_line(0, j, row[0])
                        tmp.append([row[0], line_number])
                    elif old_row_ul_dl and old_row_ul_dl[0] == ul_dl and \
                            old_row_timestamp and old_row_timestamp[0] == 'timestamp':
                        line_number = self.get_line(0, j, row[0])
                        tmp[index_for_append].append(line_number)
                        index_for_append = index_for_append + 1
                    old_row_ul_dl = old_row_timestamp
                    old_row_timestamp = row

            for i, tmp_index in enumerate(tmp, start=1):
                if tmp_index[0] not in self.list_for_check:
                    try:
                        self.column_list.append(self.get_column(self.get_line_(int(tmp_index[2]) + 1)))
                    except IndexError:
                        pass
                    self.list_for_check.append(tmp_index[0])
        else:
            self.logger.warning('file parameter is empty')

    def build_graph_data(self, dl_threshold, ul_threshold):
        value_1 = 0
        value_2 = 0
        if self.column_list:
            len2 = len(self.column_list[1]) if len(self.column_list) != 1 else ''
            len1 = len(self.column_list[0])
            if not len2:
                len_max = len1
                for i in range(len_max):
                    try:
                        self.tp_ue1.append(RateConverter().rate_converter(int(self.column_list[0][i])))
                        self.dl_threshold_list.append(float(dl_threshold))
                        self.ul_threshold_list.append(float(ul_threshold))
                    except IndexError:
                        pass
            else:
                len_max = max(len1, len2)
                for i in range(len_max):
                    try:
                        if self.column_list[0]:
                            self.tp_ue1.append(self.rate_converter(int(self.column_list[0][i])))

                        if self.column_list[1]:
                            self.tp_ue2.append(self.rate_converter(int(self.column_list[1][i])))

                        if self.column_list[0]:
                            value_1 = value_1 = self.column_list[0][i]

                        if self.column_list[1]:
                            value_2 = self.column_list[1][i]

                        self.tp_ue_tot.append(self.rate_converter(int(value_1) + int(value_2)))
                        self.dl_threshold_list.append(float(dl_threshold))
                        self.ul_threshold_list.append(float(ul_threshold))

                    except IndexError:
                        pass
        else:
            self.logger.warning('column_list parameter is empty')
