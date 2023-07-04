import logging

from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX


class OpenOrUpdateDefect:
    def __init__(self, summary, site, severity, description, label, folder_path, defect_parameters_dict=None):
        self.logger = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)

        self.reporter = 'Nessus_SVG'
        self.assignee = 'akimiagarov'

        self.summary = summary
        self.site = site
        self.severity = severity
        self.description = description
        self.label = label
        self.folder_path = folder_path

        self.defect_parameters_dict = defect_parameters_dict or {}
        self.entity_version = self.defect_parameters_dict.get('entity_version', '')
        self.entity_type = self.defect_parameters_dict.get('entity_type', 'gNB')
        self.bs_hw_type = self.defect_parameters_dict.get('bs_hw_type', 'undefined')
        self.test_environments = self.defect_parameters_dict.get('test_environments', '')

        # self.jira_client = JiraActions(app_credentials='CoreCare')
        self.jira_client = JiraActions(app_credentials='Nessus')

    def get_product_at_fault(self):
        if 'CUCP' in self.entity_type.upper():
            return 'vCU-CP'
        elif 'CUUP' in self.entity_type.upper():
            return 'vCU-UP'
        elif 'DU' in self.entity_type.upper():
            return 'vDU'
        elif 'RU' in self.entity_type.upper():
            return 'RU'
        else:
            return 'Unknown'

    @staticmethod
    def get_severity(severity):
        if severity == 'Critical':
            return 'Critical'
        elif severity == 'High':
            return 'High'
        elif severity == 'Medium':
            return 'Medium'
        elif severity in ['Info', 'Low']:
            return 'Low'
        else:
            return 'Unknown'

    def get_open_defects_by_filter(self):
        str_filter = f'project = DEF AND issuetype = Defect AND labels = "{self.label}" AND reporter in (Nessus_SVG, CoreCare-5G) AND (status = '
        for status in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX:
            str_filter += f'{status} OR status = '
        str_filter = f'{str_filter[:-13]})'
        return self.jira_client.search_by_filter(str_filter=str_filter)

    def found_defect(self):
        defect_objs = self.get_open_defects_by_filter()
        if defect_objs.iterable:
            return defect_objs[0].key
        else:
            self.logger.info('Open Defect was not found')

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def create_defect(self):
        summary = f'[SVG] Security Scan: {self.get_severity(self.severity)} | {self.label} - {self.summary}'

        minimal_defect_data = [
            # Required fields
            {'reporter': [self.reporter]},  # reporter
            {'summary': [f'{summary[:254]}']},  # summary
            {'customfield_10202': ['gNB']},  # product at fault
            # {'customfield_10202': [f'{self.get_product_at_fault()}']},  # product_at_fault
            {'customfield_10736': [{'value': f'{self.site.split(" ")[0]}', 'child': f'{self.site.split(" ")[1]}'}]},  # Discovery Site / Customer
            {'customfield_10200': [
                f'SR{self.entity_version.split("-", 1)[0]}'
                if len(self.entity_version.split("-", 1)) > 1 and self.is_number(self.entity_version.split("-", 1)[0])
                else 'Unknown'
            ]},  # Reported In Release (eNB)
            {'customfield_10800': [self.bs_hw_type]},  # BS Hardware Type
            {'customfield_10201': ['Always']},  # Reproducibility/Frequency
            {'customfield_10406': [self.get_severity(self.severity)]},  # Severity
            {'assignee': [self.assignee]},  # assignee -> from another function

            # Other fields
            {'description': [f'{self.description}']},  # description
            {'labels': ['Tenable', 'Nessus_SVG', f'{self.label}']},  # labels
            {'customfield_13707': [f'{self.entity_version}']},  # g/eNodeB SW version
            {'customfield_11003': [self.test_environments]},  # test environments
        ]

        defect_obj = self.jira_client.create_issue(project='DEF', issue_type='Defect', data=minimal_defect_data)

        if defect_obj:
            self.logger.info('Defect was created')
            self.logger.info(f'Defect key is: {defect_obj}\n')
        else:
            self.logger.error('Defect was not created')

        return defect_obj

    def return_highest_severity(self, current_severity: str, defect: str) -> str:
        severity_list = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'info': 4, 'Unknown': 5}

        self.jira_client.get_issue(defect)
        def_severity = self.jira_client.issues[defect].issue.fields.customfield_10406.value

        if severity_list[current_severity] > severity_list[def_severity]:
            return current_severity
        else:
            return def_severity

    def update_defect_if_found(self, defect):
        update_defect_data = {
            'set': [
                {'customfield_10406': [self.return_highest_severity(current_severity=self.get_severity(self.severity), defect=defect)]},  # Severity
            ],
            'add': [
                {'customfield_13707': [f'{self.entity_version}']},  # g/eNodeB SW version
                {'customfield_11003': [self.test_environments]},  # test environments
                {'customfield_10800': [self.bs_hw_type]},  # BS Hardware Type
            ]
        }

        self.jira_client.update_issue(issue_id=defect, data=update_defect_data)

        self.logger.info('Defect was updated')
        self.logger.info(f'Defect key is: {defect}\n')

    def update_defect_document_reference_name(self, defect):
        update_defect_data = {
            'set': [
                {'customfield_10713': [self.folder_path]},  # Document reference/name
            ],
            'add': []
        }

        self.jira_client.update_issue(issue_id=defect, data=update_defect_data)

        if defect:
            self.logger.info('Defect was updated')
            self.logger.info(f'Defect key is: {defect}\n')
        else:
            self.logger.info('Defect was not updated')

    def found_or_create_defect(self):
        if defect := self.found_defect():
            # Check for bigger version  # line 783
            self.update_defect_if_found(defect)
            return {'existing_defect': f'{defect}'}
        else:
            defect = self.create_defect()
            self.update_defect_document_reference_name(defect)
            return {'new_defect': f'{defect}'}
