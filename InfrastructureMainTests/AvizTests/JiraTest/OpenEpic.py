from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


if __name__ == '__main__':

    minimal_epic_data = [
        {'reporter': [f'CoreCare-5G']},  # reporter
        # {'assignee': [f'{epic_obj.assignee}']},  # assignee
        {'summary': [f'Test']},
        {'customfield_10002': [f'Test']},  # Epic Name
        {'customfield_10202': [f'{"Unknown"}']},  # product_at_fault
        {'labels': ['AvizTest']},  # labels

        {'customfield_10975': [' ']},  # Notes
    ]

    jira_client = JiraActions()

    core_name = jira_client.create_issue(project='CORE', issue_type='Epic', data=minimal_epic_data)
    print(f'Epic key is: {core_name}\n')
    print()
