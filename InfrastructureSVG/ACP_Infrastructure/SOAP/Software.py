import logging

from zeep.xsd import ComplexType

from InfrastructureSVG.ACP_Infrastructure.SOAP.ACP_Client import ACPSoapClient


class Software:
    def __init__(self, acp_name: str):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.client = ACPSoapClient(service='Software', acp_name=acp_name).connect()

    def get_node_software_status(self, node: str) -> ComplexType:
        return self.client.service.SoftwareStatusGet(NodeName=node)

    def sw_download_or_activate(self, node: str, image: str, action: str) -> ComplexType:
        return self.client.service.SoftwareConfigSet(NodeName=node, SoftwareDetails={'Request': action, 'SoftwareImage': image})
