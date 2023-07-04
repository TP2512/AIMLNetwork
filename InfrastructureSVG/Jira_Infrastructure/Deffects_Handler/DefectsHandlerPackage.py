import logging
from jira import JIRAError


class DefectsHandler:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def check_for_current_status(self, current_status, also_display=False):
        try:
            if also_display and current_status == 'Duplicate':
                return True
            elif current_status in [
                'Pending',
                'Processing',
                'Parked',
                'To Reproduce',
                'Fixed in R&D',
                'VERIFY FAIL',
                'Ready for Verification',
                'Assigned to 3rd Party',
                'Need more Info',
                'Verify Fail',
                'Screening'
            ]:
                return True  # ==>  Update Defect
            else:
                return False  # ==>  Create Defect
        except Exception as err:
            self.logger.error(err)
            return None

    def state_machine_open_defect(self, jira, epic_number, also_display=False):
        open_defect = []  # if empty ==>  Update Defect  # if not empty ==>  Create Defect

        try:
            if jira.issue(epic_number):
                if def_exist := jira.search_issues(f'issue in linkedissues({str(epic_number)})', maxResults=5000):
                    len_def_exist = len(def_exist)
                    if len_def_exist == 1:
                        defect_number = str(def_exist[0])
                        def_status_to_print = self.get_status_defects(jira, def_exist)
                        self.logger.info(str(def_status_to_print))
                        for defect in def_status_to_print:
                            if self.check_for_current_status(def_status_to_print[defect], also_display):
                                self.logger.info(f'one Defect with status open was found: {defect_number}')
                                open_defect.append(defect)
                            else:
                                self.logger.info(f'There is no Defect with status open was found: {defect_number}')

                    elif len_def_exist > 1:
                        self.logger.info('More from one Defect (with status open) was found:')
                        def_status_to_print = self.get_status_defects(jira, def_exist)
                        self.logger.info(str(def_status_to_print))
                        open_defect.extend(defect for defect in def_status_to_print if self.check_for_current_status(def_status_to_print[defect]))

                    else:
                        self.logger.info('len(Defect) < 1')
                        self.logger.info("Need to create new defect")
                        return None  # ==>  Create Defect
                else:
                    self.logger.info('Defect was not found')
                    self.logger.info("Need to create new defect")
                    return None  # ==>  Create Defect

                if open_defect:
                    self.logger.info(f"Need to update {open_defect}")
                    return open_defect  # ==>  Update Defect
                else:
                    self.logger.info("Need to create new defect - else")
                    return None  # ==>  Create Defect
        except Exception as err:
            self.logger.error(err)
            return None

    def get_status_defects(self, jira, defects_list):
        """
        This function responsible for get "status" field data from issue type "DEF" on "Defect Tracking" project
        in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "defects_list" - parameter need to be a list of defects (DEF-number)
                * for example: ['DEF-123', 'DEF-456', 'DEF-789']

        The function return 1 parameters:
            - "defects_status" - parameter need to be a dictionary of the defects status ({DEF-number: status defect})
                * for example: {'DEF-123': 'Pending', 'DEF-789': Parked}
        """
        try:
            defects_status = {}
            for defect in defects_list:
                defect_issue_num = jira.issue(defect)
                status_defect = defect_issue_num.fields.status
                defects_status[str(defect)] = str(status_defect)
                # defects_status.update(status_defect)
            return defects_status
        except JIRAError:
            self.logger.exception('')
        except Exception as err:
            self.logger.error(err)
