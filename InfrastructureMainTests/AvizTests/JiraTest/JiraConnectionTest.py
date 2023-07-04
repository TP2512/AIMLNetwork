from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira


if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    #

    jira_client = JiraActions(app_credentials='TestspanAuto')
    create_object_on_jira = CreateObjectOnJira(jira_client=jira_client)
    print()

    defect = 'DEF-42889'
    jira_client.get_issue(defect)
    print(jira_client.issues[defect].issue.fields.customfield_10406.value)
    print()
