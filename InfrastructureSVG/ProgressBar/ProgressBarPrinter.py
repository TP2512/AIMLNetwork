import logging
from colorama import Fore


class ProgressBar:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.bar = ''

    def print_progress_bar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='#'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        if self.bar != bar:
            self.logger.info(f'{Fore.MAGENTA}{prefix} |{bar}| {percent}% {suffix}')
            self.bar = fill * filledLength + '-' * (length - filledLength)
        # Print New Line on Complete
        # if iteration == total:
        #     self.logger.info('')
        return bar
