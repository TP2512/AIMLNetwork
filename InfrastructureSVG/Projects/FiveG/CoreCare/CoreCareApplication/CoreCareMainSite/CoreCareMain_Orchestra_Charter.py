import os

from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareApplication.CoreCareMainFunction import main


# Global Configuration:
# SITE = 'Orchestra_Lab Charter'
SITE = 'Orchestra_Lab None'
HOST_NAME = '192.168.127.247'  # To check availability
SERVER_PATH = '\\\\192.168.127.247\\Cores\\Orchestra\\Summary'
LAST_ROW_INDEX_PATH = os.getcwd().split("CoreCareApplication")[:-1][0] + 'CoreCareApplication' + \
                      f'\\data\\Last_Index_Of_Summery_Cores\\{SITE.replace(" ", "_")}_Last_Index_Of_Summery_Cores.csv'

# Listener Configuration:
PATTERNS = ["csv"]
RECURSIVE = False
days_before = 3
old_size = 0

# Process Configuration:
OPEN_DEFECT = True
LINK_TO_LAST_DEFECT = [False, None]
REPLACE_TEST_ENVIRONMENTS = {"REPLACE": True, "PATH": ""}

if __name__ == '__main__':
    main(
        site=SITE,
        host_name=HOST_NAME,
        server_path=SERVER_PATH,
        last_row_index_path=LAST_ROW_INDEX_PATH,
        patterns=PATTERNS,
        recursive=RECURSIVE,
        days_before=days_before,
        old_size=old_size,
        open_defect=OPEN_DEFECT,
        link_to_last_defect=LINK_TO_LAST_DEFECT,
        replace_test_environments=REPLACE_TEST_ENVIRONMENTS
    )
