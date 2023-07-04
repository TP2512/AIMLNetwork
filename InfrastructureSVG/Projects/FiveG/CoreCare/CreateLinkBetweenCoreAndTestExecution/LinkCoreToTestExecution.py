import logging
import time

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira


class LinkCoreToTestExecution:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def link_core_to_test_execution_process(self, days=5):
        while True:
            try:
                jira_client = JiraActions(app_credentials='CoreCare')
                create_object_on_jira = CreateObjectOnJira(jira_client=jira_client)

                while True:
                    try:
                        test_execution_filter = f'project = "SVG Automation (IL)" AND issuetype = "Test Execution" AND "Core file names" is not EMPTY And created >= -{days}d'
                        test_execution_list = create_object_on_jira.automation_helper.get_by_filter(str_filter=test_execution_filter)
                        self.logger.info(f'Test Execution list is: {test_execution_list}')
                        self.logger.info(f'len of Test Execution list is: {len(test_execution_list)}')
                        for test_execution_index, test_execution in enumerate(test_execution_list, start=1):
                            self.logger.info('\n\n #####################################')
                            self.logger.info(f'Test Execution index: {test_execution_index}, key: {test_execution}')
                            core_file_name_list = test_execution.fields.customfield_19502
                            self.logger.info('')
                            self.logger.info(f'Core list is: {core_file_name_list}')
                            self.logger.info(f'len of Core file name list is: {len(core_file_name_list)}')
                            for core_file_name in core_file_name_list:
                                self.logger.info('')
                                self.logger.info(f'Core file name is: {core_file_name}')
                                core_filter = f'project = CORE AND issuetype = Core AND Notes ~ "{core_file_name}"'
                                core_list = create_object_on_jira.automation_helper.get_by_filter(str_filter=core_filter)
                                self.logger.info(f'Core list is: {core_list}')
                                self.logger.info(f'len of Core list is: {len(core_list)}')
                                if not core_list:
                                    self.logger.error(f'There is no Core with the name {core_file_name}')
                                    continue
                                for core in core_list:
                                    self.logger.info('')
                                    self.logger.info(f'core details is: {core.key} - {core.fields.summary}')
                                    create_object_on_jira.create_link_between_two_object(link_from_issue=core.key, link_to_issue=test_execution.key, project='relates to')
                                    # self.logger.info(f'{core.key} was linked to {test_execution.key}')
                    except Exception:
                        self.logger.exception('while 2\n\n')
                        break
                    t = 600
                    self.logger.info(f'\n\nsleeping {t} sec\n\n')
                    time.sleep(t)
            except Exception:
                self.logger.exception('while 1\n\n')
                time.sleep(600)


if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    link_core_to_test_execution = LinkCoreToTestExecution()
    link_core_to_test_execution.link_core_to_test_execution_process(days=4)
