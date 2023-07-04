import os

from InfrastructureSVG.Projects.FiveG.CoreCare.CoreCareApplication.CoreCareMainFunction import main

# Global Configuration:
SITE = 'IL Dev'
# SITE = 'IL SVG'
# SITE = 'Customer Tier3'
HOST_NAME = '8.8.8.8'  # To check availability

username = os.getlogin()
SERVER_PATH = f'C:\\Users\\{username}\\Desktop\\Temporary - can be deleted\\CoreCare\\ForTest\\!Summary'
LAST_ROW_INDEX_PATH = \
    os.getcwd().split("CoreCareApplication")[:-1][0] + \
    'CoreCareApplication' + \
    f'\\data\\Last_Index_Of_Summery_Cores\\Test\\{SITE.replace(" ", "_")}_Last_Index_Of_Summery_Cores_Test.csv'

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
        replace_test_environments=REPLACE_TEST_ENVIRONMENTS,
        test_flag=True
    )
