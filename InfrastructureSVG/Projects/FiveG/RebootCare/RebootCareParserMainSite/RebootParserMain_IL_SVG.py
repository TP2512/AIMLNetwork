from InfrastructureSVG.Projects.FiveG.RebootCare.RebootCareParserMainFunction import reboot_care_parser_main


local = False

PROJECT_NAME = 'CoreCare 5G Parser csv'
SITE = 'IL SVG'
if local:
    LISTENER_PATH = 'C:\\Users\\azaguri\\Downloads\\RebootCare'
    PATH_TO_SAVE = 'C:\\Users\\azaguri\\Downloads\\RebootCare\\Summary'
else:
    LISTENER_PATH = '\\\\192.168.127.247\\Cores\\RebootCare'
    PATH_TO_SAVE = '\\\\192.168.127.247\\Cores\\RebootCare\\Summary'

RECURSIVE = {'is_active': False, 'recursive_number': 1}
WITHOUT_ENTITY = None


if __name__ == '__main__':
    reboot_care_parser_main(
        project_name=PROJECT_NAME,
        site=SITE,
        listener_path=LISTENER_PATH,
        path_to_save=PATH_TO_SAVE,
        recursive=RECURSIVE,
        # without_entity=WITHOUT_ENTITY
    )
