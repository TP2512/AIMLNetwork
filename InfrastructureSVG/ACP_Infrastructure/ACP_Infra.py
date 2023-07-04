from __future__ import annotations

import logging
from typing import Dict, Union, List, Any, Optional, Set, Tuple

import requests
import re
import json
from nested_lookup import nested_lookup, nested_update
import jsonref
import inspect


class ACPHelper:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    @staticmethod
    def return_header_based_on_token(token: str, content: bool = True) -> Dict[str, str]:
        """
        this function responsible to return header with token if exist , otherwise without token
        (for authentication for example we don't need any token)
        :param token: string
        :param content: bool
        :return: dict with headers
        """
        if not token:
            return {"Content-Type": "application/json-patch+json"}
        return (
            {
                "X-Authorization": token,
                "Content-Type": "application/json-patch+json",
            }
            if content
            else {"X-Authorization": token}
        )

    def check_for_response_from_acp(self, response: Union[requests.Response, None]) -> Union[object, str]:
        """
        This function checks for response from API, if success it converts it and returns it, otherwise returns an error message.
        :param response: requests.Response or None
        :return: Union[object, str]
        """
        try:
            if response and response.status_code in [200, 204, 201]:
                self.logger.info(f'Request {response.request.method} sent to {response.request.path_url} successfully ')
                try:
                    object_response = json.loads(response.text)
                except json.JSONDecodeError:
                    object_response = response.text
            else:
                object_response = None
                error_message = f"Error response with status code {response.status_code}: {response.text}"
                self.logger.info(error_message)
            return object_response
        except AttributeError:
            self.logger.exception('')
            return None

    def return_object_by_name_from_list(self, object_list: List[Dict[str, Any]], obj_search_name: str) -> Optional[Dict[str, Any]]:
        """
        This function iterates over all objects in the input list and searches for an object with a 'Name' key that matches obj_search_name.
        :param object_list: List[Dict[str, Any]] - a list of objects
        :param obj_search_name: str - the name to search for
        :return: Dict[str, Any] - the first object that matches the search criteria, or None if no object is found
        """
        if isinstance(object_list, list):
            names = ['name', 'nodeName', 'managedElementId', 'serverName']
            return next(
                (single_obj for single_obj in object_list if self.search_inside_object_by_key_and_key_value(names, obj_search_name, single_obj)), None)
        else:
            self.logger.error(f'{obj_search_name} object may not exist in ACP')
        return None

    @staticmethod
    def search_inside_object_by_key_and_key_value(keys_to_search: List[str], key_value: Any, object_to_search_inside: Dict) -> bool:
        """
           Searches inside a dictionary for the given key-value pair.
           :param keys_to_search: List[str] - list of keys to search for
           :param key_value: Any - the value to search for
           :param object_to_search_inside: dict - the dictionary to search inside
           :return: bool - True if the key-value pair is found, False otherwise
           """
        for i in keys_to_search:
            results = nested_lookup(key=i, document=object_to_search_inside)
            if results and results[0] == key_value:
                return True
        return False

    @staticmethod
    def return_object_name_from_url_based_on_url_len(url_split_in_list: List[str]) -> Optional[str, List[str]]:
        """
        this function takes API url as list ["api", "18.5", "gnb"] and extract object name from the url based on list
        len (for example extract "gnb")
        :param url_split_in_list: list
        :return: url_object - string - object name
        """
        if len(url_split_in_list) >= 4:
            return url_split_in_list[3]
        elif len(url_split_in_list) <= 3:
            return url_split_in_list[2]
        else:
            return url_split_in_list

    def return_general_object_url_based_on_len(self, url_list: List[str]) -> Optional[str]:
        """
        Takes a list of URLs that are part of the same object, and returns the general object URL without any object IDs.
        Example input: [["api", "18.5", "gnb" , "{id}"], ["api", "18.5", "gnb:re-provision"]]
        Example output: "api/18.5/gnb"

        :param url_list: A list of strings representing URLs.
        :return: A string representing the general object URL.
        """
        if url_list:
            single_url = url_list[0].split("/")
            if len(single_url) in {4, 5}:
                general_url = single_url[:4]
            elif len(single_url) == 3:
                general_url = single_url[:3]
            else:
                general_url = ""
            full_url = "/".join(general_url)
            if ":" in full_url:
                full_url = full_url.split(":")
                full_url = full_url[0]
            return full_url
        else:
            self.logger.error("url list is empty => cant extract general object URL")
            return None

    @staticmethod
    def convert_word_first_letter_upper_case(word: str) -> Optional[str]:
        """
        this function takes a single word - str and convert the first letter to upper case
        :param word: str
        :return:  / None
        """
        return word.title() if isinstance(word, str) else None

    def lowercase(self, obj: Union[Dict, List, Set, Tuple, str]) -> Union[Dict, List, Set, Tuple, str, None]:
        """
        Recursively makes all keys in a dictionary lowercase, as well as all strings.

        :param obj: The object to modify.
        :return: The modified object, or None if obj is not a dict, list, set, tuple, or str.
        """
        """ Make dictionary lowercase """
        if isinstance(obj, dict):
            return {k.lower(): self.lowercase(v) for k, v in obj.items()}
        elif isinstance(obj, (list, set, tuple)):
            t = type(obj)
            return t(self.lowercase(o) for o in obj)
        elif isinstance(obj, str):
            return obj.lower()
        else:
            return obj

    def find_id_of_object_based_on_object_name(self, object_: Dict, object_name: str, acp_object_name: str = None) -> Optional[int]:
        """
        this function iterate over object from ACP recursively until it find key "Name" , once found , we know that in
        same hierarchy the ID of the object exist, therefore we extract the id of the object from same hierarchy
        :param object_: dict - full acp object
        :param acp_object_name: acp_object_name
        :param object_name: str
        :return: found - int / None
        """
        acp_object_name = acp_object_name.lower() if acp_object_name else acp_object_name
        if acp_object_name == "gnbxpu":
            return object_['xpuProperties']['id']
        elif acp_object_name == "gnbxpusoftwareconfiguration":
            if len(object_) > 0:
                return object_[0]['id']
        elif acp_object_name == "gnb":
            for key, value in object_.items():
                if key == "name" and value == object_name:
                    return object_["id"]
                elif isinstance(value, dict):
                    found = self.find_id_of_object_based_on_object_name(value, object_name, acp_object_name=acp_object_name)
                    if found is not None:  # check if recursive call found it
                        return found
        else:
            for key, value in object_.items():
                if (
                        key in ["name", 'managedElementId', 'serverName']
                        and value == object_name
                ):
                    return object_["id"]
                elif isinstance(value, dict):
                    found = self.find_id_of_object_based_on_object_name(value, object_name)
                    if found is not None:  # check if recursive call found it
                        return found
            return None

    @staticmethod
    def search_for_failed_fields(dict_of_fields: Optional[bool, Dict[str, bool]]) -> bool:
        """
        this function iterate over fields validation status and try to find the failed field.
        :param dict_of_fields: dict
        :return: bool
        """
        valid_type = True
        if isinstance(dict_of_fields, dict):
            for validation_status in dict_of_fields.values():
                if not validation_status:
                    valid_type = False
        return valid_type

    @staticmethod
    def return_validation_failed_list(data: Dict[str, bool]) -> List[str]:
        """
        this function iterate over fields validation status and return list of fields that are failed to validate.
        :param data: dict
        :return: list
        """
        validation_failed = []
        if isinstance(data, dict):
            validation_failed.extend({field: bool_validation} for field, bool_validation in data.items() if not bool_validation)

        elif isinstance(data, bool):
            if not data:
                validation_failed.append(data)
        return validation_failed

    @staticmethod
    def decide_fields_is_failed_or_not_based_on_validation(type_validation_dict: Dict[int, bool], allowed_values_validation_dict: Dict[int, bool]) -> Dict[str, bool]:
        """
        this function decide if field pass validation based on 2 other validation:
        if the field pass the type validation
        if the field pass the allowed values validation
        if both of the validation is passed, the field marked as pass as well , otherwise it failed.
        :param type_validation_dict: dict
        :param allowed_values_validation_dict: dict
        :return: dict
        """
        # get all keys of the dicts (the keys should be the same)
        dicts_keys = type_validation_dict.keys() & allowed_values_validation_dict.keys()
        return {key: type_validation_dict[key] & allowed_values_validation_dict[key] for key in dicts_keys}

    @staticmethod
    def get_valid_items_from_user_data(items_validation_status: Dict, user_data_items: List):
        """
        This function extracts only valid items from user data, based on validation status.
        :param items_validation_status: dict with validation status of each item
        :param user_data_items: list of user data items
        :return: list of valid user data items
        """
        return [user_data_items[index_of_item] for index_of_item, validation_status in items_validation_status.items() if validation_status]

    @staticmethod
    def search_for_filter_by_name(parameters_list: List[dict], variable_as_filter: str) -> str:
        filter_name = ""
        return next(
            (
                single_param["name"]
                for single_param in parameters_list
                if variable_as_filter.lower() in single_param["name"]
            ),
            filter_name,
        )


