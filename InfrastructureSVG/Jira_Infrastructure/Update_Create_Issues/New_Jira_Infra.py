import time
import inspect

import requests
from jira import JIRA, JIRAError
import logging

from requests import ReadTimeout

from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials
from InfrastructureSVG.Jira_Infrastructure.Test_Execution.Get_Test_Execution import TestExecution


class JiraHelper:

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def extract_workflow_from_object(self, jira_object):
        """
        this function responsible to extract workflow id (str)
        :return: workflow id (str)
        """
        try:
            if jira_object:
                issue_workflow_id = jira_object.fields.status.id
                return issue_workflow_id
            else:
                self.logger.error("issue isn't fetched from JIRA")
                return None
        except Exception:
            self.logger.exception("")
            return None

    def check_field_key(self, field_schema_or_name):
        """
        in jira there are 2 types of keys that should be used when send data to api:
        the first one is "name" that used in all fields that are not custom
        the second is "value" that used only on custom fields
        this method check if the field name is custom or not and return relevant value (str)
        :param field_schema_or_name: str
        :return: str
        """
        try:
            # we found that on all customfield the key should be value,
            # and on regular fields they key should be named (issuetype, assignee etc)
            #if "customfield" in field_name:
            #    return "value"
            #else:
            #    return "name"
            if type(field_schema_or_name) is list:
                value_to_check = field_schema_or_name[0]
                if value_to_check.get('name'):
                    return 'name'
                elif value_to_check.get('value'):
                    return 'value'
                else:
                    return None
            else:
                if "customfield" in field_schema_or_name:
                    return "value"
                else:
                    return "name"
        except Exception:
            self.logger.exception("")
            return None

    def extract_values_in_schema_allowed_values(self, field_name, field_schema):
        """
        this function responsible to extract  allowed values from jira schema
        :param field_name: string - name of the field in schema
        :param field_schema: list  of allowed values inside schema
        :return: field_allowed_values_strings: list of strings represent allowed values per field name
        """
        try:
            attribute_name = JiraHelper().check_field_key(field_schema["allowedValues"])
            field_allowed_values_strings = []
            for allowed_value in field_schema["allowedValues"]:
                field_allowed_values_strings.append(allowed_value[attribute_name])
            return field_allowed_values_strings
        except Exception:
            self.logger.exception("")
            return None

    def extract_required_field_names_from_schema(self, fields_schema_dict):
        """
        this function responsible to extract  all required field names from issue schema (str)
        :param fields_schema_dict: dict contain all issue schema
        :return: list of strings represent all required field names
        """
        try:
            req_fields = []
            if fields_schema_dict:
                for field_name, schema in fields_schema_dict.items():
                    if schema["required"]:
                        # got this 3 values in create_new_jira_object function and set the attributes there,
                        # skip for checking them as required here
                        if not field_name == "issuetype" and not field_name == "project" and not field_name == "reporter":
                            req_fields.append(field_name)
                    else:
                        pass
            else:
                pass
            return req_fields
        except Exception:
            self.logger.exception("")
            return None

    def extract_user_input_field_names(self, fields_list_of_dict):
        """
        this function responsible to extract  all field names from user inputs (str)
        :param fields_list_of_dict: dict contain all fields with data from user
        :return: list of strings represent all field names that user want to change
        """
        try:
            data_fields = []
            if fields_list_of_dict:
                for single_field in fields_list_of_dict:
                    if isinstance(single_field, dict):
                        data_field_name = list(single_field.keys())
                        if len(data_field_name) > 0:
                            data_fields.append(data_field_name[0])
                        else:
                            pass
            else:
                pass
            return data_fields
        except Exception:
            self.logger.exception("")
            return None

    def convert_to_add_set_schema(self, user_data):
        try:
            if type(user_data) is list:
                return {"set": user_data, "add": []}
            else:
                self.logger.error("user sent data in wrong format, should be list of dicts")
                return None
        except Exception:
            self.logger.exception("")
            return None

    def verify_data_structure_add_set(self, user_data):
        try:
            valid_add_structure = self.verify_data_structure(user_data, "add")
            valid_set_structure = self.verify_data_structure(user_data, "set")
            if valid_add_structure and valid_set_structure:
                return True
            else:
                self.logger.error("failed to validate structure from user - > add or set dict not configured properly")
                return False
        except Exception:
            self.logger.exception("")
            return None

    def verify_data_structure(self, user_data, operation_type):
        try:
            if type(user_data) is dict:  # verify var is dict
                if user_data.get(operation_type) is not None:  # verify add or set attribute exist
                    if type(user_data[operation_type]) is list:  # verify fields in array
                        return True
                    else:
                        self.logger.error(f'got wrong format from user in add attribute - '
                                          f'expected a list but got {type(user_data[operation_type])}')
                        return False
                else:
                    return False
        except Exception:
            self.logger.exception("")
            return None

    def check_field_value_dict_contain_value_and_child(self, field_value):
        try:
            if isinstance(field_value, list) and len(field_value) == 1:  # dict in list
                if isinstance(field_value[0], dict) and "value" in field_value[0].keys() \
                            and "child" in field_value[0].keys():  # dict contain value and child keys
                    return True
                else:
                    self.logger.error(f'option-with-child - expected dict with value & child keys but got {str(field_value)}')
                    return False
            else:
                self.logger.error("we got unknown user data structure")
                return False
        except Exception:
            self.logger.exception("")
            return None

    def return_value_object_if_exist_in_list(self, list_of_objects_with_allowed_values, key_in_dict_search, value_to_search):
        try:
            for idx in list_of_objects_with_allowed_values:
                if idx[key_in_dict_search] == value_to_search:
                    return idx
                else:
                    pass
            return False
        except Exception:
            self.logger.exception("")
            return None

    def check_user_data_is_list_of_string(self, user_field_data):
        try:
            if isinstance(user_field_data, list):
                for single_value in user_field_data:
                    if not isinstance(single_value, str):
                        return False
                return True
            else:
                return False
        except Exception:
            self.logger.exception("")
            return None


