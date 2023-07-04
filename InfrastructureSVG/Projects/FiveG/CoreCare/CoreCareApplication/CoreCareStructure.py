import contextlib
import os
import time
import logging
import json
import collections
from datetime import datetime
from abc import ABC, abstractmethod
from copy import deepcopy
# from typing import Callable, Dict, List
# from datetime import datetime, timedelta, timezone
# import inspect

import random
import string
from typing import Union

from InfrastructureSVG.DateAndTimeFormats.CalculateTime_Infrastructure import CalculateTime
from InfrastructureSVG.Files_Infrastructure.Files.FilesActions_Infrastructure import FilesActions
from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import GeneralFolderActionClass
from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import IssueFieldsConstructor
from InfrastructureSVG.Notifications_Infrastructure.send_email_by_gmail import Notifications
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareApplication.CoreValidation import CoreValidation
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX, get_tar_gz_file, extract_specific_file, \
    read_tar_gz_file, close_tar_gz_file_reader, cucp_core_files_mandatory, cuup_core_files_mandatory, du_core_files_mandatory, ru_core_files_mandatory, xpu_core_files_mandatory
from InfrastructureSVG.Projects.FiveG.CoreCare.ParseDataFilesToCSV.CoreCare_ExtractStructure import build_new_summary_for_memory_exhaustion
from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import get_full_field_list

ConstructorFields = IssueFieldsConstructor()


class CoreCareInfrastructure:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def generate_id(self, length=8):
        # helper function for generating an id
        id_ = ''.join(random.choices(string.ascii_uppercase, k=length))
        self.logger.info(f'id is: {id_}')
        return id_


class JiraFilters:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_total_core_occurrence_count_by_filter_for_duplicate(self):
        if hasattr(self, 'jira_client') and hasattr(self, 'defect_duplicate_list'):
            epics = [j.inwardIssue.key for i in self.defect_duplicate_list for j in i.fields.issuelinks if hasattr(j, 'inwardIssue') and 'CORE-' in j.inwardIssue.key]
            return sum(total_core_occurrence_count.__len__()
                       if (total_core_occurrence_count :=
                           self.jira_client.search_by_filter(str_filter=f'project = CoreCare AND "Epic Link" = {epic}', fields=get_full_field_list())) else 0 for epic in epics)

    def get_last_version_core_occurrence_count_by_filter_for_duplicate(self, last_version):
        if hasattr(self, 'jira_client') and hasattr(self, 'defect_duplicate_list'):
            epics = [j.inwardIssue.key for i in self.defect_duplicate_list for j in i.fields.issuelinks if hasattr(j, 'inwardIssue') and 'CORE-' in j.inwardIssue.key]
            return sum(total_core_occurrence_count.__len__()
                       if (total_core_occurrence_count :=
                           self.jira_client.search_by_filter(str_filter=f'project = CoreCare AND "Epic Link" = {epic} AND "g/eNodeB SW version" = {last_version}',
                                                             fields=get_full_field_list()))
                       else 0 for epic in epics)

    def get_core_system_uptime_min_by_filter_for_duplicate(self, last_version):
        if hasattr(self, 'jira_client') and hasattr(self, 'defect_duplicate_list'):
            epics = [j.inwardIssue.key for i in self.defect_duplicate_list for j in i.fields.issuelinks if hasattr(j, 'inwardIssue') and 'CORE-' in j.inwardIssue.key]

            core_list = [self.jira_client.search_by_filter(
                str_filter=f'project = CoreCare AND "Epic Link" = {epic} AND "g/eNodeB SW version" = {last_version}',
                fields=get_full_field_list()
            ) for epic in epics]
            return [item for sublist in core_list for item in sublist]

    def get_cores_for_versions_by_filter_for_duplicate(self, versions):
        if hasattr(self, 'jira_client') and hasattr(self, 'epic'):
            versions_list = []
            for version in versions:
                if v := self.jira_client.search_by_filter(
                        str_filter=f'project = CoreCare AND "Epic Link" = {self.epic} AND "g/eNodeB SW version" = {version}',
                        fields=get_full_field_list()
                ):
                    # {vv.key: vv for vv in versions_list}
                    versions_list.extend(v)
            return list({vv.key: vv for vv in versions_list}.values())

    def get_total_core_occurrence_count_by_filter(self):
        if hasattr(self, 'jira_client') and hasattr(self, 'epic'):
            if total_core_occurrence_count := self.jira_client.search_by_filter(
                    str_filter=f'project = CoreCare AND "Epic Link" = {self.epic}',
                    fields=get_full_field_list()
            ):
                return total_core_occurrence_count.__len__()
            else:
                return 0

    def get_last_version_core_occurrence_count_by_filter(self, last_version):
        if hasattr(self, 'jira_client') and hasattr(self, 'epic'):
            if last_version_core_occurrence := self.jira_client.search_by_filter(
                    str_filter=f'project = CoreCare AND "Epic Link" = {self.epic} AND "g/eNodeB SW version" = {last_version}',
                    fields=get_full_field_list()
            ):
                return last_version_core_occurrence.__len__()
            else:
                return 0

    def _get_last_version_core_occurrence_count_by_filter(self, defect_object):
        if hasattr(self, 'crash_details') and hasattr(self, 'defect_is_duplicate') and hasattr(self, 'get_defect_last_version'):
            if self.defect_is_duplicate:
                return self.get_last_version_core_occurrence_count_by_filter_for_duplicate(self.get_defect_last_version(defect_object.fields.customfield_13707)) \
                    if self.crash_details['gnb_version'] != 'There_is_no_version' else -1
            else:
                return self.get_last_version_core_occurrence_count_by_filter(self.get_defect_last_version(defect_object.fields.customfield_13707)) \
                    if self.crash_details['gnb_version'] != 'There_is_no_version' else -1

    def get_core_system_uptime_min_by_filter(self, last_version):
        if hasattr(self, 'jira_client') and hasattr(self, 'epic'):
            return self.jira_client.search_by_filter(
                str_filter=f'project = CoreCare AND "Epic Link" = {self.epic} AND "g/eNodeB SW version" = {last_version}',
                fields=get_full_field_list()
            )

    def get_cores_for_versions_by_filter(self, versions):
        if hasattr(self, 'jira_client') and hasattr(self, 'epic'):
            versions_list = []
            for version in versions:
                if v := self.jira_client.search_by_filter(
                        str_filter=f'project = CoreCare AND "Epic Link" = {self.epic} AND "g/eNodeB SW version" = {version}',
                        fields=get_full_field_list()
                ):
                    # {vv.key: vv for vv in versions_list}
                    versions_list.extend(v)
            return list({vv.key: vv for vv in versions_list}.values())

    def found_epic_bt_by_filter(self):
        if hasattr(self, 'jira_client') and hasattr(self, 'crash_details'):
            if 'CUCP' in self.crash_details["type_crash_name"].upper():
                return self.jira_client.search_by_filter(
                    str_filter=f'project = CoreCare AND type = Epic AND status != Done AND labels = {self.crash_details["back_trace_hash"]} AND "Product At Fault" = vCU-CP',
                    fields=get_full_field_list()
                )
            elif 'CUUP' in self.crash_details["type_crash_name"].upper():
                return self.jira_client.search_by_filter(
                    str_filter=f'project = CoreCare AND type = Epic AND status != Done AND labels = {self.crash_details["back_trace_hash"]} AND "Product At Fault" = vCU-UP',
                    fields=get_full_field_list()
                )
            elif 'DU' in self.crash_details["type_crash_name"].upper():
                if 'PHY_ASSERT' in self.crash_details["type_crash_name"].upper():
                    return self.jira_client.search_by_filter(
                        str_filter=f'project = CoreCare AND type = Epic AND status != Done AND labels = {self.crash_details["back_trace_hash"]} AND "Product At Fault" = Phy',
                        fields=get_full_field_list()
                    )
                else:
                    return self.jira_client.search_by_filter(
                        str_filter=f'project = CoreCare AND type = Epic AND status != Done AND labels = {self.crash_details["back_trace_hash"]} AND "Product At Fault" = vDU',
                        fields=get_full_field_list()
                    )
            elif 'XPU' in self.crash_details["type_crash_name"].upper():
                return self.jira_client.search_by_filter(
                    str_filter=f'project = CoreCare AND type = Epic AND status != Done AND labels = {self.crash_details["back_trace_hash"]} AND "Product At Fault" = XPU',
                    fields=get_full_field_list()
                )
            else:
                return self.jira_client.search_by_filter(
                    str_filter=f'project = CoreCare AND type = Epic AND status != Done AND labels = {self.crash_details["back_trace_hash"]}',
                    fields=get_full_field_list()
                )
            # need change to "Hash BT" field (after he will be label type)

    def get_open_defects_by_filter(self):
        if hasattr(self, 'jira_client') and hasattr(self, 'epic'):
            str_filter = f'issue in linkedissues({self.epic}) AND (status = '
            for status in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX:
                str_filter += f'{status} OR status = '
            str_filter = f'{str_filter[:-13]})'
            return self.jira_client.search_by_filter(str_filter=str_filter, fields=get_full_field_list())

    def get_defects_by_filter(self):
        if hasattr(self, 'jira_client') and hasattr(self, 'epic'):
            return self.jira_client.search_by_filter(str_filter=f'issue in linkedissues({self.epic}) AND issuetype = Defect AND project = "Defect Tracking"',
                                                     fields=get_full_field_list())

    def get_old_epic(self):
        if hasattr(self, 'jira_client') and hasattr(self, 'crash_details'):
            return self.jira_client.search_by_filter(
                str_filter=f'project = CORE AND '
                           f'issuetype = Epic AND '
                           f'labels = "{self.crash_details["old_back_trace_hash"]}" AND '
                           f'"Hash BT" ~ "{self.crash_details["old_back_trace_hash"]}"',
                fields=get_full_field_list()
            )

    def get_old_open_defects_by_filter(self, old_epics_str):
        if hasattr(self, 'jira_client') and hasattr(self, 'crash_details'):
            str_filter = ''.join(f'issue in linkedissues({old_epic}) OR ' for old_epic in old_epics_str.split(' or '))[:-3] + 'AND (status = '

            for status in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX:
                str_filter += f'{status} OR status = '
            str_filter = f'{str_filter[:-13]})'
            return self.jira_client.search_by_filter(str_filter=str_filter, fields=get_full_field_list())


