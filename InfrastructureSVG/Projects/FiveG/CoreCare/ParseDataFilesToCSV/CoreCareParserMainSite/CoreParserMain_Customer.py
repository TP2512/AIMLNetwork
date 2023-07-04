from pathlib import Path

from InfrastructureSVG.Projects.FiveG.CoreCare.ParseDataFilesToCSV.CoreParserMainFunction import core_parser_main

"""
Create Summary Files

Steps:
1. get all files
2. parse each file and add him data to relevant csv (by date)
3. move the each file to relevant folder (by date, by version)
"""

PROJECT_NAME = 'CoreCare 5G Parser csv'
SITE = 'Customer Tier3'
LISTENER_PATH = '\\\\192.168.127.247\\Cores\\Customers'
PATH_TO_SAVE = f'{Path.cwd().parent.__str__()}\\SummaryFiles\\Customers'
SETUP_NAME_LIST_PATH = '\\\\192.168.127.247\\Cores\\Customers\\MoreInformation\\setup_names.csv'
NETWORK_ADDRESS = [
    'inet 172.20', 'inet 172.26', 'inet 172.27',
    'inet6 fc74:172:20', 'inet6 fc74:172:26', 'inet6 fc74:172:27:124', 'inet6 fc74:172:27'
]
RECURSIVE = {'is_active': True, 'recursive_number': 2}

WITHOUT_ENTITY = None


if __name__ == '__main__':
    core_parser_main(
        project_name=PROJECT_NAME,
        site=SITE,
        listener_path=LISTENER_PATH,
        path_to_save=PATH_TO_SAVE,
        setup_name_list_path=SETUP_NAME_LIST_PATH,
        network_address=NETWORK_ADDRESS,
        recursive=RECURSIVE,
        without_entity=WITHOUT_ENTITY
    )
