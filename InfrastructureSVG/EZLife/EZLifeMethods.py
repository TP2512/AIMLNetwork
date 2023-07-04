import logging
import requests
from requests import Response
from typing import Any, Union

from InfrastructureSVG.EZLife.GlobalParameters import EZLifeGlobalParameters, GlobalClassAndFunctions


class EZLifeGet:
    def __init__(self, headers, base_url):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.headers = headers
        self.base_url = base_url

    def get_by_url(self, url: str) -> tuple[int, Union[Response, Any]]:
        resp = requests.get(url, headers=self.headers)
        return resp.status_code, resp.json() if resp.status_code == 200 else resp

    def get_setup_by_id(self, ezlife_id: Union[int, str]) -> tuple[int, Union[Response, Any]]:
        if ezlife_id:
            url = f'{self.base_url}/SetupApp/{ezlife_id}/'
        else:
            url = f'{self.base_url}/SetupApp/'
        return self.get_by_url(url)

    def get_setup_by_name(self, setup_name: str) -> tuple[int, Union[Response, Any]]:
        url = f'{self.base_url}/SetupApp/?name={setup_name}'
        self.logger.debug(url)
        return self.get_by_url(url)


class EZLifePost:
    def __init__(self, headers, base_url):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.headers = headers
        self.base_url = base_url

    def post_by_url(self, url: str, data: dict) -> tuple[int, Union[Response, Any]]:
        resp = requests.post(url, data=data, headers=self.headers)
        return resp.status_code, resp.json() if resp.status_code == 200 else resp

    def create_setup(self, data: dict) -> tuple[int, Union[Response, Any]]:
        url = f'{self.base_url}/SetupApp/'
        return self.post_by_url(url, data)

    def create_ue(self, data: dict) -> tuple[int, Union[Response, Any]]:
        url = f'{self.base_url}/UeApp/'
        return self.post_by_url(url, data)

    def create_gnb(self, data: dict) -> tuple[int, Union[Response, Any]]:
        url = f'{self.base_url}/GnodeBApp/'
        return self.post_by_url(url, data)

    def create_cucp(self, data: dict) -> tuple[int, Union[Response, Any]]:
        url = f'{self.base_url}/CUCPApp/'
        return self.post_by_url(url, data)

    def create_cuup(self, data: dict) -> tuple[int, Union[Response, Any]]:
        url = f'{self.base_url}/CUUPApp/'
        return self.post_by_url(url, data)

    def create_du(self, data: dict) -> tuple[int, Union[Response, Any]]:
        url = f'{self.base_url}/DUApp/'
        return self.post_by_url(url, data)

    def create_ru(self, data: dict) -> tuple[int, Union[Response, Any]]:
        url = f'{self.base_url}/RUApp/'
        return self.post_by_url(url, data)


class EZLifePut:
    def __init__(self, headers, base_url):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.headers = headers
        self.base_url = base_url

    def put_by_url(self, url: str, data: dict) -> tuple[int, Union[Response, Any]]:
        resp = requests.put(url, data=data, headers=self.headers)
        return resp.status_code, resp.json() if resp.status_code == 200 else resp


class EZLifeMethod:
    def __init__(self, global_parameters=EZLifeGlobalParameters(), global_class_and_functions=GlobalClassAndFunctions()):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.global_parameters = global_parameters
        self.global_class_and_functions = global_class_and_functions

        self.ezlife_get = EZLifeGet(self.global_parameters.headers, self.global_parameters.base_url)
        self.ezlife_post = EZLifePost(self.global_parameters.headers, self.global_parameters.base_url)
        self.ezlife_put = EZLifePut(self.global_parameters.headers, self.global_parameters.base_url)


if __name__ == '__main__':
    ezlife_method = EZLifeMethod()
    setup_1 = ezlife_method.ezlife_get.get_setup_by_id(ezlife_id=1)

    print()
