import re
import xmltodict
import json
import pandas as pd

from InfrastructureMainTests.AvizTests.General.TmsiToImsi.strings2 import xml_data_1
from InfrastructureSVG.Network_Infrastructure.websocket_Infrastructure import WebSocketActions

cucp_log_path = '\\\\192.168.127.231\\AutomationResults\\old_runs\\ASIL-SATURN\\3894\\RobotFrameworkSVG\\Test_Logs_And_Files\\SIR-42654\\gnb_1_ED085B0164EC\\' \
                'cucp_1_SSH_Log_(CUCP-as2900-ed085b0164ec-1)\\cucp_1_(CUCP-as2900-ed085b0164ec-1).log'


def get_ue_list_from_mme_by_ws():
    web_socket = WebSocketActions(web_socket_ip_address='172.20.63.14', web_socket_port='9062')

    web_socket.web_socket_connection()
    web_socket.send_command(command='{"message": "ue_get"}', time_before_output=5)
    return json.loads(web_socket.last_output)['ue_list']


def get_xml_from_marben(amf_ue_ngap_id_hex):
    print(amf_ue_ngap_id_hex)
    return xml_data_1


def recursive_lookup(data_dict: dict, key: str):
    for k, v in data_dict.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            yield from recursive_lookup(v, key)
        elif isinstance(v, list):
            for d in v:
                yield from recursive_lookup(data_dict=d, key=key)


def get_log_data(log_path: str):
    with open(log_path, 'r') as f:
        return f.read()


def get_amf_ue_ngap_id(cucp_log):
    # regex_amf_ue_ngap_id_list = re.findall(r'((?<=CP --> AMF \[NGAP\]: UE CONTEXT RELEASE REQUEST)([\s\S]*?)(<CU_CP:UE_CONN_MGR:SYSTEM>))(.*$)', cucp_log, re.MULTILINE)
    regex_amf_ue_ngap_id_list = re.findall(r'((?<=CP --> AMF \[NGAP]: UE CONTEXT RELEASE REQUEST)([\s\S]*?)(<CU_CP:UE_CONN_MGR:SYSTEM>))(.*$)', cucp_log, re.MULTILINE)
    _amf_ue_ngap_id = None
    for _items_list in regex_amf_ue_ngap_id_list:
        for value in _items_list:
            try:
                int(value, 16)
            except Exception:
                continue
            _amf_ue_ngap_id = value
            print(_amf_ue_ngap_id)
            break
    return _amf_ue_ngap_id


def main():
    ue_details_list = []
    ue_details_list += get_ue_list_from_mme_by_ws()
    print(ue_details_list)

    print()

    cucp_log = get_log_data(log_path=cucp_log_path)
    amf_ue_ngap_id_hex = get_amf_ue_ngap_id(cucp_log=cucp_log)
    amf_ue_ngap_id_xml = get_xml_from_marben(amf_ue_ngap_id_hex)
    amf_ran_dict_data = dict(xmltodict.parse(amf_ue_ngap_id_xml, xml_attribs=False))
    amf_ue_ngap_id = list(recursive_lookup(data_dict=amf_ran_dict_data, key='AMF-UE-NGAP-ID'))
    print(f'amf_ue_ngap_id is: {amf_ue_ngap_id[0]}')
    ran_ue_ngap_id = list(recursive_lookup(data_dict=amf_ran_dict_data, key='RAN-UE-NGAP-ID'))
    print(f'ran_ue_ngap_id is: {ran_ue_ngap_id[0]}')

    print()


if __name__ == '__main__':
    main()
    print()
    #
    # # Build dataframe
    # columns = ['RNTI', 'IMSI', 'RAN ADDRESS', 'AMF UE NGAP ID', 'RAN UE NGAP ID', 'HEX MESSAGE']
    # dataframe = pd.DataFrame(columns=columns)
    #
    # dict_data_1 = dict(xmltodict.parse(xml_data_1, xml_attribs=False))
    # rrc_container = list(recursive_lookup(data_dict=dict_data_1, key='RRCContainer'))
    # print(f'rrc_container is: {rrc_container[0]}')
    # crnti = list(recursive_lookup(data_dict=dict_data_1, key='C-RNTI'))
    # print(f'crnti is: {crnti[0]}')
    #
    # dict_data_2 = dict(xmltodict.parse(xml_data_2, xml_attribs=False))
    # tmsi = list(recursive_lookup(data_dict=dict_data_2, key='ng-5G-S-TMSI-Part1'))
    # print(f'tmsi is: {tmsi[0]}')
    #
    # dict_data_3 = dict(xmltodict.parse(xml_data_3, xml_attribs=False))
    # amf_ue_ngap_id = list(recursive_lookup(data_dict=dict_data_3, key='AMF-UE-NGAP-ID'))
    # print(f'amf_ue_ngap_id is: {amf_ue_ngap_id[0]}')
    # ran_ue_ngap_id = list(recursive_lookup(data_dict=dict_data_3, key='RAN-UE-NGAP-ID'))
    # print(f'ran_ue_ngap_id is: {ran_ue_ngap_id[0]}')
    #
    # print()
