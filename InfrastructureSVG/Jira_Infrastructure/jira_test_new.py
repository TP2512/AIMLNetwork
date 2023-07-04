from datetime import datetime, timezone

import yaml
import pandas as pd

from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import IssueFieldsConstructor
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX

ConstructorFields = IssueFieldsConstructor()


def build_logger(site: str):
    log_file_name = f'{DATE_STRING}_{TIME_STRING} - {PROJECT_NAME.replace(" ", "_")}_Logs_{site.replace(" ", "_")}'
    log_path = f'C:\\Python Logs\\{PROJECT_NAME}\\{site}'
    return ProjectsLogging(project_name=PROJECT_NAME, path=log_path, file_name=log_file_name).project_logging()


PROJECT_NAME = 'Jira Test 5G'

ACTIVE_DATE_TIME = datetime.now(timezone.utc)
DATE_STRING = ACTIVE_DATE_TIME.strftime("%Y.%m.%d")
TIME_STRING = ACTIVE_DATE_TIME.strftime("%H.%M")

if __name__ == "__main__":
    logger = build_logger(site='IL SVG')
    logger.info(f'Start')

    exm = {
        'set': [
            {'summary': ['summary_aviz_test']},
            {'customfield_10202': ['Unknown']},
            {'customfield_10002': ['epic_aviz_test']},
            {'description': ['description_aviz_test']},
            {'labels': [' ']},
        ],
        'add': []
    }

    with open(f'C:\\Users\\azaguri\\Desktop\\xxx\\du_systeminfo.yaml', 'r') as fp_read:
        systeminfo = yaml.safe_load(fp_read.read().replace('\t', ' '))

    dataframe = pd.read_csv(f'\\\\asil-azaguri2\\C$\\Users\\azaguri\\Documents\\Temporary - can be deleted\\SUMMARY\\'
                            f'CORE_SUMMARY_2021_07_15.csv')

    for index, row in dataframe.iterrows():
        print(dataframe.columns.values)
        print(
            f'\nDate Line is: {row["Date Line"]}'
            f'\nDate Uploading Crash is: {row["Date Uploading Crash"]}'
            f'\nCrash Type is: {row["Crash Type"]}'
            f'\nIP Address is: {row["IP Address"]}'
            f'\nSetup Name is: {row["Setup Name"]}'
            f'\nSetup Owner is: {row["Setup Owner"]}'
            f'\nLink To Crash Folder is: {row["Link To Crash Folder"]}'
            f'\nCrash File Name is: {row["Crash File Name"]}'
            f'\nBack Trace hash is: {row["Back Trace hash"]}'
            f'\nBack Trace is: {row["Back Trace"]}'
            f'\nSystem Runtime is: {row["System Runtime"]}'
            f'\nCrash Timestamp is: {row["Crash Timestamp"]}'
            f'\nCore TTI is: {row["Core TTI"]}'
            f'\nCustomer Name is: {row["Customer Name"]}'
            f'\n'
        )

        minimal_epic_data = [
            {'summary': [f'{row["Back Trace"][-254:]}']},  # summary
            # {'customfield_10202': [f'{row["Crash Type"]}']},  # product_at_fault
            {'customfield_10202': [f'{"Unknown"}']},  # product_at_fault
            {'customfield_10002': [f'{row["Back Trace"][-254:]}']},  # Epic Name
            {'description': [f'{row["Back Trace"]}']},  # description
            {'labels': [f'{row["Back Trace hash"]}']},  # hash number

            {'customfield_11003': [f'{row["IP Address"]}', f'{row["Setup Name"]}']},  # test environments
            {'fixVersions': [f'{""}']},  # SR Versions
            {'customfield_14803': [f'{""}']},  # core system uptime

            #

            # need to be as update after core creation:
            {'customfield_15000': [f'{""}']},  # core occurrence count -> get all cores from epic after create a new core and link to epic

            # need to be as update after defect creation:
            {'customfield_13512': [f'{""}']},  # link defect -> after create a new defect
        ]

        minimal_core_data = [
            {'summary': [f'{row["Back Trace"][-254:]}']},
            {'customfield_10202': [f'{"Unknown"}']},  # product_at_fault
            {'description': [f'{row["Back Trace"]}']},
            {'labels': [f'{row["Back Trace hash"]}']},  # hash number
            {'customfield_14900': ['IL SVG']},  # core_discovery_site
            {'customfield_10000': ['IL SVG']},  # link
            {'customfield_10508': ['IL SVG']},  # epic_link
            {'customfield_12600': ['IL SVG']},  # core_files_path

            {'customfield_11003': [f'{row["IP Address"]}', f'{row["Setup Name"]}']},  # test environments
            {'fixVersions': [f'{""}']},  # SR Versions
            {'customfield_14803': [f'{""}']},  # core system uptime
            {'customfield_14900': [f'{""}']},  # core_discovery_site

            # need to be as update

        ]

        #

        jira_client = JiraActions()

        str_filter = f'issue in linkedissues(CORE-36715) AND (status = '
        for status in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX:
            str_filter += f'{status} OR status = '
        str_filter = f'{str_filter[:-13]})'
        defect_objs = jira_client.search_by_filter(str_filter=str_filter)
        x = defect_objs[0].key
        print()

        defect_objs = jira_client.search_by_filter(str_filter=f'issue in linkedissues(CORE-36715)')
        for defect in defect_objs.iterable:
            print(defect.fields.status)
            print()
        jira_client.get_issue(issue_id='DEF-38718')

        epic_name = jira_client.create_issue(project='CORE', issue_type='Epic', data=minimal_epic_data)
        print(f'EPIC key is: {epic_name}\n')

        core_name = jira_client.create_issue(project='CORE', issue_type='Core', data=minimal_core_data)
        print(f'Core key is: {core_name}\n')

        print()
    print()