class ACPGeneralSchema:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        if not hasattr(self, "_url_api"):
            raise NotImplementedError("you cant access this class directly , you need to init the class from ACPActions class")
        self.all_objects_schema = self.fetch_all_objects_schema()

    def fetch_all_objects_schema(self) -> Union[None, Dict]:
        """
        this function fetch schema of all object from ACP & convert all references to dict of objects using jsonref
        """
        if hasattr(self, '_url_api') and hasattr(self, '_acp_release') and hasattr(self, 'request_by_method'):
            url_swagger = f'{self._url_api}/swagger/{self._acp_release}/swagger.json'
            # header = ACPHelper().return_header_based_on_token(self._acp_token)
            all_objects_schema, rest_method_response = self.request_by_method('GET', url_swagger)
            # convert all references in schema to flat nested schema
            all_objects_schema_str = jsonref.dumps(all_objects_schema).lower()
            return jsonref.loads(all_objects_schema_str)

    def get_object_available_urls(self, object_name: str) -> List[str]:
        """
        this function extract from all objects schema all available urls that can be used on object
        :param object_name: str - name of the object
        :return: urls_for_object - list of urls
        """
        object_name = object_name.lower()
        urls_for_object = []
        for url_schema, methods in self.all_objects_schema['paths'].items():
            url_schema_ = url_schema.split("/")
            url_object = ACPHelper().return_object_name_from_url_based_on_url_len(url_schema_)
            if object_name in [url_object.lower(), url_object.split(":")[0].lower()]:
                urls_for_object.append(url_schema)
            elif len(urls_for_object) >= 1:  # stop iterating after iterate over all schema as we got all possible urls
                break
        return urls_for_object

    @staticmethod
    def get_object_url(urls_list: List[str], object_id: Optional[int] = None, action: Optional[str] = None) -> Optional[str]:
        """
        Get specific object URL based on ID and action parameters.

        It iterates over all available URLs for the object and searches for the matching one.
        Update/delete/patch/put actions are not part of the URL unlike re-provision, therefore they are
        hardcoded in the method. If none of the conditions are met in the method, it will return the
        general URL of the object.

        :param urls_list: List of available URLs for the object.
        :param object_id: The object ID.
        :param action: The action to perform.
        :return: The URL that should be used to perform the action.
        """
        for url_schema in urls_list:
            if "{id}" in url_schema and object_id and action:
                # '/api/18.5/gnb/{id}'
                if action in ["update", "delete", "patch"] and action not in url_schema:
                    return url_schema.replace("{id}", str(object_id))
                elif action and ':' in url_schema and action == url_schema.split(':')[1]:
                    return url_schema.replace("{id}", str(object_id))
            elif action and ':' in url_schema and action == url_schema.split(':')[1]:
                return url_schema
        # '/api/18.5/gnb'
        return ACPHelper().return_general_object_url_based_on_len(urls_list)

    def return_url_path_to_work_with(self, object_name: str, id_: int = None, action: str = None) -> str:
        """
        Return the full URL path for the specified object and optional ID and action.

        :param object_name: The name of the object to work with.
        :param id_: The ID of the object, if applicable.
        :param action: The action to perform on the object, if applicable.
        :return: The full URL path for the object and action, if applicable.
        """
        action = action.lower() if action else action
        urls_list = self.get_object_available_urls(object_name)
        object_url = self.get_object_url(urls_list, id_, action)
        if hasattr(self, '_url_api'):
            return f'{self._url_api}{object_url}'

    def get_object_schema(self, object_name: str, operation: str) -> Dict:
        """
        this is method return the specific schema for the object from all objects schema
        :param: object_name - str
        :param: operation - set/get
        :return str - dict contain object schema
        """
        object_name_upper = object_name.lower()
        sub_schema_name = f'{object_name_upper}model{operation}'
        if sub_schema_name in self.all_objects_schema['components']['schemas']:
            return self.all_objects_schema['components']['schemas'][sub_schema_name]

    def get_action_schema(self, object_name: str, action: str) -> Tuple:
        """
        this is method return the specific schema for the action on object from all available paths
        :param: object_name - str
        :param: action - str
        :return dict contain object schema
        """
        urls_list = self.get_object_available_urls(object_name)
        url_action_key = self.get_action_key_to_use_in_paths_schema(urls_list, action)
        url_methods = self.all_objects_schema['paths'][url_action_key]
        if isinstance(url_methods, dict):
            for method, schema in url_methods.items():
                if "requestbody" not in schema:
                    return method, url_action_key, None
                for type_, structure_ in schema['requestbody']['content'].items():
                    return method, url_action_key, structure_['schema']

    @staticmethod
    def get_action_key_to_use_in_paths_schema(urls_list: List[str], action: str) -> str:
        """
        this is method iterating over all available urls for object and find the relevant url based on action
        :param: urls_list - list
        :param: action - str
        :return str
        """
        for single_url in urls_list:
            url_splitted = single_url.split(":")
            if url_splitted[-1].lower() == action.lower():
                return single_url
        return ""

    def create_empty_object_with_schema(self, object_schema: Dict) -> Dict:
        """
        Recursively build an empty object based on a schema.
        :param object_schema: A dictionary representing the schema of an object.
        :return: An empty dictionary with keys based on the schema.
        """
        dict_ = {}
        for key, value in object_schema.items():
            if key == "type" and value != "object" and value != "array":
                return {}
            elif key == "items" and isinstance(value, dict) and "properties" not in value:
                found = self.create_empty_object_with_schema(value)
                if found is not None and object_schema["type"] == "array":
                    dict_ = [found]
            elif key in ["properties", "items"] and isinstance(value, dict):
                dict_to_iterate = value if key == "properties" else value["properties"]
                for field, field_schema in dict_to_iterate.items():
                    found = self.create_empty_object_with_schema(field_schema)
                    if found is not None:  # check if recursive call found it
                        dict_[field.lower()] = found
                return dict_
        return dict_


