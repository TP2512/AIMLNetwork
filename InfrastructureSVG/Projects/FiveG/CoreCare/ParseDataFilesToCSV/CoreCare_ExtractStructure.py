import contextlib
import logging
import hashlib
import re
import socket

import yaml
import pandas as pd
# from datetime import datetime
# from datetime import timedelta
from abc import ABC, abstractmethod

from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import read_tar_gz_file, PROCESS_LIST, PHY_PROCESS_LIST
from InfrastructureSVG.EZLife.EZLifeMethods import EZLifeMethod


def is_number(number):
    try:
        float(number)
        return True
    except Exception:
        return False


def build_new_summary_for_memory_exhaustion(back_trace):
    bucket_regex = r'Bucket\[\d{1,3}\]'
    bucket = re.search(bucket_regex, back_trace.replace(' -> ', ' , '))[0]

    top_alloc_regex = r'(?<=topAlloc: \[)(.*)(?=\])'
    top_alloc = re.search(top_alloc_regex, back_trace.replace(' -> ', ' , '))[0]
    top_alloc = re.sub(r":\d{1,10}", "", top_alloc)

    return f'M.E: {bucket}, Utilization[>95%], topAlloc: [{top_alloc}]'


class CoreCareExtractStrategy(ABC):
    @abstractmethod
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self._dataframe_crash = None
        self.back_trace_list = None

        self._tar_file = None
        self._tar_members = None

        self.dir_path = None
        self.new_dir_path = None
        self.file_name = None

        self.systeminfo = None
        self.ipinfo = None

        self.crash_type = None
        self.type_crash_name = None
        self.back_trace = ''
        self.memory_exhaustion_back_trace = ''
        self.full_back_trace = ''
        self.old_back_trace = ''
        self.back_trace_hash = None
        self.old_back_trace_hash = None

        self.network_address = None

        self.version_type = None
        self.crash_version = ''
        self.gnb_version = ''
        self.hostname = 'unknown_hostname'
        self.ip_address = 'unknown_ip_address'
        self.setup_name = ''
        self.setup_owner = 'akimiagarov'
        self.system_runtime = 'unknown_system_runtime'
        self.pid = 'unknown_pid'
        self.time_stamp = 'unknown_time_stamp'
        self.tti = 'unknown_tti'
        self.core_validation = {}
        self.core_validation_timestamp = None
        self.user = None  # '"USER" field does not exist'

        self.customer_name = ''

        self.ssh_demangle = None

    @abstractmethod
    def add_to_self(self, tar_file, tar_members, dir_path: str, file_name: str, network_address: str, setup_name_list_path: str, ssh_demangle):
        # sourcery skip: merge-comparisons
        """ Add parameters to self object """

        obj = {
            '_tar_file': tar_file,
            '_tar_members': tar_members,
            'dir_path': dir_path,
            'file_name': file_name,
            'network_address': network_address,
            'ssh_demangle': ssh_demangle,
            '_setup_name_list_path': setup_name_list_path,
        }

        for k, v in obj.items():
            if k != 'logger' and k != 'processing_strategy':
                setattr(self, k, v)

    @abstractmethod
    def change_setup_owner(self, site: str):
        # sourcery skip: merge-comparisons
        """ Change Setup Owner """

        if site == 'IL SVG':
            self.setup_owner = 'akimiagarov'
        elif 'Customer' in site or 'Tier2' in site or 'Tier3' in site:
            self.setup_owner = 'iperelshtein'

    @abstractmethod
    def extract_type_crash_name(self):
        """ Extract "Crash Type" from crash file """

        if 'cucp' in self.file_name:
            self.crash_type = 'cucp'
            self.type_crash_name = 'cucp crash'
        elif 'cuup' in self.file_name:
            self.crash_type = 'cuup'
            self.type_crash_name = 'cuup crash'
        elif 'du' in self.file_name:
            if [p for p in PHY_PROCESS_LIST if p.upper() in self.file_name.upper()]:
                self.crash_type = 'phy'
                self.type_crash_name = 'phy crash'
            else:
                self.crash_type = 'du'
                self.type_crash_name = 'du crash'
        elif 'ru' in self.file_name:
            self.crash_type = 'ru'
            self.type_crash_name = 'ru crash'
        else:
            self.crash_type = 'unknown'
            self.type_crash_name = 'unknown crash'

    # @abstractmethod
    # def build_memory_exhaustion_back_trace(self, entity=None):
    #     """ Build "Memory Exhaustion Back Trace" from crash file """
    #     try:
    #         fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='core_mem_info', entity=entity)
    #     except Exception:
    #         self.logger.exception('The file "core_mem_info" was not open')
    #         fp_read = None
    #
    #     if fp_read:
    #         try:
    #             fp_read_list = fp_read.decode('UTF-8').split('--------- SHOW ALLOCATION INFO ---------')[1].split('\n')
    #
    #             rows = []
    #             for i in fp_read_list:
    #                 if 'Allocations' not in i or 'file' not in i:
    #                     continue
    #
    #                 allocation = re.search(r'(?<=Allocations:)\d{1,5}', i, re.I).group()
    #                 file = re.search(r'(?<=file:)(.*)(?=:\d{1,5})', i, re.I).group().replace(' ', '')
    #                 line = i.split(':')[-1].replace(' ', '')
    #
    #                 row = [allocation, file, line]
    #                 rows.append(row)
    #             mem_info_dataframe = pd.DataFrame(rows, columns=['Allocations', 'file', 'line']).sort_values(by=['Allocations', 'line'], ascending=False)
    #             bt = ''.join(
    #                 f' -> Allocations: {line[0]}, file: {line[1]}:{line[2]}'
    #                 for line in list(mem_info_dataframe.head(4).values)
    #                 if '' not in line and int(line[2]) > 999
    #             )
    #
    #             self.back_trace = '    Memory Exhaustion: ' + bt[4:]
    #         except Exception:
    #             self.logger.exception('')
    #             self.back_trace = ['There is no BT']
    #     else:
    #         self.back_trace = ['There is no BT']

    @staticmethod
    def get_dataframe_table(columns, table):
        dataframe = pd.DataFrame(columns=columns)
        for index, line in enumerate(table.split('\n'), start=0):
            if not line or index == 0:
                continue

            new_row = pd.DataFrame([line.replace('%', '').split()], columns=columns)
            dataframe = pd.concat([dataframe, new_row], ignore_index=True)
        return dataframe

    def get_lower_bucket_ndex_of_max_utilization(self, memory_exhaustion):
        ssi_memory_utilization_table = memory_exhaustion.split('SSI Memory Utilization')[1].split('Top 20 allocators of SSI Dynamic Configuration Memory')[0]
        ssi_memory_utilization_table = re.sub(r"( {10,1000}\n-{1,1000})\n", "", ssi_memory_utilization_table)
        ssi_memory_utilization_table = re.sub(r"(-{1,1000})\n", "", ssi_memory_utilization_table)

        columns = ['BucketIndex', 'ReqSize', 'TotalNumOfBlocks', 'AllocCnt', 'Utilization']
        ssi_memory_utilization_dataframe = self.get_dataframe_table(columns, ssi_memory_utilization_table)
        new_dataframe = pd.DataFrame(columns=columns)
        for i, line in ssi_memory_utilization_dataframe.sort_values(by=['Utilization'], ascending=False).iterrows():
            if is_number(number=line['Utilization'].isdecimal()) and float(line['Utilization']) >= 90 and float(line['Utilization']) >= float(
                    ssi_memory_utilization_dataframe['Utilization'].astype(float).max()):
                new_row = pd.DataFrame([line.tolist()], columns=columns)
                new_dataframe = pd.concat([new_dataframe, new_row], ignore_index=True)

        return new_dataframe['BucketIndex'].min(), new_dataframe['Utilization'].max()

    def get_top_20_allocators_of_ssi_table(self, memory_exhaustion):
        top_20_allocators_of_ssi_table = memory_exhaustion.split('Top 20 allocators of SSI Dynamic Configuration Memory')[1]
        top_20_allocators_of_ssi_table = re.sub(r"( {1,1000}\n={1,1000})\n", "", top_20_allocators_of_ssi_table)
        top_20_allocators_of_ssi_table = re.sub(r"(={1,1000})\n", "", top_20_allocators_of_ssi_table)

        columns = ['S.No#', 'AllocCnt', 'Bucket', 'RegionId', 'ReqSize', 'LineNo', 'SrcFile']
        return self.get_dataframe_table(columns, top_20_allocators_of_ssi_table)

    @abstractmethod
    def build_memory_exhaustion_back_trace(self, entity=None):
        """ Build "Memory Exhaustion Back Trace" from crash file """
        try:
            fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='core_mem_info', entity=entity)
        except Exception:
            self.logger.exception('The file "core_mem_info" was not open')
            fp_read = None

        if fp_read:
            try:
                mem_info_txt = fp_read.decode('UTF-8')

                lower_bucket_ndex_of_max_utilization, max_utilization = self.get_lower_bucket_ndex_of_max_utilization(mem_info_txt)
                if pd.isnull(max_utilization):  # if row[column] is np.nan or row[column] is None or pd.isnull(row[column]) or math.isnan(row[column]):
                    self.memory_exhaustion_back_trace = ''
                    return

                top_20_allocators_of_ssi_dataframe = self.get_top_20_allocators_of_ssi_table(mem_info_txt)
                top_20_allocators_of_ssi_dataframe = top_20_allocators_of_ssi_dataframe.loc[top_20_allocators_of_ssi_dataframe['Bucket'] == str(lower_bucket_ndex_of_max_utilization)]
                print(top_20_allocators_of_ssi_dataframe[:2])

                func_list = [f"{line['SrcFile'].split('/')[-1]}:{line['LineNo']}" for index, line in top_20_allocators_of_ssi_dataframe[:2].iterrows()]
                self.back_trace = f'M.E: Bucket[{lower_bucket_ndex_of_max_utilization}], Utilization[{max_utilization}%] -> topAlloc: [{", ".join(func_list)}]'
                print()
            except Exception:
                self.logger.exception('')
        #         self.back_trace = ['There is no BT']
        # else:
        #     self.back_trace = ['There is no BT']

    @abstractmethod
    def build_old_back_trace(self, entity):
        """ Build "Old Back Trace" from crash file """

        try:
            fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='core_info', entity=entity)
        except Exception:
            self.logger.exception('The file "core_info" was not open')
            fp_read = None

        if fp_read:
            back_trace_list = fp_read.decode("UTF-8").split("\n")
        else:
            back_trace_list = ['There is no BT']

        if not back_trace_list:
            back_trace_list = ['There is no BT']

        # if'du_alloc_from_ngp_pool_debug' in ' '.join(back_trace_list):
        if'alloc_from_ngp_pool_debug' in ' '.join(back_trace_list):
            back_trace_list = ['Memory Exhaustion']

        # Create Back Trace DataFrame pre csv row
        self._dataframe_crash = pd.DataFrame(back_trace_list, columns=['Back Trace Parts'])

    def convert_back_trace_summary(self,):
        """ Convert "Back Trace" summary """

        summery_list = ['There is no', 'Corrupted Core']
        if [True for s in summery_list if s in self.back_trace]:
            if _ := [p for p in PROCESS_LIST if p.upper() in self.file_name.upper()]:
                self.back_trace += f' - {_[0]}'

    @abstractmethod
    def build_back_trace(self, entity, corecare_app=True):
        """ Build "Back Trace" from crash file """

        try:
            fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='core_info', entity=entity)
        except Exception:
            self.logger.exception('The file "core_info" was not open')
            fp_read = None

        if fp_read:
            back_trace_list = fp_read.decode("UTF-8").split("\n")
        else:
            back_trace_list = ['There is no BT']

        if not back_trace_list:
            back_trace_list = ['There is no BT']

        self.back_trace_list = back_trace_list
        self.check_for_memory_exhaustion()

    def check_for_memory_exhaustion(self):
        memory_exhaustion_list = ["alloc_from_ngp_pool_debug", "alloc_msg_from_ngp_pool_debug", "SGetSBufNew", "cmAllocEvnt", "ysUtlAllocEventMem", "operator new"]
        if any(i in self.back_trace for i in memory_exhaustion_list):
            # if 'alloc_from_ngp_pool_debug' in ' '.join(back_trace_list) or 'alloc_msg_from_ngp_pool_debug' in ' '.join(back_trace_list):
            self.memory_exhaustion_back_trace = ['Memory Exhaustion']

        # Create Back Trace DataFrame pre csv row
        self._dataframe_crash = pd.DataFrame(self.back_trace_list, columns=['Back Trace Parts'])

    def get_demangle(self, bt_mangle):
        try:
            try:
                bt_number = re.findall(r'(?=BT\[)(.*)(?<=\])', bt_mangle)[0]
                bt_mangle = re.findall(r'(?<=\()(.*)(?=\+)', bt_mangle)[0]
            except Exception:
                return None

            commands = [
                "d = cxxfilt.Demangler(find_library('c'), find_library('stdc++'))",
                f"demangle_output = d.demangle('{bt_mangle}')",
                "print(f'demangle is: {demangle_output}')",
            ]

            self.ssh_demangle.full_output = ''
            self.ssh_demangle.ssh_send_commands(commands=commands, with_output=True, wait_before_output=1, wait_between_commands=0.01)

            regex_pattern = r'(?<=demangle is: )(.*)'
            output_ = re.findall(regex_pattern, self.ssh_demangle.full_output)
            if output_:
                output_ = output_[-1].replace('\r', '').replace('\n', '')
                # print(f'\n{output_}')
            else:
                output_ = None
                print('\nThere is no demangle')

            if 'demangle_output' not in f'{bt_number}: {output_}':
                return f'{bt_number}: {output_}'
            self.logger.error('Something wrong - "demangle_output" in BT')
            raise socket.error
        except Exception as e:
            raise socket.error from e

    def get_bt_demangle(self):
        self.ssh_demangle.full_output = ''
        # demangle_output_dict = {bt_mangle: self.get_demangle(bt_mangle) for bt_mangle in self.back_trace.split(' -> ')}
        demangle_output_dict = {
            bt_mangle: _ if (_ := self.get_demangle(bt_mangle)) else bt_mangle
            for bt_mangle in self.back_trace.split(' -> ')
        }

        before_demangle = ' -> '.join(self.back_trace.split(' -> '))
        self.logger.debug(before_demangle)

        after_demangle = ' -> '.join([demangle_output_dict[v] for v in self.back_trace.split(' -> ') if v in list(demangle_output_dict.keys())])
        self.logger.debug(after_demangle)

        self.back_trace = after_demangle

    @abstractmethod
    def replace_to_hash(self):
        """ Convert "Back Trace" to hash """

        try:
            # hash_object = hashlib.md5(str(self.back_trace.split(' -> ')[-4:]).encode('utf-8'))
            if 'Memory Exhaustion' in self.memory_exhaustion_back_trace:
                new_summary = build_new_summary_for_memory_exhaustion(self.back_trace)
                hash_object = hashlib.md5(new_summary.encode('utf-8'))
            else:
                hash_object = hashlib.md5(str(self.back_trace.split(' -> ')[:4]).encode('utf-8'))
            hex_string = '0x' + (hash_object.hexdigest())
            hex_int = int(hex_string, 16)
            new_int = abs(hex_int % (10 ** 8))
            self.back_trace_hash = str(new_int)
        except Exception:
            self.logger.exception('')
            self.back_trace_hash = None

    @abstractmethod
    def replace_old_to_hash(self):
        """ Convert "Old Back Trace" to hash """

        try:
            hash_object = hashlib.md5(str(self.old_back_trace.split(' -> ')[-4:]).encode('utf-8'))
            hex_string = '0x' + (hash_object.hexdigest())
            hex_int = int(hex_string, 16)
            new_int = abs(hex_int % (10 ** 8))
            self.old_back_trace_hash = str(new_int)
        except Exception:
            self.logger.exception('')
            self.old_back_trace_hash = None

    @abstractmethod
    def extract_systeminfo(self, entity=None):
        """ Extract "systeminfo" from crash file """
        try:
            try:
                fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='_systeminfo', entity=entity)
            except Exception:
                self.logger.exception('The file "_systeminfo" was not open')
                fp_read = None

            if fp_read:
                fp_read = fp_read.decode("UTF-8")
                if '\t' in fp_read:
                    fp_read = fp_read.replace('\t', ' ')
                self.systeminfo = yaml.safe_load(fp_read)

                if self.systeminfo.get('SystemRunningTime'):
                    self.systeminfo['System Running Time'] = self.systeminfo.pop('SystemRunningTime')

                if self.systeminfo.get('Base ver.'):
                    self.systeminfo['Base ver.'] = self.systeminfo.pop('Base_ver')
            else:
                self.systeminfo = None
                return
        except Exception:
            self.logger.exception('There is no systeminfo')
            self.systeminfo = None
            return

        try:  # ################################################################################ Need to fix
            if type(self.systeminfo['System Running Time']) is str:
                self.systeminfo['System Running Time'] = [self.systeminfo['System Running Time'].replace("[", "").replace("]", "")]
                # self.logger.warning("self.systeminfo['System Running Time']) is str")

            if type(self.systeminfo['System Running Time']) is list:
                system_running_time = self.systeminfo['System Running Time'][0].split(' | ')
                self.systeminfo['System Running Time'] = {
                    system_running_time[0].split(':')[0]: system_running_time[0].split(':')[1],
                    system_running_time[1].split(':')[0]: system_running_time[1].split(':')[1],
                    system_running_time[2].split(':')[0]: system_running_time[2].split(':')[1]
                }
                # self.logger.warning("self.systeminfo['System Running Time']) is list")
            elif type(self.systeminfo['System Running Time']) is dict:
                # self.logger.warning("self.systeminfo['System Running Time']) is dict")
                pass
            else:
                # self.logger.warning("self.systeminfo['System Running Time']) is else")
                pass
        except Exception:
            self.logger.exception('have a problem with system_running_time')
            self.systeminfo['System Running Time'] = None

    @abstractmethod
    def extract_pid_file(self, entity=None):
        """ Extract "pid_file" from crash file """

        try:
            fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='pid_file_', entity=entity)
        except Exception:
            self.logger.exception('The file "pid_file_" was not open')
            fp_read = None

        if fp_read:
            self.pid = fp_read.decode("UTF-8").split("\n")[0]

    @abstractmethod
    def extract_ipinfo_file(self):
        """ Extract "ipinfo_file" from crash file """

        try:
            fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='airspan_systeminfo_')
        except Exception:
            self.logger.exception('The file "ipinfo_" was not open')
            fp_read = None

        if not fp_read:
            try:
                fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='var/log/cu_systeminfo_')
            except Exception:
                self.logger.exception('The file "ipinfo_" was not open')
                fp_read = None

        if fp_read:
            self.ipinfo = fp_read.decode("UTF-8")

    @abstractmethod
    def extract_version_type(self):
        """ Extract "Version Type" from crash file """

        # self.version_type = self.systeminfo.get('Platform', 'undefined')
        # if 'AIO' in self.version_type.upper():
        #     self.version_type = 'AIO'
        # elif 'RAN' in self.version_type.upper():
        #     self.version_type = 'VRRAN'
        # else:
        #     self.version_type = 'undefined'

        self.version_type = 'VRAN' if 'VRAN' in self.file_name.upper() else 'AIO'

    @abstractmethod
    def extract_crash_version(self):
        """ Extract "IP Address" from crash file """

        if self.systeminfo.get('Base_ver'):
            try:
                if self.crash_type == 'xpu':
                    self.crash_version = re.search(r'\d{1,3}.\d{1,3}-\d{1,3}', self.systeminfo['Base_ver'], re.I).group()
                else:
                    self.crash_version = re.search(r'\d{1,3}.\d{1,3}-\d{1,3}.\d{1,3}.\d{1,3}', self.systeminfo['Base_ver'], re.I).group()
            except Exception:
                self.logger.exception('have a problem with "crash_version"')

    def extract_version_file(self):
        """ Extract "pid_file" from crash file """

        if hasattr(self, 'extract_file'):
            if fp_read := self.extract_file('version.txt'):
                return fp_read.decode("UTF-8").split("\n")[0]
            else:
                return None

    @abstractmethod
    def extract_gnb_version(self, entity=None):
        """ Extract "version.txt" from crash file """
        try:
            fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='version.txt', entity=entity)
        except Exception:
            self.logger.exception('The file "version.txt" was not open')
            fp_read = None

        if fp_read:
            if data := fp_read.decode("UTF-8").split("\n")[0]:
                try:
                    if self.crash_type == 'xpu':
                        self.gnb_version = re.search(r'\d{1,3}.\d{1,3}-\d{1,3}', data, re.I).group()
                    else:
                        self.gnb_version = re.search(r'\d{1,3}.\d{1,3}-\d{1,3}.\d{1,3}.\d{1,3}', data, re.I).group()
                except Exception:
                    self.logger.exception('have a problem with "gnb_version"')

    @abstractmethod
    def extract_hostname(self):
        """ Extract "TTI" from crash file """

        if self.systeminfo.get('HOSTNAME'):
            self.hostname = self.systeminfo['HOSTNAME']

    def extract_setup_owner(self):
        with contextlib.suppress(Exception):
            # if SITE == CS:
            #   self.setup_owner = ido
            # elif ........

            if hasattr(self, '_setup_name_list_path'):
                setup_names_dataframe = pd.read_csv(self._setup_name_list_path)
                setup_network_address = f'{".".join(self.ip_address.split(".")[:-1])}.0'
                self.setup_owner = setup_names_dataframe.loc[setup_names_dataframe['IP Address'] == setup_network_address]['Setup Owner'].values[0]
        print()

    def extract_setup_name(self):
        with contextlib.suppress(Exception):
            ezlife_method = EZLifeMethod()

            ezlife_filter = '?name&' \
                                'ip_address&' \
                                'gnodeb_setup__cucp_gnodeb__name&gnodeb_setup__cucp_gnodeb__ssh_ip_address&' \
                                'gnodeb_setup__cuup_gnodeb__name&gnodeb_setup__cuup_gnodeb__ssh_ip_address&' \
                                'gnodeb_setup__du_gnodeb__name&gnodeb_setup__du_gnodeb__ssh_ip_address&' \
                                'gnodeb_setup__ru_gnodeb__name&gnodeb_setup__ru_gnodeb__ssh_ip_address'
            status_code, obj = ezlife_method.ezlife_get.get_by_url(f'{ezlife_method.global_parameters.base_url}/SetupApp/{ezlife_filter}')
            if type(obj) == list:
                if setup_name := {i['name'] for i in obj for k, v in i.items() if v == self.ip_address}:
                    self.setup_name = next(iter(setup_name))

    @abstractmethod
    def extract_ip_address(self):
        """ Extract "IP Address" from crash file """
        if not self.network_address:
            return

        ip_address_list = []
        for i in self.network_address:
            inet, net = i.split(' ')
            if len(net.split(".")) == 2:
                ip_address_regex = f'(?<={inet} )({net}' + r'.\d{1,3}.\d{1,3})(?= )'
            elif len(net.split(".")) == 3:
                ip_address_regex = f'(?<={inet} )({net}' + r'.\d{1,3})(?= )'
            else:
                ip_address_regex = f'(?<={inet} )({net}.*)(?=  prefixlen)'

            if ip_address_regex:
                with contextlib.suppress(Exception):
                    # self.ip_address = re.search(ip_address_regex, self.ipinfo, re.I).group()
                    ip_address_list.append(re.search(ip_address_regex, self.ipinfo, re.I).group())
        # for index, _ip_address in enumerate(ip_address_list, start=0):
        #     self.ip_address = _ip_address
        for index, self.ip_address in enumerate(ip_address_list, start=0):
            with contextlib.suppress(Exception):
                self.extract_setup_name()
                if self.setup_name:
                    break

    @abstractmethod
    def extract_system_runtime(self):
        """ Extract "System Runtime" from crash file """

        if self.systeminfo.get("System Running Time"):
            # self.system_runtime = datetime.strptime(
            #     f'{self.systeminfo["System Running Time"]["Hours"]}:'
            #     f'{self.systeminfo["System Running Time"]["Minutes"]}:'
            #     f'{self.systeminfo["System Running Time"]["Seconds"]}',
            #     '%H:%M:%S'
            # ).time().__str__()
            self.system_runtime = f'{self.systeminfo["System Running Time"]["Hours"]}:' \
                                  f'{self.systeminfo["System Running Time"]["Minutes"]}:'\
                                  f'{self.systeminfo["System Running Time"]["Seconds"]}'

    @abstractmethod
    def extract_user(self):
        """ Extract "USER" from crash file """

        self.user = self.systeminfo.get('USER')

    @abstractmethod
    def extract_time_stamp(self):
        """ Extract "Time Stamp" from crash file """

        self.time_stamp = 'Crash_time_stamp_'

    @abstractmethod
    def extract_tti(self):
        """ Extract "TTI" from crash file """

        self.tti = 'Crash_TTI_'

    @abstractmethod
    def extract_core_validation(self, entity=None):
        """ Extract "Core validation timestamp" from crash file """

        try:
            try:
                fp_read = read_tar_gz_file(self._tar_file, self._tar_members, tr_gz_file_name='core_validation', entity=entity)
            except Exception:
                self.logger.exception('The file "_systeminfo" was not open')
                fp_read = None

            if fp_read:
                fp_read = fp_read.decode("UTF-8")
                if '\t' in fp_read:
                    fp_read = fp_read.replace('\t', ' ')
                self.core_validation = yaml.safe_load(fp_read)
            else:
                self.core_validation = None
        except Exception:
            self.logger.exception('There is no systeminfo')
            self.core_validation = None

    @abstractmethod
    def get_core_validation_timestamp(self):
        """ Extract "Core validation timestamp" from crash file """

        try:
            if self.core_validation and self.core_validation.get('timestamp'):
                self.core_validation_timestamp = self.core_validation.pop('timestamp')
            else:
                self.core_validation_timestamp = None
        except Exception:
            self.logger.exception('There is no systeminfo')
            self.core_validation_timestamp = None


