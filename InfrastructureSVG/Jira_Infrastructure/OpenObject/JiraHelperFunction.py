import os
import re
import time
import logging
import collections
from datetime import datetime
from typing import Union
import itertools
import jira

from InfrastructureSVG.Jira_Infrastructure.OpenObject.JiraDataClass_Infrastructure import JiraParameters
from InfrastructureSVG.Jira_Infrastructure.OpenObject.JiraFilters_Infrastructure import JiraFilters
from InfrastructureSVG.Jira_Infrastructure.ConstantData import VERSIONS_PATH, DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX
from InfrastructureSVG.DateAndTimeFormats.CalculateTime_Infrastructure import CalculateTime


class AutomationHelper(JiraFilters):
    def __init__(self, jira_client=None):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = jira_client

        super(AutomationHelper, self).__init__(jira_client=jira_client)

    @staticmethod
    def build_summary_for_defect(jira_parameters_obj: Union[JiraParameters], test_name: str) -> str:
        if jira_parameters_obj.actual and jira_parameters_obj.expected:
            return f'5G: [{jira_parameters_obj.site.split(" ")[1]}], ' \
                   f'Test: [{test_name}], ' \
                   f'Actual: [{jira_parameters_obj.actual}], ' \
                   f'Expected: [{jira_parameters_obj.expected}]'.replace("_", " ")
        else:
            return f'5G: [{jira_parameters_obj.site.split(" ")[1]}], Test: [{test_name}], Please check the Test Executions for the results'.replace("_", " ")

    def update_summary_for_defect(self, defect: str, jira_parameters_obj: Union[JiraParameters]) -> str:
        self.jira_client.get_issue(issue_id=defect)
        defect_object = self.jira_client.issues[defect].issue

        summary = defect_object.fields.summary.replace("_", " ")
        summary_dict = {
            summary_part.split(": ")[0]: summary_part.split(": ")[1].replace("[", "").replace("]", "").split(", ")
            for summary_part in summary.replace("]", "]]").split("], ")
        }

        if summary_dict.get('5G') and all(
                jira_parameters_obj.site.split(" ")[1].upper() not in value.upper()
                for value in summary_dict.get('5G')
        ):
            summary_dict['5G'].append(jira_parameters_obj.site.split(" ")[1].upper())

        if (
                jira_parameters_obj.actual
                and jira_parameters_obj.expected
                and summary_dict.get('Actual')
                and summary_dict.get('Expected') == ['N/A']
                and summary_dict.get('Expected')
                and summary_dict.get('Actual') == ['N/A']
        ):
            summary_dict['Actual'] = [jira_parameters_obj.actual]
            summary_dict['Expected'] = [jira_parameters_obj.expected]

        summary = ''
        for k, v in summary_dict.items():
            vv = f'{v}'.replace("'", "")
            summary += f'{k}: {vv}, '
        return summary[:-2]

    def found_defect(self, labels: list) -> Union[str, None]:
        defect_objs = self.automation_filters.get_open_defects_by_filter(labels=labels)
        if defect_objs.iterable:
            defect = defect_objs[0].key
            self.logger.info('Defect was found')
            self.logger.info(f'Defect key is: {defect}\n')
        else:
            defect = None
            self.logger.info('Open Defect was not found, need to check close defect versions')
        return defect


