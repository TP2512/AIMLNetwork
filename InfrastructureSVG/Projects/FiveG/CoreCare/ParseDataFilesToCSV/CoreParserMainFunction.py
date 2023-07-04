import os
import socket
import time
from datetime import datetime, timezone
import shutil
import pandas as pd
# import numpy as np

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import GeneralFolderActionClass
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import COLUMNS, PROCESS_LIST, PHY_PROCESS_LIST, get_tar_gz_file, close_tar_gz_file_reader
from InfrastructureSVG.Projects.FiveG.CoreCare.ParseDataFilesToCSV.CoreCare_ExtractStructure \
    import ExtractUnknownCrash, ExtractCUCPCore, ExtractCUUPCore, ExtractDUCore, ExtractRUCore, ExtractDUPhyAssert, ExtractRUPhyAssert, ExtractXPU
from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection

# linux_ip_address = '172.20.63.185'
linux_ip_address = '192.168.125.93'
# linux_ip_address = '172.20.62.17'


def get_extract_dict():
    return {
        'unknown_crash': ExtractUnknownCrash(),
        'cucp_core': ExtractCUCPCore(),
        'cuup_core': ExtractCUUPCore(),
        'du_core': ExtractDUCore(),
        'ru_core': ExtractRUCore(),
        'du_phy': ExtractDUPhyAssert(),
        # 'ru_phy': ExtractRUPhyAssert(),
        # 'phy': ExtractDUPhyAssert(),
        'xpu_core': ExtractXPU(),
    }


def get_crash_details(extract_dict: dict, extract_dict_key: str):
    extract_dict[extract_dict_key].extract_type_crash_name()
    extract_dict[extract_dict_key].build_old_back_trace()
    extract_dict[extract_dict_key].build_back_trace()
    extract_dict[extract_dict_key].get_bt_demangle()
    extract_dict[extract_dict_key].check_for_memory_exhaustion()
    if 'Memory Exhaustion' in extract_dict[extract_dict_key].memory_exhaustion_back_trace:
        extract_dict[extract_dict_key].build_memory_exhaustion_back_trace()
    extract_dict[extract_dict_key].replace_old_to_hash()
    extract_dict[extract_dict_key].extract_pid_file()
    extract_dict[extract_dict_key].extract_systeminfo()
    extract_dict[extract_dict_key].extract_ipinfo_file()
    if extract_dict[extract_dict_key].ipinfo:
        extract_dict[extract_dict_key].extract_ip_address()
        extract_dict[extract_dict_key].extract_setup_owner()
    extract_dict[extract_dict_key].extract_gnb_version()
    if extract_dict[extract_dict_key].systeminfo:
        extract_dict[extract_dict_key].extract_version_type()
        extract_dict[extract_dict_key].extract_crash_version()
        extract_dict[extract_dict_key].extract_hostname()
        extract_dict[extract_dict_key].extract_system_runtime()
        extract_dict[extract_dict_key].extract_user()
        extract_dict[extract_dict_key].extract_time_stamp()
        extract_dict[extract_dict_key].extract_tti()
    extract_dict[extract_dict_key].extract_core_validation()
    if extract_dict[extract_dict_key].core_validation:
        extract_dict[extract_dict_key].get_core_validation_timestamp()


