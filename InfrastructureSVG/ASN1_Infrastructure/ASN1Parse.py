import logging
import json
import socket
from datetime import datetime, timezone
import re

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import GeneralFolderActionClass
from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection


class GetValuesFromASNFile:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    @staticmethod
    def get_value_by_regex(regex_pattern, text_str):
        return re.search(regex_pattern, text_str, re.I).group()

    def get_amf_ue_ngap_id(self, text_str):
        amf_pattern = r'(?<=value AMF-UE-NGAP-ID \: )(.*)(=?\d{1,10})'
        return self.get_value_by_regex(regex_pattern=amf_pattern, text_str=text_str)

    def get_ran_ue_ngap_id(self, text_str):
        ran_pattern = r'(?<=value RAN-UE-NGAP-ID \: )(.*)(=?\d{1,10})'
        return self.get_value_by_regex(regex_pattern=ran_pattern, text_str=text_str)


class ASN1Parse(GetValuesFromASNFile):
    def __init__(self, decode_type):
        super(ASN1Parse, self).__init__()

        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.asn1_host_ip_address = '192.168.126.178'  # 'ASIL-SV-AUTO'
        self.username = 'spuser'
        self.password = 'sp_user9'

        self.oss_nokalva_path = f'\\\\{self.asn1_host_ip_address}\\c\\Program Files\\OSS Nokalva'

        self.license = f'{self.oss_nokalva_path}\\ossinfo'
        self.asn1step_executable = f'{self.oss_nokalva_path}\\asn1step\\winx64\\10.2.0\\bin\\asn1step.exe'

        self.decode_type = decode_type
        if self.decode_type == 'NGAP':
            # self.asn_file_path = f'{self.oss_nokalva_path}\\Files\\schemas\\3GPP NGAP v16.5.0.asn'
            self.asn_file_path = f'{self.oss_nokalva_path}\\Files\\schemas\\3GPP NGAP v15.8.0.asn'
        elif self.decode_type == 'F1AP':
            self.asn_file_path = f'{self.oss_nokalva_path}\\Files\\schemas\\3GPP F1AP v15.3.0.asn'
        else:
            raise Exception('Incorrect decode type')

        self.store_hex_path = None
        self.json_file_path = None
        self.text_file_path = None

        self.asn_text_str = ''

    def create_setup_path(self):
        date_time = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')

        hostname = socket.gethostname()
        GeneralFolderActionClass().check_path_exist_and_create(f'{self.oss_nokalva_path}\\Setups\\{hostname}')
        GeneralFolderActionClass().check_path_exist_and_create(f'{self.oss_nokalva_path}\\Setups\\{hostname}\\{date_time}')
        self.store_hex_path = f'{self.oss_nokalva_path}\\Setups\\{hostname}\\{date_time}\\F1AP-PDU.per'
        self.json_file_path = f'{self.oss_nokalva_path}\\Setups\\{hostname}\\{date_time}\\F1AP-PDU.per.json'
        self.text_file_path = f'{self.oss_nokalva_path}\\Setups\\{hostname}\\{date_time}\\F1AP-PDU.per.txt'

    def store_hex(self, hex_str):
        with open(self.store_hex_path, "w") as f:
            f.write(hex_str)

    def parse(self):
        if self.decode_type == 'NGAP':
            # command = f'"{self.asn1step_executable}" "{self.asn_file_path}" -root -decodePdu NGAP-PDU "{self.store_hex_path}" -hex -json'
            decode_value = 'NGAP-PDU'
        elif self.decode_type == 'F1AP':
            # command = f'"{self.asn1step_executable}" "{self.asn_file_path}" -root -decodePdu F1AP-PDU "{self.store_hex_path}" -hex -json'
            decode_value = 'F1AP-PDU'
        else:
            self.logger.error('Incorrect decode type')
            return None

        command = f'"{self.asn1step_executable}" "{self.asn_file_path}" -root -decodePdu {decode_value} "{self.store_hex_path}" -hex -json -asn1Value'
        ssh = SSHConnection(
            ip_address=self.asn1_host_ip_address,
            username=self.username,
            password=self.password
        )
        ssh.ssh_connection()
        ssh.ssh_send_commands(commands=command, clean_output=True, wait_before_output=3)
        ssh.ssh_close_connection()

    def get_json_string(self):
        try:
            with open(self.json_file_path, "r") as f:
                json_str = f.read()
                return json.loads(json_str)
        except Exception:
            self.logger.exception('There was a problem to get json string')
            return None

    def get_text_string(self):
        try:
            with open(self.text_file_path, "r") as f:
                return f.read()
        except Exception:
            self.logger.exception('There was a problem to get json string')
            return None

    def parse_process(self, hex_value):
        self.create_setup_path()

        self.store_hex(hex_str=hex_value)
        self.parse()
        return self.get_text_string()


if __name__ == "__main__":
    # Logger
    PROJECT_NAME = 'ASN1_Infrastructure'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=True)

    try:
        asn1Parse = ASN1Parse(decode_type='NGAP')

        _hex_value_amf_ran = '002e4041000004000a000440013c750055000200a700260019187e02038b881c537e004509000bf202f010806501434f9e250079400f4002f010623a00000002f01000000b'

        asn_text_str = asn1Parse.parse_process(_hex_value_amf_ran)

        asn1Parse.get_amf_ue_ngap_id(text_str=asn_text_str)
        asn1Parse.get_ran_ue_ngap_id(text_str=asn_text_str)

    except Exception:
        logger.exception('')

    print()
