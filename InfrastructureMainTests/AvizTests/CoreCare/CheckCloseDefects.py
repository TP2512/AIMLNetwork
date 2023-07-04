import os
import time
from datetime import datetime, timezone
import collections


def check_close_defects_version(path, current_version):
    sr_version = current_version.split("-")[0]
    device_type = 'DU'

    current_version_dict = {}
    files_dict = {}
    for dir_path, dir_names, file_names in os.walk(path):
        for file_ in file_names:
            if file_.endswith(".pdf") and f'-{sr_version}' in file_:
                last_modified_file = os.path.getctime(f'{dir_path}\\{file_}')
                last_modified_file = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_modified_file))
                last_modified_file = datetime.strptime(last_modified_file, '%Y-%m-%d %H:%M:%S')
                files_dict.update({f'{dir_path}\\{file_}': last_modified_file})
                if f'{device_type}-{current_version}.pdf' == file_:
                    current_version_dict.update({f'{dir_path}\\{file_}': last_modified_file})
    files_dict = collections.OrderedDict({k: v for k, v in sorted(files_dict.items(), key=lambda item: item[1])})

    if current_version_dict:
        if current_version_dict[list(current_version_dict.keys())[-1]] > files_dict[list(files_dict.keys())[-1]]:
            print('Need to create a new defect + link to last close defect')
        else:
            print('Not need to create a new defect')
    else:
        print('There is no .pdf for this version => Need to create a new defect + link to last close defect')

    print()


if __name__ == '__main__':
    path_ = f'\\\\fs4\\Projects\\Development\\Builds\\5G\\DU'
    current_version_ = '18.50-334-0.0'
    # current_version = '18.50.437.0.0'
    check_close_defects_version(path_, current_version_)
