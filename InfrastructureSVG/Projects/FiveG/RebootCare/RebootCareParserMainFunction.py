import json
import os
import time
from datetime import datetime
import shutil
import pandas as pd

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchForDashboard.ELKDashboardFillData.SendDataToDashboard import RebootCareReportToELK
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import GeneralFolderActionClass
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import get_tar_gz_file, close_tar_gz_file_reader, read_tar_gz_file


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


def get_last_accessed_time(site, dir_path, listener_path, file):
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


def check_or_create_folders(listener_path, current_date):
    GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\{current_date}')
    GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\{current_date}\\There is no Version')
    GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\{current_date}\\There is a analyzing problem')
    GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\There is a problem opening\\{current_date}')
    GeneralFolderActionClass().check_path_exist_and_create(f'{listener_path}\\Private build\\{current_date}')


def reboot_care_parser_main(project_name, site, listener_path, path_to_save, recursive) -> None:
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=True)

    while True:
        try:
            time_number = 5
            # time_number = 300
            logger.debug(f'Waiting {time_number} sec')
            time.sleep(time_number)

            current_date = datetime.strftime(datetime.today(), "%Y_%m_%d")
            full_path_to_save = f'{path_to_save}\\CORE_SUMMARY_{current_date}.csv'  # Need to edit it !!!!

            # Check for current date folder. if not exist -> create it
            check_or_create_folders(listener_path, current_date)

            # Create .CSV file
            listener_path_for_lop = f'{listener_path}\\Cores Per Customer' if 'Customers' in listener_path else listener_path
            for dir_path, dir_names, file_names in os.walk(listener_path_for_lop):
                try:
                    if recursive['is_active'] and len(dir_path.split('\\')) >= len(listener_path_for_lop.split('\\')) + recursive['recursive_number']:
                        continue

                    for index, file_name in enumerate(file_names, start=0):
                        logger.info(f'{dir_path}\\{file_name}')

                        if not file_name.endswith('.tgz'):
                            continue

                        if index == 0 and 'Customer' in site:
                            time.sleep(600)

                        corrupted_core_flag = False
                        tar = None
                        logger.info('\n\n\n\n---------------------------------------------------------------------------------------------------')

                        try:
                            logger.debug(file_name)

                            # Waiting for the file to finish transferring
                            get_last_accessed_time(site, dir_path, listener_path, file_name)
                            time.sleep(3)

                            # Check for .tgz reboot
                            not_in = ['reboot_']
                            if not [True for n in not_in if n in file_name] and file_name[-7:] != '.tar.gz' and file_name[-7:] != '.tgz':
                                continue

                            # Read tar.gz file (reboot info file) and Get reboot details
                            try:
                                tar, tar_members = get_tar_gz_file(f'{dir_path}\\{file_name}')
                            except Exception:
                                logger.error(f'The file: {file_name} was not open - corrupted_core_flag = True')
                                corrupted_core_flag = True
                                tar_members = ''

                            try:
                                fp_read = read_tar_gz_file(tar, tar_members, tr_gz_file_name='.json')
                            except Exception:
                                logger.exception('The file "core_mem_info" was not open')
                                fp_read = None

                            if fp_read:
                                try:
                                    reboot_data_dict = json.loads(fp_read.decode('UTF-8'))
                                except Exception:
                                    logger.exception('')

                            # with open(f'{dir_path}\\{file_name}', "r") as f:
                            #     reboot_data_dict = json.loads(f.read())

                            reboot_data_dataframe = pd.DataFrame.from_dict([reboot_data_dict])
                            print(json.dumps(reboot_data_dict, indent=4, sort_keys=True))

                            # close tar.gz file (Crash info file)
                            close_tar_gz_file_reader(tar)

                            # Check for version folder into current date folder. if not exist -> create it
                            if reboot_data_dict.get('pack_SW') or reboot_data_dict.get('entity_SW'):
                                new_dir_path = f'{listener_path}\\{current_date}\\{reboot_data_dict.get("pack_SW")}'
                            else:
                                reboot_data_dict['pack_SW'] = 'There_is_no_version'
                                reboot_data_dict['entity_SW'] = 'There_is_no_version'

                                if corrupted_core_flag:
                                    new_dir_path = f'{listener_path}\\There is a problem opening\\{current_date}'
                                    # continue
                                else:
                                    new_dir_path = f'{listener_path}\\{current_date}\\There is no Version'

                            GeneralFolderActionClass().check_path_exist_and_create(f'{new_dir_path}')

                            # Save to .CSV file
                            save_to_csv(full_path_to_save, reboot_data_dataframe, logger)

                            # Report to ELK
                            RebootCareReportToELK().process(data_dict=reboot_data_dict, file_name=file_name)
                            print()

                            # move file to relevant folder
                            shutil.move(f'{dir_path}\\{file_name}', f'{new_dir_path}\\{file_name}')
                            logger.info(f'Move to: {new_dir_path}\\{file_name}')
                        except Exception:
                            logger.exception('There is a analyzing problem')

                            # close tar.gz file (Crash info file)
                            if tar:
                                close_tar_gz_file_reader(tar)

                            # move file to relevant folder
                            shutil.move(f'{dir_path}\\{file_name}', f'{listener_path}\\{current_date}\\There is a analyzing problem\\{file_name}')
                            logger.info(f'Move to: {listener_path}\\{current_date}\\There is a analyzing problem\\{file_name}')
                    if not recursive['is_active']:
                        break
                    else:
                        continue
                except Exception:
                    logger.exception('')
        except Exception:
            logger.exception('')

        logger.info('Waiting 600 sec')
        time.sleep(600)
