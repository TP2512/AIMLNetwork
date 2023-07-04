import logging
import re

date_and_time_pattern = r'\[\d{0,100}\] \d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}:\d{3} '


class LinkQuality:
    def __init__(self, test_results_object: dict):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.test_results_object = test_results_object

    def check_gnb_link_quality(self):
        self.logger.debug('Start "check_gnb_link_quality" function')

        for gnb_name, gnb_value in self.test_results_object['gnb'].items():
            print(self.test_results_object['gnb'][gnb_name])

        print()


class LogParser:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_error_list(self, path: str, entity: str):
        if entity.upper() == 'CUCP':
            error_pattern = ':ERROR'
        elif entity.upper() == 'RU':
            error_pattern = ':HIGH'
        else:
            self.logger.error(f'The entity "{entity.upper()}" was not founded')
            return None

        error_dict = {}
        error_dict_short = {}
        with open(path, 'r') as file:
            for line in file:
                if re.search(error_pattern, line):
                    new_line = re.sub(date_and_time_pattern, "", line)
                    timestamp = re.search(date_and_time_pattern, line)

                    error_dict[timestamp[0][:-1]] = new_line

                    if new_line in error_dict_short:
                        error_dict_short[new_line] += 1
                    else:
                        error_dict_short[new_line] = 1
        return error_dict, error_dict_short


def main_2(test_path: str):
    path = f'{test_path}\\gnb_1_under_test_EAB85C0059F2\\cucp_1_SSH_Log_(CUCP-at2200-eab85c0059f2-1)'
    file_name = 'cucp_1_(CUCP-at2200-eab85c0059f2-1).log'
    file_name = 'cucp_1_(CUCP-as2900-ed085b0164ec-1).log'
    file_name = 'ru_under_test_(RU-as2900-ed085b0164ec-1).log'
    file_name = 'cucp_1_(CUCP-as2900-ed0866012dc0-1).log'

    log_parser = LogParser()
    error_dict, error_dict_short = log_parser.get_error_list(
        path=f'{path}\\{file_name}',
        entity='CUCP'
    )
    print(f'error_dict is: {error_dict}\n error_dict_short is: {error_dict_short}')

    print()
