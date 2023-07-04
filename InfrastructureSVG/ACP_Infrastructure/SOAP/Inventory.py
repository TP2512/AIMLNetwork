import logging
from zeep.xsd import ComplexType
from InfrastructureSVG.ACP_Infrastructure.SOAP.ACP_Client import ACPSoapClient


class Inventory:
    def __init__(self, acp_name: str):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.client = ACPSoapClient(service='Inventory', acp_name=acp_name).connect()

    def node_info_status_get(self, node: str) -> ComplexType:
        return self.client.service.NodeInfoGet(NodeName=node)

    def node_reprovision(self, node: str) -> ComplexType:
        return self.client.service.NodeReprovision(NodeName=node)

    def node_provision_status_get(self, node: str) -> ComplexType:
        return self.client.service.NodeProvisioningStatusGet(NodeName=node)

    def node_reset(self, node: str) -> ComplexType:
        return self.client.service.NodeReset(NodeName=node)

    def node_reset_cold(self, node: str) -> ComplexType:
        return self.client.service.NodeResetCold(NodeName=node)

    def node_reset_forced(self, node: str) -> ComplexType:
        return self.client.service.NodeResetForced(NodeName=node)

    def node_reset_forced_cold(self, node: str) -> ComplexType:
        return self.client.service.NodeResetForcedCold(NodeName=node)


if __name__ == '__main__':
    inventory = Inventory(acp_name='172.20.63.212')
    status = inventory.node_reprovision(node='ED9A850163B8')
    print()