class CoreCareSupportData(JiraFilters):
    def __init__(self):  # sourcery skip: raise-specific-error
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        if not hasattr(self, 'crash_details'):
            raise Exception('you cant access this class directly , you need to init the class from CoreCareProcessStrategy class')

        super(CoreCareSupportData, self).__init__()

    def check_close_defects_version(self):  # sourcery skip: last-if-guard
        if hasattr(self, 'crash_details'):
            current_version_dict = {}
            files_dict = {}

            if 'AIO' in self.crash_details['version_type'].upper():
                path = '\\\\192.168.127.231\\SWImages\\AIO'
            elif 'CU' in self.crash_details['type_crash_name'].upper():
                path = '\\\\192.168.127.231\\SWImages\\CU'
            elif 'DU' in self.crash_details['type_crash_name'].upper():
                path = '\\\\192.168.127.231\\SWImages\\DU'
            elif 'RU' in self.crash_details['type_crash_name'].upper():
                path = '\\\\192.168.127.231\\SWImages\\RU'
            elif 'XPU' in self.crash_details['type_crash_name'].upper():
                path = '\\\\192.168.127.231\\SWImages\\XPU'
            else:
                return current_version_dict, files_dict

            for dir_path, dir_names, file_names in os.walk(path):
                for dir_name in dir_names:
                    if dir_name and f'_{self.crash_details["gnb_version"].split("-", 1)[0]}' in dir_name:
                        last_modified_file = os.path.getctime(f'{dir_path}\\{dir_name}')
                        last_modified_file = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_modified_file))
                        last_modified_file = datetime.strptime(last_modified_file, '%Y-%m-%d %H:%M:%S')
                        files_dict[f'{dir_path}\\{dir_name}'] = last_modified_file
                        if f'{self.crash_details["gnb_version"]}' in dir_name or f'{self.crash_details["gnb_version"].replace("-", ".")}' in dir_name:
                            current_version_dict[f'{dir_path}\\{dir_name}'] = last_modified_file
                break

            files_dict = collections.OrderedDict(dict(sorted(files_dict.items(), key=lambda item: item[1])))

            return current_version_dict, files_dict

    @staticmethod
    def check_for_open_defect(defect):  # old way - NOT USED
        return any(True for stat in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX if defect.fields.status == stat)

    @staticmethod
    def build_folder_on_prt(folder_path=None):
        GeneralFolderActionClass().check_path_exist_and_create(folder_path=folder_path)

    def moving_files(self, dst_path=None):
        if hasattr(self, 'crash_details') and hasattr(self, 'defect') and dst_path:
            # dst_path = f'\\\\fs4\\PRT_Attachments\\{self.defect}'
            dst_path = f'\\\\192.168.127.231\\defects\\{self.defect}'
            FilesActions().copy_files_per_platform(
                full_path_file=f'{self.crash_details["link_to_core"]}\\{self.crash_details["core_file_name"]}',
                dst_path=dst_path
            )

    def build_folder_in_prt_and_moving_files(self, folder_path=None):
        if hasattr(self, 'defect'):
            if not folder_path:
                # folder_path = f'\\\\fs4\\PRT_Attachments\\{self.defect}'
                folder_path = f'\\\\192.168.127.231\\defects\\{self.defect}'
            self.build_folder_on_prt(folder_path=folder_path)
            self.moving_files(dst_path=folder_path)

    def get_defect_last_version(self, enodeb_sw_versions, return_last_or_close_last=True):
        # sourcery skip: last-if-guard, remove-unnecessary-else, swap-if-else-branches
        # return_last_or_close_last - if True => last  ;  if False => close_last
        if hasattr(self, 'jira_client') and hasattr(self, 'crash_details') and hasattr(self, 'defect_is_duplicate') and hasattr(self, 'defect_duplicate_list'):
            if self.defect_is_duplicate:
                for defect_object in self.defect_duplicate_list:
                    enodeb_sw_versions += defect_object.fields.customfield_13707.copy()  # g/eNodeB SW version
            enodeb_sw_versions = list(set(enodeb_sw_versions))
            if return_last_or_close_last:
                return self.get_bigger_version_from_list(enodeb_sw_versions, self.crash_details['gnb_version'])
            else:
                return self.get_bigger_version_from_list(enodeb_sw_versions, '00-00-00')

    def get_new_summary(self):  # sourcery skip: last-if-guard, low-code-quality
        if hasattr(self, 'jira_client') and hasattr(self, 'crash_details') and hasattr(self, 'defect'):  # sourcery no-metrics skip: last-if-guard
            self.jira_client.get_issue(issue_id=self.defect)
            summary = self.jira_client.issues[self.defect].issue.fields.summary
            summary_dict = {
                summary_part.split(": ")[0]: summary_part.split(": ")[1].replace("[", "").replace("]", "").split(", ")
                for summary_part in summary.replace("]", "]]").split("], ")
            }

            for summary_key, summary_value in summary_dict.items():
                if 'CoreCare-5G' in summary_key:
                    # if all([True if self.crash_details["site"].split(" ")[1].upper() not in value.upper() else False for value in summary_value]):
                    if all(self.crash_details["site"].split(" ")[1].upper() not in value.upper() for value in summary_value):
                        summary_dict[summary_key].append(self.crash_details["site"].split(" ")[1].upper())
                    summary_dict[summary_key] = list(set(summary_dict[summary_key]))

                elif 'Core Occurrence Count' in summary_key:
                    summary_dict[summary_key][0] = f'Total; {self._get_total_core_occurrence_count_by_filter()} times'
                    if self.crash_details['back_trace'] not in {'There is no version', 'Corrupted Core'}:
                        # summary_dict[summary_key][1] = \
                        #     f'Last SR Version; {self.get_last_version_core_occurrence_count_by_filter(self.get_defect_last_version(defect_object))} times'
                        defect_object = self.jira_client.issues[self.defect].issue
                        summary_dict[summary_key][1] = f'Last SR Version; {self._get_last_version_core_occurrence_count_by_filter(defect_object)} times'
                elif 'CoreType' in summary_key:
                    if all(self.crash_details["type_crash_name"].replace(" core", "").upper() not in value.upper() for value in summary_value):
                        summary_dict[summary_key].append(self.crash_details["type_crash_name"].replace(" core", "").upper())
                    summary_dict[summary_key] = list(set(summary_dict[summary_key]))
                elif 'SR' in summary_key:
                    if all(
                            f'{self.crash_details["gnb_version"].split("-", 1)[0]}'.upper()
                            not in value.upper()
                            for value in summary_value
                    ):
                        summary_dict[summary_key].append(f'SR{self.crash_details["gnb_version"].split("-", 1)[0]}')
                    summary_dict[summary_key] = list(set(summary_dict[summary_key]))
                elif 'HashBT' in summary_key:
                    if all(
                            f'{self.crash_details["back_trace_hash"]}'.upper()
                            not in value.upper()
                            for value in summary_value
                    ):
                        summary_dict[summary_key].append(f'{self.crash_details["back_trace_hash"]}')
                    summary_dict[summary_key] = list(set(summary_dict[summary_key]))
                else:
                    continue

            summary = ''
            for k, v in summary_dict.items():
                vv = f'{v}'.replace("'", "")
                summary += f'{k}: {vv}, '
            return summary[:-2]

    def get_product_at_fault(self):
        # sourcery skip: last-if-guard, remove-unnecessary-else, swap-if-else-branches
        if hasattr(self, 'crash_details'):
            if 'CUCP' in self.crash_details["type_crash_name"].upper():
                return 'vCU-CP'
            elif 'CUUP' in self.crash_details["type_crash_name"].upper():
                return 'vCU-UP'
            elif 'DU' in self.crash_details["type_crash_name"].upper():
                if 'PHY_ASSERT' in self.crash_details["type_crash_name"].upper():
                    return 'Phy'
                else:
                    return 'vDU'
            elif 'RU' in self.crash_details["type_crash_name"].upper():
                return 'RU'
            elif 'XPU' in self.crash_details["type_crash_name"].upper():
                return 'XPU'
            else:
                return 'Unknown'
        else:
            return 'Unknown'

    def get_system_runtime_minutes(self):
        # sourcery skip: merge-duplicate-blocks, remove-unnecessary-else, swap-if-else-branches
        if hasattr(self, 'crash_details'):
            if 'unknown' not in self.crash_details["system_runtime"]:
                t = self.crash_details['system_runtime'].split(':')
                t = CalculateTime(h=t[0], m=t[1], s=t[2]).calculate_minutes()
                return t if t > 0 else 1
            else:
                return 1
        else:
            return 1

    def get_core_system_uptime(self):
        if hasattr(self, 'crash_details'):
            if system_runtime_minutes := self.get_system_runtime_minutes():
                if system_runtime_minutes == -1:
                    return 'N/A'
                elif system_runtime_minutes <= 15:
                    return '<15min'
                elif system_runtime_minutes <= 30:
                    return '16-30min'
                elif system_runtime_minutes <= 45:
                    return '31-45min'
                elif system_runtime_minutes <= 60:
                    return '46-60min'
                elif system_runtime_minutes <= 90:
                    return '1-1.5hour'
                elif system_runtime_minutes <= 120:
                    return '1.5-2hour'
                elif system_runtime_minutes <= 180:
                    return '2-3hour'
                elif system_runtime_minutes <= 240:
                    return '3-4hour'
                elif system_runtime_minutes <= 300:
                    return '4-5hour'
                elif system_runtime_minutes <= 360:
                    return '5-6hour'
                elif system_runtime_minutes <= 600:
                    return '6-10hour'
                elif system_runtime_minutes <= 900:
                    return '10-15hour'
                elif system_runtime_minutes <= 1200:
                    return '15-20hour'
                elif system_runtime_minutes <= 1500:
                    return '20-25hour'
                elif system_runtime_minutes <= 2160:
                    return '25-36hour'
                elif system_runtime_minutes <= 2880:
                    return '36-48hour'
                elif system_runtime_minutes <= 4320:
                    return '48-72hour'
                else:
                    return '48-72hour'
        return 'N/A'

    @staticmethod
    def find_min_max(cores):
        max_core = 0
        min_core = 9999999999
        for core in cores:
            if core.fields.customfield_14801 and core.fields.customfield_14801 > max_core:
                max_core = core.fields.customfield_14801

            if core.fields.customfield_14801 and core.fields.customfield_14801 < min_core:
                min_core = core.fields.customfield_14801

        if max_core != 0 and min_core != 9999999999:
            return max_core, min_core
        else:
            return 'N/A', 'N/A'

    def get_core_system_uptime_for_defect(self, last_version):
        max_last_version = 'N/A'
        min_last_version = 'N/A'
        max_all_version = 'N/A'
        min_all_version = 'N/A'

        core_system_uptime = [self.get_core_system_uptime()]

        if hasattr(self, 'defect') and hasattr(self, 'core') and hasattr(self, 'jira_client') and hasattr(self, 'defect_is_duplicate') and hasattr(self, 'defect_duplicate_list'):
            if not self.defect:
                max_last_version = self.jira_client.issues[self.core].issue.fields.customfield_14801
                min_last_version = self.jira_client.issues[self.core].issue.fields.customfield_14801
            else:
                if self.defect_is_duplicate:
                    cores_last_version = self.get_core_system_uptime_min_by_filter_for_duplicate(last_version)
                else:
                    cores_last_version = self.get_core_system_uptime_min_by_filter(last_version)
                max_last_version, min_last_version = self.find_min_max(cores_last_version)

                defect_obj = self.jira_client.issues[self.defect].issue
                if self.defect_is_duplicate:
                    enodeb_sw_versions = []
                    for defect_object in self.defect_duplicate_list:
                        enodeb_sw_versions += defect_object.fields.customfield_13707.copy()  # g/eNodeB SW version

                    cores_all_version = self.get_cores_for_versions_by_filter_for_duplicate(enodeb_sw_versions)  # g/eNodeB SW version
                else:
                    cores_all_version = self.get_cores_for_versions_by_filter(defect_obj.fields.customfield_13707)  # g/eNodeB SW version

                max_all_version, min_all_version = self.find_min_max(cores_all_version)

                if defect_obj.fields.customfield_14803:  # core system uptime
                    core_system_uptime.extend([i for i in defect_obj.fields.customfield_14803 if 'min_' not in i and 'max_' not in i])

        # core_system_uptime.extend(
        return f'min_last_version:{min_last_version} ' \
               f'max_last_version:{max_last_version} ' \
               f'min_all_version:{min_all_version} ' \
               f'max_all_version:{max_all_version} '
        # return core_system_uptime

    def get_core_system_uptime_min(self, last_version):
        # sourcery skip: assign-if-exp, remove-unnecessary-else, swap-if-else-branches
        if hasattr(self, 'jira_client') or hasattr(self, 'defect_is_duplicate'):
            if self.defect_is_duplicate:
                cores = self.get_core_system_uptime_min_by_filter_for_duplicate(last_version)
            else:
                cores = self.get_core_system_uptime_min_by_filter(last_version)
            total_core_system_uptime_min = sum(
                core.fields.customfield_14801
                for core in cores
                if core.fields.customfield_14801
            )

            if len(cores) > 1:
                return total_core_system_uptime_min // len(cores)
            else:
                return total_core_system_uptime_min
        else:
            return 1

    def _get_total_core_occurrence_count_by_filter(self):
        if hasattr(self, 'defect_is_duplicate'):
            return self.get_total_core_occurrence_count_by_filter_for_duplicate() if self.defect_is_duplicate else self.get_total_core_occurrence_count_by_filter()

    def get_reproducibility_frequency(self):
        core_occurrence_count = self._get_total_core_occurrence_count_by_filter()
        if core_occurrence_count <= 1:
            return 'Once'
        elif 1 < core_occurrence_count <= 5:
            return '2-5 times'
        else:
            return '>5 times'

    def check_if_current_bigger_from_last_version(self, current_version, last_occurred_gnb_software_version):
        if hasattr(self, 'jira_client') and hasattr(self, 'crash_details') and hasattr(self, 'defect'):
            current_sr_version = current_version.split("-", 1)[0]
            current_version = current_version.split("-", 1)[1]
            if float(last_occurred_gnb_software_version.split("-", 1)[0]) != float(current_sr_version):
                return False
            if (
                    int(current_version.split("-", 1)[0]) > int(last_occurred_gnb_software_version.split("-", 1)[1].split("-", 1)[0])) or \
                    (
                            int(current_version.split("-", 1)[0]) == int(last_occurred_gnb_software_version.split("-", 1)[1].split("-", 1)[0]) and
                            float(current_version.split("-", 1)[1]) > float(last_occurred_gnb_software_version.split("-", 1)[1].split("-", 1)[1])
                    ):
                return True

    def get_bigger_version_from_list(self, version_list, current_ver=None):
        # sourcery skip: assign-if-exp, last-if-guard, lift-duplicated-conditional, merge-else-if-into-elif, or-if-exp-identity, remove-unnecessary-else, swap-if-else-branches
        if hasattr(self, 'crash_details'):
            if current_ver:
                max_ver = current_ver
            else:
                max_ver = self.crash_details['gnb_version']

            if max_ver == 'unknown_version':
                return ''

            for ver in version_list:
                try:
                    if ver == 'unknown_version':
                        continue
                    ver = ver.split('_')[-1]

                    if float(ver.split('-')[0]) > float(max_ver.split('-')[0]):
                        max_ver = ver
                    elif float(ver.split('-')[0]) < float(max_ver.split('-')[0]):
                        max_ver = max_ver
                    else:
                        if float(ver.split('-')[1]) > float(max_ver.split('-')[1]):
                            max_ver = ver
                        elif float(ver.split('-')[1]) < float(max_ver.split('-')[1]):
                            max_ver = max_ver
                        else:
                            if len(ver.split('-')) > 2 and \
                                    (
                                            (
                                                    float(ver.split('-')[2].split('.')[0]) > float(max_ver.split('-')[2].split('.')[0])
                                            ) or
                                            (
                                                    float(ver.split('-')[2].split('.')[0]) == float(max_ver.split('-')[2].split('.')[0]) and
                                                    float(ver.split('-')[2].split('.')[1]) > float(max_ver.split('-')[2].split('.')[1])
                                            )
                                    ):
                                max_ver = ver
                            elif len(ver.split('-')) > 2 and float(ver.split('-')[2]) < float(max_ver.split('-')[2]):
                                max_ver = max_ver
                except Exception:
                    continue
            return max_ver
        else:
            return ''

    def get_last_occurred_gnb_software_version(self):
        if hasattr(self, 'jira_client') and hasattr(self, 'crash_details') and hasattr(self, 'defect') and hasattr(self, 'defect_duplicate_list'):
            # last_occurred_gnb_software_versions = self.jira_client.issues[self.defect].issue.fields.customfield_18401  # Last Occurred GNB Versions
            last_occurred_gnb_software_versions = []
            for defect in self.defect_duplicate_list:
                if defect.fields.customfield_18401:
                    last_occurred_gnb_software_versions.extend(defect.fields.customfield_18401)
            return self.get_bigger_version_from_list(last_occurred_gnb_software_versions, self.crash_details["gnb_version"])
        return ''


