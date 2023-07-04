import logging
import requests
import json


class RESTAPIActions:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def check_status_code(self, url, res):
        if res.status_code == 200:
            self.logger.info(f'resp.status_code == 200 for {url} => OK')
        elif res.status_code == 201:
            self.logger.info(f'resp.status_code == 201 for {url} => OK')
        elif res.status_code == 204:
            self.logger.info(f'resp.status_code == 204 for {url} => OK')
        else:
            self.logger.exception(f'Actual resp.status_code is "{res.status_code}", "{res.text}"'
                                  f'\nfor url: {url} => error')

    def request_by_method(self, method, url, header, verify_ssl=None, body=None):
        try:
            if method.upper() == 'GET':
                rest_method_response = requests.get(url, headers=header, verify=verify_ssl)
            elif method.upper() == 'POST':
                rest_method_response = requests.post(url, data=body, headers=header, verify=verify_ssl)
            elif method.upper() == 'PUT':
                rest_method_response = requests.put(url, data=body, headers=header, verify=verify_ssl)
            elif method.upper() == 'PATCH':
                rest_method_response = requests.patch(url, data=body, headers=header, verify=verify_ssl)
            elif method.upper() == 'DELETE':
                rest_method_response = requests.delete(url, data=body, headers=header, verify=verify_ssl)
            else:
                return None

            self.check_status_code(url, rest_method_response)
            try:
                object_response = json.loads(rest_method_response.text)
            except Exception:
                object_response = rest_method_response.text
        except Exception:
            rest_method_response = None
            object_response = None
            self.logger.exception('')

        return rest_method_response, object_response


class GetRESTAPI(RESTAPIActions):
    def __init__(self):
        self.logger = \
            logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.'
                              + self.__class__.__name__)

        super(GetRESTAPI, self).__init__()

    def get_response_by_url(self, url, header, verify_ssl=None):
        try:
            res_status = requests.get(url, headers=header, verify=verify_ssl)
            res_object = json.loads(res_status.text)
            self.check_status_code(url, res_status)
        except Exception:
            res_status = None
            res_object = None
            self.logger.exception('')
        return res_status, res_object


class PostRESTAPI(RESTAPIActions):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(PostRESTAPI, self).__init__()

    def post_request_by_url(self, url, body, header, verify_ssl=None):
        try:
            res = requests.post(url, data=body, headers=header, verify=verify_ssl)
            res_object = json.loads(res.text)
            self.check_status_code(url, res)
        except Exception:
            res = None
            res_object = None
            self.logger.exception('')
        return res, res_object


class PutRESTAPI(RESTAPIActions):
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(RESTAPIActions, self).__init__()
