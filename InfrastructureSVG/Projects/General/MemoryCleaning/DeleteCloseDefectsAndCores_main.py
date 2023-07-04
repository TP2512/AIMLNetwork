import os
import sys
import time
from pathlib import Path

# ROOT_PATH = Path.cwd().parent.parent.parent.parent.__str__()
ROOT_PATH = Path.cwd().__str__()
print(f'Root path is: {ROOT_PATH}')
sys.path.append(ROOT_PATH)
# time.sleep(5)

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Projects.General.MemoryCleaning.DeleteCloseDefects import DeletePerCloseDefect


# Project name on Jenkins: "DeleteCloseDefectsAndCores"
if __name__ == '__main__':
    # debug = True
    debug = False

    project_name, site = 'Delete Close Defects And Cores', 'IL SVG'

    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=debug)

    try:
        logger.info('Start to delete Close Core Defects')
        close_defects = DeletePerCloseDefect()
        close_defects.delete_cores_from_core_server(debug=debug)
    except Exception as err:
        logger.exception('')

    try:
        logger.info('Start to delete Close Defects From "Defect" Folder')
        close_defects = DeletePerCloseDefect()
        close_defects.delete_defects_from_defects_folder(debug=debug)
    except Exception as err:
        logger.exception('')
