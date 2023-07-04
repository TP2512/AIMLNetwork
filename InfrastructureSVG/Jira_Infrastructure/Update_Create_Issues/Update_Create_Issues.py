import logging

import requests
import time
from requests import Timeout
from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials
from jira import JIRA, JIRAError
from InfrastructureSVG.Jira_Infrastructure.Test_Execution.Get_Test_Execution import TestExecution


class JiraIssueFields:
    def __init__(self):
        self.fields = None
        self.key = None
        self.rest_api_fields = None

    pass


class JiraClass:
    # def __init__(self, jira_issue=None, username=None, password=None):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.jira_issue = kwargs.get('jira_issue')
        if kwargs.get('username') and kwargs.get('password'):
            self.user = kwargs.get('username')
            self.password = kwargs.get('password')
        else:
            self.user, self.password = Credentials().credentials_per_app('EZlife')
        self.jira_connection = None
        self.connect_to_jira(jira_username_domain=self.user, jira_password_domain=self.password)

    def connect_to_jira(self, jira_username_domain, jira_password_domain):
        """
        This function responsible for connections to Jira_Infrastructure real server
        The function get 0 parameter:
        The function return 1 parameters:
            - "jira" - client of jira (real)
        """

        c = 0
        while True:
            try:
                c = c + 1  # count
                server = 'https://helpdesk.airspan.com'  # Jira_real
                if jira := JIRA(
                    basic_auth=(jira_username_domain, jira_password_domain),
                    options={'server': server},
                    timeout=580,
                ):
                    self.jira_connection = jira
                    break
            except JIRAError:
                if c <= 2:
                    self.logger.exception('')
                else:
                    self.logger.exception('')
                self.logger.exception("still error - The Core doesnt open")
                if c > 10:
                    time.sleep(1800)
                time.sleep(20)
            except Exception:
                self.logger.exception('')

    def fetch_issue(self, issue_id):
        try:
            if not issue_id:
                return None
            for _ in range(3):
                if self.jira_connection:  # no jira connection
                    return self.jira_connection.issue(issue_id)
                else:
                    self.connect_to_jira(jira_username_domain=self.user, jira_password_domain=self.password)
        except Exception:
            self.logger.exception('')

    def update_issue(self):
        try:
            self.jira_issue.update(fields=self.jira_issue.fields)
        except Exception:
            self.logger.exception('')

    def create_new_issue(self):
        try:
            for _ in range(3):
                if self.jira_connection:  # no jira connection
                    return self.jira_connection.create_issue(fields=self.jira_issue.fields)
                else:
                    # establish jira connection
                    self.connect_to_jira(jira_username_domain=self.user, jira_password_domain=self.password)
        except Exception:
            self.logger.exception('')
            return None

    def update_with_rest_api(self):
        try:
            for attr, values in self.jira_issue.rest_api_fields.__dict__.items():
                if values:
                    for single_value in values:
                        if single_value['method'] == "put":
                            requests.put(url=single_value["url"], json=single_value["body"], timeout=240)
                        elif single_value['method'] == "post":
                            requests.post(
                                    url=single_value["url"], json=single_value["body"], timeout=240)
        except Timeout:
            self.logger.exception('The request timed out')


class JiraSchema:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.all_projects_schema = JiraIssueFields()
        self.get_scheme()

    def get_scheme(self):
        """
        the function responsible to get all projects schema from jira (include all issue types and fields inside issue)
        it set all projects as attribute in schema object
        :return:
        """
        try:
            jira = JiraClass()
            if projects_names_list := self.projects_list_objects_to_list_of_names(
                jira.jira_connection.projects()
            ):
                scheme = jira.jira_connection.createmeta(projectKeys=projects_names_list,
                                                         expand='projects.issuetypes.fields')

                for project in scheme["projects"]:
                    setattr(self.all_projects_schema, project["key"], project)
            else:
                self.logger.debug("Failed to get projects list")

        except Exception:
            self.logger.exception("")

    def projects_list_objects_to_list_of_names(self, jira_projects):
        """
        this function responsible to convert list of jira PROJECTS objects to list of projects strings (and not objects)
        :return: list of strings contain all jira project names
        """
        try:
            return [project.key for project in jira_projects]
        except Exception:
            self.logger.exception("")
            return None


