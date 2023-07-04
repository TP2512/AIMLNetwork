import time
import json

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareApplication.CoreCareDataClass import CrashParameters, \
    GlobalConfiguration, ListenerConfiguration, ProcessConfiguration
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareData import *
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareApplication.CoreCareListener_Infrastructure import CoreCareListener
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareApplication.CoreCareStructure \
    import CoreProcess, CUCPCoreProcess, CUUPCoreProcess, DUCoreProcess, RUCoreProcess, DUPhyAssertProcess, RUPhyAssertProcess, \
    L2CoreProcess, L3CoreProcess, XPUCoreProcess


def get_type_crash_dict():
    return {
        'unknown crash': CoreProcess(),
        'cucp core': CUCPCoreProcess(),
        'cuup core': CUUPCoreProcess(),
        'du core': DUCoreProcess(),
        'ru core': RUCoreProcess(),
        'du phy_assert': DUPhyAssertProcess(),
        'ru phy_assert': RUPhyAssertProcess(),
        'core l2': L2CoreProcess(),
        'core l3': L3CoreProcess(),
        'xpu core': XPUCoreProcess()
    }


def main(site: str, host_name: str, server_path: str, last_row_index_path: str, patterns: list, recursive: bool,
         days_before: int, old_size: int, open_defect: bool, link_to_last_defect, replace_test_environments: dict, test_flag=False):
    # sourcery skip: low-code-quality

    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    global_configuration = GlobalConfiguration(patterns, PROJECT_NAME, host_name, server_path, last_row_index_path)
    listener_configuration = ListenerConfiguration(recursive, days_before, old_size)
    logger.info(
        f'Initial parameters is: \n'
        f'Global Configuration is: \n{json.dumps(global_configuration.__dict__, indent=2, separators=(", ", " = "))}\n\n'
        f'Listener Configuration is: \n{json.dumps(listener_configuration.__dict__, indent=2, separators=(", ", " = "))}\n\n'
    )

    type_crash_dict = get_type_crash_dict()
    while True:
        core_care_process = CoreCareListener(**global_configuration.__dict__, **listener_configuration.__dict__)

        try:
            jira_client = JiraActions(app_credentials='CoreCare')

            dataframe = core_care_process.start_corecare_listener()
            index = 0
            for row_index, row in dataframe.iterrows():
                index += 1
                try:
                    logger.info('\n\n\n')
                    logger.info(f'Start New .csv Line - {index}/{len(dataframe)}')
                    logger.info(f'The current file is: "{row["Crash File Name"]}"')

                    if jira_client.search_by_filter(str_filter=f'project = CORE AND issuetype = Core AND Notes ~ {row["Crash File Name"]}'):
                        logger.error('This crash file already exists in Jira - continue to the next crash.')
                        if not test_flag:
                            continue

                    process_configuration = ProcessConfiguration(open_defect, link_to_last_defect, replace_test_environments)
                    # logger.info(f'Process Configuration is: \n{json.dumps(process_configuration.__dict__, indent=2, separators=(", ", " = "))}\n\n')

                    crash_details_class = CrashParameters(row=row, site=site, test_flag=test_flag)
                    crash_details = crash_details_class.__dict__

                    if not crash_details['gnb_version']:
                        logger.error(f'There is no crash version for "{row["Crash File Name"]}"')
                        continue

                    app = type_crash_dict[crash_details['type_crash_name']]
                    del crash_details['row']
                    app.process(crash_details, process_configuration=process_configuration.__dict__, jira_client=jira_client)
                    print()
                except Exception as e:
                    if e:
                        logger.error('There is a main 1 exception !!!')
                    logger.exception('')
            time.sleep(0.2)
            print()
        except Exception as e:
            if e:
                logger.error('There is a main 2 exception !!!')
            logger.exception('')