class ExtractUnknownCrash(CoreCareExtractStrategy):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        # self.logger.info('Start ExtractUnknownCrash')

        super(ExtractUnknownCrash, self).__init__()

    def add_to_self(self, tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle):
        """ Add parameters to self object """

        super(ExtractUnknownCrash, self).add_to_self(tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle)

    def change_setup_owner(self, site: str):
        # sourcery skip: merge-comparisons
        """ Change Setup Owner """

        super(ExtractUnknownCrash, self).change_setup_owner(site=site)

    def extract_type_crash_name(self):
        """ Extract "Crash Type" from crash file """

        super(ExtractUnknownCrash, self).extract_type_crash_name()
        self.crash_type = 'unknown'
        self.type_crash_name = 'unknown crash'

    def build_memory_exhaustion_back_trace(self, entity=None):
        """ Build "Memory Exhaustion Back Trace" from crash file """
        
        super(ExtractUnknownCrash, self).build_memory_exhaustion_back_trace(entity)

    def build_old_back_trace(self, entity=None):
        """ Build "Back Trace" from crash file """

        try:
            super(ExtractUnknownCrash, self).build_old_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag:
                        continue
                    flag = True
                    self.old_back_trace = ''
                elif 'WORKER_THREAD' in row[0].upper() or 'THREAD_START' in row[0].upper():
                    break
                else:
                    if row[0].upper().startswith('BT[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                        row[0] = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                        self.old_back_trace += f' -> {row[0]}'
                    # self.back_trace += f' -> {row[0]}'
        except Exception:
            self.logger.exception('There is no BT')
            self.old_back_trace = 'There is no BT'

    def build_back_trace(self, entity=None, corecare_app=True):
        """ Build "Back Trace" from crash file """

        try:
            if corecare_app:
                super(ExtractUnknownCrash, self).build_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                    _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.full_back_trace += f' -> {_}'
                else:
                    _ = None

                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.back_trace = ''
                elif _ and (row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion'):
                    # _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.back_trace += f' -> {_}'
        except Exception:
            self.logger.exception('There is no BT')
            self.back_trace = 'There is no BT'

    def replace_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractUnknownCrash, self).replace_to_hash()

    def replace_old_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractUnknownCrash, self).replace_old_to_hash()

    def extract_systeminfo(self, entity=None):
        """ Extract "systeminfo" from crash file """

        super(ExtractUnknownCrash, self).extract_systeminfo(entity)

    def extract_pid_file(self, entity=None):
        """ Extract "pid_file" from crash file """

        super(ExtractUnknownCrash, self).extract_pid_file(entity)

    def extract_ipinfo_file(self):
        """ Extract "ipinfo_file" from crash file """

        super(ExtractUnknownCrash, self).extract_ipinfo_file()

    def extract_version_type(self):
        """ Extract "Version Type" from crash file """

        super(ExtractUnknownCrash, self).extract_version_type()

    def extract_crash_version(self):
        """ Extract "IP Address" from crash file """

        super(ExtractUnknownCrash, self).extract_crash_version()

    def extract_gnb_version(self, entity=None):
        """ Extract "version.txt" from crash file """

        super(ExtractUnknownCrash, self).extract_gnb_version(entity)

    def extract_hostname(self):
        """ Extract "TTI" from crash file """

        super(ExtractUnknownCrash, self).extract_hostname()

    def extract_ip_address(self):
        """ Extract "IP Address" from crash file """

        super(ExtractUnknownCrash, self).extract_ip_address()

    def extract_system_runtime(self):
        """ Extract "System Runtime" from crash file """

        super(ExtractUnknownCrash, self).extract_system_runtime()

    def extract_user(self):
        """ Extract "USER" from crash file """

        super(ExtractUnknownCrash, self).extract_user()

    def extract_time_stamp(self):
        """ Extract "Time Stamp" from crash file """

        super(ExtractUnknownCrash, self).extract_time_stamp()

    def extract_tti(self):
        """ Extract "TTI" from crash file """

        super(ExtractUnknownCrash, self).extract_tti()

    def extract_core_validation(self, entity=None):
        """ Extract "Core validation" from crash file """

        super(ExtractUnknownCrash, self).extract_core_validation(entity)

    def get_core_validation_timestamp(self):
        """ Get "Core validation timestamp" from crash file """

        super(ExtractUnknownCrash, self).get_core_validation_timestamp()


