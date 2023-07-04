import logging

import requests
from requests import Session
from zeep import Client, Transport
from zeep.wsse.username import UsernameToken

from InfrastructureSVG.ACP_Infrastructure.NBI_REST_API import ACPRestApiException
from InfrastructureSVG.ACP_Infrastructure.helpers import get_sr_version


class ACPSoapClient:
    def __init__(self, service: str, **kwargs) -> None:
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.acp_name = kwargs.get("acp_name")
        self.service = service
        if not self.acp_name:
            raise ACPRestApiException('ACP name must be specified')
        self.acp_release = get_sr_version(self.acp_name)
        self.url = f'https://{kwargs.get("acp_name")}/ws/{self.acp_release}/{service}.asmx?WSDL'
        session = Session()
        session.verify = False
        self.transport = Transport(session=session)

    def connect(self) -> Client:
        try:
            return Client(self.url, wsse=UsernameToken('wsadmin', 'password'), transport=self.transport)
        except requests.exceptions.ConnectionError:
            self.logger.error("ACP is not reachable wait 30s and try again")
        except requests.exceptions.HTTPError:
            self.logger.error("Web services in ACP is not reachable wait 30s and try again")


if __name__ == '__main__':
    acp = ACPSoapClient(service='Software', acp_name='192.168.126.149')
    acp_client = acp.connect()
    acp_client.service.SoftwareStatusGet(Name='Cyclone_AH4200')
    print()
