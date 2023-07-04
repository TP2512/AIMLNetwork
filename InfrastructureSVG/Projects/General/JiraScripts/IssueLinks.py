from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials
from InfrastructureSVG.Jira_Infrastructure.Connection.Connection import JiraConnection


def move_test_set_to_correct_link():
    user, password = Credentials().credentials_per_app('Dashboard')
    jira_client = JiraConnection().jira_real_connection(jira_username_domain=user, jira_password_domain=password)

    test_plans = jira_client.search_issues('project = "SVG Automation (IL)"  AND type = "Test Plan"', fields='issuelinks', maxResults=5000)
    for test_plan in test_plans:
        if test_plan.fields.issuelinks:
            for link in test_plan.fields.issuelinks:
                if hasattr(link, 'outwardIssue') and 'SIR' in link.outwardIssue.key:
                    print(link.outwardIssue.key)
                    jira_client.delete_issue_link(link.id)
                    jira_client.create_issue_link('TestspanAuto by TestSet', test_plan.key, link.outwardIssue.key)


if __name__ == '__main__':
    move_test_set_to_correct_link()