def build_new_row(extract_dict: dict, line_date: str, last_modified_date: str, extract_dict_key: str):
    return [
        f'{line_date}',
        f'{last_modified_date}',
        f'{extract_dict[extract_dict_key].type_crash_name}',
        f'{extract_dict[extract_dict_key].version_type}',
        f'{extract_dict[extract_dict_key].gnb_version}',
        f'{extract_dict[extract_dict_key].crash_version}',
        f'{extract_dict[extract_dict_key].ip_address}',
        f'{extract_dict[extract_dict_key].setup_name}',
        f'{extract_dict[extract_dict_key].setup_owner}',
        f'{extract_dict[extract_dict_key].new_dir_path}',
        f'{extract_dict[extract_dict_key].file_name}',
        f'{extract_dict[extract_dict_key].back_trace_hash}',
        f'{extract_dict[extract_dict_key].back_trace.removeprefix(" -> ")}',
        f'{extract_dict[extract_dict_key].system_runtime}',
        f'{extract_dict[extract_dict_key].pid}',
        f'{extract_dict[extract_dict_key].time_stamp}',
        f'{extract_dict[extract_dict_key].tti}',
        f'{extract_dict[extract_dict_key].customer_name}',
        f'{extract_dict[extract_dict_key].full_back_trace.removeprefix(" -> ")}',
        f'{extract_dict[extract_dict_key].old_back_trace.removeprefix(" -> ")}',
        f'{extract_dict[extract_dict_key].old_back_trace_hash}',
        f'{extract_dict[extract_dict_key].core_validation_timestamp}',
    ]


def save_to_csv(full_path_to_save: str, dataframe: pd.core.frame.DataFrame, logger):
    if GeneralFolderActionClass().check_path_exist(full_path_to_save):
        current_dataframe = pd.read_csv(full_path_to_save)
        dataframe = pd.concat([current_dataframe, dataframe], ignore_index=True)
        dataframe = dataframe.drop_duplicates(keep=False)
        dataframe.to_csv(full_path_to_save, mode='w', header=True, index=False, na_rep='')
        dataframe.to_csv()
        logger.info('New row was created')
    else:
        dataframe.to_csv(full_path_to_save, mode='w', header=True, index=False, na_rep='')
        logger.info('New file with new row was created')


def connect_ssh_demangle(logger, linux_ip_address):
    ssh_demangle = SSHConnection(
        ip_address=linux_ip_address,
        username='spuser',
        password='sp_user9'
    )
    ssh_demangle.ssh_connection()
    if not ssh_demangle.check_ssh_status():
        logger.error(f'Open ssh error to {linux_ip_address}')
        return None

    commands = [
        'python3',
        'import cxxfilt',
        'from ctypes.util import find_library',
    ]
    ssh_demangle.ssh_send_commands(commands=commands, with_output=False, wait_before_output=0.01, wait_between_commands=0.01)
    return ssh_demangle


def get_extract_dict_and_extract_dict_key(file):
    extract_dict = get_extract_dict()

    # Create row data
    # extract_dict_key = [i for i in list(extract_dict.keys()) if i.split("_")[0].upper() in file.upper()]
    extract_dict_key = []
    for i in list(extract_dict.keys()):
        if i.split("_")[0].upper() in file.upper():
            if [p for p in PHY_PROCESS_LIST if p.upper() in file.upper()]:
                extract_dict_key.append('du_phy')
            else:
                extract_dict_key.append(i)
    extract_dict_key = extract_dict_key[0] if extract_dict_key else 'unknown_crash'

    return extract_dict, extract_dict_key


