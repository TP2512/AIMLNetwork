import sys
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging
from InfrastructureSVG.Projects.General.PurgeClosedDefects.PurgeClosedDefects import PurgeClosedDefects
import datetime
import os

PROJECT_NAME = 'Purge Close Defects'

ACTIVE_DATE_TIME = datetime.datetime.now(datetime.timezone.utc)
DATE_STRING = ACTIVE_DATE_TIME.strftime("%Y.%m.%d")
TIME_STRING = ACTIVE_DATE_TIME.strftime("%H.%M")
SITE = 'IL SVG'
hostname = os.getenv('COMPUTERNAME')
if hostname == 'ASIL-RBLUMBERG' or hostname == 'ASIL-SV-AU1':
    MAIL_RECIPIENTS = ['rblumberg@airspan.com']
else:
    MAIL_RECIPIENTS = ['akimiagarov@airspan.com', 'erahman@airspan.com', 'oatzmon@airspan.com', 'azaguri@airspan.com', 'yfarber@airspan.com', 'rblumberg@airspan.com']



def build_logger(site: str):
    log_file_name = f'{DATE_STRING}_{TIME_STRING} - {PROJECT_NAME.replace(" ", "_")}_Logs_{site.replace(" ", "_")}'
    log_path = f'C:\\Python Logs\\{PROJECT_NAME}\\{site}'
    return ProjectsLogging(project_name=PROJECT_NAME, path=log_path, file_name=log_file_name).project_logging(timestamp=True)


if __name__ == "__main__":
    print(f'Start {PROJECT_NAME}')
    logger = build_logger(site=SITE)

    # purged_folders_path_list_ = [
    #     r"C:\Users\rblumberg\main\TestDefectsFolder",
    #     r"C:\Users\rblumberg\main\TestDefectsFolder2"
    # ]
    try:
        purged_folders_path_list_ = sys.argv
        logger.info(purged_folders_path_list_)
        operation_start_time = datetime.datetime.now(datetime.timezone.utc)
        purge_closed_defects_ = PurgeClosedDefects(purged_folders_path_list_[1:], MAIL_RECIPIENTS)
        purged_folders_chunks_list_, removed_empty_folders_list_ = purge_closed_defects_.get_defect_chunks(operation_start_time)
        purge_closed_defects_.logStorage.calculate_average_defect_storage_size(purged_folders_chunks_list_)
        filtered_defects_chunks_list_, removed_closed_old_defect_folders_list_, error_list_ = \
            purge_closed_defects_.filter_and_delete_folder_by_chunk_by_status_closed(purged_folders_chunks_list_, operation_start_time)
        purge_closed_defects_.logStorage.purge_operation_output(purged_folders_chunks_list_,
                                                                removed_empty_folders_list_,
                                                                removed_closed_old_defect_folders_list_,
                                                                error_list_)
        purge_closed_defects_.logStorage.send_run_summary_mail(purge_closed_defects_.debug_flag)
    except Exception:
        logger.exception('Main function exception')
