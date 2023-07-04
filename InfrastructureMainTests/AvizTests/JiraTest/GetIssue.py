from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions

if __name__ == '__main__':
    project_name, site = 'Jira', 'IL SVG'

    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    jira_client = JiraActions(app_credentials='TestspanAuto')

    epic_key = 'CORE-78502'
    jira_client.get_issue(epic_key)
    epic_object = jira_client.issues[epic_key].issue

    defect_key = 'DEF-43453'
    jira_client.get_issue(defect_key)
    defect_object = jira_client.issues[defect_key].issue

    objects = {'epic_object': epic_object, 'defect_object': defect_object}

    print()

    defect_duplicate_list = [defect_object]
    epics = [j.inwardIssue.key for i in defect_duplicate_list for j in i.fields.issuelinks if hasattr(j, 'inwardIssue') and 'CORE-' in j.inwardIssue.key]
    print()

    x = sum(
        total_core_occurrence_count.__len__()
        if (total_core_occurrence_count := jira_client.search_by_filter(str_filter=f'project = CoreCare AND "Epic Link" = {epic}'))
        else 0
        for epic in epics
    )

    total_core_occurrence_count = jira_client.search_by_filter(str_filter=f'project = CoreCare AND "Epic Link" = {epics[0]}')
    y = total_core_occurrence_count.__len__()

    print()