class ExtractCUCPCore(CoreCareExtractStrategy):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        # self.logger.info('Start ExtractCUCPCore')

        super(ExtractCUCPCore, self).__init__()

    def add_to_self(self, tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle):
        """ Add parameters to self object """

        super(ExtractCUCPCore, self).add_to_self(tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle)

    def change_setup_owner(self, site: str):
        """ Change Setup Owner """

        super(ExtractCUCPCore, self).change_setup_owner(site=site)

    def extract_type_crash_name(self):
        """ Extract "Crash Type" from crash file """

        super(ExtractCUCPCore, self).extract_type_crash_name()
        self.crash_type = 'cucp'
        self.type_crash_name = 'cucp core'

    def build_memory_exhaustion_back_trace(self, entity='CP'):
        """ Build "Memory Exhaustion Back Trace" from crash file """

        super(ExtractCUCPCore, self).build_memory_exhaustion_back_trace(entity)

    def build_old_back_trace(self, entity='CP'):
        """ Build "Back Trace" from crash file """

        try:
            super(ExtractCUCPCore, self).build_old_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.old_back_trace = ''
                elif 'WORKER_THREAD' in row[0].upper() or 'THREAD_START' in row[0].upper():
                    break
                else:
                    if row[0].upper().startswith('BT[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                        row[0] = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                        self.old_back_trace += f' -> {row[0]}'
                    # self.back_trace += f' -> {row[0]}'
        except Exception:
            self.logger.exception('There is no BT')
            self.old_back_trace = 'There is no BT'

    def build_back_trace(self, entity='CP', corecare_app=True):
        """ Build "Back Trace" from crash file """

        try:
            if corecare_app:
                super(ExtractCUCPCore, self).build_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                    _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.full_back_trace += f' -> {_}'
                else:
                    _ = None

                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.back_trace = ''
                elif _ and (row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion'):
                    # _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.back_trace += f' -> {_}'
        except Exception:
            self.logger.exception('There is no BT')
            self.back_trace = 'There is no BT'

    def replace_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractCUCPCore, self).replace_to_hash()

    def replace_old_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractCUCPCore, self).replace_old_to_hash()

    def extract_systeminfo(self, entity='CP'):
        """ Extract "systeminfo" from crash file """

        super(ExtractCUCPCore, self).extract_systeminfo(entity)

    def extract_pid_file(self, entity='CP'):
        """ Extract "pid_file" from crash file """

        super(ExtractCUCPCore, self).extract_pid_file(entity)

    def extract_ipinfo_file(self):
        """ Extract "ipinfo_file" from crash file """

        super(ExtractCUCPCore, self).extract_ipinfo_file()

    def extract_version_type(self):
        """ Extract "Version Type" from crash file """

        super(ExtractCUCPCore, self).extract_version_type()

    def extract_crash_version(self):
        """ Extract "IP Address" from crash file """

        super(ExtractCUCPCore, self).extract_crash_version()

    def extract_gnb_version(self, entity='CP'):
        """ Extract "version.txt" from crash file """

        super(ExtractCUCPCore, self).extract_gnb_version(entity)

    def extract_hostname(self):
        """ Extract "TTI" from crash file """

        super(ExtractCUCPCore, self).extract_hostname()

    def extract_ip_address(self):
        """ Extract "IP Address" from crash file """

        super(ExtractCUCPCore, self).extract_ip_address()

    def extract_system_runtime(self):
        """ Extract "System Runtime" from crash file """

        super(ExtractCUCPCore, self).extract_system_runtime()

    def extract_user(self):
        """ Extract "USER" from crash file """

        super(ExtractCUCPCore, self).extract_user()

    def extract_time_stamp(self):
        """ Extract "Time Stamp" from crash file """

        super(ExtractCUCPCore, self).extract_time_stamp()

    def extract_tti(self):
        """ Extract "TTI" from crash file """

        super(ExtractCUCPCore, self).extract_tti()

    def extract_core_validation(self, entity='CP'):
        """ Extract "Core validation" from crash file """

        super(ExtractCUCPCore, self).extract_core_validation(entity)

    def get_core_validation_timestamp(self):
        """ Get "Core validation timestamp" from crash file """

        super(ExtractCUCPCore, self).get_core_validation_timestamp()


