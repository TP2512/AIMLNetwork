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

    jira_client = JiraActions()

    jira_client.create_issue_link(project='DEF', link_from_issue='DEF-38718', link_to_issue='DEF-39199')

    print()

# from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
#
#
# if __name__ == '__main__':
#     jira_client = JiraActions()
#
#     jira_client.create_issue_link('CoreCare', 'CORE-45977', 'DEF-39201')
#
#     jira_client.create_issue_link(project='CoreCare', link_from_issue='CORE-45977', link_to_issue='DEF-39199')  # work
#     jira_client.create_issue_link(project='DEF', link_from_issue='DEF-38718', link_to_issue='DEF-39199')
