import json
import logging
import re
from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection
from InfrastructureSVG.RestAPI_Infrastructure.RestAPI import RESTAPIActions


class GeneralRESTACPActionsException(Exception):
    pass


class GeneralSshACPActions:
    """
    This class is responsible to communicate to ACP server by SSH.
    """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_acp_release_version(self, acp_name):
        """
        This function responsible provide current active ACP release version

        The function get 1 parameter:
            - "acp_name" - ACP DNS name or IP address (string)

        The function return 1 parameters:
            - "current_acp_version" - active current ACP version (string)
        """
        ssh_obj = SSHConnection(
            ip_address=acp_name,
            username='spuser',
            password='sp_user9'
        )
        current_acp_version = ''
        try:
            ssh_obj.ssh_connection()
            commands = ['find -L /opt -name "server-manager"']
            for i in range(2):
                ssh_obj.ssh_send_commands(commands=commands, with_output=True)
                if i < 1:
                    acp_nms_server_dir_pattern = r'(?<=/opt/)(\S+)'
                    get_current_version_command = re.findall(acp_nms_server_dir_pattern, ssh_obj.full_output)[0]
                    commands = f'/opt/{get_current_version_command}/./ServerManagerConsole version'
                else:
                    acp_nms_version_pattern = '(?<=NMS Server Manager Console )(.*)'
                    current_acp_version = re.findall(acp_nms_version_pattern, ssh_obj.full_output)[0].replace('\r', '')
        except Exception:
            self.logger.exception('')
        return current_acp_version


class GeneralRESTACPActions:
    """
    This class is responsible to communicate to ACP server by REST API.
    """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        if not hasattr(self, 'acp_rest_api'):
            raise GeneralRESTACPActionsException('cannot call constructor, use the "ACPRestApi" Class')

        self.ssh_acp_username = 'spuser'
        self.ssh_acp_password = 'sp_user9'
        self.command = 'find -L /opt -name "server-manager"'

    def get_acp_token(self, url, username, password):
        """
        This function responsible provide token key for ACP REST API

        The function get 3 parameter:
            - "url" - url/uri (string)
            - "username" - username (string)
            - "password" - password (string)

        The function return 1 parameters:
            - "current_acp_version" - active current ACP version (string)
        """
        try:
            header = {'Content-Type': 'application/json'}
            body = json.dumps({"username": username, "password": password})
            return RESTAPIActions().request_by_method('POST', url=url, body=body, header=header, verify_ssl=False)

        except Exception:
            self.logger.exception('')

    # def get_acp_release_version(self, acp_name, output=None):
    #     try:
    #         client_ssh, remote_connect = SSHConnection().ssh_connection(acp_name, self.ssh_acp_username,
    #                                                                          self.ssh_acp_password)
    #         for i in range(2):
    #             client_ssh_connect, remote_connect, output = _SSHSendCommands().ssh_send_commands(
    #                 self.command, client_ssh, remote_connect, acp_name, self.ssh_acp_username, self.ssh_acp_password)
    #             if i == 0:
    #                 self.command = output.split('\r\n')[5] + '/./ServerManagerConsole version'
    #             else:
    #                 continue
    #     except Exception:
    #         self.logger.exception('')
    #     return output.split('\r\n')[1].split('NMS Server Manager Console ')[1]

    def get_all_objects_schemas(self, url_swagger, header):
        """
        This function responsible provide all schema objects (object)

        The function get 2 parameter:
            - "url_swagger" - url swagger (string)
            - "header" - header for token-key (string)

        The function return 1 parameters:
            - "all_acp_schemas" - all schema objects (string)
        """

        try:
            rest_method_response, all_acp_schemas = RESTAPIActions().request_by_method('GET', url_swagger, header,
                                                                                       verify_ssl=False)
            return all_acp_schemas.get('components').get('schemas')
        except Exception:
            self.logger.exception('')
            return None

    def get_specified_schema(self):
        # Waiting for David team to align convention names
        pass

    # def get_profile_object_id_by_name(self, acp_shema_name, url_search, verify_ssl):
    #     if hasattr(self, 'acp_get'):
    #         rest_method_response, json_object_response = self.acp_get(acp_shema_name=acp_shema_name,
    #                                                                   url_search=url_search,
    #                                                                   verify_ssl=verify_ssl)
    #         self.logger.info(f'Element_ID: {json_object_response["id"]}')
    #         return json_object_response["id"]
    def get_profile_object_id_by_name(self, json_object_response):
        """
        This function responsible provide element/profile name by ID

        The function get 1 parameter:
            - "json_object_response" - response from GET method (dict)

        The function return 1 parameters:
            - "profile_element_id" - found ID of element (int)
        """

        if type(json_object_response[0]["Id"]) is float:
            profile_element_id = int(json_object_response[0]["Id"])
        else:
            profile_element_id = json_object_response[0]["Id"]

        self.logger.info(profile_element_id)
        return profile_element_id

    @staticmethod
    def get_id_of_object_from_objects_list( object_name_to_search, objects_list):
        return next((object_.get("Id") for object_ in objects_list if object_.get("Name") == object_name_to_search), None)


class ValidationACPParameters:
    """
    This class is responsible to validate ACP parameters.
    """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def validate_parameter_names(self, add_user_data_obj, specified_element_schema):
        """
        This function responsible to validate correction of parameter names

        The function get 2 parameters:
            - "add_user_data_obj" - data body for REST method (dict)
            - "specified_element_schema" - specified schema of object (dict)

        The function return 0 parameters:
"""

        try:
            if invalid_param_list := [key_param_name for key_param_name in add_user_data_obj if key_param_name not in specified_element_schema.keys()]:
                self.logger.exception(f'Key name mismatch detected during validation -'
                                      f' expected name is "{invalid_param_list}"')
            else:
                return True
        except Exception:
            self.logger.exception('')
        return False

    def validate_mandatory_parameters(self):
        pass  # waiting for David response for supporting mandatory param indication

    @staticmethod
    def check_special_char_in_name(obj_name):
        """
       This function responsible check and replace a chars like ":", "#" in value name

       The function get 1 parameter:
           - "obj_name" - object name (string)

       The function return 1 parameters:
           - "obj_name" - found ID of element (string)
       """
        """
        Replace special chars like colon ':' and '#' to percent '%3A' and '%23'
        """
        if ":" in obj_name or "#" in obj_name:
            return obj_name.replace(':', '%3A').replace('#', '%23')
        else:
            return obj_name


class Errors:
    def __init__(self):
        pass
