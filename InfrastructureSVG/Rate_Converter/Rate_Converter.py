import logging


class RateConverter:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    @staticmethod
    def rate_converter(nbytes):

        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        i = 0
        while nbytes >= 1000 and i < len(suffixes) - 1:
            nbytes /= 1000
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return float(f)
