from typing import Union

from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira

jira_client = JiraActions(app_credentials='EZlife')
create_object_on_jira = CreateObjectOnJira(jira_client=jira_client)


def get_open_defect_from_duplicate_defect(defect: str, defects_dict: dict) -> Union[str, dict]:
    print(defect)
    defects_dict['defects_list'].append(defect)

    jira_client.get_issue(defect)
    if create_object_on_jira.check_if_defect_open(defect_status=jira_client.issues[defect].issue.fields.status.name):
        defects_dict['defects_open'].append(defect)

    jira_client.get_issue(defect)
    defects_linked = jira_client.search_by_filter(f'project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues({defect})')

    for defect_linked in defects_linked:
        if defect_linked.key not in defects_dict['defects_list']:
            get_open_defect_from_duplicate_defect(defect=defect_linked.key, defects_dict=defects_dict)
    return defects_dict


if __name__ == '__main__':
    _defects_dict = {'defects_list': [], 'defects_open': []}
    graph_implementation = get_open_defect_from_duplicate_defect(defect='DEF-42912', defects_dict=_defects_dict)

    if graph_implementation['defects_open']:
        print(f'\nUpdate the defect: {sorted(graph_implementation["defects_open"])}')
    else:
        print(
            f'\nDefect list is: {sorted(graph_implementation["defects_list"])}.'
            f'\nNeed to create a new Defect'
        )

    print()


"""
https://helpdesk.airspan.com/browse/DEF-42918?jql=project%20%3D%20DEF%20AND%20issuetype%20%3D%20Defect%20AND%20labels%20%3D%20AvizTest
https://helpdesk.airspan.com/browse/DEF-42916
https://helpdesk.airspan.com/browse/DEF-42912
https://helpdesk.airspan.com/browse/DEF-42917
https://helpdesk.airspan.com/browse/DEF-42918
"""
