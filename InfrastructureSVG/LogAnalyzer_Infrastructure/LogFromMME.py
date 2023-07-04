import logging
import time
import json

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger
from InfrastructureSVG.Network_Infrastructure.websocket_Infrastructure import WebSocketActions


class ConvertRanAmfToIMSI:
    def __init__(self, web_socket_ip_address, web_socket_port):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.flag = True
        self.ue_details_dict = {}
        self.ue_details_dict_filtered = {}

        self.web_socket = WebSocketActions(web_socket_ip_address=web_socket_ip_address, web_socket_port=web_socket_port)
        self.web_socket.web_socket_connection()

    def get_ue_list_from_mme_by_ws(self):
        self.web_socket.send_command(command='{"message": "ue_get"}', time_before_output=5)
        return json.loads(self.web_socket.last_output)['ue_list']

    def start_create_ue_details_dict(self, time_to_sleep=1, **kwargs):
        self.create_ue_details_dict(time_to_sleep)

    def stop_create_ue_details_dict(self, **kwargs):
        self.flag = False

    def create_ue_details_dict(self, time_to_sleep=1):
        self.logger.info('Start create_ue_details_dict')

        while self.flag:
            mme_responses_sorted = {
                i['imsi']: [{'ran_ue_id': i['ran_ue_id'], 'amf_ue_id': i['amf_ue_id']}]
                for i in self.get_ue_list_from_mme_by_ws() if i.get('ran_ue_id') and i.get('amf_ue_id')
            }

            for mme_responses_k, mme_responses_v in mme_responses_sorted.items():
                if self.ue_details_dict.get(mme_responses_k):
                    for vv in self.ue_details_dict.get(mme_responses_k):
                        if v := [v for v in mme_responses_v if v != vv]:
                            self.ue_details_dict[mme_responses_k].extend(v)
                else:
                    self.ue_details_dict[mme_responses_k] = mme_responses_v
            time.sleep(time_to_sleep)

    def found_imsi_by_ran_and_amf_ue_id(self, ran_ue_id, amf_ue_id):
        return [k for k, v in self.ue_details_dict.items() for i in v if i == {'ran_ue_id': ran_ue_id, 'amf_ue_id': amf_ue_id}]

    def filter_per_imsi_list(self, imsi_list):
        self.ue_details_dict_filtered = [{k: v} for k, v in self.ue_details_dict.items() if k in imsi_list]


if __name__ == '__main__':
    project_name = 'Convert UE details to IMSI'
    site = ''

    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=True)

    convert_to_imsi = ConvertRanAmfToIMSI(web_socket_ip_address='172.20.63.14', web_socket_port='9062')
    convert_to_imsi.create_ue_details_dict(time_to_sleep=0)

    _ran_ue_id = 476
    _amf_ue_id = 91982
    convert_to_imsi.found_imsi_by_ran_and_amf_ue_id(ran_ue_id=_ran_ue_id, amf_ue_id=_amf_ue_id)