class ExtractCUUPCore(CoreCareExtractStrategy):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        # self.logger.info('Start ExtractCUUPCore')

        super(ExtractCUUPCore, self).__init__()

    def add_to_self(self, tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle):
        """ Add parameters to self object """

        super(ExtractCUUPCore, self).add_to_self(tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle)

    def change_setup_owner(self, site: str):
        """ Change Setup Owner """

        super(ExtractCUUPCore, self).change_setup_owner(site=site)

    def extract_type_crash_name(self):
        """ Extract "Crash Type" from crash file """

        super(ExtractCUUPCore, self).extract_type_crash_name()
        self.crash_type = 'cuup'
        self.type_crash_name = 'cuup core'

    def build_memory_exhaustion_back_trace(self, entity='UP'):
        """ Build "Memory Exhaustion Back Trace" from crash file """

        super(ExtractCUUPCore, self).build_memory_exhaustion_back_trace(entity)

    def build_old_back_trace(self, entity='UP'):
        """ Build "Back Trace" from crash file """

        try:
            super(ExtractCUUPCore, self).build_old_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.old_back_trace = ''
                elif 'WORKER_THREAD' in row[0].upper() or 'THREAD_START' in row[0].upper():
                    break
                else:
                    if row[0].upper().startswith('BT[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                        row[0] = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                        self.old_back_trace += f' -> {row[0]}'
                    # self.back_trace += f' -> {row[0]}'
        except Exception:
            self.logger.exception('There is no BT')
            self.old_back_trace = 'There is no BT'

    def build_back_trace(self, entity='UP', corecare_app=True):
        """ Build "Back Trace" from crash file """

        try:
            if corecare_app:
                super(ExtractCUUPCore, self).build_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                    _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.full_back_trace += f' -> {_}'
                else:
                    _ = None

                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.back_trace = ''
                elif _ and (row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion'):
                    # _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.back_trace += f' -> {_}'
        except Exception:
            self.logger.exception('There is no BT')
            self.back_trace = 'There is no BT'

    def replace_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractCUUPCore, self).replace_to_hash()

    def replace_old_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractCUUPCore, self).replace_old_to_hash()

    def extract_systeminfo(self, entity='UP'):
        """ Extract "systeminfo" from crash file """

        super(ExtractCUUPCore, self).extract_systeminfo(entity)

    def extract_pid_file(self, entity='UP'):
        """ Extract "pid_file" from crash file """

        super(ExtractCUUPCore, self).extract_pid_file(entity)

    def extract_ipinfo_file(self):
        """ Extract "ipinfo_file" from crash file """

        super(ExtractCUUPCore, self).extract_ipinfo_file()

    def extract_version_type(self):
        """ Extract "Version Type" from crash file """

        super(ExtractCUUPCore, self).extract_version_type()

    def extract_crash_version(self):
        """ Extract "IP Address" from crash file """

        super(ExtractCUUPCore, self).extract_crash_version()

    def extract_gnb_version(self, entity='UP'):
        """ Extract "version.txt" from crash file """

        super(ExtractCUUPCore, self).extract_gnb_version(entity)

    def extract_hostname(self):
        """ Extract "TTI" from crash file """

        super(ExtractCUUPCore, self).extract_hostname()

    def extract_ip_address(self):
        """ Extract "IP Address" from crash file """

        super(ExtractCUUPCore, self).extract_ip_address()

    def extract_system_runtime(self):
        """ Extract "System Runtime" from crash file """

        super(ExtractCUUPCore, self).extract_system_runtime()

    def extract_user(self):
        """ Extract "USER" from crash file """

        super(ExtractCUUPCore, self).extract_user()

    def extract_time_stamp(self):
        """ Extract "Time Stamp" from crash file """

        super(ExtractCUUPCore, self).extract_time_stamp()

    def extract_tti(self):
        """ Extract "TTI" from crash file """

        super(ExtractCUUPCore, self).extract_tti()

    def extract_core_validation(self, entity='UP'):
        """ Extract "Core validation" from crash file """

        super(ExtractCUUPCore, self).extract_core_validation(entity)

    def get_core_validation_timestamp(self):
        """ Get "Core validation timestamp" from crash file """

        super(ExtractCUUPCore, self).get_core_validation_timestamp()


