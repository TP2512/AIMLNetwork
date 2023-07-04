# #
# # class GetIssueField(Jira):
# #     pass
# #     def __init__(self, **kwargs):
# #         super().__init__(jira_issue=kwargs.get('issue'), username=kwargs.get('username'), password=kwargs.get('password'))
# #         self.logger = \
# #             logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
# #         self.issue_data = kwargs.get('issue_data')
# #         self.issue_schema = None
# #         if not kwargs.get('schema'):
# #             self.schema = Schema()
# #         else:
# #             self.schema = kwargs.get('schema')
# #
# #         print()
# #         pass
# #
# #
# #
# # obj = GetIssueField()
# # print(obj)
# # print()
# # log_file_name = f'{str(datetime.now().strftime("%H_%M_%S"))}'
# # log_path = 'C:/' + 'Python Logs/JiraUpdateCreateInfra/' + str(
# #     datetime.now().strftime("%d_%m_%Y")) + " " + log_file_name + "/"
# # logger = ProjectsLogging('JiraUpdateCreateInfra', path=log_path, file_name=log_file_name).project_logging()
# #
# #
# # fetch exsiting issue5
# # # jira_issue = Jira().fetch_issue("SVG1-12376")
# # print()
# # fetch all projects schema
# # jira_schema = Schema()
# #
# # create verb that contain all data that should updated in jira
# # update_existing_issue = [
# #     {'set':
# #         [
# #             # {"customfield_10512": ["FC1"]}
# #             {"status": ["PASS"]},
# #             {"customfield_11005": ["SVG1-71401"]},
# #             {"customfield_10993": ["SIR-546"]}
# #         ]
# #     },
# #     {'add':
# #         [
# #             {"versions": ["SR17.50"]},
# #             {"customfield_13709": ["129.17.50.100"]}
# #         ]
# #     }
# # ]
# #
# # create_new_issue = [
# #     {"versions": ["SR17.00"]},
# #     {"customfield_13709": ["129.17.50.061", "129.17.50.099"]},
# #     {"summary": ["blabla"]},
# #     {"fixVersions": ["SR17.00"]},
# # ]
# #
# # example with usage of 1 schema in all run: schema=jira_schema
# # edit_instance = EditData(schema=jira_schema, issue=jira_issue, issue_data=update_existing_issue)
# # print("update again")
# # edit_instance.update_object_with_data_from_user(data_from_user=update_existing_issue)
# # print("update in JIRA")
# # edit_instance.trigger_update_in_jira()
# #
# #
# # example when the schema will be init when the instance create
# # print("Create new jira issue")
# # create_instance = EditData(project="SVG1", issue_type="Test Execution", issue_data=create_new_issue)
# # print("update again")
# # create_instance.update_object_with_data_from_user(data_from_user=update_existing_issue)
# # print("create in JIRA")
# # create_instance.trigger_update_in_jira()
# import logging
# from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.Update_Create_Issues import JiraClass, JiraSchema, EditData
#
# jira_issue = JiraClass()
# jira_issue1 = jira_issue.fetch_issue("SVG1-12376")
# jira_issue2 = jira_issue.fetch_issue("SVG1-12377")
# print()
# # jira_schema = JiraSchema()
#
#
# update_existing_issue = [
#     {'set':
#         [
#             {"status": ["PASS"]},
#             {"customfield_11005": ["SVG1-71401"]},
#             {"customfield_10993": ["SIR-546"]},
#             {"customfield_10512": ["FC1"]},
#         ]
#     },
#     {'add':
#         [
#             {"versions": ["SR17.50"]},
#             {"customfield_13709": ["129.17.50.100"]}
#         ]
#     }
# ]
#
# create_new_issue = [
#     {"versions": ["SR17.00"]},
#     {"customfield_13709": ["129.17.50.061", "129.17.50.099"]},
#     {"summary": ["blabla"]},
#     {"fixVersions": ["SR17.00"]},
# ]
#
#
# # edit_instance1 = EditData(issue=jira_issue1, issue_data=update_existing_issue)
# # print("update again")
# # edit_instance1.update_object_with_data_from_user(data_from_user=update_existing_issue)
# # print("update in JIRA")
# # edit_instance1.trigger_update_in_jira()
#
#
# print("Create new jira issue")
# create_instance = EditData(project="SVG1", issue_type="Test Execution", issue_data=create_new_issue)
# print("update again")
# create_instance.update_object_with_data_from_user(data_from_user=update_existing_issue)
# print("create in JIRA")
# create_instance.trigger_update_in_jira()
#
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions

if __name__ == "__main__":
    user_datax = update_existing_issue = {
        'set':
            [
                {"status": ["FAILED"]},  # rest
                # {"customfield_11005": ["SVG1-71401"]},  # rest
                # {"customfield_10993": ["SIR-546"]},  # rest
                # {"customfield_10512": ["FC1"]},
            ],
        'add':
            [
                {"versions": ["SR17.50"]},
                {"customfield_13709": ["129.17.50.100"]}
            ]
    }

    create_new_issue = {
        "add": [{"versions": ["SR17.00"]},
                {"customfield_13709": ["129.17.50.061", "129.17.50.099"]},
                {"summary": ["blabla"]},
                {"fixVersions": ["SR17.00"]}],
        "set": [
            {"customfield_10993": ["SIR-546"]}
        ]
    }

    test = {
        'set':
            [{'customfield_18401': ["a", "b", "c"]}],  # Last Occurred GNB Versions
        'add':
            []
    }
    create = [
        {"fixVersions": ["SR18.50"]},
        {"customfield_10736": [{"value": "IL", "child": "SVG"}]},
        {"summary": ["XXXX"]},
        {"labels": ["xxx", "yyy"]},
        {"customfield_10202": ["5G UE"]},
        {"customfield_10800": ["Air4G"]},
        {"customfield_10406": ["Critical"]},
        {"customfield_10200": ["Unknown"]},
        {"customfield_10201": ["Always"]},
        {"customfield_10715": ["SR18.00"]},
    ]
    xxx = JiraActions()
    object_ = xxx.update_issue(issue_id="DEF-39265", data=test)

    xxx.create_issue(project="DEF", issue_type="Defect", data=create)
    print("x")
