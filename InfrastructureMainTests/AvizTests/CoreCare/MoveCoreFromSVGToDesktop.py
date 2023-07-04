import shutil

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira


"""
find Epic by label:
===================
project = CoreCare AND type = Epic AND labels = 43207189 AND ("Product At Fault" = vCU-CP OR "Product At Fault" = vDU ) ORDER BY cf[10202] ASC


---------------------

find Core by Epic:
==================
project = CoreCare AND issuetype = Core AND "Epic Link" = CORE-65064 ORDER BY cf[10202] ASC


---------------------

find DEF by Epic:
==================
project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues(CORE-65064) ORDER BY cf[10202] ASC

"""

if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    #

    jira_client = JiraActions(app_credentials='CoreCare')
    create_object_on_jira = CreateObjectOnJira(jira_client=jira_client)

    # jira_filter = 'project = CORE AND issuetype = Core AND description ~ demangle_output AND text ~ "demangle_output" ORDER BY created DESC'
    # jira_filter = 'project = CORE AND issuetype = Core AND description ~ None AND text ~ "None" ORDER BY created DESC'
    jira_filter = 'project = CoreCare AND issuetype = Core AND "Epic Link" = CORE-72444'  # Search Cores by Epic

    core_list = create_object_on_jira.automation_helper.get_by_filter(str_filter=jira_filter)
    for core in core_list:
        if core.fields.customfield_12600 and core.fields.customfield_10975:
            shutil.copy(core.fields.customfield_12600, f'C:\\Users\\Administrator\\Desktop\\New folder\\{core.fields.customfield_10975}')
        else:
            print(f'Core {core.key} has no path (customfield_12600)')
            print(f'customfield_12600 is: {core.fields.customfield_12600}')
            print(f'customfield_10975 is: {core.fields.customfield_10975}')

    print()
