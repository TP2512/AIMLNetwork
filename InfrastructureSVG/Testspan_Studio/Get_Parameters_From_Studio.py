import logging
import xml.etree.ElementTree as ET


class GetParameters:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_studio_params(self, sir, parameter, test):
        if 'testset' in test:
            path = '\\\\asil-svg-testspan\\TS_X-Ray_cfg\\TestSet\\' + 'testset-' + sir + '-config.xml'
            params = 'globalParams'
            param = 'globalParam'
        else:
            path = '\\\\asil-svg-testspan\\TS_X-Ray_cfg\\Test\\' + 'test-' + sir + '-config.xml'
            params = 'testParams'
            param = 'testParam'
        sir_parse = ET.parse(path).getroot()
        flag = 0
        value = ''
        for _ in range(1, 50):
            if flag == 1:
                break
            for index, j in enumerate(sir_parse.findall(f'{params}/{param}/key'), start=0):
                if j.text.casefold() == parameter.casefold():
                    x = sir_parse.findall(f'{params}/{param}/value')
                    value = x[index].text
                    self.logger.info(f'The {parameter} is: {value}')
                    break
            break

        return value
