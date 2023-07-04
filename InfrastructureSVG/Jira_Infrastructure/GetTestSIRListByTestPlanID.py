from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


def get_test_sir_list_by_test_plan(test_plan_id: str):
    jira_client = JiraActions(app_credentials='TestspanAuto')

    test_set_by_test_plan_filter = f'project = SIR AND issuetype = "Test Set" AND ' \
                                   f'issueFunction in linkedIssuesOfRecursive("key={test_plan_id}", "TestspanAuto by TestSet")'
    return (test_set_objects[0] if (
        test_set_objects := jira_client.search_by_filter(str_filter=test_set_by_test_plan_filter, fields=['customfield_10990'])
    ) else [])
