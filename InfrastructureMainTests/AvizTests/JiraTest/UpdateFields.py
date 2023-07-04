from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
# from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX, DEFECT_CLOSE_STATUS_LIST_JIRA_SYNTAX


def update_fields(issue_key):
    issue_obj_list = jira_client.search_by_filter(str_filter=f'key = {issue_key}')
    if issue_obj_list:
        issue_obj = issue_obj_list[0]

        update_data = {
            'set': [
                # {'customfield_10406': [f'Critical']},  # Severity
                {'customfield_10406': [f'Low']},  # Severity
            ],
            'add': []
        }

        jira_client.update_issue(issue_id=issue_obj, data=update_data)


if __name__ == '__main__':
    project_name, site = 'Jira', 'IL SVG'

    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    jira_client = JiraActions(app_credentials='TestspanAuto')

    update_fields(issue_key='DEF-41450')

    print()