class CoreCareHelper(JiraFilters):
    def __init__(self, jira_client=None):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = jira_client

        super(CoreCareHelper, self).__init__(jira_client=jira_client)

    def build_summary_for_defect(self, jira_parameters_obj: Union[JiraParameters], epic: str) -> str:
        return f'CoreCare-5G: [{jira_parameters_obj.site.split(" ")[1]}], ' \
               f'Core Occurrence Count: [Total; {self.corecare_filters.get_total_core_occurrence_count_by_filter(epic=epic)} times, ' \
               f'Last SR Version; {self.corecare_filters.get_last_version_core_occurrence_count_by_filter(epic=epic, last_version=jira_parameters_obj.entity_version)} times], ' \
               f'CoreType: [{jira_parameters_obj.product_at_fault.replace("v", "").upper()}], ' \
               f'SR: [{jira_parameters_obj.sr_version}], ' \
               f'HashBT: [{jira_parameters_obj.hash_bt}]'

    def update_summary_for_defect(self, defect: str, jira_parameters_obj: Union[JiraParameters], epic) -> str:
        self.jira_client.get_issue(issue_id=defect)
        defect_object = self.jira_client.issues[defect].issue

        summary = defect_object.fields.summary
        summary_dict = {
            summary_part.split(": ")[0]: summary_part.split(": ")[1].replace("[", "").replace("]", "").split(", ")
            for summary_part in summary.replace("]", "]]").split("], ")
        }

        if summary_dict.get('CoreCare-5G') and all(
                jira_parameters_obj.site.split(" ")[1].upper() not in value.upper()
                for value in summary_dict.get('CoreCare-5G')
        ):
            summary_dict['CoreCare-5G'].append(jira_parameters_obj.site.split(" ")[1].upper())

        # if summary_dict.get('Core Occurrence Count') and hasattr(self, 'get_defect_last_version'):
        if summary_dict.get('Core Occurrence Count'):
            summary_dict['Core Occurrence Count'][0] = f'Total; {self.corecare_filters.get_total_core_occurrence_count_by_filter(epic=epic)} times'
            last_sr_version = self.corecare_filters.get_last_version_core_occurrence_count_by_filter(
                epic=epic,
                last_version=JiraHelper(jira_client=self.jira_client).get_defect_last_version(defect=defect_object.key, current_ver=jira_parameters_obj.entity_version)
            )
            summary_dict['Core Occurrence Count'][1] = f'Last SR Version; {last_sr_version} times'

        if summary_dict.get('CoreType') and all(
                jira_parameters_obj.product_at_fault.replace("v", "").upper()
                not in value.upper()
                for value in summary_dict.get('CoreType')
        ):
            summary_dict['CoreType'].append(jira_parameters_obj.product_at_fault.replace("v", "").upper())

        if summary_dict.get('SR') and all(
                f'{jira_parameters_obj.sr_version.replace("SR", "")}'
                not in value.upper()
                for value in summary_dict.get('SR')
        ):
            summary_dict['SR'].append(jira_parameters_obj.sr_version.replace("SR", ""))

        if summary_dict.get('HashBT') and all(
                f'{jira_parameters_obj.hash_bt}' not in value.upper()
                for value in summary_dict.get('HashBT')
        ):
            summary_dict['HashBT'].append(f'{jira_parameters_obj.hash_bt}')

        summary = ''
        for k, v in summary_dict.items():
            vv = f'{v}'.replace("'", "")
            summary += f'{k}: {vv}, '
        return summary[:-2]

    @staticmethod
    def get_entity_version_path(entity_type_name: str) -> Union[str, None]:
        if entity_type_name in {'vCU-CP', 'vCU-UP'}:
            return VERSIONS_PATH["cu_path"]
        elif entity_type_name in {'vDU'}:
            return VERSIONS_PATH["du_path"]
        elif entity_type_name in {'RU'}:
            return VERSIONS_PATH["ru_path"]
        else:
            return None

    def get_open_defect(self, epic: str) -> Union[str, None]:
        defect_objs = self.corecare_filters.get_open_defects_by_filter(epic=epic)
        if defect_objs.iterable:
            defect = defect_objs[0].key
        else:
            defect = None
            self.logger.info('Open Defect was not found')

        return defect

    def get_open_defects(self, epic: str) -> list:
        defect_objs = self.corecare_filters.get_open_defects_by_filter(epic=epic)
        if defect_objs.iterable:
            defects_list = [defect_obj.key for defect_obj in defect_objs.iterable]
        else:
            defects_list = []
            self.logger.info('Open Defect was not found')

        return defects_list

    def found_epic(self, type_crash_name: str, back_trace_hash: str) -> Union[str, None]:
        epic_obj = self.corecare_filters.found_epic_bt_by_filter(type_crash_name=type_crash_name, back_trace_hash=back_trace_hash)
        if epic_obj.iterable:
            epic = epic_obj.iterable[0].key
            self.logger.info('Epic was found')
            self.logger.info(f'Epic key is: {epic}\n')
        else:
            epic = None
            self.logger.info('Epic was not found')
        return epic

    def found_defect(self, epic: str) -> Union[str, None]:
        defect_objs = self.corecare_filters.get_open_defects_by_filter(epic=epic)
        if defect_objs.iterable:
            defect = defect_objs[0].key
            self.logger.info('Defect was found')
            self.logger.info(f'Defect key is: {defect}\n')
        else:
            defect = None
            self.logger.info('Open Defect was not found, need to check close defect versions')
        return defect

    @staticmethod
    def find_min_max(cores: list) -> tuple[str, str]:
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

    def get_core_system_uptime_for_defect(self, epic: str, core: str, defect: str = None, last_version: str = None):
        defect_obj = self.jira_client.issues[defect].issue
        core_obj = self.jira_client.issues[core].issue

        max_all_version = 'N/A'
        min_all_version = 'N/A'

        core_system_uptime = ['N/A']
        if not defect:
            max_last_version = min_last_version = core_obj.fields.customfield_14801
        else:
            if hasattr(self, 'get_core_system_uptime'):
                core_system_uptime = [self.get_core_system_uptime(system_runtime=last_version)]

            cores_last_version = self.corecare_filters.get_core_system_uptime_min_by_filter(epic=epic, last_version=last_version)
            max_last_version, min_last_version = self.find_min_max(cores_last_version)

            if hasattr(self, 'jira_client'):
                cores_all_version = self.corecare_filters.get_cores_for_versions_by_filter(epic=epic, versions=defect_obj.fields.customfield_13707)
                max_all_version, min_all_version = self.find_min_max(cores_all_version)

                if defect_obj.fields.customfield_14803:
                    core_system_uptime.extend([i for i in defect_obj.fields.customfield_14803 if 'min_' not in i and 'max_' not in i])

        core_system_uptime.extend(
            [
                f'min_last_version:{min_last_version} '
                f'max_last_version:{max_last_version} '
                f'min_all_version:{min_all_version} '
                f'max_all_version:{max_all_version} '
            ]
        )

        return core_system_uptime


