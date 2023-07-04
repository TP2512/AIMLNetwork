import logging
import datetime


class SortAndCombineLogs:
    def __init__(self, logs, path=None):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.logs = logs
        self.path = path

    def combine_logs(self, enb_1, enb_2):
        enb_1_logs = []
        if not enb_1:
            enb_1 = ''
        if not enb_2:
            enb_2 = ''
        enb1_dan1_log = [f'{enb_1}_dan1_log']
        enb1_dan2_log = [f'{enb_1}_dan2_log']
        enb_2_logs = []
        enb2_dan1_log = [f'{enb_2}_dan1_log']
        enb2_dan2_log = [f'{enb_2}_dan2_log']
        for index, enb_number in enumerate(self.logs, start=1):
            _combined_log = []
            for log in enb_number:
                if 'UeShowRate' in log or 'Debug' in log or '.zip' in log:
                    continue
                elif index == 1 and enb_1 in log and 'dans' not in log:
                    with open(self.path + '\\' + log) as file:
                        _log = file.readlines()
                        _combined_log = _combined_log + _log
                elif index == 2 and enb_2 in log and 'dans' not in log:
                    with open(self.path + '\\' + log) as file:
                        _log = file.readlines()
                        _combined_log = _combined_log + _log
                elif 'dans' in log:
                    with open(self.path + '\\' + log) as file:
                        dan_log = file.readlines()
                        if index == 1:
                            if 'dans[0]' in log:
                                enb1_dan1_log += dan_log
                            elif 'dans[1]' in log:
                                enb1_dan2_log += dan_log
                        elif index == 2:
                            if 'dans[0]' in log:
                                enb2_dan1_log += dan_log
                            elif 'dans[1]' in log:
                                enb2_dan2_log += dan_log
            if index == 1:
                enb_1_logs = _combined_log
                enb_1_logs = list(set(enb_1_logs))
            elif index == 2:
                enb_2_logs = _combined_log
                enb_2_logs = list(set(enb_2_logs))
        return enb_1_logs, enb1_dan1_log, enb1_dan2_log, enb_2_logs, enb2_dan1_log, enb2_dan2_log

    def sort_log_by_timestamp(self):
        all_logs = self.logs
        timestamp_list = []
        timestamp_ = ''
        enb_1_log = ['enb_1_log']
        enb_2_log = ['enb_2_log']
        for index_1, session_log in enumerate(all_logs, start=0):
            if not session_log:
                continue

            new_timestamp_list = []
            for index_2, session_log_line in enumerate(session_log, start=0):
                try:
                    time_line = session_log_line.split('    ::     ')
                    timestamp_ = datetime.datetime.strptime(
                        time_line[0], '%d/%m/%Y %H:%M:%S:%f').strftime('%Y/%m/%d %H:%M:%S:%f')
                except Exception:
                    try:
                        time_line = session_log_line.split('::')
                        timestamp_ = datetime.datetime.strptime(
                            time_line[0], '%d-%m-%Y-%H:%M:%S').strftime('%Y/%m/%d %H:%M:%S:%f')
                    except Exception:
                        pass
                if timestamp_ != '':
                    new_timestamp_list.append((timestamp_, session_log_line))
                    timestamp_list.append(timestamp_)
            timestamp__sort = sorted(new_timestamp_list, key=lambda annotated_line: annotated_line[0])

            for j in timestamp__sort:
                if index_1 in [0, 1, 2]:
                    enb_1_log.append(j[1])
                elif index_1 in [3, 4, 5]:
                    enb_2_log.append(j[1])
        return enb_1_log, enb_2_log, timestamp_list