class ACPInfra(ACPGeneralSchema):
    def __init__(self, acp_name: str, use_ssl: bool = False, username: Optional[str] = None, password: Optional[str] = None) -> None:
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self._acp_name = acp_name
        self._use_ssl = use_ssl or False
        self._username = username
        self._password = password
        self._acp_token = None
        self.acp_objects = {}
        if not self._username or not self._password:
            self._username = "admin"
            self._password = "password"
        if not self._acp_name:
            raise NotImplementedError('ACP name must be specified')
        self._url_api = f'https://{self._acp_name}'
        self._acp_release = self._get_sr_version()
        if not self._acp_release:
            raise NotImplementedError('Cant get SR version from ACP')
        super(ACPInfra, self).__init__()
        self._get_acp_token()

    def _get_sr_version(self) -> Optional[str]:
        """
        this is method get the SR version of the ACP , used to fetch the schema of all objects
        """
        url = f'{self._url_api}/swagger/index.html'
        resp, rest_method_response = self.request_by_method("get", url)
        json_pattern = '(?=\\[\\{\\"url\\"\\:)(.*)(?=\\,\"deepLinking)'
        output = re.findall(json_pattern, resp)
        multiple_srs = []
        if len(output) == 1:
            json_data = json.loads(output[0])
            sr_pattern = '\\d{2}\\.\\d{1,2}'
            for sr in json_data:
                sr_name = sr["name"]
                if re.match(sr_pattern, sr_name):
                    multiple_srs.append(sr_name)
        return max(multiple_srs, default=None)

    def _get_acp_token(self) -> None:
        """
        This function responsible provide token key for ACP REST API
        """
        url = self.return_url_path_to_work_with("authenticate")
        body = {"username": self._username, "password": self._password}
        token_response, rest_method_response = self.request_by_method("post", url, body)
        self._acp_token = token_response

    def _get_object_from_acp_by_name(self, acp_object: str, object_name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        This method is used to fetch object from ACP by filter - name of the object instance.

        :param acp_object: ACP object name.
        :param object_name: Name of the object instance.
        :param kwargs: Keyword arguments.
        :return: Dictionary of the object.
        """
        filter_by_name = kwargs.get('filter_by_name')
        if (
                acp_object
                in {
                    "gnbcucp",
                    "gnbcuup",
                    "gnbdu",
                    "gnbru",
                    "gnbdiscoverednetworkfunction",
                }
                and not filter_by_name
        ):
            filter_ = self.get_filter_to_use(acp_object, "get", "managedElementId")
        else:
            filter_ = self.get_filter_to_use(acp_object, "get", "name")
        full_filter = f'?{filter_}={object_name}'
        if kwargs.get('receivedBefore'):
            full_filter += f'&{kwargs.get("receivedBefore").replace(":", "%3A")}'
        if kwargs.get('receivedAfter'):
            full_filter += f'&{kwargs.get("receivedAfter").replace(":", "%3A")}'
        url_path = self.return_url_path_to_work_with(acp_object)
        full_url = f'{url_path}{full_filter}'
        response, rest_method_response = self.request_by_method("get", full_url)
        if filtered_object := response:
            if acp_object not in ['alarm', 'event', 'gnbxpusoftwareconfiguration'] and not filter_by_name:
                return ACPHelper().return_object_by_name_from_list(filtered_object, object_name)
            else:
                return filtered_object
        self.logger.info(f'{full_url} returned empty response')
        return None

    def get_object_from_acp_by_id(self, element_name: str, element_id: int, action: Optional[str] = None) -> requests.Response:
        url_path = (
            f'{self.return_url_path_to_work_with(element_name, id_=element_id, action=action)}'
            if action
            else f'{self.return_url_path_to_work_with(element_name)}/{element_id}'
        )
        response, rest_method_response = self.request_by_method("get", url_path)
        return response

    def get_filter_to_use(self, object_name: str, http_method: str, variable_as_filter: str) -> str:
        """
    Find the name of the filter associated with the given object and HTTP method.

        :param object_name: The name of the object to search for.
        :param http_method: The HTTP method to search for (e.g. 'GET', 'POST', etc.).
        :param variable_as_filter: The name of the filter to search for.
        :return: The name of the filter associated with the object and HTTP method, or None if not found.
        """
        object_name = object_name.lower()
        filter_name = ""
        for url_schema, methods in self.all_objects_schema['paths'].items():
            url_schema_ = url_schema.split("/")
            url_object = ACPHelper().return_object_name_from_url_based_on_url_len(url_schema_)
            if object_name == url_object.lower():
                if not (method_schema := methods.get(http_method)):
                    break
                if parameters := method_schema.get("parameters"):
                    filter_name = ACPHelper().search_for_filter_by_name(parameters, variable_as_filter)
                    if filter_name:
                        return filter_name
                self.logger.error(f'filter {variable_as_filter} not found in method allowed parameters')
        return filter_name

    def _get_all_instance_of_object(self, acp_object: str) -> requests.Response:
        """
        this is method used to fetch all object instances (for example all gnbs under /api/18.5/gnb)
        :param: acp_object - str
        :return str - list of objects
        """
        url_path = self.return_url_path_to_work_with(acp_object)
        filtered_object, rest_method_response = self.request_by_method("get", url_path)
        return filtered_object

    def request_by_method(self, http_method: str, url: str, body: Optional[Dict[str, Any]] = None, content: bool = True) -> Optional[Tuple[Any, requests.Response]]:
        """
        this is method used to preform requests on the ACP
        :param: method - get/post/patch str
        :param: url - str - full url to request
        :param: body - dict - body of the request
        :return response from the ACP
        """
        try:
            header = ACPHelper().return_header_based_on_token(self._acp_token, content)
            if body and content:
                body = json.dumps(body)
            if http_method.upper() == 'GET':
                rest_method_response = requests.get(url, headers=header, verify=self._use_ssl, timeout=60)
            elif http_method.upper() == 'POST':
                if content:
                    rest_method_response = requests.post(url, data=body, headers=header, verify=self._use_ssl, timeout=60)
                else:
                    rest_method_response = requests.post(url, files=body, headers=header, verify=self._use_ssl, timeout=60)
            elif http_method.upper() == 'PUT':
                rest_method_response = requests.put(url, data=body, headers=header, verify=self._use_ssl, timeout=60)
            elif http_method.upper() == 'PATCH':
                rest_method_response = requests.patch(url, data=body, headers=header, verify=self._use_ssl, timeout=60)
            elif http_method.upper() == 'DELETE':
                rest_method_response = requests.delete(url, data=body, headers=header, verify=self._use_ssl, timeout=60)
            else:
                return None
            return ACPHelper().check_for_response_from_acp(rest_method_response), rest_method_response
        except requests.Timeout:
            self.logger.exception(f'{http_method.upper()} method timeout expired, no response from ACP')
            return None

    def delete_object(self, acp_object: str, object_name: str, validate: bool = True, object_id: int | None = None) -> None:
        """
        this is method used to preform delete object from acp
        :param: acp_object - str
        :param: object_name - str
        """
        if not validate:
            acp_object_info = self.get_object(acp_object, object_name)
            if not object_id:
                object_id = ACPHelper().find_id_of_object_based_on_object_name(
                    acp_object_info, object_name, acp_object)
            if object_id:
                url_path = self.return_url_path_to_work_with(acp_object, id_=int(object_id), action="delete")
                self.request_by_method("delete", url_path)
        else:
            full_object = self._get_object_from_acp_by_name(acp_object.lower(), object_name)
            if isinstance(full_object, dict):
                url = self.return_url_path_to_work_with(acp_object, full_object["Id"], "delete")
                response, rest_method_response = self.request_by_method("delete", url)
                if response == '':
                    self.logger.info(f'{object_name} deleted from {acp_object} successfully')
                else:
                    self.logger.info(f'failed to delete {object_name} from {acp_object} \n got response: {str(response)}')

    def get_object(self, acp_object: str, object_name: str = None, **kwargs) -> Optional[Optional[Dict[str, Any]], requests.Response]:
        """
        this is method used to fetch objects from acp
        :param: acp_object - str
        :param: object_name - str
        """
        if not object_name:
            return self._get_all_instance_of_object(acp_object.lower())
        if full_object := self._get_object_from_acp_by_name(acp_object.lower(), object_name, **kwargs):
            return full_object
        if acp_object not in ['alarm']:
            self.logger.error(f'{object_name} not exist in {acp_object}')
        return None

    def update_object(self, acp_object_name: str, object_name: str, user_data: Dict[str, Any], path_to_fields: Optional[bool] = None, validate: bool = True) -> Optional[Dict[str, Any]]:
        """
        This method is used to perform an update object in ACP.
        First we fetch the object and then perform all the changes.
        :param acp_object_name: str - ACP object name.
        :param object_name: str - object name.
        :param user_data: dict - fields and values to update.
        :param path_to_fields: bool - if True, the fields will be included in the request URL path (optional).
        :param validate: bool - if True, the fields will be validated against the ACP schema (optional).
        :return: dict - the updated object, or None if an error occurred.
        """
        if not validate:
            acp_object = self.get_object(acp_object_name, object_name)
            if object_id := ACPHelper().find_id_of_object_based_on_object_name(
                    acp_object, object_name, acp_object_name
            ):
                url_path = self.return_url_path_to_work_with(acp_object_name, id_=object_id, action="patch")
                return self.request_by_method("patch", url_path, user_data)
        elif acp_object_name and object_name and user_data:
            self.prepare_fields(
                acp_object_name, object_name, user_data, path_to_fields
            )

        else:
            self.logger.error(
                f'Not all variables passed - acp_object_name - {acp_object_name} or object_name - {object_name} or user_data - {user_data}'
            )

    def update_object_id(self, acp_object_name: str, object_id: Optional[int, str], user_data: dict, path_to_fields=None, validate=True) -> Optional[Any, requests.Response]:
        """
        this is method used to preform update object in ACP, first we fetch the object and then preform all the changes
        :param: acp_object_name - str
        :param: object_id - str
        :param: user_data - dict of fields and values
        """
        if not validate:
            url_path = self.return_url_path_to_work_with(acp_object_name, id_=object_id, action="patch")
            return self.request_by_method("patch", url_path, user_data)
        elif acp_object_name and object_id and user_data:
            self.prepare_fields(
                acp_object_name, object_id, user_data, path_to_fields
            )

        else:
            self.logger.error(
                f'Not all variables passed - acp_object_name - {acp_object_name} or object_name - {object_id} or user_data - {user_data}'
            )

    def prepare_fields(self, acp_object_name: str, object_name: str, user_data: Dict, path_to_fields: bool) -> None:
        acp_object = self.get_object(acp_object_name, object_name)
        object_schema = self.get_object_schema(acp_object_name, "set")
        self.acp_objects[f'{acp_object_name}_tmp'] = ACPObject(acp_object=acp_object, object_schema=object_schema)
        self.acp_objects[f'{acp_object_name}_tmp'].validate_user_data(user_data)
        self.acp_objects[f'{acp_object_name}_tmp'].insert_user_data_to_schema(path_to_fields=path_to_fields)
        if object_id := ACPHelper().find_id_of_object_based_on_object_name(
                acp_object, object_name, acp_object_name
        ):
            url_path = self.return_url_path_to_work_with(acp_object_name, id_=object_id, action="patch")
            self.request_by_method("patch", url_path, self.acp_objects[f'{acp_object_name}_tmp'].acp_object)
        else:
            self.logger.error(f'Cant get Id of object {acp_object_name}')
        self.acp_objects[f'{acp_object_name}_tmp'].print_all_validation_errors()
        del self.acp_objects[f'{acp_object_name}_tmp']

    def create_object(self, acp_object_name: str, data: Dict[str, Any], content: bool, validate_fields: bool) -> None:
        """
        this is method used to create new object in ACP, using data provided from user
        its validation data, and convert to relevant structure
        :param: acp_object_name - str
        :param: data - dict
        """
        if acp_object_name and data and not data.get('File'):
            if validate_fields:
                self.create_object_with_field_validation(acp_object_name, data, content)
            else:
                url_path = self.return_url_path_to_work_with(acp_object_name)
                return self.request_by_method("post", url_path, data, content)
        elif data.get('File'):
            url_path = self.return_url_path_to_work_with(acp_object_name)
            return self.request_by_method("post", url_path, data, content)

    def create_object_with_field_validation(self, acp_object_name: str, data: Dict[str, Any], content: bool) -> None:
        object_schema = self.get_object_schema(acp_object_name, "set")
        empty_acp_object = self.create_empty_object_with_schema(object_schema)
        self.acp_objects[f'{acp_object_name}_tmp'] = ACPObject(
            acp_object=empty_acp_object, object_schema=object_schema)
        # need to validate got required fields based on manual schema
        self.acp_objects[f'{acp_object_name}_tmp'].validate_user_data(data)
        # clean list of objects that are failed to validate (inside array objects)
        self.acp_objects[f'{acp_object_name}_tmp'].insert_user_data_to_schema()
        # remove empty keys from object
        self.acp_objects[f'{acp_object_name}_tmp'].remove_empty_attributes_from_object()

        # send post request
        url_path = self.return_url_path_to_work_with(acp_object_name)
        self.request_by_method("post", url_path, self.acp_objects[f'{acp_object_name}_tmp'].acp_object, content)
        self.acp_objects[f'{acp_object_name}_tmp'].print_all_validation_errors()


    def prepare_data(self, acp_object_name: str, object_name: str, object_schema, data: Dict[str, Any], action: str, skip_data_validation: bool = False) -> tuple[int | None | str, dict[str, Any] | None | Any] | None:
        if acp_object_name and action and object_name and object_schema and acp_object_name not in {'gnbCell'}:  # "action_on_instance_with_data - associateNetworkFunction "
            acp_object = self.get_object(acp_object_name, object_name)
            object_id = ACPHelper().find_id_of_object_based_on_object_name(acp_object, object_name, acp_object_name)
            req_body = data if skip_data_validation \
                    else self._check_and_manipulate_user_data(data, acp_object_name, object_schema)
        elif skip_data_validation and acp_object_name in {'gnbCell', 'GnbUeTrace'}:
            object_id = object_name
            req_body = data if action and action == 'updateFromNode' else None
        elif acp_object_name and action and object_name:  # "action_on_instance_without_data - re-provision" ---> tested
            acp_object = self.get_object(acp_object_name, object_name)
            object_id = ACPHelper().find_id_of_object_based_on_object_name(acp_object, object_name, acp_object_name)
            req_body = None
        else:
            self.logger.error(
                f'didnt get one of the parameters: acp_object_name ({acp_object_name}) / action ({action}) / object_name ({object_name}'
            )

            return None
        return object_id, req_body

    def action_on_object(
            self,
            acp_object_name: str,
            action: str,
            object_name: Optional[str] = None,
            data: Optional[Union[Dict, List]] = None,
            skip_data_validation: Optional[bool] = None
    ) -> Optional[requests.Response, None]:
        """
        this is method used to preform action objects and instances in ACP
        :param: acp_object_name - str
        :param: action - str
        :param: object_name - str
        :param: data - dict / list (if preform action on multiple objects)
        :return: dict / bool
        """
        method, url_structure_to_use, object_schema = self.get_action_schema(acp_object_name, action)
        object_id = None
        if "{id}" in url_structure_to_use:
            object_id, req_body = self.prepare_data(acp_object_name, object_name, object_schema, data, action, skip_data_validation)  # action on instance
            url_path = self.return_url_path_to_work_with(acp_object_name, id_=object_id, action=action)
            response, rest_method_response = self.request_by_method(method, url_path, req_body)
            return response

        if acp_object_name and action and object_schema:  # "action_on_object_with_data - reprovisionMulti"
            object_id = None
            req_body = data if skip_data_validation \
                else self._check_and_manipulate_user_data(data, acp_object_name, object_schema)
        elif acp_object_name and action:  # "action_on_object_without_data - getNamesList" ---> tested
            object_id = req_body = None
        else:
            self.logger.error(f'didnt get one of the parameters: acp_object_name ({acp_object_name}) / action ({action})')
            return None
        if object_schema and not req_body:
            return None
        url_path = self.return_url_path_to_work_with(acp_object_name, id_=object_id, action=action)
        response, rest_method_response = self.request_by_method(method, url_path, req_body)
        return response

    def _check_and_manipulate_user_data(self, user_data: Union[dict, list], acp_object_name: str, object_schema: Dict[str, Any]):
        """
        this is method used validate and insert user data when preform action on object/ instance
        :param: user_data - dict / list
        :param: acp_object_name - str
        :param: object_schema - str
        :return: dict
        """
        if not user_data:
            self.logger.error("Based on schema, data is expected but nothing was received.")
            return None
        user_data_lower_case = ACPHelper().lowercase(user_data)
        dummy_action_object = self.create_empty_object_with_schema(object_schema)
        # convert dummy to object if the return value is list without any keys --> (like reprovisionmulti)
        self.acp_objects[f'{acp_object_name}_action'] = ACPObject()
        self.acp_objects[f'{acp_object_name}_action'].acp_object = {"array_action": dummy_action_object} \
            if isinstance(dummy_action_object, list) \
            else dummy_action_object
        self.acp_objects[f'{acp_object_name}_action'].object_schema = {"array_action": object_schema} if \
            self.acp_objects[f'{acp_object_name}_action'].acp_types_to_python[object_schema["type"]] is list \
            else object_schema
        user_data_lower_case = {"array_action": user_data_lower_case} \
            if isinstance(user_data_lower_case, list) else user_data_lower_case
        # self.acp_objects[f'{acp_object_name}_action'] = ACPObject(acp_object=dummy_action_object,
        #                                                          object_schema=object_schema)
        self.acp_objects[f'{acp_object_name}_action'].validate_user_data(user_data_lower_case)
        self.acp_objects[f'{acp_object_name}_action'].insert_user_data_to_schema()
        self.acp_objects[f'{acp_object_name}_action'].remove_empty_attributes_from_object()

        req_body = self.acp_objects[f'{acp_object_name}_action'].acp_object["array_action"] \
            if "array_action" in self.acp_objects[f'{acp_object_name}_action'].acp_object \
            else self.acp_objects[f'{acp_object_name}_action'].acp_object
        self.acp_objects[f'{acp_object_name}_action'].print_all_validation_errors()
        return req_body

    def convert_list_of_names_to_ids(self, acp_object_name: str, list_of_names: List[str]) -> List[int]:
        """
        this is method convert list of object names to their ids in ACP
        :param: acp_object_name - str
        :param: list_of_names - list
        """
        ids = []
        for single_name in list_of_names:
            acp_object = self.get_object(acp_object_name, single_name)
            if object_id := ACPHelper().find_id_of_object_based_on_object_name(acp_object, single_name, acp_object_name):
                ids.append(object_id)
        return ids


class ACPObjectSchema:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        if not hasattr(self, "acp_object"):
            raise NotImplementedError("you cant access this class directly , you need to init the class from ACPActions class")
        self.object_schema = kwargs.get("object_schema")
        self.acp_types_to_python = {
            "number": float,
            "integer": int,
            "string": str,
            "boolean": bool,
            "object": dict,
            "array": list,
        }


class ACPEditData(ACPObjectSchema):
    def __init__(self, **kwargs):
        super(ACPEditData, self).__init__(**kwargs)
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        if not hasattr(self, "acp_object"):
            raise NotImplementedError("you cant access this class directly , you need to init the class from ACPActions class")

        self.field_validation = {}
        self.fields_not_exist_in_schema = {}

    def validate_user_data(self, user_data: Dict[str, Any]):
        """
        this is method iterate over user fields and validate it
        once it check all validation it will insert to field_validation attribute the result - True / False
        if the user field not exist in schema it will insert the field name and its value to fields_not_exist_in_schema
        attribute
        :param: user_data - dict of field names and their values
        """
        if isinstance(user_data, dict):
            setattr(self, "user_data", user_data)
            if hasattr(self, 'user_data'):
                for field_name, field_value in self.user_data.items():
                    if field_schema := self.get_field_from_object(field_name, self.object_schema):
                        # add here field required validation
                        field_value_validation = self.validate_field_data(field_schema, field_value)
                        self.field_validation[field_name] = field_value_validation
                    else:
                        self.fields_not_exist_in_schema[field_name] = field_value
        else:
            self.logger.error(f'user data should be dict type - {user_data}')

    def get_field_from_object(self, field_name: str, nested_object: Dict[str, Any], insert_data: bool = False) -> Any:
        """
        this is method extract field value from nested object using nested lookup library
        :param: field_name - str
        :param: nested_object - nested dict
        :return field value if found
        """
        nested_object_lower_case = ACPHelper().lowercase(nested_object)
        field_name_lower = field_name.lower()
        # wild & with_keys enabled used to find objects with keys that are similar to keys in nested object but
        # not identical for example if user will give us data: ipaddress , and schema will contain ipAddress
        # it will find it and return
        # field_value = nested_lookup(key=field_name_lower, document=nested_object_lower_case, wild=True, with_keys=True)
        field_value = nested_lookup(key=field_name_lower, document=nested_object_lower_case, with_keys=True)
        if len(field_value) == 1:
            for key_found, value in field_value.items():
                return (key_found, value[0]) if insert_data else value[0]
        elif len(field_value) > 1:
            self.logger.error(f'there is more then one field with name {field_name}')
            return None
        else:
            self.logger.error(f'{field_name} field not exist in schema')
            return None

    def validate_field_data(self, field_schema: Dict[str, Any], field_value: Any) -> Dict[str, bool] | bool | None | Any:
        """
        this is method validate used data based on 2 aspects:
        - validate fields that user try to update exist in schema
        - validate the values of the fields is in the relevant type
        :param: field_schema - str
        :param: field_value - int/float/str
        :return boolean True/False
        """
        if isinstance(field_schema, dict):
            valid_type = self.validate_field_type(field_schema["type"], field_value)
            # if the type is valid and is list -> need to check inside list structure
            if valid_type and self.acp_types_to_python[field_schema["type"]] is list:
                validation_objects = self.validate_inside_array_type(field_schema, field_value)
                validation_allowed_values_objects = self.validate_inside_array_allowed_values(
                    field_schema, field_value)
                return ACPHelper().decide_fields_is_failed_or_not_based_on_validation(
                    validation_objects, validation_allowed_values_objects)
            elif valid_type:  # if the object is not list type and still valid
                allowed_value = self.validate_field_allowed_values(field_schema, field_value)
                return valid_type and allowed_value
            else:
                return False
        else:
            return False

    def validate_field_type(self, field_type: str, field_value: Any) -> bool:
        """
        this is method validate field value based on its type (int, float, str, dict , list using the schema
        :param: field_type - str represent type of the value (int, float, str, dict)
        :param: field_value
        :return boolean True/False
        """
        python_type = self.acp_types_to_python[field_type]
        if isinstance(field_value, python_type):
            return True
        return python_type == float and isinstance(float(field_value), python_type)

    def validate_inside_array_type(self, field_schema: Dict[str, Any], field_value: List[Any]) -> Dict[int, bool]:
        validation_failed = {}
        # its list of objects if objects_in_list_schema exist
        array_items = field_schema["items"]
        for index, single_ in enumerate(field_value):
            if self.acp_types_to_python[array_items["type"]] is dict:
                dict_of_fields_validation = self.validate_array_object_type(array_items, single_)
                valid_type = ACPHelper().search_for_failed_fields(dict_of_fields_validation)
            else:
                valid_type = self.validate_field_type(array_items["type"], single_)
            # add result of validation to dict by index of the field value
            validation_failed[index] = valid_type
        return validation_failed

    def validate_inside_array_allowed_values(self, field_schema: Dict[str, Any], field_value: Any) -> Dict[int, bool]:
        validation_failed = {}
        array_items = field_schema["items"]
        for index, single_ in enumerate(field_value):
            value_type = array_items["type"]
            if self.acp_types_to_python[value_type] == dict:
                validation_result = self.validate_array_objects_allowed_value(array_items, single_)
            else:
                validation_result = self.validate_field_allowed_values(field_schema, field_value)
            validation_failed[index] = ACPHelper().search_for_failed_fields(validation_result)
        return validation_failed

    def validate_array_objects_allowed_value(self, array_attributes_schema: Dict, array_single_object_value: Dict) -> bool | dict[Any, dict]:
        dict_ = {}
        for schema_key, schema_value in array_attributes_schema.items():
            if schema_key == "type" and schema_value != "object":
                return self.validate_field_allowed_values(array_attributes_schema, array_single_object_value)
            elif schema_key == "properties" and isinstance(schema_value, dict):
                for properties_key, properties_value in schema_value.items():
                    if properties_key in array_single_object_value:
                        valid = self.validate_array_objects_allowed_value(
                            properties_value, array_single_object_value[properties_key])
                        if valid is not None:  # check if recursive call found it
                            dict_[properties_key] = valid
                    else:
                        # key in schema not exist in user input object -> set key as false
                        # dict_[properties_key] = False
                        self.logger.error(f'field {properties_key} not exist in user data but exist in schema'
                                          f' - it might be required')
                return dict_
        return dict_

    def validate_array_object_type(
            self,
            array_attributes_schema: Dict[str, Any],
            array_single_object_value: Dict[str, Any]) -> Optional[bool, Dict[str, Optional[bool]]]:

        dict_ = {}
        for schema_key, schema_value in array_attributes_schema.items():
            if schema_key == "type" and schema_value != "object":
                return self.validate_field_type(schema_value, array_single_object_value)
            elif schema_key == "properties" and isinstance(schema_value, dict):
                for properties_key, properties_value in schema_value.items():
                    if properties_key in array_single_object_value:
                        valid = self.validate_array_object_type(
                            properties_value, array_single_object_value[properties_key])
                        if valid is not None:  # check if recursive call found it
                            dict_[properties_key] = valid
                    else:
                        # key in schema not exist in input object -> set key as false
                        # dict_[properties_key] = False
                        self.logger.error(f'field {properties_key} not exist in user data but exist in schema'
                                          f' - it might be required')
                return dict_
        return dict_

    @staticmethod
    def validate_field_allowed_values(field_schema: Dict[str, Any], field_value: Any) -> bool:
        """
        this is method validate field value is legal based on allowed values in schema
        :param: field_schema - dict
        :param: field_value - data
        :return boolean True/False
        """
        return (
                "enum" in field_schema
                and field_value in field_schema["enum"]
                or "enum" not in field_schema
        )

    def insert_user_data_to_schema(self, update: bool = False, path_to_fields: Optional[str] = None) -> None:
        """
        this is method iterate over all user data fields that passed the validation and insert the value to
        relevant schema, its update the acp_object attribute each iteration
        """
        if not hasattr(self, 'user_data') or not isinstance(getattr(self, 'user_data'), dict):
            return
        for field_name, field_value in getattr(self, 'user_data').items():
            if field_name in self.field_validation and self.field_validation[field_name]:
                field_name_schema, field_schema = self.get_field_from_object(field_name, self.object_schema, insert_data=True)
                if isinstance(self.field_validation[field_name], dict):
                    # field that contain sub items inside
                    # (list of items - the dict represent index of the item in user data and the
                    # validation status)
                    # extract only valid items from user data:
                    field_value_inside_schema = ACPHelper().get_valid_items_from_user_data(
                        self.field_validation[field_name], field_value)
                else:
                    # regular fields
                    field_value_inside_schema = self.insert_value_to_schema_based_on_type(
                        field_schema["type"], field_name, field_value)
                # convert field name to upper case - only in update state
                field_name_upper = ACPHelper().convert_word_first_letter_upper_case(field_name_schema) if \
                    update else field_name_schema
                # insert data to object
                if path_to_fields:  # when we have 2 identical objects need to decide where to update the fields
                    eval(f"self.acp_object{path_to_fields}")[field_name] = field_value_inside_schema
                else:
                    self.acp_object = nested_update(
                        self.acp_object, key=field_name_upper, value=field_value_inside_schema)

    def clean_empty(self, d: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any]]:
        if isinstance(d, dict):
            return {
                k: v
                for k, v in ((k, self.clean_empty(v)) for k, v in d.items())
                if v
            }
        return [v for v in map(self.clean_empty, d) if v] if isinstance(d, list) else d

    def remove_empty_attributes_from_object(self):
        if hasattr(self, 'acp_object'):
            self.acp_object = self.clean_empty(self.acp_object)
        # for key in empty_keys:
        #     nested_delete(self.acp_object, key, in_place=True)

    def insert_value_to_schema_based_on_type(self, schema_type: str, field_name: str, value: Any) -> Any:
        """
        this is method insert the user value to relevant structure based on schema
        :param: schema_type - str represent type - int / float etc
        :param: field_name - str
        :param: value
        return value inside schema
        """
        field_python_type = self.acp_types_to_python[schema_type]
        #  leave AS IS as we already check that type is valid
        if field_python_type in [int, float, str, bool, list]:
            return value
        elif field_python_type == dict:
            return {field_name: value}
        else:
            return ""

    def print_all_validation_errors(self) -> None:
        """
        this method print all the errors that occur during the action process (update/ create)
        """
        self.print_fields_failed_validation()
        self.print_fields_not_exist_in_schema()

    def print_fields_failed_validation(self) -> None:
        """
        this method print all fields that is failed on validation state
        """
        for field, pass_validation in self.field_validation.items():
            if not pass_validation and hasattr(self, 'user_data'):
                self.logger.error(f'field - {field} - {self.user_data[field]} validation failed')

    def print_fields_not_exist_in_schema(self) -> None:
        """
        this method print all fields that is not exist in object schema
        """
        for field, value in self.fields_not_exist_in_schema.items():
            self.logger.error(f"field {field} - {value} not exist in object schema - therefore wasn't updated")


class ACPObject(ACPEditData):

    def __init__(self, **kwargs):
        self.acp_object = kwargs.get("acp_object")
        super(ACPObject, self).__init__(**kwargs)
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__.__name__
        if the_class != 'ACPInfra':
            the_method = stack[1][0].f_code.co_name
            self.logger.error(f"I was called by {the_class}.{the_method}()")
            raise NotImplementedError('you cant access this class directly , you need to init the class from ACPActions class')
