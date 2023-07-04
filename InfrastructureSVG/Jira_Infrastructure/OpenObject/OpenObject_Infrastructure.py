import logging
from copy import deepcopy
from typing import Union
import jira

from InfrastructureSVG.Files_Infrastructure.Files.FilesActions_Infrastructure import FilesActions
from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import GeneralFolderActionClass
from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import get_full_field_list
from InfrastructureSVG.Jira_Infrastructure.OpenObject.JiraDataClass_Infrastructure import JiraParameters
from InfrastructureSVG.Jira_Infrastructure.OpenObject.JiraHelperFunction import JiraHelper


class CreateObjectOnJira(JiraHelper):
    def __init__(self, jira_client):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(CreateObjectOnJira, self).__init__(jira_client=jira_client)

        self.jira_client = jira_client
        self.username = self.jira_client._username

        self.defect_is_duplicate = False
        self.defect_duplicate_list = []

    def get_open_defects_include_links(self, defect_str: str, defects_dict: dict) -> dict:
        self.jira_client.get_issue(defect_str)
        defects_dict['all_defects_dict'].update({defect_str: self.jira_client.issues[defect_str].issue})

        if self.check_if_defect_open(defect_status=self.jira_client.issues[defect_str].issue.fields.status.name):
            defects_dict['defects_open'].append(defect_str)

        self.jira_client.get_issue(defect_str)
        # defects_linked = self.jira_client.search_by_filter(f'project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues({defect}) AND status = Duplicate')
        defects_linked = self.jira_client.search_by_filter(
            # f'project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues({defect_str}) AND reporter = CoreCare-5G',
            f'project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues({defect_str})',
            fields=get_full_field_list()
        )

        for defect_linked in defects_linked:
            if defect_linked.key not in defects_dict['all_defects_dict']:
                self.get_open_defects_include_links(defect_str=defect_linked.key, defects_dict=defects_dict)
        return defects_dict

    def get_open_defects_include_links_old(self, defect_str: Union[str, jira.resources.Issue], defects_dict: dict) -> dict:
        """ defects_dict = {'all_defects_dict': {}, 'defects_open': []} """

        # if type(defect_str) == jira.resources.Issue:
        if type(defect_str) == str:
            self.jira_client.get_issue(defect_str)
            defect_obj = self.jira_client.issues[defect_str].issue
        else:
            defect_obj = deepcopy(defect_str)
            defect_str = defect_obj.key

        defects_dict['all_defects_dict'].update({defect_str: defect_obj})

        if self.check_if_defect_open(defect_status=defect_obj.fields.status.name):
            defects_dict['defects_open'].append(defect_str)

        defects_linked = self.jira_client.search_by_filter(f'project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues({defect_str})')

        for defect_linked in defects_linked:
            if defect_linked.key not in list(defects_dict['all_defects_dict'].keys()):
                self.get_open_defects_include_links(defect_str=defect_linked.key, defects_dict=defects_dict)
        return defects_dict

    def create_link_between_two_object(self, link_from_issue: str, link_to_issue: str, project: str = 'created') -> None:
        self.jira_client.create_issue_link(project=project, link_from_issue=link_from_issue, link_to_issue=link_to_issue)

    def create_link_between_core_and_epic(self, epic: str, core: str) -> None:
        self.jira_client.issues[f'{core}'].issue.update(fields={"customfield_10000": f'{epic}'})  # Epic Link

    def create_link_between_defect_and_epic(self, defect: str, epic: str) -> None:
        self.create_link_between_two_object(link_from_issue=defect, link_to_issue=epic)

    @staticmethod
    def build_folder_in_prt_and_moving_files(src_path: str, dst_path: str) -> None:
        GeneralFolderActionClass().check_path_exist_and_create(folder_path=dst_path)
        FilesActions().move_files_per_platform(full_path_file=src_path, dst_path=dst_path)

    def update_defect_document_reference_name(self, defect: str, dst_path: str = '\\\\192.168.127.231\\Defects') -> None:
        update_defect_data = {
            'set': [
                {'customfield_10713': [f'{dst_path}\\{defect}']},  # Document reference/name
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=defect, data=update_defect_data)

        if defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def update_epic_core_occurrence_count(self, epic: str) -> None:
        core_occurrence_count = self.corecare_helper.corecare_filters.get_total_core_occurrence_count_by_filter(epic=epic)
        update_epic_data = {
            'set': [
                {'customfield_15000': [core_occurrence_count]},  # core occurrence count
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=epic, data=update_epic_data)

        if epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {epic}\n')
        else:
            self.logger.info('Epic was not updated')

    def update_defect(self, defect: str, defect_obj: Union[JiraParameters], summary: str = None, epic: str = None, core: str = None) -> None:
        defect_data = {
            'set': [],
            'add': []
        }

        if epic and core:
            defect_obj.core_occurrence_count = self.corecare_helper.corecare_filters.get_total_core_occurrence_count_by_filter(epic=epic)
            defect_data['add'].extend([
                {'customfield_14803': [self.corecare_helper.get_core_system_uptime_for_defect(epic=epic, core=core, defect=defect,
                                                                                              last_version=self.get_defect_last_version(defect=defect,
                                                                                                                                        current_ver=defect_obj.entity_version))]},
                # Core SystemUpTime
            ])

        # Set
        if (
                defect_obj.entity_version
                and (not defect_obj or self.check_if_need_to_create_new_defect(customfield='customfield_18401', defect_objects=defect, entity_type_name=defect_obj.product_at_fault,
                                                                               current_ver=defect_obj.entity_version))
        ):
            defect_data['set'].extend([
                {'customfield_18401': [f'{defect_obj.entity_version}']},  # Last Occurred GNB Versions
            ])

        if summary:
            defect_data['set'].extend([
                {'summary': [f'{summary}'[-254:]]},  # summary
            ])

        if (
                epic and defect_obj.entity_version
                and (not defect_obj or self.check_if_need_to_create_new_defect(customfield='customfield_18401', defect_objects=defect,
                                                                               entity_type_name=defect_obj.product_at_fault,
                                                                               current_ver=defect_obj.entity_version))
        ):
            defect_data['set'].extend([
                {'customfield_14801': [self.get_avg_core_system_uptime_min(epic=epic, last_version=defect_obj.entity_version)]},  # Core SystemUpTime (min)
            ])

        if defect_obj.core_occurrence_count:
            defect_data['set'].extend([
                {'customfield_10201': [f'{self.get_reproducibility_frequency(defect_obj.core_occurrence_count)}']},  # Reproducibility/Frequency
                {'customfield_15000': [defect_obj.core_occurrence_count]},  # core occurrence count
            ])

        # Add
        if defect_obj.entity_version:
            defect_data['add'].extend([
                {'fixVersions': [f'{defect_obj.sr_version}']},  # SR Versions
            ])
            if defect_obj.ems_type != 'EMS':
                defect_data['add'].extend([
                    {'customfield_13707': [f'{defect_obj.entity_version}']},  # g/eNodeB SW version
                ])

        if defect_obj.labels:
            defect_data['add'].extend([
                {'labels': defect_obj.labels},  # labels
            ])

        if defect_obj.test_environments:
            defect_data['add'].extend([
                {'customfield_11003': defect_obj.test_environments},  # test environments
            ])

        self.jira_client.update_issue(issue_id=defect, data=defect_data)

        if defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def create_defect(self, defect_obj: Union[JiraParameters], summary: str = None, description: str = None, epic: str = None, core: str = None) -> Union[str, None]:
        # sourcery skip: low-code-quality
        if not summary:
            summary = defect_obj.summary
        if not description:
            description = defect_obj.description

        defect_data = [
            # Required fields
            {'reporter': [f'{self.username}']},  # reporter
            {'assignee': [f'{defect_obj.assignee}']},  # assignee
            {'summary': [f'{summary}'[-254:]]},  # summary
            {'customfield_10736': [{'value': f'{defect_obj.site.split(" ")[0]}', 'child': f'{defect_obj.site.split(" ")[1]}'}]},  # Discovery Site / Customer
            {'customfield_10200': [f'{defect_obj.sr_version}']},  # Reported In Release (eNB)
            {'customfield_10202': [f'{defect_obj.product_at_fault}']},  # product at fault
            {'customfield_10800': defect_obj.bs_hardware_type},  # BS Hardware Type
            {'customfield_10406': [f'{defect_obj.severity}']},  # Severity
        ]

        if epic:
            defect_obj.core_occurrence_count = self.corecare_helper.corecare_filters.get_total_core_occurrence_count_by_filter(epic=epic)
            if core and defect_obj.entity_version:
                defect_data.extend([
                    {'customfield_14803': [self.corecare_helper.get_core_system_uptime_for_defect(epic=epic, core=core, last_version=defect_obj.entity_version)]},
                    # Core SystemUpTime
                ])

        if defect_obj.core_occurrence_count:
            defect_data.extend([
                {'customfield_10201': [f'{self.get_reproducibility_frequency(defect_obj.core_occurrence_count)}']},  # Reproducibility/Frequency
            ])
        else:
            defect_data.extend([
                {'customfield_10201': [f'{defect_obj.reproducibility_frequency}']},  # Reproducibility/Frequency
            ])

        # Other fields
        if description:
            defect_data.extend([
                {'description': [f'{description}']},  # description
            ])

        if defect_obj.entity_version:
            defect_data.extend([
                {'versions': [f'{defect_obj.sr_version}']},  # Affects Version/s
                {'fixVersions': [f'{defect_obj.sr_version}']},  # SR Versions
                {'customfield_10715': [f'{defect_obj.sr_version}']},  # Target Release
            ])
            if defect_obj.product_at_fault != 'EMS':
                defect_data.extend([
                    # {'customfield_10726': [f'{defect_obj.entity_version}']},  # eNB /CD/DU - SW
                    {'customfield_13707': [f'{defect_obj.entity_version}']},  # g/eNodeB SW version
                    # {'customfield_10725': [defect_obj.entity_version]},  # Last Occurred BS Software Version
                    {'customfield_18401': [f'{defect_obj.entity_version}']},  # Last Occurred GNB Versions
                ])

        if epic and defect_obj.entity_version:
            defect_data.extend([
                {'customfield_14801': [self.get_avg_core_system_uptime_min(epic=epic, last_version=defect_obj.entity_version)]},  # Core SystemUpTime (min)
            ])

        if defect_obj.labels:
            defect_data.extend([
                {'labels': defect_obj.labels},  # labels
            ])

        if defect_obj.core_occurrence_count:
            defect_data.extend([
                {'customfield_15000': [defect_obj.core_occurrence_count]},  # core occurrence count
            ])

        if defect_obj.customer_name:
            defect_data.extend([
                {'customfield_13300': defect_obj.customer_name},  # Customer name
            ])

        if defect_obj.ems_type:
            defect_data.extend([
                {'customfield_10731': [f'{defect_obj.ems_type}']},  # EMS Type
            ])

        if defect_obj.ems_software_version:
            defect_data.extend([
                {'customfield_10737': [f'{defect_obj.ems_software_version}']},  # EMS Software Version
            ])

        if defect_obj.impact:
            defect_data.extend([
                {'customfield_11449': [f'{defect_obj.impact}']},  # Defect Impact
            ])

        if defect_obj.frequency_band:
            defect_data.extend([
                # {'customfield_10704': [f'{defect_obj.frequency_band}']},  # Frequency Band
                {'customfield_10511': [f'{defect_obj.frequency_band}']},  # Band
            ])

        if defect_obj.bandwidth:
            defect_data.extend([
                # {'customfield_10734': [f'{defect_obj.bandwidth}']},  # Bandwidth
                {'customfield_10513': [f'{defect_obj.bandwidth}']},  # Bandwidth
            ])

        if defect_obj.notes:
            defect_data.extend([
                {'customfield_10975': [f'{defect_obj.notes}']},  # Notes
            ])

        if defect_obj.linux_kernel:
            defect_data.extend([
                {'customfield_12682': [f'{defect_obj.linux_kernel}']},  # Linux Kernel
            ])

        if defect_obj.cucp_version:
            defect_data.extend([
                {'customfield_16800': [f'{defect_obj.cucp_version}']},  # 5G_CUCP_Ver
            ])

        if defect_obj.cuup_version:
            defect_data.extend([
                {'customfield_16801': [f'{defect_obj.cuup_version}']},  # 5G_CUUP_Ver
            ])

        if defect_obj.du_version:
            defect_data.extend([
                {'customfield_16200': [f'{defect_obj.du_version}']},  # 5G_DU_Ver
            ])

        if defect_obj.ru_version:
            defect_data.extend([
                {'customfield_16203': [f'{defect_obj.ru_version}']},  # 5G_RU_Ver
            ])

        if defect_obj.test_environments:
            defect_data.extend([
                {'customfield_11003': defect_obj.test_environments},  # test environments
            ])
        if defect_obj.defect_module_sub_feature:
            defect_data.extend([
                {'customfield_10712': [defect_obj.defect_module_sub_feature]},  # Defect Module / Sub-feature
            ])

        if defect_obj.show_stopper:
            defect_data.extend([
                {'customfield_11200': [f'{defect_obj.show_stopper}']},  # Showstopper
            ])

        defect = self.jira_client.create_issue(project='DEF', issue_type='Defect', data=defect_data)

        if defect:
            self.logger.info('Defect was created')
            self.logger.info(f'Defect key is: {defect}\n')
        else:
            self.logger.error('Defect was not created')

        return defect

    def update_epic(self, epic: str, epic_obj: Union[JiraParameters]) -> None:
        epic_data = {
            'set': [],
            'add': []
        }

        # Add
        if epic_obj.entity_version:
            epic_data['add'].extend([
                {'fixVersions': [f'{epic_obj.sr_version}']},  # SR Versions
                {'customfield_13707': [f'{epic_obj.entity_version}']},  # g/eNodeB SW version
                # {'customfield_18401': [f'{epic_obj.entity_version}']},  # Last Occurred GNB Versions  # waiting for replace field to list (instead of string)
            ])

        if epic_obj.test_environments:
            epic_data['add'].extend([
                {'customfield_11003': epic_obj.test_environments},  # test environments
            ])

        if epic_obj.system_runtime:
            epic_data['add'].extend([
                {'customfield_14803': [f'{self.get_core_system_uptime(epic_obj.system_runtime)}']},  # CoreSysUpTime
            ])

        self.jira_client.update_issue(issue_id=epic, data=epic_data)

        if epic:
            self.logger.info('Epic was updated')
            self.logger.info(f'Epic key is: {epic}\n')
        else:
            self.logger.info('Epic was not updated')

    def create_epic(self, epic_obj: Union[JiraParameters], summary: str = None, description: str = None) -> Union[str, None]:
        if not summary:
            summary = epic_obj.summary
        if not description:
            description = epic_obj.description

        epic_data = [
            # Required fields
            {'reporter': [f'{self.username}']},  # reporter
            # {'assignee': [f'{epic_obj.assignee}']},  # assignee
            {'summary': [f'{summary}'[-254:]]},  # summary
            {'customfield_10002': [f'{epic_obj.epic_name[-254:]}']},  # Epic Name
            {'customfield_10202': [f'{epic_obj.product_at_fault}']},  # product at fault
        ]

        # Other fields
        if description:
            epic_data.extend([
                {'description': [f'{description}']},  # description
            ])

        if epic_obj.entity_version:
            epic_data.extend([
                {'fixVersions': [f'{epic_obj.sr_version}']},  # SR Versions
                {'customfield_13707': [f'{epic_obj.entity_version}']},  # g/eNodeB SW version
                {'customfield_18401': [f'{epic_obj.entity_version}']},  # Last Occurred GNB Versions
            ])

        if epic_obj.labels:
            epic_data.extend([
                {'labels': epic_obj.labels},  # labels
            ])

        if epic_obj.test_environments:
            epic_data.extend([
                {'customfield_11003': epic_obj.test_environments},  # test environments
            ])

        if epic_obj.system_runtime:
            epic_data.extend([
                {'customfield_14803': [f'{self.get_core_system_uptime(epic_obj.system_runtime)}']},  # CoreSysUpTime
            ])

        if epic_obj.customer_name:
            epic_data.extend([
                {'customfield_13300': epic_obj.customer_name},  # Customer name
            ])

        if epic_obj.core_customer_name:
            epic_data.extend([
                {'customfield_15900': epic_obj.core_customer_name},  # Core Customer Name
            ])

        if epic_obj.notes:
            epic_data.extend([
                {'customfield_10975': [f'{epic_obj.notes}']},  # Notes
            ])

        if epic_obj.hash_bt:
            epic_data.extend([
                {'customfield_18301': [f'{epic_obj.hash_bt}']},  # Hash BT
            ])

        # if epic_obj.core_layer_type:
        #     epic_obj.extend([
        #         {'customfield_14800': epic_obj.core_layer_type},  # Core Layer Type
        #     ])
        # if epic_obj.site:
        #     epic_obj.extend([
        #         {'customfield_14900': [f'{epic_obj.site}']},  # core discovery site
        #     ])

        epic = self.jira_client.create_issue(project='CORE', issue_type='Epic', data=epic_data)

        if epic:
            self.logger.info('Epic was created')
            self.logger.info(f'Epic key is: {epic}\n')
        else:
            self.logger.error('Epic was not created')

        return epic

    def create_core(self, core_obj: Union[JiraParameters], summary: str = None, description: str = None) -> Union[str, None]:
        if not summary:
            summary = core_obj.summary
        if not description:
            description = core_obj.description

        core_data = [
            # Required fields
            {'reporter': [f'{self.username}']},  # reporter
            # {'assignee': [f'{epic_obj.assignee}']},  # assignee
            {'summary': [f'{summary}'[-254:]]},  # summary
            {'customfield_10202': [f'{core_obj.product_at_fault}']},  # product at fault
        ]

        # Other fields
        if description:
            core_data.extend([
                {'description': [f'{description}']},  # description
            ])

        if core_obj.entity_version:
            core_data.extend([
                {'fixVersions': [f'{core_obj.sr_version}']},  # SR Versions
                {'customfield_13707': [f'{core_obj.entity_version}']},  # g/eNodeB SW version
                {'customfield_18401': [f'{core_obj.entity_version}']},  # Last Occurred GNB Versions
            ])

        if core_obj.labels:
            core_data.extend([
                {'labels': core_obj.labels},  # labels
            ])

        if core_obj.test_environments:
            core_data.extend([
                {'customfield_11003': core_obj.test_environments},  # test environments
            ])

        if core_obj.path:
            core_data.extend([
                {'customfield_12600': [f'{core_obj.path}']},  # Path
            ])

        if core_obj.system_runtime:
            core_data.extend([
                {'customfield_14803': [f'{self.get_core_system_uptime(core_obj.system_runtime)}']},  # CoreSysUpTime
                {'customfield_14801': [int(self.get_system_runtime_minutes(system_runtime=core_obj.system_runtime, threshold=1))]},  # Core SystemUpTime (min)
            ])

        if core_obj.site:
            core_data.extend([
                {'customfield_10736': [{'value': f'{core_obj.site.split(" ")[0]}', 'child': f'{core_obj.site.split(" ")[1]}'}]},  # Discovery Site / Customer
                {'customfield_14900': [f'{core_obj.site}']},  # core discovery site
            ])

        if core_obj.customer_name:
            core_data.extend([
                {'customfield_13300': core_obj.customer_name},  # Customer name
            ])

        if core_obj.core_crashed_process:
            core_data.extend([
                {'customfield_15001': core_obj.core_crashed_process},  # Core Crashed Process
            ])

        if core_obj.core_customer_name:
            core_data.extend([
                {'customfield_15900': core_obj.core_customer_name},  # Core Customer Name
            ])

        if core_obj.cucp_version:
            core_data.extend([
                {'customfield_16800': [f'{core_obj.cucp_version}']},  # 5G_CUCP_Ver
            ])

        if core_obj.cuup_version:
            core_data.extend([
                {'customfield_16801': [f'{core_obj.cuup_version}']},  # 5G_CUUP_Ver
            ])

        if core_obj.du_version:
            core_data.extend([
                {'customfield_16200': [f'{core_obj.du_version}']},  # 5G_DU_Ver
            ])

        if core_obj.ru_version:
            core_data.extend([
                {'customfield_16203': [f'{core_obj.ru_version}']},  # 5G_RU_Ver
            ])

        if core_obj.notes:
            core_data.extend([
                {'customfield_10975': [f'{core_obj.notes}']},  # Notes
            ])

        if core_obj.hash_bt:
            core_data.extend([
                {'customfield_18301': [f'{core_obj.hash_bt}']},  # Hash BT
            ])

        if core_obj.crash_pid:
            core_data.extend([
                {'customfield_18302': core_obj.crash_pid},  # Crash PID
            ])

        # if core_obj.core_layer_type:
        #     core_data.extend([
        #         {'customfield_14800': core_obj.core_layer_type},  # Core Layer Type
        #     ])

        core = self.jira_client.create_issue(project='CORE', issue_type='Core', data=core_data)

        if core:
            self.logger.info('Core was created')
            self.logger.info(f'Core key is: {core}\n')
        else:
            self.logger.error('Core was not created')

        return core