class JiraSchema:
    def __init__(self):
        # if not hasattr(self, "issue"):
        #     raise Exception("Init Class from JirActions")
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.rest_api_fields_schema = {"customfield_10993": {"body": {"add": "array"},
                                                             "url": "/testexec/issue_key/test", "method": "post",
                                                             "url_variable_type": ["issue_key"]},
                                       "customfield_11005": {"body": {"add": "array"},
                                                             "url": "/testplan/user_value/testexecution",
                                                             "method": "post", "url_variable_type": ["user_value"]},
                                       "customfield_11004": {"body": {"add": "array"},
                                                             "url": "/testplan/test_plan_id/test",
                                                             "method": "post", "url_variable_type": ["test_plan_id"]},
                                       "status": {"body": {"status": "string"},
                                                  "url": "/testrun/issue_id/?status=user_value",
                                                  "url_variable_type": ["issue_id", "user_value"],
                                                  "method": "put"}}
        self.jiraTypesToPython = {"regular": ["string", "number", "issuelinks"], "array": ["array"],
                                  "option-with-child": ["option-with-child"]}

        self.fields_schema_normal_permission = None
        self.fields_schema_transition = None
        self.project_transitions = None
        self.tranistion_name = None

    def get_schema_by_project_and_issue_type(self, jira_con, project_name, issue_key):
        """
        this function responsible to fetch schema of issue by project name & issue key
        :param jira_con: object - jira connection (obje
        :param project_name: string - name of the project to fetch all issues of the project
        :param issue_key: string - name of the issue type that should be extracted from all issues that got to
        specific project
        """
        try:
            all_issue_schema_in_project = self._get_schema_of_all_issues_in_project(jira_con, project_name)
            self._extract_schema_of_relevant_issue_type_to_create_new_issue(issue_key, all_issue_schema_in_project)
        except Exception:
            self.logger.exception("")

    def _extract_schema_of_relevant_issue_type_to_create_new_issue(self, issue_key, all_issue_schema_in_project):
        """
        this function responsible to extract relevent issue type schema from all issues per project shcmea
        :param all_issue_schema_in_project: list of issue related to project
        :param issue_key: string - name of the issue that need to extract from the list of issues
        """
        try:
            for issue_type in all_issue_schema_in_project:
                if issue_type["name"] == issue_key:
                    self.fields_schema_normal_permission = issue_type["fields"]
                    break
        except Exception:
            self.logger.exception("")

    def _get_schema_of_all_issues_in_project(self, jira_connection, project_name):
        """
        this function responsible to fetch all issues types and their schemas per project
        :param jira_connection: object
        :param project_name: string - name of the project in jira
        """
        try:
            schema_per_issue_type_in_project = jira_connection.createmeta(projectKeys=[project_name],
                                                                          expand='projects.issuetypes.fields')
            return schema_per_issue_type_in_project['projects'][0]['issuetypes']
        except Exception:
            self.logger.exception("")

    def get_fields_schema_with_normal_permission(self, issue_key):
        """
        this function responsible to fetch schema of specific issue with regular permission (regular edit) trough rest
        """
        try:
            jira_rst_url = f'https://{self.username}:{self.password}@helpdesk.airspan.com/rest/api/2/issue/' \
                           f'{issue_key}/editmeta'
            response = requests.get(url=jira_rst_url, timeout=240)
            if response.status_code == 200:
                self.fields_schema_normal_permission = response.json()["fields"]
            else:
                self.logger.error(f'failed to get issue editable fields with normal permission {issue_key}')
        except Exception:
            self.logger.exception("")

    def get_fields_schema_with_transition(self, issue_key):
        """
        this function responsible to get schema of tranistion fields based on current status of the issue
        """
        try:
            issue_workflow_id = JiraHelper().extract_workflow_from_object(self.issue)
            all_transitions = self._fetch_issue_transitions(issue_key)
            self._get_fields_schema_from_transition_by_current_issue_workflow_id(all_transitions, issue_workflow_id)
            self._filter_duplicates_from_transition_fields_list_and_normal_fields()
        except Exception:
            self.logger.exception("")

    def verify_tranistion_name_exist_in_issue_current_workflow(self, tranistion_name):
        """
        this function responsible to verify transition name exist in issue current workflow
        """
        try:
            issue_workflow_id = JiraHelper().extract_workflow_from_object(self.issue)
            all_transitions = self._fetch_issue_transitions(self.issue.key)
            if self.issue.fields.issuetype.name == "Test Execution":
                allowed_tranistion = self._check_tranistion_name_exist_in_all_transitions_of_issue_test_execution(
                    all_transitions, tranistion_name)
            else:
                allowed_tranistion = self._verify_tranistion_name_is_allowed_in_workflow(all_transitions, issue_workflow_id, tranistion_name)
            return allowed_tranistion
        except Exception:
            self.logger.exception("")

    def _check_tranistion_name_exist_in_all_transitions_of_issue_test_execution(
            self, transitions_dict, tranistion_name):
        """
        this function responsible check if tranistion name exist in list of allowed tranistion of workflow
        used only in test excution as in test excution the tranistion attached to workflow in wrong way
        so we only check that the tranistion that user try to preform exist in issue and not if its allowed in workflow
        :param transitions_dict: dict of all available tranistion for issue for specific workflow
        """
        try:
            # workflow = issue status
            allowed_tranistion_for_workflow = []
            if type(transitions_dict) is dict:
                for transition in transitions_dict["transitions"]:
                    allowed_tranistion_for_workflow.append(transition["name"])
                if tranistion_name in allowed_tranistion_for_workflow:
                    return True
                else:
                    return False
            else:
                self.logger.error("failed to get issue transition dict from jira")
                return False
        except Exception:
            self.logger.exception("")

    def _verify_tranistion_name_is_allowed_in_workflow(self, transitions_dict, workflow_id, tranistion_name):
        """
        this function responsible to extract the relevant tranistion to current status of the issue (workflow)
        :param workflow_id: string - id of the current workflow (status of the issue)
        :param transitions_dict: dict of all available tranistion for issue
        """
        try:
            # workflow = issue status
            if type(transitions_dict) is dict:
                for transition in transitions_dict["transitions"]:
                    # if transition["to"]["id"] == workflow_id and transition["name"] == tranistion_name:
                    if transition["name"] == tranistion_name:
                        return True
                return False
            else:
                self.logger.error("failed to get issue transition dict from jira")
        except Exception:
            self.logger.exception("")

    def _get_fields_schema_from_transition_by_current_issue_workflow_id(self, transitions_dict, workflow_id):
        """
        this function responsible to extract the relevant tranistion to current status of the issue (workflow)
        :param workflow_id: string - id of the current workflow (status of the issue)
        :param transitions_dict: dict of all available tranistion for issue
        """
        try:
            # workflow = issue status
            if type(transitions_dict) is dict:
                for transition in transitions_dict["transitions"]:
                    if transition["to"]["id"] == workflow_id:
                        self.fields_schema_transition = transition["fields"]
                        self.tranistion_name = transition["name"]
                        return
                self.fields_schema_transition = {}
                self.tranistion_name = ""
            else:
                self.logger.error("failed to get issue transition dict from jira")
        except Exception:
            self.logger.exception("")

    def _fetch_issue_transitions(self, issue_key):
        """
        this function responsible to fetch schema of specific issue with  all available tranistion permission
        trough rest
        """
        try:
            jira_rst_url = f'https://{self.username}:{self.password}@helpdesk.airspan.com/rest/api/2/issue/' \
                           f'{issue_key}/transitions?expand=transitions.fields'
            response = requests.get(url=jira_rst_url, timeout=240)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f'failed to get issue editable fields with normal permission {issue_key}')
                return None
        except Exception:
            self.logger.exception("")

    def _filter_duplicates_from_transition_fields_list_and_normal_fields(self):
        """
        their might be fields that appeer in regular fields schema and tranistion fields schema , we need to filter them
        from the tranistion fields schema, so the field will be updated as regular field
        """
        try:
            # remove fields that appear in transition fields and normal fields
            tranistion_fields_list = set(self.fields_schema_transition) - set(self.fields_schema_normal_permission)
            tranistion_fields_schema = {}
            for field_name in tranistion_fields_list:
                tranistion_fields_schema[field_name] = self.fields_schema_transition[field_name]
            self.fields_schema_transition = tranistion_fields_schema
        except Exception:
            self.logger.exception("")

    def validate_got_required_fields_from_user(self, data):
        """
        this method responsible to validate that we got all the required fields from user to create new issue
        based on issue schema
        """
        try:
            # collect required fields from schema
            required_fields = JiraHelper().extract_required_field_names_from_schema(
                self.fields_schema_normal_permission)
            # collect user data fields
            user_data_fields = JiraHelper().extract_user_input_field_names(data)
            req_fields_in_data_fields = all(field_name in user_data_fields for field_name in required_fields)
            none_existing_fields = list(set(required_fields) - set(user_data_fields))
            return req_fields_in_data_fields, none_existing_fields
        except Exception:
            self.logger.exception("")
            return None, None


