import logging
import requests
import json

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


class GetBSHWTypes:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = JiraActions(app_credentials='EZlife')

        self.bs_hw_types = []

    def get_bs_hw_types(self):
        exclude_list = [
            '2.5G',
            'AIO',
            'Air4G',
            'AirCard',
            'AirDensity (AD386)',
            'AirDensity (AD420)',
            'AirDensity (AD480)',
            'AirDensity (AD480) Altair Based',
            'AirDensity (AD480) GCT Based',
            'AirDensity 140',
            'AirHarmony 1000D',
            'AirHarmony 4000',
            'AirHarmony 4000 FDD',
            'AirHarmony 4200',
            'AirHarmony 4400',
            'AirHarmony1000',
            'AirHarmony1000+',
            'AirSpeed 1000',
            'Airspeed 1030',
            'Airspeed 1032',
            'AirSpeed 1035',
            'AirSpeed 1050',
            'AirSpeed 1200',
            'AirSpeed 1200B',
            'AirSpeed 1200E',
            'AirSpeed 1200R/R2',
            'AirSpeed 1250 / ODUR',
            'AirSpeed 1250E',
            'AirSpeed 1300',
            'AirSpeed 1900',
            'AirSpeed/AirStrand 1200T',
            'AirSpeed1050',
            'AirSpeed1130',
            'AirStar 1200',
            'AirUnity 480 (APT)',
            'AirUnity 484',
            'AirUnity 484B',
            'AirUnity 484E',
            'AirUnity 540',
            'AirUnity 544',
            'AirUnity 545',
            'AirUnity 546',
            'AirUnity 587',
            'AirUnity 587 DA',
            'AirUnity 588 DA',
            'AirVelocity',
            'AirVelocity 1000',
            'AirVelocity 1500',
            'AirVelocity 500',
            'AirVelocity-NG 1200',
            'AirVelocity-NG 600',
            'All FSM based HW',
            'All XLP & FSM based HW',
            'All XLP & FSM based HW - Do not use it',
            'All XLP based HW',
            'AllinOne(DU+vCU)',
            'ATG RU (GoGo)',
            'AV-C',
            'AV100c',
            'Band 38 (U38) TDD 2570-2620MHz',
            'Band 40 (U40) TDD 2300-2400MHz',
            'Band 41 TDD (FULL) 2496-2690MHz',
            'Band 41 TDD (Mid) 2560-2630MHz',
            'Cisco-UCS',
            'CU',
            'CU Over VM',
            'DU',
            'iB400',
            'iB400/450/460',
            'iB440',
            'iB440Lite',
            'iB450',
            'iB460',
            'iBridge-2-A',
            'iBridge-2-B',
            'iBridge-2-C',
            'iR468H',
            'iRelay (iR460)',
            'iRelay (iR464)',
            'iRelay (iR464UC)',
            'iRelay (iR468)',
            'Legacy16eHW',
            'mmW RDU',
            'RIU-D',
            'Sub-6 RU',
            'Survey Tool (iR460M)',
            'Survey Tool (iR460S)',
            'Synergy2',
            'Synergy2 or 3',
            'Synergy2000',
            'Synergy3',
            'undefined',
            'VRAN',
            'XPU'
        ]
        url_versions_unreleased = f'https://{self.jira_client._username}:{self.jira_client._password}@helpdesk.airspan.com/rest/api/2/issue/createmeta?projectKeys=SVGA&issuetype=subtask&expand=projects.issuetypes.fields.customfield_10800'
        response_data = requests.get(url=url_versions_unreleased, timeout=600)
        response = json.loads(response_data.text)
        for i in response['projects'][0]['issuetypes']:
            if i['name'] == 'Sub-task':
                return [j['value'] for j in i['fields']['customfield_10800']['allowedValues'] if j['value'] not in exclude_list]


if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)
    hw_types = GetBSHWTypes()
    automation_ur_versions_unreleased = hw_types.get_bs_hw_types()
    print(automation_ur_versions_unreleased)
