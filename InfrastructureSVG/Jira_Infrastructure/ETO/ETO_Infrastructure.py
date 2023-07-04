import logging
from jira import JIRAError


class CreateETOClass:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def create_eto_issue(self, jira, version, chipset):
        try:
            return jira.create_issue(
                project={'id': '12700'},
                summary=f'{str(chipset)} {str(version)}',
                issuetype={'name': 'SwBuildEngineTime'},
                customfield_10510={'value': chipset}
            )

        except JIRAError:
            self.logger.exception('')
            return None
        except Exception:
            self.logger.exception('')
            return None

    def create_eto_issue_num(self, jira, eto):
        """
        This function responsible Create "Epic/Core issue client" on "CoreCare" project in Jira_Infrastructure -
        Checks whether this "CORE-number" exists

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "eto" - parameter need to be CORE-number,
                * for example: SVG-12345

        The function return 1 parameters:
            - "epic_core_issue_num" - client of jira per "Epic" or "Core" issue type
        """

        try:
            return jira.issue(eto)
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception:
            self.logger.exception('')
            return None


class UpdateETOClass:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def update_minimum_run_time(self, jira, eto_number, min_run_time):
        """
           This function responsible for update_actual_result

           The function get 2 parameters:
               - "execution" - parameter need to be a string (execution key)
               - "Traffic Transport Layer Protocol" -  parameter need to be a string

           The function return PUT response (200 = ok, else = fail)
        """
        try:
            issue_num = jira.issue(eto_number)
            issue_num.update(fields={"customfield_12652": min_run_time})  # minimum_run_time
            self.logger.info(f'{str(eto_number)} was updated with {str(min_run_time)}')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.exception(f'{str(eto_number)} was not updated with {str(min_run_time)}')

            self.logger.exception(f"description_ = {str(min_run_time)}")

    def update_maximum_run_time(self, jira, eto_number, max_run_time):
        """
           This function responsible for update_actual_result

           The function get 2 parameters:
               - "execution" - parameter need to be a string (execution key)
               - "Traffic Transport Layer Protocol" -  parameter need to be a string

           The function return PUT response (200 = ok, else = fail)
        """
        try:
            issue_num = jira.issue(eto_number)
            issue_num.update(fields={"customfield_12667": max_run_time})  # minimum_run_time
            self.logger.info(f'{str(eto_number)} was updated with {str(max_run_time)}')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.exception(f'{str(eto_number)} was not updated with {str(max_run_time)}')

            self.logger.exception(f"description_ = {str(max_run_time)}")

    def update_core_occurrence_count(self, jira, eto_number, core_count):
        """
           This function responsible for update_actual_result

           The function get 2 parameters:
               - "execution" - parameter need to be a string (execution key)
               - "Traffic Transport Layer Protocol" -  parameter need to be a string

           The function return PUT response (200 = ok, else = fail)
        """
        try:
            issue_num = jira.issue(eto_number)
            issue_num.update(fields={"customfield_15000": core_count})  # minimum_run_time
            self.logger.info(f'{str(eto_number)} was updated with {str(core_count)}')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.exception(f'{str(eto_number)} was not updated with {str(core_count)}')

            self.logger.exception(f"Core_count = {str(core_count)}")

    def update_time_to_first_crash(self, jira, eto_number, time_to_first_crash):
        """
           This function responsible for update_actual_result

           The function get 2 parameters:
               - "execution" - parameter need to be a string (execution key)
               - "Traffic Transport Layer Protocol" -  parameter need to be a string

           The function return PUT response (200 = ok, else = fail)
        """
        try:
            issue_num = jira.issue(eto_number)
            issue_num.update(fields={"customfield_16400": time_to_first_crash})  # minimum_run_time
            self.logger.info(f'{str(eto_number)} was updated with {str(time_to_first_crash)}')

        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.exception(f'{str(eto_number)} was not updated with {str(time_to_first_crash)}')

            self.logger.exception(f"Time_to_first_crash = {str(time_to_first_crash)}")

    def update_system_uptime(self, jira, eto_number, system_uptime):
        """
           This function responsible for update_actual_result

           The function get 2 parameters:
               - "execution" - parameter need to be a string (execution key)
               - "Traffic Transport Layer Protocol" -  parameter need to be a string

           The function return PUT response (200 = ok, else = fail)
        """
        try:
            issue_num = jira.issue(eto_number)
            issue_num.update(fields={"customfield_14801": system_uptime})  # minimum_run_time
            self.logger.info(f'{str(eto_number)} was updated with {str(system_uptime)}')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.exception(f'{str(eto_number)} was not updated with {str(system_uptime)}')

            self.logger.exception(f"system_uptime = {str(system_uptime)}")

    def update_total_scenario_runtime(self, jira, eto_number, total_scenario_runtime):
        """
           This function responsible for update_actual_result

           The function get 2 parameters:
               - "execution" - parameter need to be a string (execution key)
               - "Traffic Transport Layer Protocol" -  parameter need to be a string

           The function return PUT response (200 = ok, else = fail)
        """
        try:
            issue_num = jira.issue(eto_number)
            issue_num.update(fields={"customfield_16500": total_scenario_runtime})  # minimum_run_time
            self.logger.info(f'{str(eto_number)} was updated with {str(total_scenario_runtime)}')

        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.exception(f'{str(eto_number)} was not updated with {str(total_scenario_runtime)}')

            self.logger.exception(f"system_uptime = {str(total_scenario_runtime)}")

    def update_mtbf(self, jira, eto_number, mtbf):
        try:
            issue_num = jira.issue(eto_number)
            issue_num.update(fields={"customfield_16306": mtbf})  # minimum_run_time
            self.logger.info(f'{str(eto_number)} was updated with {str(mtbf)}')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.exception(f'{str(eto_number)} was not updated with {str(mtbf)}')
            self.logger.exception(f"system_uptime = {str(mtbf)}")

    def update_cores_count_per_build(self, jira, eto_number, core_count):
        try:
            issue_num = jira.issue(eto_number)
            issue_num.update(fields={"customfield_15000": core_count})  # minimum_run_time
            self.logger.info(f'{str(eto_number)} was updated with {str(core_count)}')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.exception(f'{str(eto_number)} was not updated with {str(core_count)}')

            self.logger.exception(f"core_count = {str(core_count)}")

    def update_mtbf_cores_count_per_build(self, jira, eto_number, mtbf_core_count):
        """
           This function responsible for update_actual_result

           The function get 2 parameters:
               - "execution" - parameter need to be a string (execution key)
               - "Traffic Transport Layer Protocol" -  parameter need to be a string

           The function return PUT response (200 = ok, else = fail)
        """
        try:
            issue_num = jira.issue(eto_number)
            issue_num.update(fields={"customfield_16700": mtbf_core_count})  # minimum_run_time
            self.logger.info(f'{str(eto_number)} was updated with {str(mtbf_core_count)}')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.exception(f'{str(eto_number)} was not updated with {str(mtbf_core_count)}')

            self.logger.exception(f"mtbf_core_count = {str(mtbf_core_count)}")