class EditData(JiraSchema):
    def __init__(self):
        super(EditData, self).__init__()
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.transition_fields = {"add": [], "set": []}
        self.regular_fields = {"add": [], "set": []}
        self.rest_api_fields = []

        self.transition_fields_validation = {}
        self.regular_fields_validation = {}
        self.fields_not_exist_in_schema = {}
        # self.rest_api_fields_validation = {}

        self.rest_api_fields_ready_to_send = {}
        self.regular_fields_ready_to_send = {}
        self.transition_fields_ready_to_send = {}

    def sort_user_fields_by_edit_type(self, user_data):
        """
        this function responsible to sort user data by edit type: regular edit , tranistion edit & rest edit
        :param user_data: list of fields sorted by "add" and "set"
        """
        try:
            self._iterate_over_user_data_fields_by_operation_type(user_data, "add")
            self._iterate_over_user_data_fields_by_operation_type(user_data, "set")
        except Exception:
            self.logger.exception('')

    def _iterate_over_user_data_fields_by_operation_type(self, user_data, operation_type):
        """
        this function responsible to iterate over each field and insert it to relevant edit type regular/tranistion/rest
        :param user_data: list of fields sorted by "add" and "set"
        :param operation_type: string "add" and "set"
        """
        try:
            if operation_type in user_data:
                for single_field in user_data[operation_type]:
                    self._insert_user_data_field_to_transition_regular_or_rest_fields_attribute(single_field,
                                                                                                operation_type)
            else:
                self.logger.info(f'{operation_type} operation not exist in user data input -> skip it ')
        except Exception:
            self.logger.exception('')

    def _insert_user_data_field_to_transition_regular_or_rest_fields_attribute(self, user_field, operation_type):
        """
        this function responsible to insert field data to relevant edit type regular/tranistion/rest
        :param user_field: dict of field name and the value of the field
        :param operation_type: string "add" and "set"
        """
        try:
            for field_name, field_value in user_field.items():
                if self.rest_api_fields_schema and field_name in self.rest_api_fields_schema:
                    self.rest_api_fields.append({field_name: field_value})
                elif self.fields_schema_normal_permission and field_name in self.fields_schema_normal_permission:
                    self.regular_fields[operation_type].append({field_name: field_value})
                elif self.fields_schema_transition and field_name in self.fields_schema_transition:
                    self.transition_fields[operation_type].append({field_name: field_value})
                else:
                    self.fields_not_exist_in_schema[field_name] = field_value
                    self.logger.error(f'field {field_name} not exist in issue schema for current user, '
                                      f'it might be a permission issue or the field not exist in this issue type')
        except Exception:
            self.logger.exception("")
            return None

    def _preform_validation_to_user_data_by_fields_edit_type_and_operation_type(self, fields_type, operation_type):
        """
        this function responsible to preform all validation of user data
        verify that the field is in relevant operation - set / add
        verify valid values inserted to field - by schema allowed values
        if its pass both test it will insert the field_validation attribute a key with field name and boolean True
        :param fields_type: string - regular / strniastion / rest
        :param operation_type: string "add" and "set"
        """
        try:
            """
            fields_type --> rest, regular, tranistion 
            regular_fields / fields_schema_normal_permission / regular_fields_validation
            transition_fields / fields_schema_transition / transition_fields_validation 
            rest_api_fields / rest_api_fields_schema / rest_api_fields_validation
            """
            user_data_fields, fields_schema, fields_validation = self._get_attributes_by_field_type(fields_type)
            if user_data_fields and fields_schema and fields_validation is not None:
                for user_field in user_data_fields[operation_type]:
                    for field_name, field_value in user_field.items():
                        field_schema = fields_schema[field_name]
                        valid_operation = self._validate_field_data_with_operation(
                            field_value, field_schema["operations"])
                        valid_values = self._validate_field_data_with_allowed_values(
                            field_name, field_schema, field_value)
                        if valid_operation and valid_values:
                            self.logger.info(f'${field_name} pass all validation - continue next step')
                            fields_validation[field_name] = True
                        else:
                            fields_validation[field_name] = False
                            self.logger.error(f'${field_name} failed on validation - operation type is not allowed or user tried to insert illegal values to field')
                            self.logger.error(f'The value of field "{field_name}" is: {field_value}')
            else:
                self.logger.info(f'field to get attributes for {fields_type}')
        except Exception:
            self.logger.exception('')

    def _get_attributes_by_field_type(self, fields_type, ready_attribute=False):
        """
        this function responsible to return relevant attributes  based on field type to use
        :param fields_type: string - regular / strniastion / rest
        :param ready_attribute: used when we want to return only 1 attribute - ready to send by field type
        """
        try:
            if ready_attribute:
                return self._return_ready_to_send_attribute_by_type(fields_type)
            else:
                return self._return_bundle_attributes_by_type(fields_type)
        except Exception:
            self.logger.exception('')

    def _return_ready_to_send_attribute_by_type(self, fields_type):
        """
        this function responsible to return ready to send attribute  based on field type
        :param fields_type: string - regular / strniastion / rest
        :return relevant attribute
        """
        try:
            if fields_type == "regular":
                return self.regular_fields_ready_to_send
            elif fields_type == "tranistion":
                return self.transition_fields_ready_to_send
            elif fields_type == "rest":
                return self.rest_api_fields_ready_to_send
            else:
                return None
        except Exception:
            self.logger.exception('')

    def _return_bundle_attributes_by_type(self, fields_type):
        """
        this function responsible to return 3 attributs  based on field type
        :param fields_type: string - regular / strniastion / rest
        :return relevant 3 attributes
        """
        try:
            if fields_type == "regular":
                return self.regular_fields, self.fields_schema_normal_permission, self.regular_fields_validation
            elif fields_type == "tranistion":
                return self.transition_fields, self.fields_schema_transition, self.transition_fields_validation
            else:
                self.logger.error(f'unknown field type ${fields_type}')
                return None, None, None
        except Exception:
            self.logger.exception('')

    def preform_validation_to_user_data_regular_edit(self):
        """
        this function responsible to preform validation to regulat edit data
        """
        try:
            self._preform_validation_to_user_data_by_fields_edit_type_and_operation_type("regular", "add")
            self._preform_validation_to_user_data_by_fields_edit_type_and_operation_type("regular", "set")
        except Exception:
            self.logger.exception('')

    def preform_validation_to_user_data_transition_edit(self):
        """
        this function responsible to preform validation to tranistion edit data
        """
        try:
            self._preform_validation_to_user_data_by_fields_edit_type_and_operation_type("tranistion", "add")
            self._preform_validation_to_user_data_by_fields_edit_type_and_operation_type("tranistion", "set")
        except Exception:
            self.logger.exception('')

    def insert_user_data_to_ready_to_send_attribute_regular_edit(self):
        """
        this function responsible to insert user data inside schema to regular ready to send attribute
        """
        try:
            self._insert_user_data_inside_schema_to_final_ready_to_send_attribute("regular", "add")
            self._insert_user_data_inside_schema_to_final_ready_to_send_attribute("regular", "set")
        except Exception:
            self.logger.exception('')

    def insert_user_data_to_ready_to_send_attribute_transition_edit(self):
        """
        this function responsible to insert user data inside schema to tranistion ready to send attribute
        """
        try:
            self._insert_user_data_inside_schema_to_final_ready_to_send_attribute("tranistion", "add")
            self._insert_user_data_inside_schema_to_final_ready_to_send_attribute("tranistion", "set")
        except Exception:
            self.logger.exception('')

    def _insert_user_data_inside_schema_to_final_ready_to_send_attribute(self, fields_type, operation_type):
        """
        this function responsible to insert user data inside schema to relevant attribute
        param: fields_type - string regular / tranistion / rest
        param: operation_type - rest
        """
        try:
            user_data_fields, fields_schema, fields_validation = self._get_attributes_by_field_type(fields_type)
            if user_data_fields and fields_schema and fields_validation:
                for user_field in user_data_fields[operation_type]:
                    for field_name, field_value in user_field.items():
                        if field_name in fields_validation and fields_validation[field_name]:
                            field_schema = fields_schema[field_name]
                            field_data_inside_schema = self._insert_field_data_to_field_schema(
                                field_name, field_schema, operation_type, field_value)
                            if field_data_inside_schema is not None:
                                self._insert_field_to_ready_attribute(fields_type, field_name, field_data_inside_schema)
                            else:
                                self.logger.error("cant insert field data to schema")
                                self.logger.error(f"The field name is: {field_name}")
                                self.logger.error(f"The field value is: {field_value}\n")
        except Exception:
            self.logger.exception("")

    def _insert_field_to_ready_attribute(self, fields_type, field_name, field_data_inside_schema):
        """
        this function responsible to insert user data inside schema to relevant attribute
        param: field_data_inside_schema - dict
        param: fields_type - string regular / tranistion / rest
        param: field_name - string
        """
        try:
            attribute_to_insert = self._get_attributes_by_field_type(fields_type, True)
            attribute_to_insert[field_name] = field_data_inside_schema
        except Exception:
            self.logger.exception('')

    def _validate_field_data_with_operation(self, field_data, operation_list):
        """
        this function responsible to validate user preform valid operation on field add/set
        param: field_data - list, string
        param: operation_list - list from schema
        """
        try:
            if "add" in operation_list:
                # check the field data is list type
                return isinstance(field_data, list)
                # can contain multiple values
            elif "set" in operation_list:
                if isinstance(field_data, list):
                    if len(field_data) == 1:
                        return True
                    else:
                        return False
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

    def _validate_field_data_with_allowed_values(self, field_name, field_schema, field_data):
        """
        this method checks that the 'values' user try to change are valid , based on fields
         allowed values in field schema
        :param field_name:  str
        :param field_schema: dict - schema of field
        :param field_data: list of values from user
        :return: bool True/False
        """
        try:
            if "allowedValues" in field_schema:
                self.logger.debug("Checking if the values from user is valid based on allowed values in schema")
                if field_schema["schema"]["type"] in self.jiraTypesToPython["option-with-child"]:
                    return self._validation_option_with_child_allowed_values(field_schema, field_data)
                else:
                    return self._validation_normal_allowed_values_fields(field_name, field_schema, field_data)
            else:
                self.logger.debug("No allowed values found in field schema - continue next step")
                return True
        except Exception:
            self.logger.exception("")
            return None

    def _validation_normal_allowed_values_fields(self, field_name, field_schema, field_data):
        try:
            field_allowed_values_strings = JiraHelper(). \
                extract_values_in_schema_allowed_values(field_name, field_schema)
            is_strings_inside_list = JiraHelper().check_user_data_is_list_of_string(field_data)
            if is_strings_inside_list:
                not_allowed_fields = set(field_data) - set(field_allowed_values_strings)
                if len(not_allowed_fields) == 0:
                    return True
                else:
                    return False
            else:
                return False
        except Exception:
            self.logger.exception("")
            return None

    def _validation_option_with_child_allowed_values(self, field_schema, field_data):
        try:
            valid_data = JiraHelper().check_field_value_dict_contain_value_and_child(field_data)
            if valid_data:  # has value & child in and is a dict
                value_object = JiraHelper().return_value_object_if_exist_in_list(
                    field_schema["allowedValues"], "value", field_data[0]["value"])
                if value_object:  #
                    return self._validation_children_exist_in_allowed_value(
                        value_object["children"], field_data[0]["child"])
                else:
                    self.logger.error(f'value not found in values allowed dict {str(field_schema["allowedValues"])}')
                    return False
            else:
                self.logger.error(f'got invalid data from user {str(valid_data)}')
                return False
        except Exception:
            self.logger.exception("")
            return None

    def _validation_children_exist_in_allowed_value(self, child_allowed_values, child_value):
        children_exist = JiraHelper().return_value_object_if_exist_in_list(child_allowed_values, "value", child_value)
        if children_exist:
            return True
        else:
            self.logger.error(f'Child not exist in allowed values {str(child_allowed_values)}')
            return False

    def _insert_field_data_to_field_schema(self, field_name, field_schema, operation_type, new_field_data=None):
        """
        this method convert the user input (strings) to relevant jira structure that will allow
        to send it via API
        :param field_name: str
        :param field_schema: dict of field schema
        :param new_field_data: optional - used to convert user's field values to relevant structure
        :return: if field_schema type is list - list of string/dicts/number otherwise: dict/string
        """
        try:
            in_arry_schema = field_schema['schema']
            if in_arry_schema['type'] in self.jiraTypesToPython['array']:  # array type
                if hasattr(self, "issue") and operation_type == "add":
                    old_field_data = getattr(self.issue.fields, field_name)
                else:
                    old_field_data = []
                field_with_data = self. \
                    _insert_user_data_to_array_type_field(field_name, field_schema, new_field_data, old_field_data)
            elif in_arry_schema['type'] in self.jiraTypesToPython['option-with-child']:  # option with child type
                field_with_data = self._insert_user_data_as_option_with_child(field_name, field_schema, new_field_data)
            else:  # rest of the types is single values types
                field_with_data = self. \
                    _insert_user_data_as_single_value(field_name, field_schema, new_field_data)
            return field_with_data
        except Exception:
            self.logger.exception("")
            return None

    def _insert_user_data_as_option_with_child(self, field_name, field_schema, field_data):
        """
        this method check that the data is in valid structure and trigger insert used data to schema
        :param field_name: str
        :param field_data: string / list
        :return: field inside schema
        """
        try:
            # check that the user gave to us 2 values inside dict
            valid_data = JiraHelper().check_field_value_dict_contain_value_and_child(field_data)
            if valid_data:
                key_ = JiraHelper().check_field_key(field_schema["allowedValues"])
                return {key_: field_data[0]["value"], 'child': {'value': field_data[0]["child"]}}
            else:
                self.logger.error("Got wrong input format from user - should be list of dict with value & child keys")
                return False
        except Exception:
            self.logger.exception("")
            return None

    def _insert_user_data_as_single_value(self, field_name, field_schema, new_field_data):
        """
        this method check that the data is in valid structure and trigger insert used data to schema
        :param field_name: str
        :param field_schema: dict of field schema
        :param new_field_data: string / list
        :return: field inside schema
        """
        try:
            # check that the user gave to us the value inside array
            if isinstance(new_field_data, list) and len(new_field_data) == 1:
                return self._handle_single_value_field(field_name, field_schema, new_field_data)
            else:
                self.logger.error("Got wrong input format from user - should be list of values - even when it single value")
                return False
        except Exception:
            self.logger.exception("")
            return None

    def _handle_single_value_field(self, field_name, field_schema, new_field_data):
        """
        this method insert user data to field schema
        :param field_name: str
        :param field_schema: dict of field schema
        :param new_field_data: string / list
        :return: field inside schema
        """
        try:
            key_ = JiraHelper().check_field_key(field_schema["allowedValues"] if "allowedValues" in field_schema else field_name)
            if field_schema['schema']['type'] in self.jiraTypesToPython["regular"]:
                return new_field_data[0]  # string or number
            else:
                return {key_: new_field_data[0]}  # object
        except Exception:
            self.logger.exception("")
            return None

    def _insert_user_data_to_array_type_field(self, field_name, field_schema, new_field_data, old_field_data):
        """
        this method insert user data with old issue data if exist
        :param field_name: str
        :param field_schema: dict of field schema
        :param new_field_data: string / list
        :param old_field_data: string / list
        :return: array with combined fields with new and old data inside schema
        """
        try:
            # only if array there are items key
            arr = []
            in_list_schema = field_schema["schema"]
            if "items" in in_list_schema:  # validate items key exist
                if in_list_schema["items"] in self.jiraTypesToPython["regular"]:
                    # array of regular items - string/ number/ issue type - no need to manipulate it
                    arr = self._insert_user_data_to_field_as_is(new_field_data, old_field_data)
                else:
                    # rest of the options that isn't array of string / numbers / issue types is array of objects - need to manipulate it
                    field_type = JiraHelper().check_field_key(field_schema['allowedValues'] if 'allowedValues' in field_schema else field_name)
                    old_values_converted = self._handle_old_field_data(field_name, field_schema, old_field_data)
                    new_values_converted = self._convert_array_to_jira_structure(new_field_data, field_type)
                    arr = old_values_converted + new_values_converted
            else:
                pass
            return arr
        except Exception:
            self.logger.exception("")
            return None

    def _insert_user_data_to_field_as_is(self, new_field_data, old_field_data):
        """
        this method return new or old field data (no need to convert it with schema as its already converted)
        :param new_field_data: string / list
        :param old_field_data: string / list
        :return: list field data inside schema
        """
        try:
            if new_field_data and old_field_data:
                self.logger.debug("No need to convert anything, insert list of new & old fields as is")
                arr_field = new_field_data + old_field_data
            elif new_field_data:
                self.logger.debug("No need to convert anything, insert list of new fields as is")
                arr_field = new_field_data
            else:
                self.logger.debug("No need to convert anything, insert list of old fields as is")
                arr_field = old_field_data
            return arr_field
        except Exception:
            self.logger.exception("")
            return None

    def _handle_old_field_data(self, field_name, field_schema, old_field_data):
        """
        this method handle old field data - insert old data to schema if needed and return
        :param field_name: str
        :param old_field_data: string / list
        :return: list of values inside schema of old data
        """
        try:
            field_type = JiraHelper().check_field_key(field_schema['allowedValues'] if 'allowedValues' in field_schema else field_name)
            if old_field_data:
                self.logger.debug("Extract old field data")
                need_to_convert = self._check_if_old_data_already_in_structure(old_field_data)
                if need_to_convert:
                    old_field_data_extracted_to_list = self._extract_values_from_list_of_objects(
                        old_field_data, field_type)
                    converted_data = self._convert_array_to_jira_structure(old_field_data_extracted_to_list, field_type)
                    return converted_data
                else:
                    return old_field_data
            else:
                return []
        except Exception:
            self.logger.exception("")
            return None

    def _convert_array_to_jira_structure(self, fields_values_list, field_type):
        """
        this method convert each field value from user to jira structure
        :param fields_values_list: list of string - values from user
        :param field_type: string
        :return: list of values inside schema of new values
        """
        try:
            if fields_values_list:
                self.logger.debug("Convert data to allowed jira structure")
                return [{field_type: field} for field in fields_values_list]
            else:
                self.logger.debug("Field data is None or empty")
                return None
        except Exception:
            self.logger.exception("")
            return None

    def _extract_values_from_list_of_objects(self, old_data, attribute_name):
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

    def _check_if_old_data_already_in_structure(self, old_field_data):
        """
        method used to check if the field data is already converted to structure that allow to send it to api
        :param old_field_data:
        :return:
        """
        try:
            if not isinstance(old_field_data, list):
                return False
            for single_field in old_field_data:
                return not isinstance(single_field, dict)
        except Exception:
            self.logger.exception("")
            return None

    def insert_user_data_to_rest_api_ready_to_send_attribute(self):
        """
        method used to insert user data to rest api ready attribute
        """
        try:
            for user_field in self.rest_api_fields:
                for field_name, field_value in user_field.items():
                    field_schema = self.rest_api_fields_schema[field_name]
                    field_data_inside_schema = self._insert_field_data_to_rest_field_schema(
                        field_value, field_schema)
                    self.rest_api_fields_ready_to_send[field_name] = field_data_inside_schema
        except Exception:
            self.logger.exception("")
            return None

    def _insert_field_data_to_rest_field_schema(self, field_value, field_schema):
        """
        method used to insert used data to field schema
        :param field_value - list of values
        :param field_schema: - field schema
        :return: value in field schema
        """
        try:
            # array -> for multiple updates in jira (add multiple test plans for example)
            field_data_in_schema = []
            for value in field_value:
                url = self._build_rest_url(field_schema, value)
                if f'testplan/{value}/testexecution' in url and hasattr(self, 'issue'):
                    body = self._build_rest_body(field_schema["body"], self.issue.key)
                else:
                    body = self._build_rest_body(field_schema["body"], value)
                method = field_schema["method"]
                field_data_in_schema.append({"body": body, "url": url, "method": method})
            return field_data_in_schema
        except Exception:
            self.logger.exception("")
            return None

    def _build_rest_body(self, field_schema, field_value):
        """
        method used to build rest body
        :param field_value - list of values
        :param field_schema: - field schema
        :return: value in field schema
        """
        try:
            body = {}
            for key, value_schema in field_schema.items():
                if value_schema == "array":
                    body[key] = [field_value]
                elif value_schema == "string":
                    body[key] = field_value
            return body
        except Exception:
            self.logger.exception("")
            return None

    def _build_rest_url(self, field_schema, field_value):
        """
        method used to build rest url
        :param field_value - list of values
        :param field_schema: - field schema
        :return: url of the rest field
        """
        try:
            if hasattr(self, 'issue') and hasattr(self, 'jira_rst_url') and hasattr(self, 'username') and hasattr(self, 'password'):
                issue_key = self.issue.key
                url = f'{self.jira_rst_url}{field_schema["url"]}'
                for url_var in field_schema["url_variable_type"]:
                    if (
                        url_var == "issue_key"
                        or url_var != "user_value"
                        and url_var != "issue_id"
                        and url_var == "test_plan_id"
                    ):
                        url = url.replace(url_var, issue_key)
                    elif url_var == "user_value":
                        url = url.replace(url_var, field_value)
                    elif url_var == "issue_id":
                        execution_id = TestExecution().get_test_execution_id(
                            issue_key, self.username, self.password)
                        url = url.replace(url_var, str(execution_id))
                return url
        except Exception:
            self.logger.exception("")

    def insert_basic_data_to_ready_to_send_attribute(self, project, issue_type, reporter):
        """
        method used insert basic data proejct , issue type and reporter to new jira issue
        :param project - list of values
        :param issue_type: - field schema
        :param reporter: - field schema
        """
        try:
            self.regular_fields_ready_to_send["project"] = project
            self.regular_fields_ready_to_send["issuetype"] = issue_type
            self.regular_fields_ready_to_send["reporter"] = {"name": reporter}
        except Exception:
            self.logger.exception("")
            return None

    def print_failed_fields(self):
        try:
            self._iterate_over_failed_validation_fields(self.regular_fields_validation)
            self._iterate_over_failed_validation_fields(self.transition_fields_validation)
            self._iterate_over_non_existing_fields_in_schema()
        except Exception:
            self.logger.exception("")
            return None

    def _iterate_over_failed_validation_fields(self, validation_attribute):
        try:
            for field, validation in validation_attribute.items():
                if not validation:
                    self.logger.error(f"{field} failed to pass validation therefore wasn't updated in Jira")
        except Exception:
            self.logger.exception("")
            return None

    def _iterate_over_non_existing_fields_in_schema(self):
        for field, value in self.fields_not_exist_in_schema.items():
            self.logger.error(f"{field} with data {value} not exist in jira "
                              f"schema therefore wasn't updated in jira")