class ExtractDUCore(CoreCareExtractStrategy):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        # self.logger.info('Start ExtractDUCore')

        super(ExtractDUCore, self).__init__()

    def add_to_self(self, tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle):
        """ Add parameters to self object """

        super(ExtractDUCore, self).add_to_self(tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle)

    def change_setup_owner(self, site: str):
        """ Change Setup Owner """

        super(ExtractDUCore, self).change_setup_owner(site=site)

    def extract_type_crash_name(self):
        """ Extract "Crash Type" from crash file """

        super(ExtractDUCore, self).extract_type_crash_name()
        self.crash_type = 'du'
        self.type_crash_name = 'du core'

    # def build_memory_exhaustion_back_trace(self, entity='DU_L2'):
    def build_memory_exhaustion_back_trace(self, entity='DU_L2'):
        """ Build "Memory Exhaustion Back Trace" from crash file """

        super(ExtractDUCore, self).build_memory_exhaustion_back_trace(entity)

    # def build_old_back_trace(self, entity='DU_L2'):
    def build_old_back_trace(self, entity='DU_L2'):
        """ Build "Back Trace" from crash file """

        try:
            super(ExtractDUCore, self).build_old_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.old_back_trace = ''
                elif 'WORKER_THREAD' in row[0].upper() or 'THREAD_START' in row[0].upper():
                    break
                else:
                    if row[0].upper().startswith('BT[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                        row[0] = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                        self.old_back_trace += f' -> {row[0]}'
                    # self.old_back_trace += f' -> {row[0]}'
        except Exception:
            self.logger.exception('There is no BT')
            self.old_back_trace = 'There is no BT'

    # def build_back_trace(self, entity='DU_L2'):
    def build_back_trace(self, entity='DU_L2', corecare_app=True):
        """ Build "Back Trace" from crash file """

        try:
            if corecare_app:
                super(ExtractDUCore, self).build_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                    _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.full_back_trace += f' -> {_}'
                else:
                    _ = None

                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.back_trace = ''
                elif _ and (row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion'):
                    # _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.back_trace += f' -> {_}'
        except Exception:
            self.logger.exception('There is no BT')
            self.back_trace = 'There is no BT'

    def replace_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractDUCore, self).replace_to_hash()

    def replace_old_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractDUCore, self).replace_old_to_hash()

    # def extract_systeminfo(self, entity='DU_L2'):
    def extract_systeminfo(self, entity='DU_L2'):
        """ Extract "systeminfo" from crash file """

        super(ExtractDUCore, self).extract_systeminfo(entity)

    # def extract_pid_file(self, entity='DU_L2'):
    def extract_pid_file(self, entity='DU_L2'):
        """ Extract "pid_file" from crash file """

        super(ExtractDUCore, self).extract_pid_file(entity)

    def extract_ipinfo_file(self):
        """ Extract "ipinfo_file" from crash file """

        super(ExtractDUCore, self).extract_ipinfo_file()

    def extract_version_type(self):
        """ Extract "Version Type" from crash file """

        super(ExtractDUCore, self).extract_version_type()

    def extract_crash_version(self):
        """ Extract "IP Address" from crash file """

        super(ExtractDUCore, self).extract_crash_version()

    # def extract_gnb_version(self, entity='DU_L2'):
    def extract_gnb_version(self, entity='DU_L2'):
        """ Extract "version.txt" from crash file """

        super(ExtractDUCore, self).extract_gnb_version(entity)

    def extract_hostname(self):
        """ Extract "TTI" from crash file """

        super(ExtractDUCore, self).extract_hostname()

    def extract_ip_address(self):
        """ Extract "IP Address" from crash file """

        super(ExtractDUCore, self).extract_ip_address()

    def extract_system_runtime(self):
        """ Extract "System Runtime" from crash file """

        super(ExtractDUCore, self).extract_system_runtime()

    def extract_user(self):
        """ Extract "USER" from crash file """

        super(ExtractDUCore, self).extract_user()

    def extract_time_stamp(self):
        """ Extract "Time Stamp" from crash file """

        super(ExtractDUCore, self).extract_time_stamp()

    def extract_tti(self):
        """ Extract "TTI" from crash file """

        super(ExtractDUCore, self).extract_tti()

    def extract_core_validation(self, entity='DU_L2'):
        """ Extract "Core validation" from crash file """

        super(ExtractDUCore, self).extract_core_validation(entity)

    def get_core_validation_timestamp(self):
        """ Get "Core validation timestamp" from crash file """

        super(ExtractDUCore, self).get_core_validation_timestamp()