def core_parser_main(project_name, site, listener_path, path_to_save, setup_name_list_path, network_address, recursive, without_entity=None) -> None:
    # sourcery skip: low-code-quality
    # sourcery no-metrics
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=True)

    while True:
        try:
            logger.debug('Waiting 5 sec')
            time.sleep(5)
            # logger.debug('Waiting 5 min')
            # time.sleep(300)

            current_date = datetime.strftime(datetime.today(), "%Y_%m_%d")
            full_path_to_save = f'{path_to_save}\\CORE_SUMMARY_{current_date}.csv'  # Need to edit it !!!!

            # Check for current date folder. if not exist -> create it
            GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\{current_date}')
            GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\{current_date}\\There is no Version')
            GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\{current_date}\\There is a analyzing problem')
            GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\There is a problem opening\\{current_date}')
            GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\Private build\\{current_date}')

            ssh_demangle = connect_ssh_demangle(logger=logger, linux_ip_address=linux_ip_address)
            if not ssh_demangle:
                continue

            # Create .CSV file
            listener_path_for_lop = f'{listener_path}\\Cores Per Customer' if 'Customers' in listener_path else listener_path
            for dir_path, dir_names, file_names in os.walk(listener_path_for_lop):
                try:
                    if recursive['is_active'] and len(dir_path.split('\\')) >= len(listener_path_for_lop.split('\\')) + recursive['recursive_number']:
                        continue

                    for index, file in enumerate(file_names, start=0):
                        if not file.endswith('.tgz'):
                            continue

                        if index == 0 and 'Customer' in site:
                            time.sleep(600)

                        corrupted_core_flag = False
                        private_build_flag = False
                        tar = None
                        logger.info('\n\n\n\n---------------------------------------------------------------------------------------------------')

                        try:
                            if without_entity == 'without_cu' and 'cu' in file:  # ##### waiting for DEF-39414
                                logger.debug('Skipping on CU crash')
                                continue
                            if without_entity == 'without_du' and 'du' in file:  # ##### waiting for DEF-39414
                                logger.debug('Skipping on DU crash')
                                continue

                            logger.debug(file)

                            # Waiting for the file to finish transferring
                            last_accessed_time = 0
                            while True:
                                time.sleep(5)
                                if 'Customer' in site:
                                    current_accessed_time = os.path.getmtime(f'{dir_path}\\{file}')
                                else:
                                    current_accessed_time = os.path.getmtime(f'{listener_path}\\{file}')

                                if current_accessed_time == last_accessed_time:
                                    break
                                else:
                                    last_accessed_time = current_accessed_time
                            time.sleep(3)

                            not_in = ['core_info', 'airspaninfo']
                            if not [True for n in not_in if n in file] and file[-7:] != '.tar.gz' and file[-7:] != '.tgz':
                                continue

                            full_path_file = f'{dir_path}\\{file}'

                            dataframe = pd.DataFrame(columns=COLUMNS)

                            extract_dict, extract_dict_key = get_extract_dict_and_extract_dict_key(file=file)
                            # Read tar.gz file (Crash info file)
                            try:
                                tar, tar_members = get_tar_gz_file(full_path_file)
                            except Exception as err:
                                logger.error(f'The file: {file} was not open - corrupted_core_flag = True')
                                corrupted_core_flag = True
                                tar_members = ''

                            # Fill row data
                            extract_dict[extract_dict_key].add_to_self(tar_file=tar, tar_members=tar_members, dir_path=dir_path, file_name=file,
                                                                       network_address=network_address, setup_name_list_path=setup_name_list_path,
                                                                       ssh_demangle=ssh_demangle)

                            # Get Modified Date
                            try:
                                mtime = os.path.getmtime(f'{dir_path}\\{file}')
                            except OSError:
                                mtime = 0
                            try:
                                last_modified_date = datetime.fromtimestamp(mtime).strftime("%Y/%m/%d %H:%M:%S")
                            except OSError:
                                last_modified_date = datetime.fromtimestamp(0).strftime("%Y/%m/%d %H:%M:%S")
                            line_date = datetime.now(timezone.utc).strftime("%Y/%m/%d %H:%M:%S")

                            # Get Crash Details
                            get_crash_details(extract_dict, extract_dict_key)
                            if 'Customer' in site:
                                if len(dir_path.split(listener_path+'\\Cores Per Customer\\')) > 1:
                                    extract_dict[extract_dict_key].customer_name = dir_path.split(listener_path+'\\Cores Per Customer\\')[1]
                                    extract_dict[extract_dict_key].ip_address = f'{site}_{extract_dict[extract_dict_key].customer_name}'.replace(" ", "_")
                                else:
                                    # extract_dict[extract_dict_key].customer_name = 'Tier3'
                                    # extract_dict[extract_dict_key].customer_name = '*** Use Customer name field below instead ***'
                                    extract_dict[extract_dict_key].customer_name = 'None'
                            extract_dict[extract_dict_key].change_setup_owner(site=site)

                            # close tar.gz file (Crash info file)
                            close_tar_gz_file_reader(tar)

                            # Check for version folder into current date folder. if not exist -> create it
                            if extract_dict[extract_dict_key].gnb_version:
                                extract_dict[extract_dict_key].new_dir_path = f'{listener_path}\\{current_date}\\{extract_dict[extract_dict_key].gnb_version}'
                            else:
                                if corrupted_core_flag:
                                    extract_dict[extract_dict_key].new_dir_path = f'{listener_path}\\There is a problem opening\\{current_date}'
                                    extract_dict[extract_dict_key].back_trace = 'Corrupted Core'
                                    extract_dict[extract_dict_key].full_back_trace = 'Corrupted Core'
                                    extract_dict[extract_dict_key].old_back_trace = 'Corrupted Core'
                                    # continue
                                else:
                                    extract_dict[extract_dict_key].new_dir_path = f'{listener_path}\\{current_date}\\There is no Version'
                                    extract_dict[extract_dict_key].back_trace = 'There is no version'
                                    extract_dict[extract_dict_key].full_back_trace = 'There is no version'
                                    extract_dict[extract_dict_key].old_back_trace = 'There is no version'
                                extract_dict[extract_dict_key].gnb_version = 'There_is_no_version'
                                extract_dict[extract_dict_key].crash_version = 'There_is_no_version'
                                extract_dict[extract_dict_key].replace_to_hash()
                                extract_dict[extract_dict_key].replace_old_to_hash()

                            GeneralFolderActionClass().check_path_exist_and_create(f'{extract_dict[extract_dict_key].new_dir_path}')

                            # Build Row
                            extract_dict[extract_dict_key].convert_back_trace_summary()
                            extract_dict[extract_dict_key].replace_to_hash()

                            # if extract_dict[extract_dict_key].user is not None and extract_dict[extract_dict_key].user != 'build':
                            # if extract_dict[extract_dict_key].user and extract_dict[extract_dict_key].user != 'build':
                            # if extract_dict[extract_dict_key].user and extract_dict[extract_dict_key].user not in ['build', 'root', 'swuser', 'bkoren']:
                            if extract_dict[extract_dict_key].user and extract_dict[extract_dict_key].user not in ['build', 'root', 'sapirdavid']:
                                logger.warning(f'This Core is a private build - user = {extract_dict[extract_dict_key].user}')
                                extract_dict[extract_dict_key].new_dir_path = f'{listener_path}\\Private build\\{current_date}'
                                private_build_flag = True

                            if not private_build_flag:
                                row = build_new_row(extract_dict, line_date, last_modified_date, extract_dict_key)
                                if len(row) == len(COLUMNS):
                                    new_row = pd.DataFrame([row], columns=COLUMNS)
                                    dataframe = pd.concat([dataframe, new_row], ignore_index=True)
                                else:
                                    logger.error(f'len_row != len_columns \n{len(row) != len(COLUMNS)}')

                                # Save to .CSV file
                                save_to_csv(full_path_to_save, dataframe, logger)

                            # move file to relevant folder
                            shutil.move(f'{dir_path}\\{file}', f'{extract_dict[extract_dict_key].new_dir_path}\\{file}')
                            logger.info(f'Move to: {extract_dict[extract_dict_key].new_dir_path}\\{file}')
                        except socket.error as err:
                            logger.exception(f'socket.error {err}')
                            if ssh_demangle:
                                # ssh_demangle = None
                                break
                        except Exception as err:
                            logger.exception('There is a analyzing problem')

                            # close tar.gz file (Crash info file)
                            if tar:
                                close_tar_gz_file_reader(tar)

                            # move file to relevant folder
                            shutil.move(f'{dir_path}\\{file}', f'{listener_path}\\{current_date}\\There is a analyzing problem\\{file}')
                            logger.info(f'Move to: {listener_path}\\{current_date}\\There is a analyzing problem\\{file}')

                    if not recursive['is_active'] or not ssh_demangle:
                        break
                    else:
                        continue
                except Exception as err:
                    logger.exception('')
            ssh_demangle.ssh_close_connection()
        except Exception as err:
            logger.exception('')

        logger.info('Waiting 600 sec')
        time.sleep(600)
