from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


def check_allowed_values(schema_fields: dict, customfield: str, value: str):
    bandwidth_list = [i['value'] for i in schema_fields[customfield]['allowedValues']]
    return value in bandwidth_list


if __name__ == '__main__':
    jira_client = JiraActions(app_credentials='CoreCare')

    schema_fields_ = jira_client._jira_connection.createmeta(projectKeys=['DEF'], expand='projects.issuetypes.fields')['projects'][0]['issuetypes'][0]['fields']
    # print(check_allowed_values(schema_fields=schema_fields_, customfield='customfield_10734', value='-1'))

    x = '1' if check_allowed_values(schema_fields=schema_fields_, customfield='customfield_10734', value='-1') else '2'
    print(x)

    print()
