import logging
from typing import Dict

from zeep.xsd import ComplexType

from InfrastructureSVG.ACP_Infrastructure.SOAP.ACP_Client import ACPSoapClient


class EnbState:
    def __init__(self, acp_name):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.client = ACPSoapClient(service='Lte', acp_name=acp_name).connect()

    def get_node_state(self, node: str) -> ComplexType:
        return self.client.service.EnbStateGet(NodeName=node)

    def set_node_state(self, node: str, node_state: str, cells_states: Dict[int, str]) -> ComplexType:
        cells = [
            {'CellNumber': cell, 'CellState': cell_state}
            for cell, cell_state in cells_states.items()
        ]
        return self.client.service.EnbStateSet(NodeName=node, EnbState=node_state, CellState=cells)

    def pnp_config_convert_from_node(self, node: str) -> ComplexType:
        return self.client.service.PnpConfigConvertFromNode(NodeName=node)
