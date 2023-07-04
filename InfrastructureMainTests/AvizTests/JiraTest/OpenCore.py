from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


if __name__ == '__main__':
    minimal_core_data = [
        {'reporter': [f'CoreCare-5G']},  # reporter
        {'summary': [f'Test']},
        {'customfield_10202': [f'{"Unknown"}']},  # product_at_fault
        {'description': [f'Back Trace']},
        {'labels': [f'007']},  # hash number
        {'customfield_14900': ['IL SVG']},  # core_discovery_site
    ]

    jira_client = JiraActions()

    core_name = jira_client.create_issue(project='CORE', issue_type='Core', data=minimal_core_data)
    print(f'Core key is: {core_name}\n')
    print()