class CoreCareProcessStrategy(ABC, CoreCareSupportData):
    @abstractmethod
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.crash_details = None
        self.process_configuration = None
        self.jira_client = None

        self.epic = None
        self.core = None
        self.defect = None
        self.defect_is_duplicate = False
        self.defect_duplicate_list = []

        super(CoreCareProcessStrategy, self).__init__()
        super(CoreCareSupportData, self).__init__()

        self._tar = None
        self._tar_members = None

    @abstractmethod
    def add_to_self(self, obj: dict):
        # sourcery skip: merge-comparisons, remove-redundant-continue
        for k, v in obj.items():
            if k == 'logger' or k == 'processing_strategy':
                continue
            else:
                setattr(self, k, v)

    @abstractmethod
    def print_start(self):
        pass  # Used in child class

    @abstractmethod
    def get_more_data_from_files(self):
        pass

    @abstractmethod
    def get_data_from_acp(self):
        pass

    @abstractmethod
    def found_customer(self):
        pass

    @abstractmethod
    def replace_ip_address_with_setup_name(self):
        # self.crash_details['ip_address'] =
        # print(self.process_configuration['REPLACE_TEST_ENVIRONMENTS']["PATH"])
        pass

    @abstractmethod
    def found_epic(self):
        epic_obj = self.found_epic_bt_by_filter()
        if epic_obj.iterable:
            self.epic = epic_obj.iterable[0].key
            self.logger.info('Epic was found')
            self.logger.info(f'Epic key is: {self.epic}\n')
        else:
            self.epic = None
            self.logger.info('Epic was not found')

    @abstractmethod
    def create_epic(self):  # sourcery skip: remove-redundant-fstring
        minimal_epic_data = [
            # Required fields
            {'reporter': [f'CoreCare-5G']},  # reporter
            {'summary': [
                build_new_summary_for_memory_exhaustion(self.crash_details["back_trace"])
                if 'M.E:' in self.crash_details["back_trace"]
                else f'{self.crash_details["back_trace"][:254]}'
            ]},
            {'customfield_10002': [
                build_new_summary_for_memory_exhaustion(self.crash_details["back_trace"])
                if 'M.E:' in self.crash_details["back_trace"]
                else f'{self.crash_details["back_trace"][:254]}'
            ]},  # Epic Name

            # Other fields
            # {'description': [f'']},
            {'customfield_10800': [f'{self.crash_details["version_type"]}' if self.crash_details["version_type"] != 'None' else 'undefined']},  # BS Hardware Type
            {'customfield_18301': [f'{self.crash_details["back_trace_hash"]}']},  # Hash BT
            {'labels': [f'{self.crash_details["back_trace_hash"]}']},  # hash number
            {'fixVersions': [f'SR{self.crash_details["gnb_version"].split("-", 1)[0]}'
                             if self.crash_details['gnb_version'] != 'There_is_no_version' else 'Unknown']},  # SR Versions
            {'customfield_10202': [f'{self.get_product_at_fault()}']},  # product at fault
            {'customfield_11003': [f'{self.crash_details["ip_address"]}', f'{self.crash_details["setup_name"]}']},  # test environments
            {'customfield_14803': [f'{self.get_core_system_uptime()}']},  # core system uptime
            {'customfield_13707': [f'{self.crash_details["gnb_version"]}']},  # g/eNodeB SW version
        ]

        if self.crash_details['test_flag']:
            minimal_epic_data.extend((
                {'labels': [f'{self.crash_details["back_trace_hash"]}', 'AvizTest']},  # labels
            ))

        self.epic = self.jira_client.create_issue(project='CORE', issue_type='Epic', data=minimal_epic_data)

        if self.epic:
            self.logger.info(f'Epic was created')
            self.logger.info(f'Epic key is: {self.epic}\n')
            self.update_epic_after_create()
        else:
            self.logger.error(f'Epic was not created')

    @abstractmethod
    def update_epic_if_found(self):
        update_epic_data = {
            'set': [],
            'add': [
                {'customfield_11003': [f'{self.crash_details["ip_address"]}', f'{self.crash_details["setup_name"]}']},  # test environments
                {'customfield_10800': [f'{self.crash_details["version_type"]}' if self.crash_details["version_type"] != 'None' else 'undefined']},  # BS Hardware Type
                {'fixVersions': [f'SR{self.crash_details["gnb_version"].split("-", 1)[0]}'
                                 if self.crash_details['gnb_version'] != 'There_is_no_version' else 'Unknown']},  # SR Versions
                {'customfield_13707': [f'{self.crash_details["gnb_version"]}']},  # g/eNodeB SW version
                {'customfield_14803': [f'{self.get_core_system_uptime()}']},  # core system uptime
            ]
        }
        self.jira_client.update_issue(issue_id=self.epic, data=update_epic_data)

        if self.epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {self.epic}\n')
        else:
            self.logger.info('Epic was not updated')

    @abstractmethod
    def found_or_create_epic(self):
        self.found_epic()
        if self.epic:
            self.update_epic_if_found()
        else:
            self.create_epic()

    @abstractmethod
    def update_epic_after_create(self):
        pass  # Used in child class

    @abstractmethod
    def update_epic(self):
        pass  # Used in child class

    @abstractmethod
    def update_epic_after_core(self):
        update_epic_data = {
            'set': [
                {'customfield_15000': [self.get_total_core_occurrence_count_by_filter()]},  # core occurrence count
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.epic, data=update_epic_data)

        if self.epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {self.epic}\n')
        else:
            self.logger.info('Epic was not updated')

    @abstractmethod
    def link_defect_to_epic(self):
        self.jira_client.create_issue_link(project='CoreCare', link_from_issue=self.epic, link_to_issue=self.defect)

    @abstractmethod
    def link_defect_to_last_defect(self):
        self.jira_client.create_issue_link(project='Defect', link_from_issue=self.process_configuration['LINK_TO_LAST_DEFECT'][1],
                                           link_to_issue=self.defect)

    def link_defect_tracking_to_bubble_bugs(self, bubble_bug_issue):
        self.jira_client.transition_issue(bubble_bug_issue, 'Duplicate')
        self.jira_client.create_issue_link(project='duplicates', link_from_issue=bubble_bug_issue, link_to_issue=self.defect)

    @abstractmethod
    def update_epic_after_defect(self):
        pass

    @abstractmethod
    def update_core_after_defect(self):
        update_core_data = {
            'set': [],
            'add': [
                {'labels': [f'{self.defect}']},  # labels
            ],
        }

        self.jira_client.update_issue(issue_id=self.core, data=update_core_data)

        if self.core:
            self.logger.info('Core was updated')
            self.logger.info(f'Core key is: {self.core}\n')
        else:
            self.logger.info('Core was not updated')

    @abstractmethod
    def create_core(self):  # sourcery skip: remove-redundant-fstring
        description = '{code:java|title=Core Headline}\n' + self.crash_details["back_trace"].replace(" -> ", "\n") + '{code}\n\n' + \
                      '{code:java|title=Full BT}\n' + self.crash_details["full_bt"].replace(" -> ", "\n") + '{code}\n\n'
        minimal_core_data = [
            # Required fields
            {'reporter': [f'CoreCare-5G']},  # reporter
            {'summary': [f'{self.crash_details["back_trace"][:254]}']},  # summary
            {'customfield_10202': [f'{self.get_product_at_fault()}']},  # product at fault

            # Other fields
            {'description': [f'{description}']},  # description
            {'customfield_10800': [f'{self.crash_details["version_type"]}' if self.crash_details["version_type"] != 'None' else 'undefined']},  # BS Hardware Type
            {'customfield_18301': [f'{self.crash_details["back_trace_hash"]}']},  # Hash BT
            {'customfield_18302': [f'{self.crash_details["core_pid"]}']},  # Crash PID
            {'labels': [f'{self.crash_details["back_trace_hash"]}']},  # hash number
            {'fixVersions': [f'SR{self.crash_details["gnb_version"].split("-", 1)[0]}'
                             if self.crash_details['gnb_version'] != 'There_is_no_version' else 'Unknown']},  # SR Versions
            {'customfield_13707': [f'{self.crash_details["gnb_version"]}']},  # g/eNodeB SW version
            {'customfield_14900': [f'{self.crash_details["site"]}']},  # core discovery site
            {'customfield_10736': [{
                'value': f'{self.crash_details["site"].split(" ", 1)[0]}',
                'child': f'{self.crash_details["site"].split(" ", 1)[1]}'
            }]
            },  # Discovery Site / Customer
            {'customfield_10508': [f'{self.epic}']},  # link
            {'customfield_12600': [f'{self.crash_details["link_to_core"]}\\{self.crash_details["core_file_name"]}']},  # core files path
            {'customfield_11003': [f'{self.crash_details["ip_address"]}', f'{self.crash_details["setup_name"]}']},  # test environments
            {'customfield_14803': [f'{self.get_core_system_uptime()}']},  # core system uptime
            {'customfield_14801': [int(self.get_system_runtime_minutes())]},  # Core SystemUpTime (min)
            {'customfield_10975': [f'{self.crash_details["core_file_name"]}']},  # Notes
            {'customfield_19502': [f'{self.crash_details["core_file_name"]}']},  # Core file names
        ]

        if self.crash_details['test_flag']:
            minimal_core_data.extend((
                {'labels': [f'{self.crash_details["back_trace_hash"]}', 'AvizTest']},  # labels
            ))

        self.core = self.jira_client.create_issue(project='CORE', issue_type='Core', data=minimal_core_data)
        # self.jira_client.issues[self.core].issue.update(fields={"customfield_10000": str(self.epic)})  # Epic Link

        if self.core:
            self.logger.info(f'Core was created')
            self.logger.info(f'Core key is: {self.core}\n')
        else:
            self.logger.error(f'Core was not created')

    @abstractmethod
    def update_core(self):
        self.jira_client.issues[self.core].issue.update(fields={"customfield_10000": str(self.epic)})  # Epic Link

    @abstractmethod
    def update_defect_document_reference_name(self):
        self.build_folder_in_prt_and_moving_files()
        update_defect_data = {
            'set': [
                # {'customfield_10713': [f'\\\\fs4\\PRT_Attachments\\{self.defect}']},  # Document reference/name
                {'customfield_10713': [f'\\\\192.168.127.231\\defects\\{self.defect}']},  # Document reference/name
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info('Defect was not updated')

    @abstractmethod
    def create_defect(self, entity=None):
        # sourcery skip: assign-if-exp, remove-redundant-fstring, use-named-expression
        if 'There is no version' in self.crash_details['back_trace']:
            description = '{code:java|title=Core Headline}\nCore data is missing - ' + self.crash_details["back_trace"].replace(" -> ", "\n") + '{code}\n\n'
            summary = f'CoreCare-5G: [{self.crash_details["site"].split(" ")[1]}], ' \
                      f'Core Occurrence Count: [Total; {self._get_total_core_occurrence_count_by_filter()} times, ' \
                      f'CoreType: [{self.crash_details["type_crash_name"].replace(" core", "").upper()}], ' \
                      f'HashBT: [{self.crash_details["back_trace_hash"]}]' \
                      f' - Core data is missing'
        elif 'Corrupted Core' in self.crash_details['back_trace']:
            description = '{code:java|title=Core Headline}\n' + self.crash_details["back_trace"].replace(" -> ", "\n") + '{code}\n\n'
            summary = f'CoreCare-5G: [{self.crash_details["site"].split(" ")[1]}], ' \
                      f'Core Occurrence Count: [Total; {self._get_total_core_occurrence_count_by_filter()} times, ' \
                      f'CoreType: [{self.crash_details["type_crash_name"].replace(" core", "").upper()}], ' \
                      f'HashBT: [{self.crash_details["back_trace_hash"]}]' \
                      f' - {self.crash_details["back_trace"]}'
        else:
            summary = f'CoreCare-5G: [{self.crash_details["site"].split(" ")[1]}], ' \
                      f'Core Occurrence Count: [Total; {self._get_total_core_occurrence_count_by_filter()} times, ' \
                      f'Last SR Version; {self.get_last_version_core_occurrence_count_by_filter(self.crash_details["gnb_version"])} times], ' \
                      f'CoreType: [{self.crash_details["type_crash_name"].replace(" core", "").upper()}], ' \
                      f'SR: [{self.crash_details["gnb_version"].split("-", 1)[0]}], ' \
                      f'HashBT: [{self.crash_details["back_trace_hash"]}]'

            description = ''
            if old_epics := self.get_old_epic():
                link_str = '|https://helpdesk.airspan.com/browse'
                # if old_epics_str := ' or '.join([i.key for i in old_epics if i and i.key != self.epic]):
                if old_epics_str := ' or '.join(f'[{_epic.key}{link_str}/{_epic.key}]' for _epic in old_epics if _epic and _epic.key != self.epic):
                    open_defects = self.get_old_open_defects_by_filter(' or '.join([i.key for i in old_epics if i and i.key != self.epic]))
                    # if open_defects_str := ' or '.join([i.key for i in open_defects if i]):
                    if open_defects_str := ' or '.join(f'[{_def.key}{link_str}/{_def.key}]' for _def in open_defects if _def):
                        description = f'+*Pay Attention!*+\n' \
                                          f'*Can be related to BT crash (Epic):* {old_epics_str}\n' \
                                          f'Can be duplicate to Defect: {open_defects_str}\n\n'
                    else:
                        description = f'+*Pay Attention!*+\n' \
                                          f'*Can be related to BT crash (Epic):* {old_epics_str}|https://helpdesk.airspan.com/browse/{old_epics_str}\n\n'

            try:
                if 'memory exhaustion' in summary.lower():
                    tr_gz_file_name = 'core_mem_info'
                    if not hasattr(self, '_tar') or not hasattr(self, '_tar_members'):
                        raise
                    fp_read = read_tar_gz_file(self._tar, self._tar_members, tr_gz_file_name=tr_gz_file_name, entity=entity)
                    description += '{code:java|title=Core Headline}\n' + fp_read.decode('UTF-8') + '{code}\n\n'
                else:
                    description += '{code:java|title=Core Headline}\n' + self.crash_details["back_trace"].replace(" -> ", "\n") + '{code}\n\n' + \
                                   '{code:java|title=Full BT}\n' + self.crash_details["full_bt"].replace(" -> ", "\n") + '{code}\n\n'
            except Exception:
                description += '{code:java|title=Core Headline}\n' + self.crash_details["back_trace"].replace(" -> ", "\n") + '{code}\n\n' + \
                                   '{code:java|title=Full BT}\n' + self.crash_details["full_bt"].replace(" -> ", "\n") + '{code}\n\n'

        epic_object = self.jira_client.issues[list(self.jira_client.issues.keys())[0]].issue
        ward_issue_link_list = ['inwardIssue', 'outwardIssue']
        old_defects = [
            getattr(epic_issue_links, ward_issue_link).key for epic_issue_links in epic_object.fields.issuelinks for ward_issue_link in ward_issue_link_list
            if getattr(epic_issue_links, ward_issue_link, None) and getattr(epic_issue_links, ward_issue_link).fields.issuetype.name.lower() == 'Defect'.lower()
        ]
        if old_defects:
            full_description = f'*Please Pay attention , there are old closed Defects on this BT Epic ([{self.epic}|https://helpdesk.airspan.com/browse/{self.epic}])*\n\n'
            description = full_description + description

        minimal_defect_data = [
            # Required fields
            {'reporter': [f'CoreCare-5G']},  # reporter
            {'summary': [f'{summary[:254]}']},  # summary
            {'customfield_10202': [f'{self.get_product_at_fault()}']},  # product at fault
            {'customfield_10736': [{
                'value': f'{self.crash_details["site"].split(" ", 1)[0]}',
                'child': f'{self.crash_details["site"].split(" ", 1)[1]}'
            }]
            },  # Discovery Site / Customer
            {'customfield_10200': [
                f'{"SR"+self.crash_details["gnb_version"].split("-", 1)[0] if len(self.crash_details["gnb_version"].split("-", 1)) > 1 else "Unknown"}'
            ]},  # Reported In Release (eNB)
            {'customfield_10800': [f'{self.crash_details["version_type"]}' if self.crash_details["version_type"] != 'None' else 'undefined']},  # BS Hardware Type
            {'customfield_10201': [f'{self.get_reproducibility_frequency()}']},  # Reproducibility/Frequency
            {'customfield_10406': ['High' if self._get_total_core_occurrence_count_by_filter() < 2 else 'Critical']},  # Severity

            # Other fields
            {'description': [f'{description}']},  # description
            {'labels': [f'Created_By_Core-Care', f'{self.crash_details["back_trace_hash"]}']},  # labels
            {'fixVersions': [f'SR{self.crash_details["gnb_version"].split("-", 1)[0]}'
                             if self.crash_details['gnb_version'] != 'There_is_no_version' else 'Unknown']},  # SR Versions
            {'customfield_18401': [self.crash_details["gnb_version"]]},  # Last Occurred GNB Versions
            # {'customfield_10726': [f'{self.crash_details["gnb_version"]}']},  # eNB /CD/DU - SW
            {'customfield_13707': [f'{self.crash_details["gnb_version"]}']},  # g/eNodeB SW version
            {'customfield_11003': [f'{self.crash_details["ip_address"]}', f'{self.crash_details["setup_name"]}']},  # test environments
            {'customfield_10731': [f'ACP']},  # EMS Type
            # {'customfield_10737': [f'aviz_test']},  # EMS Software Version
            {'customfield_11449': [f'Service disruption']},  # Defect Impact
            {'customfield_11200': [f'TBD']},  # Showstopper
            # {'customfield_10712': [{'value': 'Stability 2 Ues', 'child': 'small automation setups'}]},  # Defect Module / Sub-feature
            {'customfield_10712': [{'value': 'Stability 2 Ues', 'child': 'Empty'}]},  # Defect Module / Sub-feature
            {'customfield_19201': [self._get_total_core_occurrence_count_by_filter()]},  # Total Core Occurrence Count
            {'customfield_15000': [self.get_last_version_core_occurrence_count_by_filter(self.crash_details['gnb_version'])]},  # Occurrence count
            {'customfield_14801': [self.get_core_system_uptime_min(self.crash_details['gnb_version'])]},  # Core SystemUpTime (min)
            {'customfield_14803': [self.get_core_system_uptime_for_defect(self.crash_details['gnb_version'])]},  # CoreSysUpTime
            {'customfield_10715': [f'SR{self.crash_details["gnb_version"].split("-", 1)[0]}']},  # Target Release

            {'customfield_10734': [f'-1']},  # Bandwidth
            {'assignee': [f'{self.crash_details["setup_owner"]}']},  # assignee -> from another function
            {'customfield_19502': [f'{self.crash_details["core_file_name"]}']},  # Core file names
        ]
        if 'Customer' in self.crash_details['site']:
            minimal_defect_data.extend((
                {'customfield_13300': [f'{self.crash_details["site"].split(" ", 1)[1]}']},  # Customer name
                {'customfield_10736': [{'value': f'Customer', 'child': f'None'}]},  # Discovery Site / Customer
            ))

        if self.crash_details['test_flag']:
            minimal_defect_data.extend((
                {'labels': [f'Created_By_Core-Care', f'{self.crash_details["back_trace_hash"]}', 'AvizTest']},  # labels
            ))

        if self.check_if_master():
            project_name = 'DEF'
        else:
            project_name = 'BUG'

        self.defect = self.jira_client.create_issue(project=project_name, issue_type='Defect', data=minimal_defect_data)

        if self.defect:
            self.logger.info(f'Defect was created on {project_name}')
            self.logger.info(f'Defect key is: {self.defect}\n')
            self.update_defect_after_create()
        else:
            self.logger.error('Defect was not created')

    @abstractmethod
    def update_defect_if_found(self):  # sourcery skip: remove-redundant-fstring
        defect_object = self.jira_client.issues[self.defect].issue
        summary = self.get_new_summary()
        update_defect_data = {
            'set': [
                {'reporter': ['CoreCare-5G']},
                {'summary': [f'{summary[:254]}']},  # summary
                {'customfield_10201': [f'{self.get_reproducibility_frequency()}']},  # Reproducibility/Frequency
                {'customfield_19201': [self._get_total_core_occurrence_count_by_filter()]},  # Total Core Occurrence Count
                {'customfield_15000': [self._get_last_version_core_occurrence_count_by_filter(defect_object)]},  # Core Occurrence count
                {'customfield_14801': [
                    # self.get_core_system_uptime_min(self.get_defect_last_version(defect_object))
                    self.get_core_system_uptime_min(self.get_defect_last_version(defect_object.fields.customfield_13707))
                    if self.crash_details['gnb_version'] != 'There_is_no_version' else -1
                ]},  # Core SystemUpTime (min)
                {'customfield_14803': [
                     # self.get_core_system_uptime_for_defect(self.get_defect_last_version(defect_object))
                     self.get_core_system_uptime_for_defect(self.get_defect_last_version(defect_object.fields.customfield_13707))
                     if self.crash_details['gnb_version'] != 'There_is_no_version'
                     else 'N/A'
                 ]},  # CoreSysUpTime

                # waiting for replace field to list (instead of string)
                {'customfield_18401': [
                    self.get_last_occurred_gnb_software_version()
                    if self.crash_details['gnb_version'] != 'There_is_no_version'
                    else ''
                ]},  # Last Occurred GNB Versions
                {'customfield_10406': [f'Critical']},  # Severity
            ],
            'add': [
                {'labels': [f'Update_By_Core-Care', f'{self.crash_details["back_trace_hash"]}']},  # labels
                {'fixVersions': [f'SR{self.crash_details["gnb_version"].split("-", 1)[0]}'
                                 if self.crash_details['gnb_version'] != 'There_is_no_version' else 'Unknown']},  # SR Versions
                {'customfield_11003': [f'{self.crash_details["ip_address"]}', f'{self.crash_details["setup_name"]}']},  # test environments
                {'customfield_13707': [f'{self.crash_details["gnb_version"]}',
                                       self.get_last_occurred_gnb_software_version() if self.crash_details['gnb_version'] != 'There_is_no_version' else
                                       f'{self.crash_details["gnb_version"]}']},  # g/eNodeB SW version
                {'customfield_10800': [f'{self.crash_details["version_type"]}' if self.crash_details["version_type"] != 'None' else 'undefined']},  # BS Hardware Type
                {'customfield_19502': [f'{self.crash_details["core_file_name"]}']},  # Core file names

                # {'customfield_10737': [f'aviz_test']},  # EMS Software Version - ?????
            ]
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info(f'Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info(f'Defect was not updated')

    @abstractmethod
    def get_open_defects(self):
        defect_objs = self.get_open_defects_by_filter()
        if defect_objs.iterable:
            if any('DEF' in j for j in [i.key for i in defect_objs]):
                self.defect = [i.key for i in defect_objs if 'DEF' in i.key][0]
            else:
                self.defect = [i.key for i in defect_objs if 'BUG' in i.key][0]
                # self.defect = defect_objs[0].key
        else:
            self.defect = None
            self.logger.info('Open Defect was not found')

        if self.defect:
            self.jira_client.get_issue(self.defect)
            self.defect = self.jira_client.issues[self.defect].issue

    @staticmethod
    def check_if_defect_open(defect_status: str) -> bool:
        return any(True for stat in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX if f'"{defect_status}"' == stat)

    def get_open_defects_for_duplicate(self, defect: Union[str, object], defects_dict: dict) -> Union[str, dict]:
        defects_dict['defects_list'].append(defect)
        defects_dict['defects_list_key'].append(defect.key)

        self.jira_client.get_issue(defect.key)
        if self.check_if_defect_open(defect_status=self.jira_client.issues[defect.key].issue.fields.status.name):
            defects_dict['defects_open'].append(defect)

        self.jira_client.get_issue(defect)
        # defects_linked = self.jira_client.search_by_filter(f'project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues({defect}) AND status = Duplicate')
        defects_linked = self.jira_client.search_by_filter(
            f'project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues({defect}) AND reporter = CoreCare-5G ',
            fields=get_full_field_list()
        )

        for defect_linked in defects_linked:
            if defect_linked.key not in defects_dict['defects_list_key']:
                self.get_open_defects_for_duplicate(defect=defect_linked, defects_dict=defects_dict)
        return defects_dict

    @abstractmethod
    def found_defect(self):
        self.get_open_defects()
        if self.crash_details['gnb_version'] == 'There_is_no_version':
            return True

        if self.defect:
            defect = self.jira_client.search_by_filter(f'issuekey = {self.defect}', fields=get_full_field_list())
            # defects = defect + self.jira_client.search_by_filter(f'issue in linkedissues({self.defect}) AND (status = "Duplicate")', fields=get_full_field_list())
            # defects += self.jira_client.search_by_filter(f'issue in linkedissues({self.epic}) AND (status = "Duplicate") AND project = DEF', fields=get_full_field_list())
            defects = defect + self.jira_client.search_by_filter(f'issuetype = Defect AND issue in linkedissues({self.defect})', fields=get_full_field_list())
            defects += self.jira_client.search_by_filter(f'issuetype = Defect AND issue in linkedissues({self.epic}) AND (status = "Duplicate")', fields=get_full_field_list())
        else:
            # defects = self.jira_client.search_by_filter(f'issue in linkedissues({self.epic}) AND (status = "Duplicate")', fields=get_full_field_list())
            defects = self.jira_client.search_by_filter(f'issuetype = Defect AND issue in linkedissues({self.epic})', fields=get_full_field_list())
        self.defect_is_duplicate = False
        self.defect_duplicate_list = []
        _defects_dict = {'defects_list': [], 'defects_list_key': [], 'defects_open': []}

        for defect in defects:
            _defects_dict = self.get_open_defects_for_duplicate(defect=defect, defects_dict=_defects_dict)
        # self.logger.info(f'defect duplicate list is: {[i.key for i in _defects_dict["defects_list"]]}')

        for k, v in _defects_dict.items():
            _defects_dict[k] = list(set(v))

        if _defects_dict['defects_open'] and (self.defect or _defects_dict['defects_open'][0].fields.project.key == 'DEF'):
            self.defect_is_duplicate = True
            self.defect_duplicate_list = _defects_dict['defects_list']
            if not self.defect or self.jira_client.issues[self.defect].issue.fields.project.key != 'DEF':
                if any(
                    'DEF' in j
                    for j in [i.key for i in _defects_dict['defects_open']]
                ):
                    self.defect = [i for i in _defects_dict['defects_open'] if 'DEF' in i.key][0]
                else:
                    self.defect = [i for i in _defects_dict['defects_open'] if 'BUG' in i.key][0]
            return self.defect_is_duplicate

        if self.defect:
            return True

        defect_objs = self.get_defects_by_filter()
        if defect_objs.iterable:
            current_version_dict, files_dict = self.check_close_defects_version()
            if current_version_dict:
                # close_defect_last_version = self.get_defect_last_version(defect_objs.iterable[0], False)
                close_defect_last_version = self.get_defect_last_version(list({d_version for d in defect_objs.iterable for d_version in d.fields.customfield_13707}), False)
                k = None
                for k in list(files_dict.keys()):
                    if close_defect_last_version in k or close_defect_last_version.replace("-", ".") in k:
                        break
                    else:
                        k = None
                if k and current_version_dict and current_version_dict[list(current_version_dict.keys())[-1]] > files_dict[k]:
                    self.logger.info('Need to create a new defect + link to last close defect')
                    self.process_configuration['OPEN_DEFECT'] = True
                elif k and current_version_dict[list(current_version_dict.keys())[-1]] <= files_dict[k]:
                    self.logger.info('Not need to create a new defect')
                    self.process_configuration['OPEN_DEFECT'] = False
                else:
                    self.logger.info('There is no .pdf for close defect last version => Need to create a new defect')
                    self.process_configuration['OPEN_DEFECT'] = True
            else:
                self.logger.info('There is no .pdf for this version => Not need to create a new defect + link to last close defect')
                self.process_configuration['OPEN_DEFECT'] = False
                self.process_configuration['LINK_TO_LAST_DEFECT'][1] = defect_objs.iterable[0].key
        else:
            self.logger.info('There is no Defect, Need to create a new defect + link to Epic')
            self.process_configuration['OPEN_DEFECT'] = True

    def check_if_master(self):
        try:
            bubble_id = int(self.crash_details['gnb_version'].split('-')[2].split('.')[0]) if 'xpu'.upper() not in self.crash_details['type_crash_name'].upper() else 101
        except IndexError:
            bubble_id = -1
        return (
            'xpu'.upper() in self.crash_details['type_crash_name'].upper()
            or bubble_id < 100
        )

    @abstractmethod
    def found_or_create_defect(self):
        create_defect_flag = False
        self.get_open_defects()
        open_def_on_current_epic = deepcopy(self.defect)
        self.found_defect()
        if self.defect and open_def_on_current_epic and self.defect.key != open_def_on_current_epic.key and \
                self.jira_client.issues[self.defect.key].issue.fields.project.name in ['DEF', 'Defect Tracking'] and \
                self.jira_client.issues[open_def_on_current_epic.key].issue.fields.project.name in ['BUG', 'Bubble bugs']:
            self.link_defect_tracking_to_bubble_bugs(bubble_bug_issue=open_def_on_current_epic.key)

        if self.process_configuration['OPEN_DEFECT']:
            if self.defect:
                self.jira_client.get_issue(issue_id=self.defect)
                if self.jira_client.issues[self.defect].issue.fields.project.name in ['BUG', 'Bubble bugs'] and self.check_if_master():
                    bubble_bug_issue = deepcopy(self.defect)
                    # Need to create a new Defect
                    self.create_defect()
                    create_defect_flag = True
                    # Need to copy all the data from the Bugs to the new Defect ???
                    # Need to link between defect from "Defect Tracking" to defect from "Bubble bugs"
                    self.link_defect_tracking_to_bubble_bugs(bubble_bug_issue=bubble_bug_issue)
                else:
                    self.update_defect_if_found()
            else:
                self.create_defect()
                create_defect_flag = True

            if create_defect_flag:
                if self.process_configuration['LINK_TO_LAST_DEFECT'][0] and self.process_configuration['LINK_TO_LAST_DEFECT'][1]:
                    self.link_defect_to_last_defect()
                if self.defect:
                    self.link_defect_to_epic()
                    self.update_defect_document_reference_name()
                    self.set_assignee_on()
                    # self.set_reporter_on()  # not need

    @abstractmethod
    def update_defect_after_create(self):
        pass  # Used in child class

    @abstractmethod
    def update_defect(self):
        update_defect_data = {
            'set': [
                {'reporter': ['CoreCare-5G']}
            ],
            'add': [],
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info('Defect was not updated')

    @abstractmethod
    def set_assignee_on(self):
        pass

    @abstractmethod
    def set_reporter_on(self):
        pass

    @abstractmethod
    def check_missing_file_list(self, core_files_mandatory=None):
        missing_file_list = []
        for file in core_files_mandatory:
            try:
                fp_read = read_tar_gz_file(self._tar, self._tar_members, tr_gz_file_name=file, entity='DU_L2')
            except Exception:
                self.logger.exception('The file "_systeminfo" was not open')
                continue
            if not fp_read:
                missing_file_list.append(file)
        return missing_file_list

    def sanity_core_process(self, tar, tar_members):
        missing_file_list = self.check_missing_file_list()
        if gz_path := extract_specific_file(tar, tar_members, self.crash_details["core_file_name"].replace(".tgz", ".gz").replace("_test", ""), self.crash_details["link_to_core"], entity=None):
            core_validation_ins = CoreValidation(
                core_file_path=f'{gz_path}\\{self.crash_details["core_file_name"].replace(".tgz", ".gz")}',
                binary_timestamp=self.crash_details['core_validation_timestamp']
            )
            is_valid, _mass = core_validation_ins.core_validation(debug=False)
            if is_valid:
                self.logger.info('Sanity Pass')
                subject = f'Sanity {self.crash_details["entity_crash_name"]} Core - Pass'
                message_body = f'Sanity Pass - \n' \
                               f'The full path to the core file is: {self.crash_details["link_to_core"]}\\{self.crash_details["core_file_name"]} \n' \
                               f'BT is valid + there is no missing mandatory files \n\n' \
                               f'* "{_mass}" \n'
            else:
                self.logger.error('Sanity FAIL')
                subject = f'Sanity {self.crash_details["entity_crash_name"]} Core - Fail'
                message_body = f'Sanity Fail - ' \
                               f'The full path to the core file is: {self.crash_details["link_to_core"]}\\{self.crash_details["core_file_name"]} \n' \
                               f'\nThe missing mandatory files is: {missing_file_list}' \
                               f'\nThe Error massage is: {_mass} '
            os.remove(f'{gz_path}\\{self.crash_details["core_file_name"].replace(".tgz", ".gz")}')
        else:
            subject = f'Sanity {self.crash_details["entity_crash_name"]} Core - Fail'
            message_body = f'Sanity Fail - ' \
                           f'The full path to the core file is: {self.crash_details["link_to_core"]}\\{self.crash_details["core_file_name"]} \n' \
                           f'\nThe missing mandatory files is: {missing_file_list}' \
                           f'\nThe Error massage is: Unable to extract core '

        Notifications().send_email_by_gmail(
            # to=['azaguri@airspan.com', 'sdavid@airspan.com'],
            to=['azaguri@airspan.com', 'sdavid@airspan.com'],
            subject=subject,
            message_body=message_body
        )

    def process(self, crash_details: dict, process_configuration: dict, jira_client):
        self.__init__()

        self.logger.info(f'The class "{self.__class__.__name__}" is running')
        self.print_start()
        setattr(self, 'crash_details', crash_details)
        setattr(self, 'process_configuration', process_configuration)
        setattr(self, 'jira_client', jira_client)
        self.logger.info(f'The crash details is: \n{json.dumps(self.crash_details, indent=4, separators=(", ", " = "))}')
        self.logger.info(f'The process configuration is: \n{json.dumps(self.process_configuration, indent=4, separators=(", ", " = "))}')

        full_path_file = f'{self.crash_details["link_to_core"]}\\{self.crash_details["core_file_name"]}'
        if self.crash_details['gnb_version'] != 'There_is_no_version':
            tar, tar_members = get_tar_gz_file(full_path_file)
            setattr(self, '_tar', tar)
            setattr(self, '_tar_members', tar_members)
            # close_tar_gz_file_reader(tar)
        else:
            tar = None
            tar_members = None

        # Initialization process
        self.get_more_data_from_files()  # pass
        self.get_data_from_acp()  # pass
        self.found_customer()  # pass
        if self.process_configuration['REPLACE_TEST_ENVIRONMENTS']["REPLACE"]:
            self.replace_ip_address_with_setup_name()  # need to fill

        # Real process
        self.found_or_create_epic()
        if not self.epic:
            self.logger.exception('Epic was not found !!!')
            return
        self.update_epic()
        self.create_core()
        if not self.core:
            self.logger.exception('Core was not found !!!')
            return
        self.update_core()
        self.update_epic_after_core()

        if self.crash_details['core_validation_timestamp']:
            self.sanity_core_process(tar, tar_members)

        if self.process_configuration['OPEN_DEFECT']:
            if 'Customer' in self.crash_details['site']:
                self.crash_details['site'] = f"Customer {self.crash_details['customer_name']}"

            self.found_or_create_defect()
            if self.defect:
                self.update_defect()  # pass
                self.update_epic_after_defect()  # pass
                self.update_core_after_defect()  # pass

        with contextlib.suppress(Exception):
            if tar:
                close_tar_gz_file_reader(tar)

            if hasattr(self, '_tar'):
                close_tar_gz_file_reader(self._tar)

        print()


class CoreProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(CoreProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(CoreProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Unknown Core ...')

    def get_more_data_from_files(self):
        super(CoreProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(CoreProcess, self).get_data_from_acp()

    def found_customer(self):
        super(CoreProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(CoreProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(CoreProcess, self).found_epic()

    def create_epic(self):
        super(CoreProcess, self).create_epic()

    def update_epic_if_found(self):
        super(CoreProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(CoreProcess, self).found_or_create_epic()

    def update_epic(self):
        super(CoreProcess, self).update_epic()

    def update_epic_after_create(self):
        super(CoreProcess, self).update_epic_after_create()

    def update_epic_after_core(self):
        super(CoreProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(CoreProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(CoreProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(CoreProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(CoreProcess, self).update_core_after_defect()

    def create_core(self):
        super(CoreProcess, self).create_core()

    def update_core(self):
        super(CoreProcess, self).update_core()

    def update_defect_document_reference_name(self):
        super(CoreProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity=None):
        super(CoreProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(CoreProcess, self).update_defect_if_found()

    def found_defect(self):
        super(CoreProcess, self).found_defect()

    def get_open_defects(self):
        super(CoreProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(CoreProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(CoreProcess, self).update_defect_after_create()

    def update_defect(self):
        super(CoreProcess, self).update_defect()

    def set_assignee_on(self):
        super(CoreProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(CoreProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(CoreProcess, self).check_missing_file_list([])


class CUCPCoreProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(CUCPCoreProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(CUCPCoreProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Core CUCP ...')

    def get_more_data_from_files(self):
        super(CUCPCoreProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(CUCPCoreProcess, self).get_data_from_acp()

    def found_customer(self):
        super(CUCPCoreProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(CUCPCoreProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(CUCPCoreProcess, self).found_epic()

    def create_epic(self):
        super(CUCPCoreProcess, self).create_epic()

    def update_epic_if_found(self):
        super(CUCPCoreProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(CUCPCoreProcess, self).found_or_create_epic()

    def update_epic_after_create(self):
        super(CUCPCoreProcess, self).update_epic_after_create()
        update_epic_data = {
            'set': [
                {'customfield_16800': [self.crash_details["crash_version"]]},  # 5G_CU-CP_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.epic, data=update_epic_data)

        if self.epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {self.epic}\n')
        else:
            self.logger.info('Epic was not updated')

    def update_epic(self):
        super(CUCPCoreProcess, self).update_epic()

    def update_epic_after_core(self):
        super(CUCPCoreProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(CUCPCoreProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(CUCPCoreProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(CUCPCoreProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(CUCPCoreProcess, self).update_core_after_defect()

    def create_core(self):
        super(CUCPCoreProcess, self).create_core()

    def update_core(self):
        super(CUCPCoreProcess, self).update_core()
        update_core_data = {
            'set': [
                {'customfield_16800': [self.crash_details["crash_version"]]},  # 5G_CU-CP_Ver
                {'customfield_16801': [self.crash_details["crash_version"]]},  # 5G_CU-UP_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.core, data=update_core_data)

        if self.core:
            self.logger.info('Core was updated')
            self.logger.info(f'Core key is: {self.core}\n')
        else:
            self.logger.info('Core was not updated')

    def update_defect_document_reference_name(self):
        super(CUCPCoreProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity='CP'):
        super(CUCPCoreProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(CUCPCoreProcess, self).update_defect_if_found()

    def found_defect(self):
        super(CUCPCoreProcess, self).found_defect()

    def get_open_defects(self):
        super(CUCPCoreProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(CUCPCoreProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(CUCPCoreProcess, self).update_defect_after_create()
        update_defect_data = {
            'set': [
                {'customfield_16800': [self.crash_details["crash_version"]]},  # 5G_CU-CP_Ver
                {'customfield_16801': [self.crash_details["crash_version"]]},  # 5G_CU-UP_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def update_defect(self):
        super(CUCPCoreProcess, self).update_defect()

    def set_assignee_on(self):
        super(CUCPCoreProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(CUCPCoreProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(CUCPCoreProcess, self).check_missing_file_list(cucp_core_files_mandatory)


class CUUPCoreProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(CUUPCoreProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(CUUPCoreProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Core CUUP ...')

    def get_more_data_from_files(self):
        super(CUUPCoreProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(CUUPCoreProcess, self).get_data_from_acp()

    def found_customer(self):
        super(CUUPCoreProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(CUUPCoreProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(CUUPCoreProcess, self).found_epic()

    def create_epic(self):
        super(CUUPCoreProcess, self).create_epic()

    def update_epic_if_found(self):
        super(CUUPCoreProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(CUUPCoreProcess, self).found_or_create_epic()

    def update_epic_after_create(self):
        super(CUUPCoreProcess, self).update_epic_after_create()
        update_epic_data = {
            'set': [
                {'customfield_16800': [self.crash_details["crash_version"]]},  # 5G_CU-CP_Ver
                {'customfield_16801': [self.crash_details["crash_version"]]},  # 5G_CU-UP_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.epic, data=update_epic_data)

        if self.epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {self.epic}\n')
        else:
            self.logger.info('Epic was not updated')

    def update_epic(self):
        super(CUUPCoreProcess, self).update_epic()

    def update_epic_after_core(self):
        super(CUUPCoreProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(CUUPCoreProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(CUUPCoreProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(CUUPCoreProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(CUUPCoreProcess, self).update_core_after_defect()

    def create_core(self):
        super(CUUPCoreProcess, self).create_core()

    def update_core(self):
        super(CUUPCoreProcess, self).update_core()
        update_core_data = {
            'set': [
                {'customfield_16800': [self.crash_details["crash_version"]]},  # 5G_CU-CP_Ver
                {'customfield_16801': [self.crash_details["crash_version"]]},  # 5G_CU-UP_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.core, data=update_core_data)

        if self.core:
            self.logger.info('Core was updated')
            self.logger.info(f'Core key is: {self.core}\n')
        else:
            self.logger.info('Core was not updated')

    def update_defect_document_reference_name(self):
        super(CUUPCoreProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity='UP'):
        super(CUUPCoreProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(CUUPCoreProcess, self).update_defect_if_found()

    def found_defect(self):
        super(CUUPCoreProcess, self).found_defect()

    def get_open_defects(self):
        super(CUUPCoreProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(CUUPCoreProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(CUUPCoreProcess, self).update_defect_after_create()
        update_defect_data = {
            'set': [
                {'customfield_16800': [self.crash_details["crash_version"]]},  # 5G_CU-CP_Ver
                {'customfield_16801': [self.crash_details["crash_version"]]},  # 5G_CU-UP_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def update_defect(self):
        super(CUUPCoreProcess, self).update_defect()

    def set_assignee_on(self):
        super(CUUPCoreProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(CUUPCoreProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(CUUPCoreProcess, self).check_missing_file_list(cuup_core_files_mandatory)


class DUCoreProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(DUCoreProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(DUCoreProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Core DU ...')

    def get_more_data_from_files(self):
        super(DUCoreProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(DUCoreProcess, self).get_data_from_acp()

    def found_customer(self):
        super(DUCoreProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(DUCoreProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(DUCoreProcess, self).found_epic()

    def create_epic(self):
        super(DUCoreProcess, self).create_epic()

    def update_epic_if_found(self):
        super(DUCoreProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(DUCoreProcess, self).found_or_create_epic()

    def update_epic_after_create(self):
        super(DUCoreProcess, self).update_epic_after_create()
        update_epic_data = {
            'set': [
                {'customfield_16200': [self.crash_details["crash_version"]]},  # 5G_DU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.epic, data=update_epic_data)

        if self.epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {self.epic}\n')
        else:
            self.logger.info('Epic was not updated')

    def update_epic(self):
        super(DUCoreProcess, self).update_epic()

    def update_epic_after_core(self):
        super(DUCoreProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(DUCoreProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(DUCoreProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(DUCoreProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(DUCoreProcess, self).update_core_after_defect()

    def create_core(self):
        super(DUCoreProcess, self).create_core()

    def update_core(self):
        super(DUCoreProcess, self).update_core()
        update_core_data = {
            'set': [
                {'customfield_16200': [self.crash_details["crash_version"]]},  # 5G_DU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.core, data=update_core_data)

        if self.core:
            self.logger.info('Core was updated')
            self.logger.info(f'Core key is: {self.core}\n')
        else:
            self.logger.info('Core was not updated')

    def update_defect_document_reference_name(self):
        super(DUCoreProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity='DU'):
        super(DUCoreProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(DUCoreProcess, self).update_defect_if_found()

    def found_defect(self):
        super(DUCoreProcess, self).found_defect()

    def get_open_defects(self):
        super(DUCoreProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(DUCoreProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(DUCoreProcess, self).update_defect_after_create()
        update_defect_data = {
            'set': [
                {'customfield_16200': [self.crash_details["crash_version"]]},  # 5G_DU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def update_defect(self):
        super(DUCoreProcess, self).update_defect()

    def set_assignee_on(self):
        super(DUCoreProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(DUCoreProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(DUCoreProcess, self).check_missing_file_list(du_core_files_mandatory)


class RUCoreProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(RUCoreProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(RUCoreProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Core RU ...')

    def get_more_data_from_files(self):
        super(RUCoreProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(RUCoreProcess, self).get_data_from_acp()

    def found_customer(self):
        super(RUCoreProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(RUCoreProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(RUCoreProcess, self).found_epic()

    def create_epic(self):
        super(RUCoreProcess, self).create_epic()

    def update_epic_if_found(self):
        super(RUCoreProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(RUCoreProcess, self).found_or_create_epic()

    def update_epic_after_create(self):
        super(RUCoreProcess, self).update_epic_after_create()
        update_epic_data = {
            'set': [
                {'customfield_16203': [self.crash_details["crash_version"]]},  # 5G_RU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.epic, data=update_epic_data)

        if self.epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {self.epic}\n')
        else:
            self.logger.info('Epic was not updated')

    def update_epic(self):
        super(RUCoreProcess, self).update_epic()

    def update_epic_after_core(self):
        super(RUCoreProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(RUCoreProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(RUCoreProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(RUCoreProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(RUCoreProcess, self).update_core_after_defect()

    def create_core(self):
        super(RUCoreProcess, self).create_core()

    def update_core(self):
        super(RUCoreProcess, self).update_core()
        update_core_data = {
            'set': [
                {'customfield_16203': [self.crash_details["crash_version"]]},  # 5G_RU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.core, data=update_core_data)

        if self.core:
            self.logger.info('Core was updated')
            self.logger.info(f'Core key is: {self.core}\n')
        else:
            self.logger.info('Core was not updated')

    def update_defect_document_reference_name(self):
        super(RUCoreProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity='RU'):
        super(RUCoreProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(RUCoreProcess, self).update_defect_if_found()

    def found_defect(self):
        super(RUCoreProcess, self).found_defect()

    def get_open_defects(self):
        super(RUCoreProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(RUCoreProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(RUCoreProcess, self).update_defect_after_create()
        update_defect_data = {
            'set': [
                {'customfield_16203': [self.crash_details["crash_version"]]},  # 5G_RU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def update_defect(self):
        super(RUCoreProcess, self).update_defect()

    def set_assignee_on(self):
        super(RUCoreProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(RUCoreProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(RUCoreProcess, self).check_missing_file_list(ru_core_files_mandatory)


class DUPhyAssertProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(DUPhyAssertProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(DUPhyAssertProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Phy Assert ...')

    def get_more_data_from_files(self):
        super(DUPhyAssertProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(DUPhyAssertProcess, self).get_data_from_acp()

    def found_customer(self):
        super(DUPhyAssertProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(DUPhyAssertProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(DUPhyAssertProcess, self).found_epic()

    def create_epic(self):
        super(DUPhyAssertProcess, self).create_epic()

    def update_epic_if_found(self):
        super(DUPhyAssertProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(DUPhyAssertProcess, self).found_or_create_epic()

    def update_epic_after_create(self):
        super(DUPhyAssertProcess, self).update_epic_after_create()
        update_epic_data = {
            'set': [
                {'customfield_16200': [self.crash_details["crash_version"]]},  # 5G_DU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.epic, data=update_epic_data)

        if self.epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {self.epic}\n')
        else:
            self.logger.info('Epic was not updated')

    def update_epic(self):
        super(DUPhyAssertProcess, self).update_epic()

    def update_epic_after_core(self):
        super(DUPhyAssertProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(DUPhyAssertProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(DUPhyAssertProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(DUPhyAssertProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(DUPhyAssertProcess, self).update_core_after_defect()

    def create_core(self):
        super(DUPhyAssertProcess, self).create_core()

    def update_core(self):
        super(DUPhyAssertProcess, self).update_core()
        update_core_data = {
            'set': [
                {'customfield_16200': [self.crash_details["crash_version"]]},  # 5G_DU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.core, data=update_core_data)

        if self.core:
            self.logger.info('Core was updated')
            self.logger.info(f'Core key is: {self.core}\n')
        else:
            self.logger.info('Core was not updated')

    def update_defect_document_reference_name(self):
        super(DUPhyAssertProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity='DU'):
        super(DUPhyAssertProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(DUPhyAssertProcess, self).update_defect_if_found()

    def found_defect(self):
        super(DUPhyAssertProcess, self).found_defect()

    def get_open_defects(self):
        super(DUPhyAssertProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(DUPhyAssertProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(DUPhyAssertProcess, self).update_defect_after_create()
        update_defect_data = {
            'set': [
                {'customfield_16200': [self.crash_details["crash_version"]]},  # 5G_DU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def update_defect(self):
        super(DUPhyAssertProcess, self).update_defect()

    def set_assignee_on(self):
        super(DUPhyAssertProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(DUPhyAssertProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(DUPhyAssertProcess, self).check_missing_file_list(du_core_files_mandatory)


class RUPhyAssertProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(RUPhyAssertProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(RUPhyAssertProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Phy Assert ...')

    def get_more_data_from_files(self):
        super(RUPhyAssertProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(RUPhyAssertProcess, self).get_data_from_acp()

    def found_customer(self):
        super(RUPhyAssertProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(RUPhyAssertProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(RUPhyAssertProcess, self).found_epic()

    def create_epic(self):
        super(RUPhyAssertProcess, self).create_epic()

    def update_epic_if_found(self):
        super(RUPhyAssertProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(RUPhyAssertProcess, self).found_or_create_epic()

    def update_epic_after_create(self):
        super(RUPhyAssertProcess, self).update_epic_after_create()
        update_epic_data = {
            'set': [
                {'customfield_16203': [self.crash_details["crash_version"]]},  # 5G_RU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.epic, data=update_epic_data)

        if self.epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {self.epic}\n')
        else:
            self.logger.info('Epic was not updated')

    def update_epic(self):
        super(RUPhyAssertProcess, self).update_epic()

    def update_epic_after_core(self):
        super(RUPhyAssertProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(RUPhyAssertProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(RUPhyAssertProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(RUPhyAssertProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(RUPhyAssertProcess, self).update_core_after_defect()

    def create_core(self):
        super(RUPhyAssertProcess, self).create_core()

    def update_core(self):
        super(RUPhyAssertProcess, self).update_core()
        update_core_data = {
            'set': [
                {'customfield_16203': [self.crash_details["crash_version"]]},  # 5G_RU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.core, data=update_core_data)

        if self.core:
            self.logger.info('Core was updated')
            self.logger.info(f'Core key is: {self.core}\n')
        else:
            self.logger.info('Core was not updated')

    def update_defect_document_reference_name(self):
        super(RUPhyAssertProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity='RU'):
        super(RUPhyAssertProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(RUPhyAssertProcess, self).update_defect_if_found()

    def found_defect(self):
        super(RUPhyAssertProcess, self).found_defect()

    def get_open_defects(self):
        super(RUPhyAssertProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(RUPhyAssertProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(RUPhyAssertProcess, self).update_defect_after_create()
        update_defect_data = {
            'set': [
                {'customfield_16203': [self.crash_details["crash_version"]]},  # 5G_RU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def update_defect(self):
        super(RUPhyAssertProcess, self).update_defect()

    def set_assignee_on(self):
        super(RUPhyAssertProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(RUPhyAssertProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(RUPhyAssertProcess, self).check_missing_file_list(ru_core_files_mandatory)


class L2CoreProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(L2CoreProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(L2CoreProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Core L2 ...')

    def get_more_data_from_files(self):
        super(L2CoreProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(L2CoreProcess, self).get_data_from_acp()

    def found_customer(self):
        super(L2CoreProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(L2CoreProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(L2CoreProcess, self).found_epic()

    def create_epic(self):
        super(L2CoreProcess, self).create_epic()

    def update_epic_if_found(self):
        super(L2CoreProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(L2CoreProcess, self).found_or_create_epic()

    def update_epic_after_create(self):
        super(L2CoreProcess, self).update_epic_after_create()

    def update_epic(self):
        super(L2CoreProcess, self).update_epic()

    def update_epic_after_core(self):
        super(L2CoreProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(L2CoreProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(L2CoreProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(L2CoreProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(L2CoreProcess, self).update_core_after_defect()

    def create_core(self):
        super(L2CoreProcess, self).create_core()

    def update_core(self):
        super(L2CoreProcess, self).update_core()

    def update_defect_document_reference_name(self):
        super(L2CoreProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity=None):
        super(L2CoreProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(L2CoreProcess, self).update_defect_if_found()

    def found_defect(self):
        super(L2CoreProcess, self).found_defect()

    def get_open_defects(self):
        super(L2CoreProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(L2CoreProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(L2CoreProcess, self).update_defect_after_create()

    def update_defect(self):
        super(L2CoreProcess, self).update_defect()

    def set_assignee_on(self):
        super(L2CoreProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(L2CoreProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(L2CoreProcess, self).check_missing_file_list([])


class L3CoreProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(L3CoreProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(L3CoreProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Core L3 ...')

    def get_more_data_from_files(self):
        super(L3CoreProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(L3CoreProcess, self).get_data_from_acp()

    def found_customer(self):
        super(L3CoreProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(L3CoreProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(L3CoreProcess, self).found_epic()

    def create_epic(self):
        super(L3CoreProcess, self).create_epic()

    def update_epic_if_found(self):
        super(L3CoreProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(L3CoreProcess, self).found_or_create_epic()

    def update_epic_after_create(self):
        super(L3CoreProcess, self).update_epic_after_create()

    def update_epic(self):
        super(L3CoreProcess, self).update_epic()

    def update_epic_after_core(self):
        super(L3CoreProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(L3CoreProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(L3CoreProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(L3CoreProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(L3CoreProcess, self).update_core_after_defect()

    def create_core(self):
        super(L3CoreProcess, self).create_core()

    def update_core(self):
        super(L3CoreProcess, self).update_core()

    def update_defect_document_reference_name(self):
        super(L3CoreProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity=None):
        super(L3CoreProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(L3CoreProcess, self).update_defect_if_found()

    def found_defect(self):
        super(L3CoreProcess, self).found_defect()

    def get_open_defects(self):
        super(L3CoreProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(L3CoreProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(L3CoreProcess, self).update_defect_after_create()

    def update_defect(self):
        super(L3CoreProcess, self).update_defect()

    def set_assignee_on(self):
        super(L3CoreProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(L3CoreProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(L3CoreProcess, self).check_missing_file_list([])


class XPUCoreProcess(CoreCareProcessStrategy, CoreCareSupportData):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(XPUCoreProcess, self).__init__()
        super(CoreCareSupportData, self).__init__()

    def add_to_self(self, obj):
        super(XPUCoreProcess, self).add_to_self(obj)

    def print_start(self):
        self.logger.info('Start Process On Core L3 ...')

    def get_more_data_from_files(self):
        super(XPUCoreProcess, self).get_more_data_from_files()

    def get_data_from_acp(self):
        super(XPUCoreProcess, self).get_data_from_acp()

    def found_customer(self):
        super(XPUCoreProcess, self).found_customer()

    def replace_ip_address_with_setup_name(self):
        super(XPUCoreProcess, self).replace_ip_address_with_setup_name()

    def found_epic(self):
        super(XPUCoreProcess, self).found_epic()

    def create_epic(self):
        super(XPUCoreProcess, self).create_epic()

    def update_epic_if_found(self):
        super(XPUCoreProcess, self).update_epic_if_found()

    def found_or_create_epic(self):
        super(XPUCoreProcess, self).found_or_create_epic()

    def update_epic_after_create(self):
        super(XPUCoreProcess, self).update_epic_after_create()

    def update_epic(self):
        super(XPUCoreProcess, self).update_epic()

    def update_epic_after_core(self):
        super(XPUCoreProcess, self).update_epic_after_core()

    def link_defect_to_epic(self):
        super(XPUCoreProcess, self).link_defect_to_epic()

    def link_defect_to_last_defect(self):
        super(XPUCoreProcess, self).link_defect_to_last_defect()

    def update_epic_after_defect(self):
        super(XPUCoreProcess, self).update_epic_after_defect()

    def update_core_after_defect(self):
        super(XPUCoreProcess, self).update_core_after_defect()

    def create_core(self):
        super(XPUCoreProcess, self).create_core()

    def update_core(self):
        super(XPUCoreProcess, self).update_core()
        # update_core_data = {
        #     'set': [
        #         {'customfield_19404': [self.crash_details["crash_version"]]},  # 5G_XPU_Ver
        #     ],
        #     'add': []
        # }
        #
        # self.jira_client.update_issue(issue_id=self.core, data=update_core_data)
        #
        # if self.core:
        #     self.logger.info('Core was updated')
        #     self.logger.info(f'Core key is: {self.core}\n')
        # else:
        #     self.logger.info('Core was not updated')

    def update_defect_document_reference_name(self):
        super(XPUCoreProcess, self).update_defect_document_reference_name()

    def create_defect(self, entity=None):
        super(XPUCoreProcess, self).create_defect(entity)

    def update_defect_if_found(self):
        super(XPUCoreProcess, self).update_defect_if_found()

    def found_defect(self):
        super(XPUCoreProcess, self).found_defect()

    def get_open_defects(self):
        super(XPUCoreProcess, self).get_open_defects()

    def found_or_create_defect(self):
        super(XPUCoreProcess, self).found_or_create_defect()

    def update_defect_after_create(self):
        super(XPUCoreProcess, self).update_defect_after_create()
        update_defect_data = {
            'set': [
                {'customfield_19404': [self.crash_details["crash_version"]]},  # 5G_XPU_Ver
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=self.defect, data=update_defect_data)

        if self.defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {self.defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def update_defect(self):
        super(XPUCoreProcess, self).update_defect()

    def set_assignee_on(self):
        super(XPUCoreProcess, self).set_assignee_on()

    def set_reporter_on(self):
        super(XPUCoreProcess, self).set_reporter_on()

    def check_missing_file_list(self, core_files_mandatory=None):
        return super(XPUCoreProcess, self).check_missing_file_list(xpu_core_files_mandatory)