class ExtractRUCore(CoreCareExtractStrategy):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        # self.logger.info('Start ExtractRUCore')

        super(ExtractRUCore, self).__init__()

    def add_to_self(self, tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle):
        """ Add parameters to self object """

        super(ExtractRUCore, self).add_to_self(tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle)

    def change_setup_owner(self, site: str):
        """ Change Setup Owner """

        super(ExtractRUCore, self).change_setup_owner(site=site)

    def extract_type_crash_name(self):
        """ Extract "Crash Type" from crash file """

        super(ExtractRUCore, self).extract_type_crash_name()
        self.crash_type = 'ru'
        self.type_crash_name = 'ru core'

    def build_memory_exhaustion_back_trace(self, entity='RU'):
        """ Build "Memory Exhaustion Back Trace" from crash file """

        super(ExtractRUCore, self).build_memory_exhaustion_back_trace(entity)

    def build_old_back_trace(self, entity='RU'):
        """ Build "Back Trace" from crash file """

        try:
            super(ExtractRUCore, self).build_old_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.old_back_trace = ''
                elif 'WORKER_THREAD' in row[0].upper() or 'THREAD_START' in row[0].upper():
                    break
                else:
                    if row[0].upper().startswith('BT[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                        row[0] = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                        self.old_back_trace += f' -> {row[0]}'
                    # self.back_trace += f' -> {row[0]}'
        except Exception:
            self.logger.exception('There is no BT')
            self.old_back_trace = 'There is no BT'

    def build_back_trace(self, entity='RU', corecare_app=True):
        """ Build "Back Trace" from crash file """

        try:
            if corecare_app:
                super(ExtractRUCore, self).build_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                    _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.full_back_trace += f' -> {_}'
                else:
                    _ = None

                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.back_trace = ''
                elif _ and (row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion'):
                    # _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.back_trace += f' -> {_}'
        except Exception:
            self.logger.exception('There is no BT')
            self.back_trace = 'There is no BT'

    def replace_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractRUCore, self).replace_to_hash()

    def replace_old_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractRUCore, self).replace_old_to_hash()

    def extract_systeminfo(self, entity='RU'):
        """ Extract "systeminfo" from crash file """

        super(ExtractRUCore, self).extract_systeminfo(entity)

    def extract_pid_file(self, entity='RU'):
        """ Extract "pid_file" from crash file """

        super(ExtractRUCore, self).extract_pid_file(entity)

    def extract_ipinfo_file(self):
        """ Extract "ipinfo_file" from crash file """

        super(ExtractRUCore, self).extract_ipinfo_file()

    def extract_version_type(self):
        """ Extract "Version Type" from crash file """

        super(ExtractRUCore, self).extract_version_type()

    def extract_crash_version(self):
        """ Extract "IP Address" from crash file """

        super(ExtractRUCore, self).extract_crash_version()

    def extract_gnb_version(self, entity='RU'):
        """ Extract "version.txt" from crash file """

        super(ExtractRUCore, self).extract_gnb_version(entity)

    def extract_hostname(self):
        """ Extract "TTI" from crash file """

        super(ExtractRUCore, self).extract_hostname()

    def extract_ip_address(self):
        """ Extract "IP Address" from crash file """

        super(ExtractRUCore, self).extract_ip_address()

    def extract_system_runtime(self):
        """ Extract "System Runtime" from crash file """

        super(ExtractRUCore, self).extract_system_runtime()

    def extract_user(self):
        """ Extract "USER" from crash file """

        super(ExtractRUCore, self).extract_user()

    def extract_time_stamp(self):
        """ Extract "Time Stamp" from crash file """

        super(ExtractRUCore, self).extract_time_stamp()

    def extract_tti(self):
        """ Extract "TTI" from crash file """

        super(ExtractRUCore, self).extract_tti()

    def extract_core_validation(self, entity='RU'):
        """ Extract "Core validation" from crash file """

        super(ExtractRUCore, self).extract_core_validation(entity)

    def get_core_validation_timestamp(self):
        """ Get "Core validation timestamp" from crash file """

        super(ExtractRUCore, self).get_core_validation_timestamp()


