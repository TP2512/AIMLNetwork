import contextlib
import os
from pathlib import Path
import datetime
from datetimerange import DateTimeRange
import shutil
from colorama import Fore

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger

path_list = ['\\\\192.168.127.231\\SWImages\\AIO']


class Cleaner:

    @staticmethod
    def get_time_range():
        now = datetime.datetime.now()
        three_month_range = now - datetime.timedelta(days=14)
        return DateTimeRange(three_month_range, now)

    def collect_paths(self):
        time_range = self.get_time_range()
        for path in path_list:
            path = Path(path).iterdir()
            for i in path:
                if i.is_dir() and 'airspan' in i.name and datetime.datetime.fromtimestamp(i.stat().st_ctime) not in time_range:
                    content = os.listdir(i)
                    for obj in content:
                        if obj not in [f'{i.name}.tgz', 'versions.txt']:
                            print(f'{Fore.GREEN}Deleting old runs from {i}\\{obj}')
                            with contextlib.suppress(OSError, PermissionError):
                                if Path(f'{i.absolute()}\\{obj}').is_dir():
                                    shutil.rmtree(f'{i.absolute()}\\{obj}')
                                elif Path(f'{i.absolute()}\\{obj}').is_file():
                                    os.remove(f'{i.absolute()}\\{obj}')


def main():
    cleaner = Cleaner()
    cleaner.collect_paths()


if __name__ == '__main__':
    project_name, site = 'Old Runs Cleaner', 'IL SVG'
    print_before_logger(project_name=project_name, site=site)
    main()
