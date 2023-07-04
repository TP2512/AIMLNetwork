import sys
import os
from termcolor import colored
import logging


class Exceptions:
    def __init__(self):
        self.logger = logging.getLogger(
            'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)

    def common_exception(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)
        self.logger.debug(colored('##########', 'red'))
        print('The Exception is: ')
        print(e)
        print('The error in: ')
        print('File: ' + str(fname))
        print('Class: ' + str(exc_type))
        print('Line: ' + str(exc_tb.tb_lineno))
        print(colored('##########', 'red'))


    def jira_error_exception(self, err):
        print(colored('##########', 'red'))
        print(err.status_code, err.text)
        print(err)
        print(colored('##########', 'red'))



