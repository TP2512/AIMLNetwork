import logging

from zeep.xsd import ComplexType

from InfrastructureSVG.ACP_Infrastructure.SOAP.ACP_Client import ACPSoapClient


class Statistics:
    def __init__(self, acp_name: str):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.client = ACPSoapClient(service='Statistics', acp_name=acp_name).connect()

    def get_handover_kpi_by_time_range(self, node: str, start_time: str, end_time: str) -> ComplexType:
        return self.client.service.HandoverRawGet(NodeName=node, DateStart=start_time, DateEnd=end_time)


if __name__ == "__main__":
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging

    logger = ProjectsLogging(project_name='EZLifeTest').project_logging()
    stat = Statistics(acp_name='192.168.126.149')
    # state = uploader.get_node_software_status(node='Cyclone_AV1500T', start_time='2023-05-03T14:50:00', end_time='2023-05-03T14:55:00')
    kpi_result = stat.get_handover_kpi_by_time_range(node='Cyclone_AV1500T', start_time='2023-05-03T12:50:00', end_time='2023-05-03T14:55:00')
    print(kpi_result)
    print()
