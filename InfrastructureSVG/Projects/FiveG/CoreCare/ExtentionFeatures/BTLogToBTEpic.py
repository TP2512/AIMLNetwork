import logging
import pandas as pd

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Projects.FiveG.CoreCare.ParseDataFilesToCSV.CoreParserMainFunction import get_extract_dict, connect_ssh_demangle, linux_ip_address


class ConvertBTLogToBTEpic:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.bt_list_from_log = []
        self.back_trace = None
        self.memory_exhaustion_back_trace = None
        self._dataframe_crash = None

    def get_bt_list_from_bt_log_file(self, path):
        with open(path, 'r') as f:
            x = f.readlines()
            for line in x:
                self.bt_list_from_log.append(f'BT[{"".join(line.split("BT[")[1:])}'.strip())

    def build_back_trace(self):
        """ Build "Back Trace" from crash file """

        if not self.bt_list_from_log:
            self.bt_list_from_log = ['There is no BT']

        if 'alloc_from_ngp_pool_debug' in ' '.join(self.bt_list_from_log) or 'alloc_msg_from_ngp_pool_debug' in ' '.join(self.bt_list_from_log):
            self.memory_exhaustion_back_trace = ['Memory Exhaustion']

        # Create Back Trace DataFrame pre csv row
        self._dataframe_crash = pd.DataFrame(self.bt_list_from_log, columns=['Back Trace Parts'])


def entity_option_list():
    return [
        'unknown_crash',
        'cucp_core',
        'cuup_core',
        'du_core',
        'ru_core',
        'du_phy',
        'xpu_core',
    ]


def hash_bt_converter(entity, bt_path):
    project_name, site = '', None
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=True)

    convert_bt_log_to_epic_fn = ConvertBTLogToBTEpic()

    convert_bt_log_to_epic_fn.get_bt_list_from_bt_log_file(path=bt_path)
    convert_bt_log_to_epic_fn.build_back_trace()

    #

    extract_dict = get_extract_dict()
    extract_dict_key = entity

    extract_dict[extract_dict_key]._dataframe_crash = convert_bt_log_to_epic_fn._dataframe_crash
    extract_dict[extract_dict_key].ssh_demangle = connect_ssh_demangle(logger=logger, linux_ip_address=linux_ip_address)

    extract_dict[extract_dict_key].build_back_trace(corecare_app=False)
    extract_dict[extract_dict_key].get_bt_demangle()
    extract_dict[extract_dict_key].replace_to_hash()
    extract_dict[extract_dict_key].ssh_demangle.ssh_close_connection()

    logger.info(f'back_trace_hash is: {extract_dict[extract_dict_key].back_trace_hash}')

    return extract_dict[extract_dict_key].back_trace_hash


if __name__ == '__main__':
    entity = 'du_core'
    full_file_name = 'bt_log_for_test.txt'
    hash_bt = hash_bt_converter(
        entity=entity,
        bt_path=f'\\\\192.168.127.247\\Cores\\HashBT Converter\\{full_file_name}',
    )
