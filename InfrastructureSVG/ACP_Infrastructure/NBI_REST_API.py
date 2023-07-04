import json
from InfrastructureSVG.ACP_Infrastructure.General_Actions import GeneralRESTACPActions
from InfrastructureSVG.ACP_Infrastructure.helpers import get_sr_version
from InfrastructureSVG.RestAPI_Infrastructure.RestAPI import RESTAPIActions



class ACPRestApiException(Exception):
    pass


class ACPRestApi(RESTAPIActions, GeneralRESTACPActions):
    def __init__(self, **kwargs):
        self.acp_rest_api = True

        super(ACPRestApi, self).__init__()
        super(RESTAPIActions, self).__init__()

        self.acp_name = kwargs.get("acp_name")
        if not self.acp_name:
            raise ACPRestApiException('ACP name must be specified')

        # self.acp_release = self.get_acp_release_version(self.acp_name)[4:8]
        # self.acp_release = GeneralSshACPActions().get_acp_release_version(self.acp_name)[4:8]
        self.acp_release = get_sr_version(self.acp_name)
        self.url_api = f'https://{kwargs.get("acp_name")}/api/{self.acp_release}'
        self.url_swagger = f'http://{self.acp_name}/swagger/{self.acp_release}/swagger.json'
        _token_status, self._token = self.get_acp_token(f'https://{self.acp_name}/api/authenticate',
                                                        kwargs.get('username'), kwargs.get('password'))
        self.header = {"X-Authorization": self._token, "Content-Type": "application/json-patch+json"}
        self.all_element_schemas = self.get_all_objects_schemas(self.url_swagger, self.header)

    def get_response_by_rest_api_per_method_request(self, method, acp_element_name, element_id=None, url_search=None,
                                                    use_colon=False, colon_command=None, body=None, verify_ssl=False):
        if use_colon and element_id and str(element_id).isdecimal():  # for example: /Gnb/1:reprovision
            if colon_command:
                url = f'{self.url_api}/{acp_element_name}/{element_id}:{colon_command}'
            else:
                self.logger.info("unknown command after colon")
                return None
        elif use_colon and colon_command:  # for example : gnb:getNameIdList
            url = f'{self.url_api}/{acp_element_name}:{colon_command}'
        elif element_id and str(element_id).isdecimal():
            url = f'{self.url_api}/{acp_element_name}/{element_id}'
        elif url_search:
            url = f'{self.url_api}/{acp_element_name}/?name={url_search}'
        else:
            url = f'{self.url_api}/{acp_element_name}'
        if method.upper() == 'GET':
            body = None

        elif type(body) is not str:
            body = json.dumps(body)
        if not method or not acp_element_name or method.upper() != 'GET' and not body:
            raise ACPRestApiException('"method" & "acp_element_name" or "body" must be specified')
        rest_method_response, json_object_response = self.request_by_method(method=method,
                                                                            url=url,
                                                                            header=self.header,
                                                                            verify_ssl=verify_ssl,
                                                                            body=body)
        # self.logger.info(json_object_response)
        return rest_method_response, json_object_response

    def acp_get_authenticate(self, acp_element_name, url_search=None, element_id=None, verify_ssl=False):
        if url_search:
            rest_method_response, json_object_response = \
                self.get_response_by_rest_api_per_method_request(method='get',
                                                                 acp_element_name=acp_element_name,
                                                                 url_search=url_search,
                                                                 verify_ssl=verify_ssl)
        elif element_id:
            rest_method_response, json_object_response = \
                self.get_response_by_rest_api_per_method_request(method='get',
                                                                 acp_element_name=acp_element_name,
                                                                 element_id=element_id,
                                                                 verify_ssl=verify_ssl)
        else:
            rest_method_response, json_object_response = \
                self.get_response_by_rest_api_per_method_request(method='get',
                                                                 acp_element_name=acp_element_name,
                                                                 verify_ssl=verify_ssl)

        return rest_method_response, json_object_response

    def acp_get(self, acp_element_name, url_search=None, element_id=None, verify_ssl=False):
        if url_search:
            rest_method_response, json_object_response = \
                self.get_response_by_rest_api_per_method_request(method='get',
                                                                 acp_element_name=acp_element_name,
                                                                 url_search=url_search,
                                                                 verify_ssl=verify_ssl)
        elif element_id:
            rest_method_response, json_object_response = \
                self.get_response_by_rest_api_per_method_request(method='get',
                                                                 acp_element_name=acp_element_name,
                                                                 element_id=element_id,
                                                                 verify_ssl=verify_ssl)
        else:
            rest_method_response, json_object_response = \
                self.get_response_by_rest_api_per_method_request(method='get',
                                                                 acp_element_name=acp_element_name,
                                                                 verify_ssl=verify_ssl)

        return rest_method_response, json_object_response

    def send_request_with_colon(self, method, acp_element_name, colon_command,
                                body_request=None, element_id=None, verify_ssl=False):
        try:
            self.logger.info(f'\n### {method} Request with Colon After Id started ###')
            validation_status = True  # Temporary state, waiting for David response about schema names convention
            if validation_status:
                if method and type(method) == str:
                    rest_method_response, json_object_response = \
                        self.get_response_by_rest_api_per_method_request(method=method,
                                                                         acp_element_name=acp_element_name,
                                                                         element_id=element_id,
                                                                         body=body_request if body_request is not None else {},
                                                                         use_colon=True,
                                                                         colon_command=colon_command,
                                                                         verify_ssl=verify_ssl)
                    return json_object_response if rest_method_response.status_code == 200 else rest_method_response

                else:
                    self.logger.info("Method (str) not passed to func")
        except Exception:
            self.logger.exception('')

    def acp_post_create(self, acp_element_name, body_request, verify_ssl=False):
        """ POST """
        self.logger.info('### POST (create) request started ###')
        try:
            validation_status = True  # Temporary state, waiting for David response about schema names convention
            # validation_status = ValidationACPParameters().validate_parameter_names(body_request,
            #                                                                        self.all_element_schemas.get(
            #                                                                            f'{acp_element_name}').get(
            #                                                                            'properties'))
            if validation_status:
                rest_method_response, json_object_response = \
                    self.get_response_by_rest_api_per_method_request(method='post',
                                                                     acp_element_name=acp_element_name,
                                                                     body=body_request,
                                                                     verify_ssl=verify_ssl)
                if rest_method_response.status_code == 201:
                    rest_method_response, json_object_response = self.acp_get(acp_element_name=acp_element_name,
                                                                              element_id=json_object_response["id"],
                                                                              verify_ssl=verify_ssl)
                    self.logger.info('New element was created:')
                    self.logger.info(json.dumps(json_object_response))
                else:
                    return rest_method_response
                self.logger.info('### POST (create) request ended ###')
                return rest_method_response, json_object_response
        except Exception:
            self.logger.exception('')

    def acp_post_clone(self, acp_element_name, url_search, new_name, verify_ssl=False):
        """ POST """
        self.logger.info('\n### POST (clone) request started ###')
        rest_method_response, json_object_response = self.acp_get(acp_element_name=acp_element_name,
                                                                  element_id=url_search,
                                                                  verify_ssl=verify_ssl)

        rest_method_response, json_object_response = \
            self.get_response_by_rest_api_per_method_request(method='post',
                                                             acp_element_name=acp_element_name,
                                                             # element_id=json_object_response["id"],
                                                             element_id=
                                                             self.get_profile_object_id_by_name(json_object_response),
                                                             body='{name=' + new_name + '}',
                                                             verify_ssl=verify_ssl)

        rest_method_response, json_object_response = self.acp_get(acp_element_name=acp_element_name,
                                                                  # element_id=json_object_response["id"],
                                                                  element_id=self.get_profile_object_id_by_name(
                                                                      json_object_response),
                                                                  verify_ssl=verify_ssl)

        self.logger.info(f'New element was cloned: \n{json_object_response}')
        self.logger.info('### POST (clone) request ended ###\n')
        return rest_method_response, json_object_response

    def acp_put(self, acp_element_name, url_search=None, body_request=None, verify_ssl=False):
        """ PUT """
        rest_method_response, json_object_response = self.acp_get(acp_element_name=acp_element_name,
                                                                  url_search=url_search,
                                                                  verify_ssl=verify_ssl)

        rest_method_response, json_object_response = \
            self.get_response_by_rest_api_per_method_request(method='put',
                                                             acp_element_name=acp_element_name,
                                                             body=body_request,
                                                             element_id=json_object_response["id"],
                                                             verify_ssl=verify_ssl)

        rest_method_response, json_object_response = self.acp_get(acp_element_name=acp_element_name,
                                                                  element_id=json_object_response["id"],
                                                                  verify_ssl=verify_ssl)

        return rest_method_response, json_object_response

    def acp_patch(self, acp_element_name, element_id, url_search=None, body_request=None, verify_ssl=False):
        """ PATCH - (recommended - cause it's not require all object fields)"""
        self.logger.info('### PATCH (update) request started ###')
        # get_rest_method_response, get_json_object_response = self.acp_get(acp_element_name=acp_element_name,
        #                                                                   url_search=url_search,
        #                                                                   verify_ssl=verify_ssl)

        rest_method_response, json_object_response = \
            self.get_response_by_rest_api_per_method_request(method='patch',
                                                             acp_element_name=acp_element_name,
                                                             body=body_request,
                                                             # element_id=json_object_response["id"],
                                                             element_id=element_id,
                                                             verify_ssl=verify_ssl)

        get_rest_method_response, get_json_object_response = self.acp_get(acp_element_name=acp_element_name,
                                                                          # element_id=json_object_response["id"],
                                                                          element_id=element_id,
                                                                          verify_ssl=verify_ssl)
        # return rest_method_response, json_object_response
        self.logger.info(f'Element was updated to: \n {json_object_response}')
        self.logger.info('### PATCH (update) request ended ###\n')
        return get_rest_method_response, get_json_object_response

    def acp_delete(self, acp_element_name, url_search=None, verify_ssl=False):
        """ DELETE """
        self.logger.info('DELETE request started')
        rest_method_response, json_object_response = self.acp_get(acp_element_name=acp_element_name,
                                                                  url_search=url_search,
                                                                  verify_ssl=verify_ssl)

        rest_method_response, json_object_response = \
            self.get_response_by_rest_api_per_method_request(method='delete',
                                                             acp_element_name=acp_element_name,
                                                             # element_id=json_object_response["id"],
                                                             element_id=
                                                             self.get_profile_object_id_by_name(json_object_response),
                                                             verify_ssl=verify_ssl)
        self.logger.info('### DELETE request ended ###\n')
        return rest_method_response, json_object_response
