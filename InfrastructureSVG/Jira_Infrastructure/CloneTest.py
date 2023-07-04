from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials
from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import IssueFieldsConstructor
from InfrastructureSVG.Jira_Infrastructure.FieldsValidator import validate_field
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions

from atlassian import Xray

fields = IssueFieldsConstructor()


def get_jira_issue(client, issue):
    client.get_issue(issue)
    return client.issues[issue].issue


def get_fix_versions(issue):
    return [i.name for i in issue.fields.fixVersions]


def get_fields_from_test_obj(test):
    test_fields = test.fields
    return [
        {
            getattr(fields, field_key): [validate_field(getattr(test_fields, field_value))]
        }
        for field_key, field_value in fields.__dict__.items()
        if field_value and hasattr(test_fields, field_value) and
        validate_field(getattr(test_fields, field_value)) and field_value not in ['fixVersions', fields.FIX_VERSIONS, 'summary']]


def get_issues_by_filter(client, jql_filter):
    return client.search_by_filter(jql_filter)


def create_test_copy():
    user, password = Credentials().credentials_per_app('Dashboard')
    xray = Xray(url='https://helpdesk.airspan.com/',
                username=user,
                password=password)
    client = JiraActions(app_credentials='Dashboard')
    issues = get_issues_by_filter(client, 'key = SIR-47403')
    for issue in issues:
        create_new_issue = get_fields_from_test_obj(issue)
        create_new_issue.append({fields.SUMMARY: [issue.fields.summary.replace('16', '32').replace('8', '16')]})
        create_new_issue.append({fields.FIX_VERSIONS: get_fix_versions(issue)})
        create_new_issue.append({fields.NUMBER_OF_UES: [32]})
        create_new_issue.append({'customfield_17100': [issue.fields.customfield_17100]})
        create_new_issue.append({'customfield_12671': [issue.fields.customfield_12671.value]})
        print(create_new_issue)
        new_test = client.create_issue(project='SIR', issue_type='Test', data=create_new_issue)
        print(new_test)
        step = xray.get_test_steps(issue.key)
        for i in step:
            xray.create_test_step(new_test, i['step']['raw'], i['data']['raw'], i['result']['raw'])


if __name__ == '__main__':
    create_test_copy()
    print()