class JiraIssue(EditData):
    def __init__(self, username=None, password=None, jira_rst_url=None):
        super(JiraIssue, self).__init__()
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        stack = inspect.stack()

        the_class = stack[1][0].f_locals["self"].__class__.__name__
        if the_class != 'JiraActions':
            the_method = stack[1][0].f_code.co_name
            self.logger.error(f"I was called by {the_class}.{the_method}()")
            raise Exception('you cant access this class directly , you need to init the class from JiraAction class')

        self.username = username
        self.password = password
        self.jira_rst_url = jira_rst_url


class JiraActions:
    def __init__(self, username=None, password=None, app_credentials='EZlife'):
        super(JiraActions, self).__init__()
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.issues = {}
        self._jira_connection = None
        if not username or not password:
            self._username, self._password = Credentials().credentials_per_app(app_credentials)
        else:
            self._username = username
            self._password = password
        self._connect_to_jira()
        self._jira_rst_url = f'https://{self._username}:{self._password}@helpdesk.airspan.com/rest/raven/1.0/api'

    def get_issue(self, issue_id: str):
        """
        method used to fetch issue from JIRA using JIRA API
        param: issue_id - string
        """
        try:
            if issue_id:
                for i in range(0, 2):
                    if self._jira_connection:  # has jira connection
                        # self.issue = self.jira_connection.issue(issue_id)
                        issue_object = self._jira_connection.issue(issue_id)
                        self.issues[issue_id] = JiraIssue(self._username, self._password, self._jira_rst_url)
                        setattr(self.issues[issue_id], "issue", issue_object)
                        break
                    else:
                        time.sleep(3)
                        self._connect_to_jira()
            else:
                self.logger.error(f'cant get issue as its not configured, got {issue_id}')
        except Exception:
            self.logger.exception('')

    def update_issue(self, issue_id: str, data: dict):
        """
        method used update already existing issue with data from user
        :return: issue key
        """
        try:
            valid_user_data = JiraHelper().verify_data_structure_add_set(data)
            if issue_id and data and valid_user_data:
                # self.issues[issue_id] = JiraIssue(self._username, self._password, self._jira_rst_url)
                self.get_issue(issue_id)
                self.issues[issue_id].get_fields_schema_with_normal_permission(issue_id)
                self.issues[issue_id].get_fields_schema_with_transition(issue_id)
                self.issues[issue_id].sort_user_fields_by_edit_type(data)  # regular/ tranistion/ rest api
                self.issues[issue_id].preform_validation_to_user_data_regular_edit()
                self.issues[issue_id].insert_user_data_to_ready_to_send_attribute_regular_edit()
                self.issues[issue_id].preform_validation_to_user_data_transition_edit()
                self.issues[issue_id].insert_user_data_to_ready_to_send_attribute_transition_edit()
                self.issues[issue_id].insert_user_data_to_rest_api_ready_to_send_attribute()
                self._trigger_update_issue_regular_edit(issue_id)
                self._trigger_update_issue_transition_edit(issue_id)
                self._trigger_update_trough_rest(issue_id)
                self.issues[issue_id].print_failed_fields()
                self.get_issue(issue_id)  # get last updated issue
                return self.issues[issue_id].issue.key
            else:
                self.logger.error(f'user didnt send one of the following arguments: issue_id '
                                  f'or data {str(issue_id)} {str(data)}')
                return None
        except Exception:
            self.logger.exception("")
            return None

    def create_issue(self, project: str, issue_type: str, data: list):
        """
        method used to create new issue using data from user
        :return: created issue key
        """
        try:
            user_data = JiraHelper().convert_to_add_set_schema(data)
            if user_data and project and issue_type:
                tmp_issue_id = "tmp"
                self.issues[tmp_issue_id] = JiraIssue(self._username, self._password, self._jira_rst_url)
                # insert basic data to ready_to_send attribute as it required to create the issue
                self.issues[tmp_issue_id].insert_basic_data_to_ready_to_send_attribute(project, issue_type, self._username)
                self.issues[tmp_issue_id].get_schema_by_project_and_issue_type(self._jira_connection, project, issue_type)
                required_field_exist_check, none_existing_fields = \
                        self.issues[tmp_issue_id].validate_got_required_fields_from_user(user_data["set"])
                if required_field_exist_check:
                    self.issues[tmp_issue_id].sort_user_fields_by_edit_type(user_data)  # regular/ tranistion/ rest api
                    self.issues[tmp_issue_id].preform_validation_to_user_data_regular_edit()
                    self.issues[tmp_issue_id].insert_user_data_to_ready_to_send_attribute_regular_edit()
                    issue_object = self._create_issue(tmp_issue_id)
                    created_issue_key = self._set_new_attribute(issue_object)
                    self._get_sorted_fields_from_old_attribute(created_issue_key, tmp_issue_id)
                    self.issues[created_issue_key].insert_user_data_to_rest_api_ready_to_send_attribute()
                    self._trigger_update_trough_rest(created_issue_key)
                    self.issues[created_issue_key].print_failed_fields()
                    return created_issue_key

                else:
                    self.logger.error(f'Cant Create issue , missing required fields: {str(none_existing_fields)}')
                    self._remove_jira_issue_from_dict(tmp_issue_id)
                    return None
            else:
                self.logger.error(
                    f'user didnt send one of the following arguments: project, issue type or data {data} {project} {issue_type}'
                )
                return None
        except Exception:
            self.logger.exception("")
            return None

    def transition_issue(self, issue_key: str, tranistion_name: str, trigger_directly=True, transition_fields=None, comment=None):
        """
        method used preform tranistion action to existing issues
        """
        try:
            if trigger_directly:
                self.logger.info("trigger directly by user -> need to verify transition is allowed")
                self.issues[issue_key] = JiraIssue(self._username, self._password, self._jira_rst_url)
                self.get_issue(issue_key)
                allowed_tranistion = \
                    self.issues[issue_key].verify_tranistion_name_exist_in_issue_current_workflow(tranistion_name)
                if allowed_tranistion:
                    self._jira_connection.transition_issue(issue_key, transition=tranistion_name, fields=transition_fields, comment=comment)
                else:
                    self.logger.error(f'the tranistion you trying to preform is not allowed for current work flow, '
                                      f'{tranistion_name}')
            else:
                self._jira_connection.transition_issue(issue_key, transition=tranistion_name, fields=transition_fields, comment=comment)
        except Exception:
            self.logger.exception("")

    def create_issue_link(self, project: str, link_from_issue: str, link_to_issue: str):
        """
        method used to connect 2 issues between both of them
        """
        try:
            self._jira_connection.create_issue_link(project, link_from_issue, link_to_issue)
            self.logger.info(f'issue {link_from_issue} linked to {link_to_issue}')
        except Exception:
            self.logger.exception("")

    def search_by_filter(self, str_filter: str, max_results=5000, fields="*all"):
        """
        method used to return all the jira object by filtering
        """
        try:
            return self._jira_connection.search_issues(str_filter, maxResults=max_results, fields=fields)
        except Exception:
            self.logger.exception("")

    def _set_new_attribute(self, issue_object):
        """
        method used to create new issues in self.issues with new created issue key and the created object
        :param issue_object - JIRA object
        :return: created issue key
        """
        try:
            if issue_object.key:
                # init new object with new key & insert the object inside
                self.issues[issue_object.key] = JiraIssue(self._username, self._password, self._jira_rst_url)
                setattr(self.issues[issue_object.key], "issue", issue_object)
                return issue_object.key
            else:
                self.logger.error(f'failed to create the issue {str(issue_object)}')
                return issue_object
        except Exception:
            self.logger.exception("")
            return None

    def _get_sorted_fields_from_old_attribute(self, new_issue_key, tmp_issue_id):
        """
        method used to insert all sorted data from tmp issue to new created issue with new key
        :param new_issue_key - new issue key from JIRA
        :param tmp_issue_id - tmp issue key to extract data from
        """
        try:
            # tranistion is empty - as we dont know the fields in tranistion before we create it so get only rest fields
            # get sorted rest api fields from old object --> to ovid sorting again
            self.issues[new_issue_key].rest_api_fields = self.issues[tmp_issue_id].rest_api_fields
            self.issues[new_issue_key].regular_fields_validation = self.issues[tmp_issue_id].regular_fields_validation
            self.issues[new_issue_key].transition_fields_validation = \
                self.issues[tmp_issue_id].transition_fields_validation
            # delete the old attribute
            self._remove_jira_issue_from_dict(tmp_issue_id)
        except Exception:
            self.logger.exception("")

    def _trigger_update_issue_regular_edit(self, issue_id):
        """
        method used update issue using JIRA API
        param: issue_id - string
        """
        try:
            if self.issues[issue_id].regular_fields_ready_to_send:
                self.logger.info('now updating issue with regular update')
                self.issues[issue_id].issue.update(fields=self.issues[issue_id].regular_fields_ready_to_send)
            else:
                self.logger.info('no fields to update trough regular method')
        except Exception:
            self.logger.exception("")

    def _trigger_update_issue_transition_edit(self, issue_id):
        """
        method used to preform tranistion to  issue using JIRA API
        param: issue_id - string
        """
        try:
            if self.issues[issue_id].transition_fields_ready_to_send and self.issues[issue_id].tranistion_name:
                self.logger.info('now updating issue with transition')
                self.transition_issue(issue_id, self.issues[issue_id].tranistion_name,
                                      transition_fields=self.issues[issue_id].transition_fields_ready_to_send)
            else:
                self.logger.info('no fields to update trough transition method')
        except Exception:
            self.logger.exception("")


    def _retry_rest_request(self, url, body, method, field_name, count=0, retry=False):
        response = None

        if count <= 4:
            try:
                if method == "post":
                    if field_name == 'customfield_11005':
                        body.update({"addTestsToPlan": False})
                    response = requests.post(url=url, json=body, timeout=10)
                elif method == "put":
                    response = requests.put(url=url, json=body, timeout=10)
                if response:
                    self.logger.info(f'URL is {url}')
                    self.logger.info(f'Body is {body}')
                    self.logger.info(f'Response status is {response.status_code}')
                    self.logger.info(f'Response text is {response.text}')
                    self.logger.info(f'Response reason is {response.reason}')
            except ReadTimeout:
                count += 1
                if retry:
                    self._retry_rest_request(url, body, method, field_name, count)
                else:
                    return
        else:
            self.logger.info('Check below url field')
            self.logger.info(f'URL is {url}')
            self.logger.info(f'Body is {body}')

    def _trigger_update_trough_rest(self, issue_id):
        """
        method used update issue using REST API
        param: issue_id - string
        """
        try:
            for field_name, request in self.issues[issue_id].rest_api_fields_ready_to_send.items():
                self.logger.info(f'now updating {field_name} trough Rest')
                for single_request in request:
                    self._retry_rest_request(single_request["url"], single_request["body"], single_request["method"], field_name)
        except Exception:
            self.logger.exception("")

    def _remove_jira_issue_from_dict(self, issue_key):
        try:
            del self.issues[issue_key]
        except Exception:
            self.logger.exception("")

    def _create_issue(self, issue_id):
        """
        method used update create issue using JIRA API
        param: issue_id - string
        """
        try:
            self.issues[issue_id].regular_fields_ready_to_send.pop('reporter')
            return self._jira_connection.create_issue(
                fields=self.issues[issue_id].regular_fields_ready_to_send
            )
        except Exception:
            self.logger.exception("")
            return None

    def _connect_to_jira(self):
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
                jira = JIRA(basic_auth=(self._username, self._password), options={'server': server},
                            timeout=580)
                if jira:
                    self._jira_connection = jira
                    break
            except JIRAError:
                if c <= 2:
                    self.logger.exception('')
                else:
                    self.logger.exception('')
                self.logger.exception("still error")
                if c > 10:
                    time.sleep(1800)
                time.sleep(20)
            except Exception:
                self.logger.exception('')
