import logging
import time
from datetime import datetime, timezone
from elasticsearch_dsl import Search

from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchForDashboard.ElasticSearchDashboard import SendDataForDashboard


class DNSDashboard:
    def __init__(self, index_name, elk_client):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.send_data_for_dashboard = SendDataForDashboard()

        self.index_name = index_name
        self.elk_client = elk_client

        self.headers = [r"Slave/VDI Name", " Cisco IT VPN", "Forti SVG VPN"]
        self.dic_content = []

        self.username = "root"
        self.password = "sp_user9"

        self.airspan_dns_server = '192.168.127.210'
        self.svg_dns_server = '192.168.231.210'

    def delete_index_data(self):
        try:
            s = Search(index=self.index_name, using=self.elk_client)
            return s.query("match_all").delete()
        except Exception:
            self.logger.exception('')

    def set_cisco_content(self):
        cisco_lines = self.get_files_by_sftp(self.airspan_dns_server)

        for line in cisco_lines:
            line = line.split()
            for index, item in enumerate(line):
                if item != "A":  # ip address will be after "A"
                    continue

                dic = {
                    "dns_slave_name": line[0][:-1],
                    "setup_ip_address_by_cisco": line[index + 1],
                    "timestamp": datetime.now(timezone.utc),
                }
                self.dic_content.append(dic)

    def append_airspan_content(self):
        airspan_lines = self.get_files_by_sftp(self.svg_dns_server)
        for line in airspan_lines:
            if line := line.split():
                for slave in self.dic_content:
                    if line[0][:-1] != slave["dns_slave_name"]:
                        continue

                    slave["setup_ip_address_by_forti"] = line[line.index("A") + 1]

    def open_ssh_client(self, ip_addr):
        ssh_connection_inst = SSHConnection(
            ip_address=ip_addr,
            username=self.username,
            password=self.password
        )
        ssh_connection_inst.ssh_connection()

        return ssh_connection_inst.client_ssh

    def get_files_by_sftp(self, ip_addr):  # Need to create as infra
        client = self.open_ssh_client(ip_addr)
        sftp = client.open_sftp()
        with sftp.file("/var/named/forward.airspan.labs", mode='r') as file:
            return file.readlines()

    def process(self):
        self.delete_index_data()

        self.set_cisco_content()
        self.append_airspan_content()

        list_of_docs = []
        for elk_doc in inst.dic_content:
            self.send_data_for_dashboard.fill_list_of_docs(list_of_docs=list_of_docs, index_name=inst.index_name, doc=elk_doc)
        self.send_data_for_dashboard.set_list_of_docs(elk_client=inst.elk_client, list_of_docs=list_of_docs)


if __name__ == '__main__':
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger

    PROJECT_NAME = 'ELK Add and Delete Automation and Manual UR Version'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    time.sleep(1)

    inst = DNSDashboard(
        index_name='dashboard_results_dns_production',
        elk_client=ElasticSearchConnection().connect_to_svg_elasticsearch()
    )
    inst.process()

    print()
