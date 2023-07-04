import logging

from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger


class CreateCore:
    def __init__(self, crash_details):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.crash_details = crash_details
        self.jira_client = JiraActions(app_credentials='CoreCare')

        self.core = None

    def create_core(self):  # sourcery skip: remove-redundant-fstring
        description = '{code:java|title=core headline}\n' + self.crash_details["back_trace"].replace(" -> ", "\n") + '{code}\n\n'
        minimal_core_data = [
            # Required fields
            {'reporter': [f'CoreCare-5G']},  # reporter
            {'summary': [f'{self.crash_details["back_trace"][-254:]}']},  # summary
            {'customfield_10202': ['Unknown']},  # product at fault

            # Other fields
            {'description': [f'{description}']},  # description
            {'customfield_18301': [f'{self.crash_details["back_trace_hash"]}']},  # Hash BT
            {'customfield_18302': [f'{self.crash_details["core_pid"]}']},  # Crash PID
            {'labels': [f'{self.crash_details["back_trace_hash"]}']},  # hash number
            {'fixVersions': [f'SR{self.crash_details["crash_version"].split("-", 1)[0]}']},  # SR Versions
            {'customfield_13707': [f'{self.crash_details["crash_version"]}']},  # g/eNodeB SW version
            {'customfield_14900': [f'{self.crash_details["site"]}']},  # core discovery site
            {'customfield_10736': [{
                'value': f'{self.crash_details["site"].split(" ", 1)[0]}',
                'child': f'{self.crash_details["site"].split(" ", 1)[1]}'
            }]
            },  # Discovery Site / Customer
            {'customfield_12600': [f'{self.crash_details["link_to_core"]}\\{self.crash_details["core_file_name"]}']},  # core files path
            {'customfield_11003': [f'{self.crash_details["ip_address"]}', f'{self.crash_details["setup_name"]}']},  # test environments

            #
            {'customfield_10975': [f'{self.crash_details["core_file_name"]}']},  # Notes
        ]

        self.core = self.jira_client.create_issue(project='CORE', issue_type='Core', data=minimal_core_data)

        if self.core:
            self.logger.info(f'Core was created')
            self.logger.info(f'Core key is: {self.core}\n')
        else:
            self.logger.error(f'Core was not created')

        print()


if __name__ == '__main__':
    PROJECT_NAME = 'CreateCore'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    crash_details_ = {
        "site": 'IL SVG',
        "back_trace": 'Back Trace Aviz Test',
        "description": "Description Aviz Test",
        "back_trace_hash": "12345",
        "core_pid": "555",
        "crash_version": "19.00-147-1.13",
        "link_to_core": "xxx",
        "core_file_name": "SomeFileName",
        "ip_address": "1.1.1.1",
        "setup_name": "AvizTest",
    }

    CreateCore(crash_details_).create_core()
