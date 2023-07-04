import logging
from InfrastructureSVG.Files_Infrastructure.CSV_Files.Read_From_CSV_File_Infrastructure import ReadFromCSVFileClass
from pathlib import Path


class GetCalcValues:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_calc_values(self, label, threshold, executive=False):
        try:
            dl_threshold = 0
            ul_threshold = 0
            home = str(Path.home())
            path = '\\\\asil-dashboard\\Testspan_Runners\\src\\main\\resources\\Traffic\\auto_calculator.csv'
            file = ReadFromCSVFileClass().read_csv_from_full_path(path)
            for i in file:
                if i[10].casefold() == label.casefold():
                    if executive:
                        dl_threshold = float(i[7])
                        ul_threshold = float(i[6])
                        return dl_threshold, ul_threshold
                    else:
                        dl_threshold = float(i[7]) * (float(threshold)/100)
                        ul_threshold = float(i[6]) * (float(threshold)/100)
                        break

                else:
                    continue

            self.logger.info('Threshold from calc')
            dl_threshold = "%.2f" % dl_threshold
            ul_threshold = "%.2f" % ul_threshold
            self.logger.info(f'{dl_threshold}, {ul_threshold}')

            return dl_threshold, ul_threshold
        except Exception:
            self.logger.exception('')
            return None
