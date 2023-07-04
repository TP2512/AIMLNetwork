from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.OpenObject.JiraDataClass_Infrastructure import JiraParameters
from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger


if __name__ == '__main__':
    PROJECT_NAME = 'Jira check for new def'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    jira_client = JiraActions(app_credentials='TestspanAuto')
    jira_parameters_obj = JiraParameters(
        site='IL SVG',
        entity_version='19.00-999.00',
        product_at_fault='DU',
        labels=['AvizTest'],
        hash_bt='007',
    )
    create_object_on_jira = CreateObjectOnJira(jira_client=jira_client)

    current_ver = '19.00-161-1.12'
    current_ver = '19.00-161-1.11'
    x = create_object_on_jira.check_if_need_to_create_new_defect_for_corecare(epic='CORE-69131',
                                                                              entity_type_name=jira_parameters_obj.product_at_fault,
                                                                              current_ver=current_ver)
    print(x)

    print()