class EditData(JiraClass):
    # def __init__(self, schema=None, issue=None, project=None, issue_type=None, issue_data=None, username=None,
    #              password=None):
    def __init__(self, **kwargs):
        super().__init__(jira_issue=kwargs.get('issue'),
                         username=kwargs.get('username'), password=kwargs.get('password'))
        self.logger = logging.getLogger(
            f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}'
        )
        self.jiraTypesToPython = {"regular": ["string", "number", "issuelinks"], "array": ["array"]}
        self.issue_data = kwargs.get('issue_data')
        self.issue_schema = None
        self.schema = kwargs.get('schema') or JiraSchema()
        if kwargs.get('project') and kwargs.get('issue_type') and kwargs.get('issue_data'):
            self.create_new_jira_object(kwargs.get('project'), kwargs.get('issue_type'))
        elif kwargs.get('issue') and kwargs.get('issue_data'):
            self.update_object_with_data_from_user()

    def extract_project_and_issuetype_from_object(self):
        """
        this function responsible to extract project name (str) and issue type (str)
         from jira issue ( jira object type)
        :return: project (str) issue type (str)
        """
        try:
            if hasattr(self.jira_issue, "key") and self.jira_issue.key:
                project = self.jira_issue.fields.project.key
                issue_type = self.jira_issue.fields.issuetype.name
            else:
                project = self.jira_issue.fields.project
                issue_type = self.jira_issue.fields.issuetype
            return project, issue_type
        except Exception:
            self.logger.exception("")
            return None, None

    def extract_issuetype_fields_from_schema(self, project, issue_type):
        """
        the function responsible to extract all fields schema associated with issue_type from project
        this function extract from the schema object the project object and then iterate over
        all issue types of the project to find the relevant issue_type , once found - set issue_fields_schema
        as fields schema for issue type and return it
        :param project: str (project name in schema object)
        :param issue_type: str (issue name in project)
        :return: dict of fields schema associated with issue type
        """
        try:
            issue_fields_schema = None
            if hasattr(self.schema.all_projects_schema, project):
                project_object = getattr(self.schema.all_projects_schema, project)
                for issue in project_object['issuetypes']:
                    if issue["name"] == issue_type:
                        self.logger.debug(f"issue type {str(issue_type)} found!")
                        issue_fields_schema = issue["fields"]
                        break
            else:
                self.logger.info(f"Project {str(project)} not exist in Jira")
            return issue_fields_schema
        except Exception:
            self.logger.exception("")
            return None

    def update_object_with_data_from_user(self, data_from_user=None):
        """
        this is the main function to update jira object with new data fields from user
        :param data_from_user: fields and data from user that should be updated
        jira
        :return: nothing , the update of the values inside jira_object that we got by reference
        """
        try:
            if data_from_user:  # if user want to update an already existing object
                # he will call this method with new data
                self.issue_data = data_from_user
            # check if it's exiting object from jira or new created object in code that still
            # doesnt have id SVG1-XXXX for example
            if hasattr(self.jira_issue, "key") and self.jira_issue.key:
                project, issue_type = self.extract_project_and_issuetype_from_object()
                if project and issue_type:
                    issue_fields_schema = self.extract_issuetype_fields_from_schema(project, issue_type)
                    self.logger.debug(f"Project: {project} Issue Type:{issue_type}")
                    if issue_fields_schema:
                        setattr(self, "issue_schema", issue_fields_schema)
                        if self.jira_issue:  # need to update existing object
                            self.logger.debug(f"Working on issue #:{str(self.jira_issue.key)}")
                            add_fields = self.get_all_fields_by_operation_type_from_user_data("add")
                            set_fields = self.get_all_fields_by_operation_type_from_user_data("set")
                            if add_fields:
                                self.logger.debug("Start work on fields that set as ADD")
                                self.update_field_based_on_operation_type(add_fields, "add")
                            else:
                                pass
                            if set_fields:
                                self.logger.debug("Start work on fields that set as SET")
                                self.update_field_based_on_operation_type(set_fields, "set")
                            else:
                                pass
                        else:  # need to create new object
                            pass
                    else:
                        self.logger.debug(
                                f"Cant find issue schema, project: {project} issue type: {issue_type}")
                else:
                    self.logger.debug("Cant get project name or issue type")
            else:  # its new object created that still wasn't uploaded to jira (its second time triggered)
                project, issue_type = self.extract_project_and_issuetype_from_object()
                if project and issue_type:
                    issue_fields_schema = self.extract_issuetype_fields_from_schema(project, issue_type)
                    setattr(self, "issue_schema", issue_fields_schema)
                    if self.jira_issue:  # verify object
                        self.logger.debug("Working on issue uncreated issue in jira")
                        add_fields = self.get_all_fields_by_operation_type_from_user_data("add")
                        set_fields = self.get_all_fields_by_operation_type_from_user_data("set")
                        if add_fields:
                            self.logger.debug("Start work on fields that set as ADD")
                            self.update_field_based_on_operation_type(add_fields, "add")
                        else:
                            pass
                        if set_fields:
                            self.logger.debug("Start work on fields that set as SET")
                            self.update_field_based_on_operation_type(set_fields, "set")
                        else:
                            pass
                    else:  # need to create new object
                        pass
                else:
                    self.logger.debug("cant get project and issue type from issue")
        except Exception:
            self.logger.exception("")

    def update_field_based_on_operation_type(self, field_data, operation_type):
        """
        the function split into 2 parts: ADD (add to existing list of values from jira)
        and SET (Override the values from jira)
        the Add section extract the old values from jira object with relevant structure and then merge new data
        (with relevant jira structure) with old data and then update the jira object with merged data the
         Set section
        just add the field data to jira object in the relevant structure.
        param operation_type: str ADD/SET
        :return:
        """
        try:
            rest_fields_attribute_set = False
            for field in field_data:
                field_copy = field.copy()  # this is to prevent from pop items in the original dict
                key, value = field_copy.popitem()
                if rest_api_update := self.check_if_update_trough_rest(key):
                    # that have id SVG1-XXXXX
                    # set relevant attributes and data for that fields
                    # check for valid operation
                    if self.jira_issue.key:  # verify that the issue exist in jira (has issue id SVG-XXXXX)
                        if not rest_fields_attribute_set:  # set attribute only once
                            fields = JiraIssueFields()
                            setattr(self.jira_issue, "rest_api_fields", fields)
                            rest_fields_attribute_set = True
                        if hasattr(self.jira_issue, "key"):
                            field_schema = self.prepare_values_to_rest_api_schema(
                                    key, value, self.jira_issue.key)
                            setattr(self.jira_issue.rest_api_fields, key, field_schema)
                    else:
                        self.logger.info(
                                "Try to update fields that can be updated only when issue exist in JIRA")
                elif key in self.issue_schema:  # check that field exists in issuetype schema
                    self.logger.debug(f"Working on Field {str(key)}")
                    field_schema = self.issue_schema[key]
                    if valid_operation := self.validate_field_data_with_operation(
                        value, field_schema["operations"]
                    ):
                        self.logger.debug("Got valid input from user to insert")
                        # check allowed values if attribute exist in schema
                        if "allowedValues" in field_schema:
                            self.logger.debug(
                                    "Checking if the values from user is valid based on allowed"
                                    " values in schema")
                            valid_values = self.validate_values_with_allowed_values(key, field_schema["allowedValues"], value)
                        else:
                            self.logger.debug(
                                    "No allowed values found in field schema - continue next step")
                            valid_values = True
                            # don't compare values as nothing to validate with
                        if valid_values:
                            self.logger.debug("The values is valid")
                            field_data_inside_schema = self.insert_field_data_to_field_schema(key, field_schema['schema'], value)
                            if field_data_inside_schema is None:
                                self.logger.info(f"Cant update jira issue with field: {str(key)}")
                            elif str.lower(operation_type) == "set":
                                self.logger.debug(f"Set field {key} with {str(field_data_inside_schema)}")
                                setattr(self.jira_issue.fields, key, field_data_inside_schema)
                            elif str.lower(operation_type) == "add":
                                if data_from_issue := self.extract_old_data_from_jira_issue(
                                    key
                                ):
                                    self.logger.debug("Merge new data with old data")
                                    merged_data = field_data_inside_schema + data_from_issue
                                else:
                                    self.logger.debug("No need t0 merge - use only new data")
                                    merged_data = field_data_inside_schema
                                self.logger.info(
                                        f"Add data {merged_data}) to field {key} is DONE")
                                setattr(self.jira_issue.fields, key, merged_data)
                            else:
                                self.logger.info(
                                    f"Got unknown operation type: {operation_type} only add/set is allowed"
                                )
                        else:
                            self.logger.info(f"Values {str(value)}for field {str(key)} is invalid")
                    else:
                        self.logger.info(
                            f"The operation {str(operation_type)} for field {str(key)} is not allowed"
                        )
                else:
                    self.logger.info(f"User try to use unknown field: {str(key)}")
        except Exception:
            self.logger.exception("")

    def check_if_update_trough_rest(self, key):
        try:
            # customfield_10993 - test
            # customfield_11005 - test plan
            # status - PASS/FAIL
            return key in ["customfield_10993", "customfield_11005", "status"]
        except Exception:
            self.logger.exception("")
            return None

    def prepare_values_to_rest_api_schema(self, key, value, execution):
        try:
            jira_rst_url = f'https://{self.user}:{self.password}@helpdesk.airspan.com/rest/raven/1.0/api'
            field_schema = []
            if key and value and execution:
                for single in value:
                    if key == "customfield_10993":  # test
                        schema = {"add": [single]}
                        field_url = f'{jira_rst_url}/testexec/{str(execution)}/test'
                        field_schema.append({"body": schema, "url": field_url, "method": "post"})
                    elif key == "customfield_11005":  # test plan
                        schema = {"add": [execution]}
                        field_url = f'{jira_rst_url}/testplan/{str(single)}/testexecution'
                        field_schema.append({"body": schema, "url": field_url, "method": "post"})
                    else:
                        execution_id = TestExecution().get_test_execution_id(
                                execution, self.user, self.password)
                        if key == "status":  # status
                            schema = {"status": single}
                            field_url = f'{jira_rst_url}/testrun/{str(execution_id)}/?status={single}'
                            field_schema.append({"body": schema, "url": field_url, "method": "put"})
                        else:
                            self.logger.info("unknown rest API field ")
            else:
                self.logger.info("cant get Key/Value/Execution")
            return field_schema
        except Exception:
            self.logger.exception("")
            return None

    def extract_old_data_from_jira_issue(self, field_name):
        """
        this function probably will be used when ADD operation is used.
        the function responsible to extract field values from jira_object by field name and convert it to
        structure that allow to send it to jira as update
        :param field_name: str field name that should extract from jira object
        :return:list of values in allowed jira structure ["STR", "STR"] or [{"name1": "str1"}, {"name2": "str2}]
        """
        try:
            # get the old values from jira object
            data_from_issue = []
            if hasattr(self.jira_issue.fields, field_name):
                self.logger.debug(f"Extract data from field {str(field_name)}")
                old_data = getattr(self.jira_issue.fields, field_name)
                if old_data and isinstance(old_data, list):  # list of jira objects / list of string / numbers
                    field_schema = self.issue_schema[field_name]
                    data_from_issue = self.insert_field_data_to_field_schema(field_name, field_schema['schema'],
                                                                             old_field_data=old_data)
                self.logger.debug(str(data_from_issue))
            else:
                self.logger.debug(f"No attribute{str(field_name)} in jira object")
            return data_from_issue
        except Exception:
            self.logger.exception("")
            return None

    def extract_values_from_list_of_objects(self, old_data, attribute_name):
        """
        this function extracts the values of specific field from old_data object list (jira type object)
        :param old_data: list of jira objects that data should be extracted
        :param attribute_name: name of the attribute that hold the value of the object
        :return: list of strings that contain the relevant values extracted from all objects in field
        """
        try:
            old_data_str_list = []
            self.logger.debug("Extract Data from list of jira objects inside field")
            for single_value in old_data:
                if hasattr(single_value, attribute_name):
                    old_data_value = getattr(single_value, attribute_name)
                    old_data_str_list.append(old_data_value)
                else:
                    self.logger.debug(f"No attribute {attribute_name} in jira object")
            return old_data_str_list
        except Exception:
            self.logger.exception("")
            return None

    def trigger_update_in_jira(self):
        """
        this method clean the jira object before it trigger the update/ create methods
        :return:
        """
        try:
            # clean unnecessary attributes from fields object
            update = self.check_if_need_update_issue()
            self.clean_jira_issue_from_none_exist_attributes_in_schema()
            if update:
                self.clean_jira_issue_from_objects()
                # update jira_object in jira
                self.update_issue()
                if hasattr(self.jira_issue, "rest_api_fields") and self.jira_issue.rest_api_fields:
                    self.update_with_rest_api()
            elif data := self.create_new_issue():
                self.jira_issue = data
        except Exception:
            self.logger.exception("")

    def check_if_need_update_issue(self):
        return bool(hasattr(self.jira_issue, "key") and self.jira_issue.key)

    def validate_field_data_with_operation(self, field_data, operation_list):
        """
        this method checks that the 'values' user try to change is acceptable by the field schema
        :param field_data: list of values from user (list of str's)
        :param operation_list: list of operations from jira schema (list of str's)
        :return: bool True/ False
        """
        try:
            if "add" in operation_list:
                # check the field data is list type
                return isinstance(field_data, list)
                # can contain multiple values
            elif "set" in operation_list:
                if isinstance(field_data, list):
                    return len(field_data) == 1
                else:
                    # check the field data is dict or str (single value)
                    return isinstance(field_data, (dict, str))
                    # can contain single value only
            else:
                self.logger.debug("Unknown operation")
                return False
        except Exception:
            self.logger.exception("")
            return None

    def validate_values_with_allowed_values(self, field_name, field_allowed_values, field_data):
        """
        this method checks that the 'values' user try to change are valid , based on fields
         allowed values in field schema
        :param field_name:  str
        :param field_allowed_values: list of dicts that contain allowed values of field
        :param field_data: list of values from user
        :return: bool True/False
        """
        try:
            if attribute_name := self.check_field_key(field_name):
                valid = []
                # iterate over each value and compare to allowed values
                for value in field_data:
                    for allowed_value in field_allowed_values:
                        if value == allowed_value[attribute_name]:
                            valid.append(value)
                            break
                return len(valid) == len(field_data)
            else:
                self.logger.debug("Unknown attribute key in allowed values check")
                return False
        except Exception:
            self.logger.exception("")
            return None

    def insert_field_data_to_field_schema(self, field_name, field_schema,
                                          new_field_data=None, old_field_data=None):
        """
        this method convert the user input (strings) to relevant jira structure that will allow
        to send it via API
        :param field_name: str
        :param field_schema: dict of field schema
        :param new_field_data: optional - used to convert user's field values to relevant structure
        :param old_field_data:  - optional - used to extract for jira object the values of
        the field and convert it to relevant structure (when using he "ADD" operation in the main function)
        :return: if field_schema type is list - list of string/dicts/number otherwise: dict/string
        """
        try:
            if field_schema['type'] == 'array':
                # only if array there are items key
                arr = []
                if "items" in field_schema:  # validate items key exist
                    if field_schema['items'] in self.jiraTypesToPython["regular"]:
                        if new_field_data:
                            self.logger.debug("No need to convert anything, insert list of new fields as is")
                            arr = new_field_data
                        else:
                            self.logger.debug("No need to convert anything, insert list of old fields as is")
                            arr = old_field_data
                    else:  # rest of the options that isn't string is array of objects
                        # check for item type
                        field_type = self.check_field_key(field_name)
                        if old_field_data:
                            self.logger.debug("Extract old field data")
                            if need_to_convert := self.check_if_old_data_already_in_structure(
                                old_field_data
                            ):
                                new_field_data = self.extract_values_from_list_of_objects(
                                        old_field_data, field_type)
                            else:
                                return old_field_data
                        # iterate over field_data (can be list of values) and insert to array as object
                        if field_type:
                            if new_field_data:
                                self.logger.debug("Convert data to allowed jira structure")
                                for field in new_field_data:
                                    arr.append({field_type: field})
                            else:
                                self.logger.debug("Field data is None or empty")
                        else:
                            self.logger.debug(f"Cant find structure type for item {field_type}")
                return arr
            else:
                if key_ := self.check_field_key(field_name):
                    if isinstance(new_field_data, list) and len(new_field_data) == 1:
                        return (
                            new_field_data[0]
                            if field_schema['type']
                            in self.jiraTypesToPython["regular"]
                            else {key_: new_field_data[0]}
                        )
                    self.logger.info(
                            "Got wrong input format from user - should be list of values - "
                            "even when it single value")
                    return False
                else:
                    self.logger.debug("Cant get field key")
        except Exception:
            self.logger.exception("")
            return None

    def check_if_old_data_already_in_structure(self, old_field_data):
        """
        method used to check if the field data is already converted to structure that allow to send it to api
        will run only once
        :param old_field_data:
        :return:
        """
        try:
            for single_field in old_field_data:
                return not isinstance(single_field, dict)
        except Exception:
            self.logger.exception("")
            return None

    def check_field_key(self, field_name):
        """
        in jira there are 2 types of keys that should be used when send data to api:
        the first one is "name" that used in all fields that are not custom
        the second is "value" that used only on custom fields
        this method check if the field name is custom or not and return relevant value (str)
        :param field_name: str
        :return: str
        """
        try:
            # we found that on all customfield the key should be value,
            # and on regular fields they key should be named (issuetype, assignee etc)
            return "value" if "customfield" in field_name else "name"
        except Exception:
            self.logger.exception("")
            return None

    def clean_jira_issue_from_none_exist_attributes_in_schema(self):
        """
        to send data to jira api we need to clean the jira objects with irrelevant
         attributes
        this method checks if the attribute name exist in issue schema
        (when we get jira object from jira it contains a lot of fields that isn't relevant
         to specific issue type, we clean them)
        it returns a dict of values that can be sent to jira API
        :return: set (not return)
            dict of fields that exist in issue type schema (with values that should be sent to jira API)
        """
        try:
            self.logger.debug("Clean jira fields from none existing attributes in schema")
            if hasattr(self, "issue_schema"):
                object_dict = {}
                for attr, value in self.jira_issue.fields.__dict__.items():
                    if attr in self.issue_schema and value is not None:
                        object_dict[attr] = value
                    elif attr == "status":  # specific for status attribute that doesn't exist in schema
                        object_dict[attr] = value
                setattr(self.jira_issue, "fields", object_dict)
            else:
                self.logger.debug(
                        "No schema attribute found in jira issue --> probably wasn't added during the run")
        except Exception:
            self.logger.exception("")

    def clean_jira_issue_from_objects(self):
        """
        when we get jira object, fields attribute contain fields that are jira objects type ,
         that can't be sent to jira API, we clean all attributes that is not list, str, int ,
         float or dict type
        :return: set (not return) dict of fields that are list, str, int , float
        """
        try:
            object_dict = {}
            self.logger.debug("Clean jira fields that are object type")
            for attr, value in self.jira_issue.fields.items():
                if isinstance(value, list):
                    for single in value:
                        if isinstance(single, (list, str, int, float, dict)):
                            object_dict[attr] = value
                elif isinstance(value, (float, int, str, dict)):
                    object_dict[attr] = value

            setattr(self.jira_issue, "fields", object_dict)
        except Exception:
            self.logger.exception("")
            return None

    def get_all_fields_by_operation_type_from_user_data(self, operation_type):
        """
        extract user fields data by operation
        :param operation_type: str add/set
        :return: user data with specific operation type
        """
        try:
            for index, operation_data in enumerate(self.issue_data, start=0):
                if self.issue_data[index].get(operation_type):
                    if data := operation_data.get(operation_type):
                        self.logger.debug(f"Got all fields that should be{str(operation_type)}")
                        return data
            self.logger.debug(
                f"Wrong data format or no fields that should be{str(operation_type)}"
            )
            return []
        except Exception:
            self.logger.exception("")
            return None

    def create_new_jira_object(self, project, issue_type):
        """
        this is the main method to create new jira object using data from user
        :param project: str
        :param issue_type: str
        if the username and password won't receive , it will use the default hardcoded username and password.
        """
        try:
            if project and issue_type:
                self.jira_issue = JiraIssueFields()
                fields_obj = JiraIssueFields()
                if issue_fields_schema := self.extract_issuetype_fields_from_schema(
                    project, issue_type
                ):
                    setattr(self, "issue_schema", issue_fields_schema)
                    setattr(self.jira_issue, "fields", fields_obj)
                    setattr(self.jira_issue.fields, "issuetype", issue_type)
                    setattr(self.jira_issue.fields, "project", project)
                    setattr(self.jira_issue.fields, "reporter", {"name": self.user})
                    # add all fields and not just required to allow update fields during the run
                    self.add_all_fields()
                    # check that got all required fields from user
                    required_field_check, none_existing_fields = self.validate_got_required_fields_from_user()
                    if required_field_check:
                        self.update_field_based_on_operation_type(self.issue_data, "set")
                    else:
                        self.logger.info(
                                "Cant Create issue , missing required fields: " + str(none_existing_fields))
                else:
                    self.logger.debug(
                        f"Cant find issue schema, project: {str(project)} issue type:{str(issue_type)}"
                    )
            else:
                self.logger.info("Can't get project or issue type from user")
        except Exception:
            self.logger.exception("")
            return None

    def add_all_fields(self):
        """
        add fields that relevant to jira issue schema inside jira issue as attributes
        :return:
        """
        try:
            if hasattr(self, "issue_schema"):
                self.logger.debug("Add all fields from schema")
                for field_name, schema in self.issue_schema.items():
                    if not hasattr(self.jira_issue.fields, field_name):
                        setattr(self.jira_issue.fields, field_name, None)
                self.logger.debug("done")
            else:
                self.logger.debug("jira issue doesnt contain schema attribute")
        except Exception:
            self.logger.exception("")

    def validate_got_required_fields_from_user(self):
        """
        this method validates that the required fields to create new jira object is received from user based on
        each field schema
        :return: req_fields_in_data_fields - bool True/False ,
                none_existing_fields - list of fields that is required and not got from user (if exist)
        """
        try:
            data_fields = []
            req_fields = [
                field_name
                for field_name, schema in self.issue_schema.items()
                if schema["required"]
                and field_name not in ["issuetype", "project", "reporter"]
            ]
            for single_field in self.issue_data:
                if isinstance(single_field, dict):
                    if data_field_name := list(single_field.keys()):
                        data_fields.append(data_field_name[0])
            req_fields_in_data_fields = all(field_name in data_fields for field_name in req_fields)
            none_existing_fields = list(set(req_fields) - set(data_fields))
            return req_fields_in_data_fields, none_existing_fields
        except Exception:
            self.logger.exception("")
            return None, None
