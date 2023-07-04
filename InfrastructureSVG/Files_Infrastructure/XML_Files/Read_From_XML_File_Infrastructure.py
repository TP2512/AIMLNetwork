import xml.etree.ElementTree as ET
import logging

from InfrastructureSVG.Projects_Dictionaries.DashboardDict import hwdic


class ReadFromXmlClass:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def extract_ip_and_enb_name_from_sut(self, sut, enb_id):
        """
           This function responsible for extracting eNB name from SUT by comparing it to given IP

           The function get 2 parameters:
               - "sut" - full path to SUT including .xml
               - "ip" -  parameter need to be a string (PASS/FAIL/Automation_Fail/TO DO)

           The function return PUT response (200 = ok, else = fail)
        """
        enb_name = ''
        ip = ''
        try:
            sut_parse = ET.parse(sut).getroot()
            for j in sut_parse.findall(f'{enb_id}/snmp/strAddress'):
                ip = j.text
                for i in sut_parse.findall(f'{enb_id}/netspanName'):
                    enb_name = i.text
                    break
                if not enb_name:
                    for i in sut_parse.findall(f'{enb_id}/nms'):
                        enb_name = i.text

            return enb_name, ip

        except Exception:
            self.logger.exception("Node ID was not found")

    def extract_hardware_type_from_sut(self, sut, enb_list):
        """
           This function responsible for extracting eNB name from SUT by comparing it to given IP

           The function get 2 parameters:
               - "sut" - full path to SUT including .xml
               - "ip" -  parameter need to be a string (PASS/FAIL/Automation_Fail/TO DO)

           The function return PUT response (200 = ok, else = fail)
        """
        flag = 0
        hw_dict = {}
        try:
            for enb in enb_list:
                if enb:
                    sut_parse = ET.parse(sut).getroot()
                    for _ in range(1, 50):
                        if flag == 1:
                            break
                        for j in sut_parse.findall(f'{enb}/class'):
                            hw_dict[enb] = hwdic[str(j.text.split('.')[-1])]
                            break
                        break
            return hw_dict

        except Exception:
            self.logger.exception("Node ID was not found")

    def read_from_xml(self, full_path, path_key, key_value):
        """
           This function responsible for extracting eNB name from SUT by comparing it to given IP

           The function get 2 parameters:
               - "full_path" - full path to XML including .xml
               - "path_key" -  the path into the XML (string type)
                    * For example: Actions/ServerParameters/Value_IpAddress
               - "key_value" - the key to get the value
                    * For example: IpAddress

           The function return 1 parameters:
               - "value_list" - List of values (list type)
        """

        try:
            value_list = []
            xml_parse = ET.parse(full_path).getroot()
            for tag in xml_parse.findall(path_key):
                value_ = tag.get(key_value)
                value_list.append(value_)
            return value_list
        except Exception:
            self.logger.exception("Can't read from txt file")
            return None