class ExtractDUPhyAssert(CoreCareExtractStrategy):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        # self.logger.info('Start ExtractDUPhyAssert')

        super(ExtractDUPhyAssert, self).__init__()

    def add_to_self(self, tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle):
        """ Add parameters to self object """

        super(ExtractDUPhyAssert, self).add_to_self(tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle)

    def change_setup_owner(self, site: str):
        """ Change Setup Owner """

        super(ExtractDUPhyAssert, self).change_setup_owner(site=site)

    def extract_type_crash_name(self):
        """ Extract "Crash Type" from crash file """

        super(ExtractDUPhyAssert, self).extract_type_crash_name()
        self.crash_type = 'phy_assert'
        self.type_crash_name = 'du phy_assert'

    def build_memory_exhaustion_back_trace(self, entity='PHY-'):
        """ Build "Memory Exhaustion Back Trace" from crash file """

        super(ExtractDUPhyAssert, self).build_memory_exhaustion_back_trace(entity)

    def build_old_back_trace(self, entity='PHY-'):
        """ Build "Back Trace" from crash file """
        try:
            super(ExtractDUPhyAssert, self).build_old_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.old_back_trace = ''
                elif 'WORKER_THREAD' in row[0].upper() or 'THREAD_START' in row[0].upper():
                    break
                else:
                    if row[0].upper().startswith('BT[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                        row[0] = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                        self.old_back_trace += f' -> {row[0]}'
                    # self.back_trace += f' -> {row[0]}'
        except Exception:
            self.logger.exception('There is no BT')
            self.old_back_trace = 'There is no BT'

    def build_back_trace(self, entity='PHY-', corecare_app=True):
        """ Build "Back Trace" from crash file """

        try:
            if corecare_app:
                super(ExtractDUPhyAssert, self).build_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                    _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.full_back_trace += f' -> {_}'
                else:
                    _ = None

                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.back_trace = ''
                elif _ and (row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion'):
                    # _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.back_trace += f' -> {_}'
        except Exception:
            self.logger.exception('There is no BT')
            self.back_trace = 'There is no BT'

    def replace_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractDUPhyAssert, self).replace_to_hash()

    def replace_old_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractDUPhyAssert, self).replace_old_to_hash()

    def extract_systeminfo(self, entity='PHY-'):
        """ Extract "systeminfo" from crash file """

        super(ExtractDUPhyAssert, self).extract_systeminfo(entity)

    def extract_pid_file(self, entity='PHY-'):
        """ Extract "pid_file" from crash file """

        super(ExtractDUPhyAssert, self).extract_pid_file(entity)

    def extract_ipinfo_file(self):
        """ Extract "ipinfo_file" from crash file """

        super(ExtractDUPhyAssert, self).extract_ipinfo_file()

    def extract_version_type(self):
        """ Extract "Version Type" from crash file """

        super(ExtractDUPhyAssert, self).extract_version_type()

    def extract_crash_version(self):
        """ Extract "IP Address" from crash file """

        super(ExtractDUPhyAssert, self).extract_crash_version()

    def extract_gnb_version(self, entity='PHY-'):
        """ Extract "version.txt" from crash file """

        super(ExtractDUPhyAssert, self).extract_gnb_version(entity)

    def extract_hostname(self):
        """ Extract "TTI" from crash file """

        super(ExtractDUPhyAssert, self).extract_hostname()

    def extract_ip_address(self):
        """ Extract "IP Address" from crash file """

        super(ExtractDUPhyAssert, self).extract_ip_address()

    def extract_system_runtime(self):
        """ Extract "System Runtime" from crash file """

        super(ExtractDUPhyAssert, self).extract_system_runtime()

    def extract_user(self):
        """ Extract "USER" from crash file """

        super(ExtractDUPhyAssert, self).extract_user()

    def extract_time_stamp(self):
        """ Extract "Time Stamp" from crash file """

        super(ExtractDUPhyAssert, self).extract_time_stamp()

    def extract_tti(self):
        """ Extract "TTI" from crash file """

        super(ExtractDUPhyAssert, self).extract_tti()

    def extract_core_validation(self, entity='PHY-'):
        """ Extract "Core validation" from crash file """

        super(ExtractDUPhyAssert, self).extract_core_validation(entity)

    def get_core_validation_timestamp(self):
        """ Get "Core validation timestamp" from crash file """

        super(ExtractDUPhyAssert, self).get_core_validation_timestamp()


