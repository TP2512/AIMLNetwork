from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
# from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX, DEFECT_CLOSE_STATUS_LIST_JIRA_SYNTAX


def update_epic_bs_hardware_type():
    epic_list = jira_client.search_by_filter(str_filter='project = CORE AND issuetype = Epic AND reporter in (CoreCare-5G) AND "BS Hardware Type" is empty')
    for index, epic in enumerate(epic_list, start=1):
        print(f'{index}/{len(epic_list)} - epic is: {epic}')

        version_type_set = set()
        core_list = jira_client.search_by_filter(str_filter=f'project = CoreCare AND issuetype = Core AND "Epic Link" = {epic}')
        for core in core_list:
            if core.fields.customfield_10975 and 'VRAN' in core.fields.customfield_10975:
                version_type_set.add('VRAN')
            else:
                version_type_set.add('AIO')

        update_epic_data = {
            'set': [],
            'add': [
                {'customfield_10800': list(version_type_set)},  # BS Hardware Type
            ]
        }

        jira_client.update_issue(issue_id=epic.key, data=update_epic_data)


def update_defect_bs_hardware_type():
    epic_list = jira_client.search_by_filter(str_filter='project = CORE AND issuetype = Epic AND reporter in (CoreCare-5G)')
    for index, epic in enumerate(epic_list, start=1):
        print(f'{index}/{len(epic_list)} - epic is: {epic}')

        defect_list = jira_client.search_by_filter(str_filter=f'project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues({epic})')
        for defect in defect_list:
            if epic.fields.customfield_10800:
                update_defect_data = {
                    'set': [],
                    'add': [
                        {'customfield_10800': [i.value for i in epic.fields.customfield_10800]},  # BS Hardware Type
                    ]
                }

                jira_client.update_issue(issue_id=defect.key, data=update_defect_data)


if __name__ == '__main__':
    project_name, site = 'Jira', 'IL SVG'

    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    jira_client = JiraActions(app_credentials='TestspanAuto')

    # update_epic_bs_hardware_type()
    update_defect_bs_hardware_type()

    print()