class JiraHelper:
    def __init__(self, jira_client=None):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = jira_client
        self.automation_helper = AutomationHelper(jira_client=jira_client)
        self.corecare_helper = CoreCareHelper(jira_client=jira_client)

    @staticmethod
    def order_by_time(_, sr_ver: str) -> dict:
        # reg_pattern = f'({sr_ver})(.*)(?=.pdf)'
        reg_pattern = f'({sr_ver})(.*)(?=)'
        _ = collections.OrderedDict(dict(sorted(_.items(), key=lambda item: item[1], reverse=True)))
        return {index: {'file_path': f'{k}', 'version': re.search(reg_pattern, k, re.I).group(), 'Date created': v} for index, (k, v) in enumerate(_.items())}

    @staticmethod
    def automation_vran_check_if_new_bigger_from_old(new_version: str, old_version: str) -> bool:
        # check for SR
        if new_version.split('-', 1)[0] > old_version.split('-', 1)[0]:
            return True
        elif new_version.split('-', 1)[0] < old_version.split('-', 1)[0]:
            return False

        # check for each entity [CU, DU, RU]
        for index, old_ver in enumerate(old_version.split('-', 1)[1].split('_'), start=0):
            # check for CU and DU
            if index != len(old_version.split('-', 1)[1].split('_')) - 1 and float(new_version.split('-', 1)[1].split('_')[index].replace("-", "")) != float(
                    old_ver.replace("-", "")):
                return float(new_version.split('-', 1)[1].split('_')[index].replace("-", "")) > float(old_ver.replace("-", ""))

            # check for RU
            if index == len(old_version.split('-', 1)[1].split('_')) - 1:
                ru_version = None
                if 'AV27-R' in new_version:
                    ru_version = 'AV27-R'
                elif 'A5G57' in new_version:
                    ru_version = f"{new_version.split('-', 1)[1].split('_', index)[index].split('-', 1)[0]}-"

                try:
                    if ru_version:
                        return float(new_version.split('-', 1)[1].split('_', index)[index].replace(ru_version, "").replace(".", "").replace("_", "").replace("-", "")) > \
                               float(old_ver.replace(ru_version, "").replace(".", ""))
                    else:
                        return False
                except Exception:
                    return False

    def check_version_by_pdf(self, entity_type_name: str, version: str) -> tuple[dict, dict]:
        current_version_dict = {}
        files_dict = {}

        path = self.corecare_helper.get_entity_version_path(entity_type_name)
        if not path:
            return current_version_dict, files_dict

        for dir_path, dir_names, file_names in os.walk(path):
            for dir_name in dir_names:
                if dir_name and f'_{version.split("-", 1)[0]}' in dir_name:
                    date_created_file = os.path.getctime(f'{dir_path}\\{dir_name}')
                    date_created_file = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date_created_file))
                    date_created_file = datetime.strptime(date_created_file, '%Y-%m-%d %H:%M:%S')

                    files_dict[f'{dir_path}\\{dir_name}'] = date_created_file

                    # if f'{version.replace("-", ".")}.pdf' in file_:
                    if f'{version}' in dir_name:
                        current_version_dict[f'{dir_path}\\{dir_name}'] = date_created_file
            break

        sr_ver = version.split("-", 1)[0]
        files_dict = self.order_by_time(files_dict, sr_ver=sr_ver)
        current_version_dict = self.order_by_time(current_version_dict, sr_ver=sr_ver)

        return current_version_dict, files_dict

    @staticmethod
    def check_if_defect_open(defect_status: str) -> bool:
        return any(True for stat in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX if f'"{defect_status}"' == stat)

    @staticmethod
    def get_system_runtime_minutes(system_runtime: Union[str, dict], threshold: int = 0) -> int:
        if type(system_runtime) is str:
            t = system_runtime.split(':')
            system_runtime_min = CalculateTime(h=t[0], m=t[1], s=t[2]).calculate_minutes()
        else:
            system_runtime_min = CalculateTime(h=system_runtime['Hours'], m=system_runtime['Minutes'], s=system_runtime['Seconds']).calculate_minutes()

        return max(system_runtime_min, threshold)

    def get_core_system_uptime(self, system_runtime: Union[dict, int]) -> str:
        if type(system_runtime) is dict:
            system_runtime_minutes = self.get_system_runtime_minutes(system_runtime=system_runtime)
        elif type(system_runtime) is int:
            system_runtime_minutes = system_runtime
        else:
            system_runtime_minutes = -1

        if system_runtime_minutes:
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
                return 'N/A'

    def get_avg_core_system_uptime_min(self, epic: str, last_version: str) -> int:
        cores = self.corecare_helper.corecare_filters.get_core_system_uptime_min_by_filter(epic=epic, last_version=last_version)
        total_core_system_uptime_min = sum(core.fields.customfield_14801 for core in cores if core.fields.customfield_14801)

        if len(cores) > 1:
            return total_core_system_uptime_min // len(cores)
        else:
            return total_core_system_uptime_min

    @staticmethod
    def get_reproducibility_frequency(occurrence_count: int) -> str:
        if occurrence_count <= 1:
            return 'Once'
        elif 1 < occurrence_count < 5:
            return '2-5 times'
        elif occurrence_count > 5:
            return '>5 times'
        else:
            return 'None'

    @staticmethod
    def get_bigger_version_by_analyze_string(version_list: list, current_ver: str) -> str:
        if current_ver == 'unknown_version':
            return ''
        else:
            max_ver = current_ver

        for ver in version_list:
            if ver == 'unknown_version':
                continue

            if float(ver.split('-')[0]) > float(max_ver.split('-')[0]):
                max_ver = ver
            elif float(ver.split('-')[0]) < float(max_ver.split('-')[0]):
                max_ver = max_ver
            elif float(ver.split('-')[1]) > float(max_ver.split('-')[1]):
                max_ver = ver
            elif float(ver.split('-')[1]) < float(max_ver.split('-')[1]):
                max_ver = max_ver
            elif (float(ver.split('-')[2].split('.')[0]) > float(max_ver.split('-')[2].split('.')[0])) or \
                    (float(ver.split('-')[2].split('.')[0]) == float(max_ver.split('-')[2].split('.')[0]) and
                     float(ver.split('-')[2].split('.')[1]) > float(max_ver.split('-')[2].split('.')[1])):
                max_ver = ver
            elif float(ver.split('-')[2]) < float(max_ver.split('-')[2]):
                max_ver = max_ver
        return max_ver

    def check_if_need_to_create_new_defect(self, customfield, defect_objects: Union[str, jira.client.ResultList], entity_type_name: str, current_ver: str) -> bool:
        if type(defect_objects) is str:
            self.jira_client.get_issue(issue_id=defect_objects)
            defect_objects = self.jira_client.issues[defect_objects].issue
        if customfield == 'customfield_13707' and defect_objects.iterable:
            defect_version_list = [defect_object.fields.customfield_13707 for defect_object in defect_objects.iterable if defect_object.fields.customfield_13707]
            defect_version_list = list(itertools.chain(*defect_version_list))
        elif customfield == 'customfield_18401' and defect_objects:
            defect_version_list = defect_objects.fields.customfield_18401
        else:
            self.logger.error('There is no relevant customfield')
            return False

        if defect_objects:
            current_version_dict, files_dict = self.check_version_by_pdf(entity_type_name=entity_type_name, version=current_ver)
            pdf_versions = [v['version'] for k, v in files_dict.items()]
            if not pdf_versions or not current_version_dict:
                self.logger.info('There is no pdf versions, need to check who is bigger version bt "get_bigger_version_from_list"')
                if current_ver in defect_version_list:
                    self.logger.info('max old defects versions >= current versions')
                    return False

                max_ver = self.get_bigger_version_by_analyze_string(version_list=defect_version_list, current_ver=current_ver)
                if max_ver == current_ver and current_ver not in defect_version_list:
                    self.logger.info('current versions > max old defects versions')
                    return True
                else:
                    self.logger.info('max old defects versions >= current versions')
                    return False

            defect_version_list_order = [i for i in pdf_versions if i in defect_version_list]
            if not defect_version_list_order:
                self.logger.info('There is no old defect versions')
                return True

            defect_version_date_time = [v['Date created'] for k, v in files_dict.items() if v['version'] == defect_version_list_order[0]][0]
            if current_version_dict and defect_version_date_time and current_version_dict[0]['Date created'] > defect_version_date_time:
                self.logger.info('The new defect version is bigger than old defects versions')
                return True
            else:
                self.logger.info('The new defect version is less than or equal to old defects versions')
                return False
        else:
            self.logger.info('There is no defects')
            return True

    def check_if_need_to_create_new_defect_for_corecare(self, epic: str, entity_type_name: str, current_ver: str) -> bool:
        defect_objects = self.corecare_helper.corecare_filters.get_defects_by_filter(epic=epic)
        if not defect_objects or self.check_if_need_to_create_new_defect(customfield='customfield_13707', defect_objects=defect_objects, entity_type_name=entity_type_name,
                                                                         current_ver=current_ver):
            self.logger.info('need to create a new defect')
            return True
        else:
            self.logger.info('No need to create a new defect')
            return False

    def check_if_need_to_create_new_defect_for_automation(self, labels: list, entity_type_name: str, current_ver: str) -> bool:
        defect_objects = self.automation_helper.automation_filters.get_defects_by_filter(labels=labels)
        if not defect_objects or self.check_if_need_to_create_new_defect(customfield='customfield_13707', defect_objects=defect_objects, entity_type_name=entity_type_name,
                                                                         current_ver=current_ver):
            self.logger.info('need to create a new defect')
            return True
        else:
            self.logger.info('No need to create a new defect')
            return False

    def get_defect_last_version(self, defect: str, current_ver: str) -> str:
        self.jira_client.get_issue(issue_id=defect)
        defect_object = self.jira_client.issues[defect].issue
        enodeb_sw_versions = defect_object.fields.customfield_13707.copy()  # g/eNodeB SW version

        return self.get_bigger_version_by_analyze_string(version_list=enodeb_sw_versions, current_ver=current_ver)
