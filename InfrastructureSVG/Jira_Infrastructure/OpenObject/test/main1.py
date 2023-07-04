from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.OpenObject.JiraDataClass_Infrastructure import Defect, Epic, Core
from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger


def main(jira_client):
    create_object_on_jira = CreateObjectOnJira(jira_client=jira_client)

    defect_obj = Defect(
        site='IL SVG',
        entity_version='19.00-161-0.0',
        labels=['AvizTest'],
    )
    defect = create_object_on_jira.create_defect(defect_obj=defect_obj)
    print()

    epic_obj = Epic(
        site='IL SVG',
        entity_version='19.00-161-0.0',
        labels=['AvizTest'],
    )
    epic = create_object_on_jira.create_epic(epic_obj=epic_obj)
    print()

    core_obj = Core(
        site='IL SVG',
        entity_version='19.00-161-0.0',
        labels=['AvizTest'],
    )
    core = create_object_on_jira.create_core(core_obj=core_obj)
    print()

    create_object_on_jira.create_link_between_core_and_epic(epic=epic, core=core)
    print()

    create_object_on_jira.create_link_between_two_object(link_from_issue=defect, link_to_issue=epic)
    print()

    jira_objects = {'defect_obj': defect_obj, 'epic_obj': epic_obj, 'core_obj': core_obj}
    print(
        f'Epic is: {epic}\n'
        f'Core is: {core}\n'
        f'Defect is: {defect}\n'
    )

    print()


if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    jira_client_ = JiraActions(app_credentials='TestspanAuto')

    main(jira_client_)

    print()
