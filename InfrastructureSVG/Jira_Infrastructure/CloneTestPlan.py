from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import IssueFieldsConstructor
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


def get_jira_issue(client, issue):
    client.get_issue(issue)
    return client.issues[issue].issue


def get_fix_versions(test_plan):
    return [i.name for i in test_plan.fields.fixVersions]


def get_labels(test_plan):
    if 'EZLifeTree' not in test_plan.fields.labels:
        return test_plan.fields.labels.append('EZLifeTree')
    return test_plan.fields.labels


def extract_testset_from_test_plan(test_plan):
    return [getattr(i, 'inwardIssue').key for i in test_plan.fields.issuelinks if hasattr(i, 'inwardIssue') and 'SIR' in getattr(i, 'inwardIssue').key][0]


def extract_env_config_from_test_plan(test_plan):
    return [getattr(i, 'outwardIssue').key for i in test_plan.fields.issuelinks if hasattr(i, 'outwardIssue') and 'SVGA' in getattr(i, 'outwardIssue').key][0]


def create_test_plan_copy(test_plan, setup_name, env_config, summary=None, hw_type=None):
    client = JiraActions(app_credentials='Dashboard')
    fields = IssueFieldsConstructor()
    test_plan_obj = get_jira_issue(client, test_plan)
    test_set = extract_testset_from_test_plan(test_plan_obj)
    test_set_obj = get_jira_issue(client, test_set)
    test_plans_data = [
        {fields.SUMMARY: [summary or test_plan_obj.fields.summary.replace(f"{test_plan_obj.fields.summary.split(']')[0].replace('[', '')}", setup_name.replace("ASIL-", ""))]},
        {'customfield_11003': [setup_name]},
        {fields.HW_TYPE: [hw_type or test_plan_obj.fields.customfield_10800[0].value]},
        {fields.FIX_VERSIONS: get_fix_versions(test_plan_obj)},
        {fields.LABELS: get_labels(test_plan_obj)},
    ]
    new_test_plan = client.create_issue(project='SVGA', issue_type='Test Plan', data=test_plans_data)
    test_plan_data = {
        'set': [],
        'add': [{'customfield_11004': test_set_obj.fields.customfield_10990}]
    }
    client.update_issue(new_test_plan, test_plan_data)
    client.create_issue_link('relates to', env_config, new_test_plan)
    client.create_issue_link('TestspanAuto For TestPlan', test_set, new_test_plan)

    return new_test_plan


if __name__ == '__main__':
    tp = create_test_plan_copy(test_plan='SVGA-14', setup_name='Asil-Toyota', env_config='SVGA-6')
    print()
