from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


def get_jira_client():
    return JiraActions(app_credentials='Dashboard')


def get_test_plans_by_filter(client):
    return client.search_by_filter("labels  =  EZLifeTree", fields=['customfield_11004', 'issuelinks'])


def return_jql_filter(test_plans_list):
    test_plans_jql_filter = 'key in '
    tp_list = []
    test_set_key = None
    for test_plan in test_plans_list:
        test_in_test_plans = len(test_plan.fields.customfield_11004)
        try:
            test_set_key = [i.inwardIssue.key for i in test_plan.fields.issuelinks if hasattr(i, 'inwardIssue') and 'SIR' in i.inwardIssue.key][0]
        except Exception:
            print(test_plan.key)
            # print(test_plan.key)
        test_set_obj = jira_client.search_by_filter(f'key = {test_set_key}')
        test_in_test_set = len(test_set_obj[0].fields.customfield_10990)
        if test_in_test_set != test_in_test_plans:
            tp_list.append(test_plan.key)

    test_plans_jql_filter += f'({", ".join(tp_list)})'
    print(test_plans_jql_filter)
    return test_plans_jql_filter


if __name__ == '__main__':
    jira_client = get_jira_client()
    test_plans = get_test_plans_by_filter(jira_client)
    jql_filter = return_jql_filter(test_plans)
