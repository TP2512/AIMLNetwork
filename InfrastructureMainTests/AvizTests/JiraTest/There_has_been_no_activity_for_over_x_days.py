from datetime import datetime, timezone, timedelta

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX
from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import get_full_field_list


def get_open_defects_by_filter():
        str_filter = 'project = DEF AND reporter = CoreCare-5G AND (status = '
        for status in DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX:
            str_filter += f'{status} OR status = '
        str_filter = f'{str_filter[:-13]})'
        return jira_client.search_by_filter(str_filter=str_filter, fields=get_full_field_list())


if __name__ == '__main__':
    project_name, site = 'Jira', 'IL SVG'
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    jira_client = JiraActions(app_credentials='TestspanAuto')
    create_object_on_jira = CreateObjectOnJira(jira_client=jira_client)

    active_date_time = datetime.now(timezone.utc)
    corecare_defect_list = get_open_defects_by_filter()
    for corecare_defect in corecare_defect_list:
        if datetime.strptime(corecare_defect.fields.updated.split('T')[0][2:], '%y-%m-%d') > datetime.today() - timedelta(days=18):
            # jira_client.transition_issue(corecare_defect.key, 'Parked-Archive')
            jira_client.transition_issue(issue_key='DEF-45467', tranistion_name='Parked Archive', comment='There has been no activity for over 18 days')
            print()

    print()