class ExtractRUPhyAssert(CoreCareExtractStrategy):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        # self.logger.info('Start ExtractRUPhyAssert')

        super(ExtractRUPhyAssert, self).__init__()

    def add_to_self(self, tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle):
        """ Add parameters to self object """

        super(ExtractRUPhyAssert, self).add_to_self(tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle)

    def change_setup_owner(self, site: str):
        """ Change Setup Owner """

        super(ExtractRUPhyAssert, self).change_setup_owner(site=site)

    def extract_type_crash_name(self):
        """ Extract "Crash Type" from crash file """

        super(ExtractRUPhyAssert, self).extract_type_crash_name()
        self.crash_type = 'phy_assert'
        self.type_crash_name = 'ru phy_assert'

    def build_memory_exhaustion_back_trace(self, entity='RU'):
        """ Build "Memory Exhaustion Back Trace" from crash file """

        super(ExtractRUPhyAssert, self).build_memory_exhaustion_back_trace(entity)

    def build_old_back_trace(self, entity='RU'):
        """ Build "Back Trace" from crash file """
        try:
            super(ExtractRUPhyAssert, self).build_old_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.old_back_trace = ''
                elif 'WORKER_THREAD' in row[0].upper() or 'THREAD_START' in row[0].upper():
                    break
                else:
                    if row[0].upper().startswith('BT[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                        row[0] = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                        self.old_back_trace += f' -> {row[0]}'
                    # self.back_trace += f' -> {row[0]}'
        except Exception:
            self.logger.exception('There is no BT')
            self.old_back_trace = 'There is no BT'

    def build_back_trace(self, entity='RU', corecare_app=True):
        """ Build "Back Trace" from crash file """

        try:
            if corecare_app:
                super(ExtractRUPhyAssert, self).build_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                    _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.full_back_trace += f' -> {_}'
                else:
                    _ = None

                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.back_trace = ''
                elif _ and (row[0].upper().startswith('BT[') or row[0].upper().startswith('P[') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion'):
                    # _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.back_trace += f' -> {_}'
        except Exception:
            self.logger.exception('There is no BT')
            self.back_trace = 'There is no BT'

    def replace_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractRUPhyAssert, self).replace_to_hash()

    def replace_old_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractRUPhyAssert, self).replace_old_to_hash()

    def extract_systeminfo(self, entity='RU'):
        """ Extract "systeminfo" from crash file """

        super(ExtractRUPhyAssert, self).extract_systeminfo(entity)

    def extract_pid_file(self, entity='RU'):
        """ Extract "pid_file" from crash file """

        super(ExtractRUPhyAssert, self).extract_pid_file(entity)

    def extract_ipinfo_file(self):
        """ Extract "ipinfo_file" from crash file """

        super(ExtractRUPhyAssert, self).extract_ipinfo_file()

    def extract_version_type(self):
        """ Extract "Version Type" from crash file """

        super(ExtractRUPhyAssert, self).extract_version_type()

    def extract_crash_version(self):
        """ Extract "IP Address" from crash file """

        super(ExtractRUPhyAssert, self).extract_crash_version()

    def extract_gnb_version(self, entity='RU'):
        """ Extract "version.txt" from crash file """

        super(ExtractRUPhyAssert, self).extract_gnb_version(entity)

    def extract_hostname(self):
        """ Extract "TTI" from crash file """

        super(ExtractRUPhyAssert, self).extract_hostname()

    def extract_ip_address(self):
        """ Extract "IP Address" from crash file """

        super(ExtractRUPhyAssert, self).extract_ip_address()

    def extract_system_runtime(self):
        """ Extract "System Runtime" from crash file """

        super(ExtractRUPhyAssert, self).extract_system_runtime()

    def extract_user(self):
        """ Extract "USER" from crash file """

        super(ExtractRUPhyAssert, self).extract_user()

    def extract_time_stamp(self):
        """ Extract "Time Stamp" from crash file """

        super(ExtractRUPhyAssert, self).extract_time_stamp()

    def extract_tti(self):
        """ Extract "TTI" from crash file """

        super(ExtractRUPhyAssert, self).extract_tti()

    def extract_core_validation(self, entity='RU'):
        """ Extract "Core validation" from crash file """

        super(ExtractRUPhyAssert, self).extract_core_validation(entity)

    def get_core_validation_timestamp(self):
        """ Get "Core validation timestamp" from crash file """

        super(ExtractRUPhyAssert, self).get_core_validation_timestamp()


class ExtractXPU(CoreCareExtractStrategy):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        # self.logger.info('Start ExtractRUPhyAssert')

        super(ExtractXPU, self).__init__()

    def add_to_self(self, tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle):
        """ Add parameters to self object """

        super(ExtractXPU, self).add_to_self(tar_file, tar_members, dir_path, file_name, network_address, setup_name_list_path, ssh_demangle)

    def change_setup_owner(self, site: str):
        """ Change Setup Owner """

        super(ExtractXPU, self).change_setup_owner(site=site)

    def extract_type_crash_name(self):
        """ Extract "Crash Type" from crash file """

        super(ExtractXPU, self).extract_type_crash_name()
        self.crash_type = 'xpu'
        self.type_crash_name = 'xpu core'

    def build_memory_exhaustion_back_trace(self, entity='XPU'):
        """ Build "Memory Exhaustion Back Trace" from crash file """

        super(ExtractXPU, self).build_memory_exhaustion_back_trace(entity)

    def build_old_back_trace(self, entity='XPU'):
        """ Build "Back Trace" from crash file """
        try:
            super(ExtractXPU, self).build_old_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.old_back_trace = ''
                elif 'WORKER_THREAD' in row[0].upper() or 'THREAD_START' in row[0].upper():
                    break
                else:
                    if row[0].upper().startswith('P[') or row[0].upper().startswith('[P') or row[0] == 'There is no Process' or row[0] == 'Memory Exhaustion':
                        row[0] = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                        self.old_back_trace += f' -> {row[0]}'
                    # self.back_trace += f' -> {row[0]}'
        except Exception:
            self.logger.exception('There is no Process')
            self.old_back_trace = 'There is no Process'

    def build_back_trace(self, entity='XPU', corecare_app=True):
        """ Build "Back Trace" from crash file """

        try:
            if corecare_app:
                super(ExtractXPU, self).build_back_trace(entity)

            flag = False
            ignore_list = ['?', '/usr/', '/home/', '/lib64/', 'SigDumpHandler', 'gnb_du()']
            for row in self._dataframe_crash.values:
                if row[0].upper().startswith('P[') or row[0].upper().startswith('[P') or row[0] == 'There is no BT' or row[0] == 'Memory Exhaustion':
                    _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.full_back_trace += f' -> {_}'
                else:
                    _ = None

                if any(i in row[0] for i in ignore_list) or row[0] == '':
                    if flag or row[0] == '':
                        continue
                    flag = True
                    self.back_trace = ''
                elif _ and (row[0].upper().startswith('P[') or row[0].upper().startswith('[P') or row[0] == 'There is no Process' or row[0] == 'Memory Exhaustion'):
                    # _ = re.sub(r"(?= \[0x)(.*)]", "", row[0])
                    self.back_trace += f' -> {_}'
        except Exception:
            self.logger.exception('There is no Process')
            self.back_trace = 'There is no Process'

    def replace_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractXPU, self).replace_to_hash()

    def replace_old_to_hash(self):
        """ Convert "Back Trace" to hash """

        super(ExtractXPU, self).replace_old_to_hash()

    def extract_systeminfo(self, entity='XPU'):
        """ Extract "systeminfo" from crash file """

        super(ExtractXPU, self).extract_systeminfo(entity)

    def extract_pid_file(self, entity='XPU'):
        """ Extract "pid_file" from crash file """

        super(ExtractXPU, self).extract_pid_file(entity)

    def extract_ipinfo_file(self):
        """ Extract "ipinfo_file" from crash file """

        super(ExtractXPU, self).extract_ipinfo_file()

    def extract_version_type(self):
        """ Extract "Version Type" from crash file """

        super(ExtractXPU, self).extract_version_type()

    def extract_crash_version(self):
        """ Extract "IP Address" from crash file """

        super(ExtractXPU, self).extract_crash_version()

    def extract_gnb_version(self, entity='XPU'):
        """ Extract "version.txt" from crash file """

        super(ExtractXPU, self).extract_gnb_version(entity)

    def extract_hostname(self):
        """ Extract "TTI" from crash file """

        super(ExtractXPU, self).extract_hostname()

    def extract_ip_address(self):
        """ Extract "IP Address" from crash file """

        super(ExtractXPU, self).extract_ip_address()

    def extract_system_runtime(self):
        """ Extract "System Runtime" from crash file """

        super(ExtractXPU, self).extract_system_runtime()

    def extract_user(self):
        """ Extract "USER" from crash file """

        super(ExtractXPU, self).extract_user()

    def extract_time_stamp(self):
        """ Extract "Time Stamp" from crash file """

        super(ExtractXPU, self).extract_time_stamp()

    def extract_tti(self):
        """ Extract "TTI" from crash file """

        super(ExtractXPU, self).extract_tti()

    def extract_core_validation(self, entity='XPU'):
        """ Extract "Core validation" from crash file """

        super(ExtractXPU, self).extract_core_validation(entity)

    def get_core_validation_timestamp(self):
        """ Get "Core validation timestamp" from crash file """

        super(ExtractXPU, self).get_core_validation_timestamp()
