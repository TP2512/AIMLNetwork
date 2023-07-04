from termcolor import colored
from jira import JIRAError
import logging

""" 
In this py file have 3 class
    - CreateCoreCareClass
    - UpdateCoreCareClass
    - GetFromCoreCareClass
"""


class CreateCoreCareClass:
    """ This class ("CreateCoreCareClass") responsible for creating on "CoreCare" project in Jira """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    # def create_epic_issue_num(self, jira, epic_core_number):
    def create_epic_core_issue_num(self, jira, epic_core_number):
        """
        This function responsible Create "Epic/Core issue client" on "CoreCare" project in Jira -
        Checks whether this "CORE-number" exists

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "epic_core_issue_num" - client of jira per "Epic" or "Core" issue type
        """

        try:
            return jira.issue(epic_core_number)
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def create_minimal_epic(self, jira, epic_summary, epic_name, epic_description='', epic_labels_list=''):
        """
        This function responsible Create minimal "Epic" issue type on "CoreCare" project in Jira

        The function get 5 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_summary" - the summary of the "Epic" issue type (string type)
            - "epic_name" - the name of the "Epic" issue type (string type)
            - "epic_description" - the description of the "Epic" issue type (string type) [optional]
            - "epic_labels_list" - the labels of the "Epic" issue type (list of string type) [optional]

        The function return 1 parameters:
            - "epic_number" - parameter need to be CORE-number,
                * for example: CORE-12345
        """
        try:
            return jira.create_issue(
                project='CORE',
                issuetype={'name': 'Epic'},
                customfield_10002=epic_name[-254:],
                summary=epic_summary[-254:],
                description=epic_description[:32767],
                labels=epic_labels_list,
            )

        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def create_minimal_core(self, jira, core_summary, core_description, core_discovery_site, core_labels_list='',
                            core_product_at_fault='BS / eNB'):
        """
        This function responsible Create minimal "Core" issue type on "CoreCare" project in Jira -

        The function get 5 parameter:
            - "jira" - parameter need to be client of jira
            - "core_summary" - the summary of the "Core" issue type (string type)
            - "core_description" - the description of the "Core" issue type (string type)
            - "core_discovery_site" - the discovery site of the "Core" issue type (list of string type)
            - "core_labels_list" - the labels of the "Core" issue type (list of string type) [optional]
            - "core_product_at_fault" - the product type of the "Core" issue type (string type) [optional]

        The function return 1 parameters:
            - "core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
        """

        try:
            return jira.create_issue(
                project={'id': '12700'},
                issuetype={'name': 'Core'},
                summary=core_summary[-254:],
                description=core_description[:32767],
                customfield_10202={'value': core_product_at_fault},
                labels=core_labels_list,
                customfield_14900={'value': core_discovery_site},
            )

        except JIRAError:
            self.logger.exception('')
        except Exception as err:
            self.logger.error(err)

    def create_minimal_phy_assert(self, jira, phy_assert_summary, phy_assert_description, core_discovery_site,
                                  sr_version,
                                  phy_assert_labels_list='', phy_assert_product_at_fault='BS / eNB'):
        """
        This function responsible Create minimal "PhyAssert" issue type on "CoreCare" project in Jira -

        The function get 5 parameter:
            - "jira" - parameter need to be client of jira
            - "phy_assert_summary" - the summary of the "PhyAssert" issue type (string type)
            - "phy_assert_description" - the description of the "PhyAssert" issue type (string type)
            - "phy_assert_labels_list" - the labels of the "PhyAssert" issue type (list of string type) [optional]
            - "phy_assert_product_at_fault" - the product type of the "PhyAssert" issue type (string type) [optional]

        The function return 1 parameters:
            - "core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
        """

        try:
            core_number = jira.create_issue(project={'id': '12700'},
                                            issuetype={'name': 'PhyAssert'},
                                            fixVersions=[{'name': sr_version}],
                                            summary=phy_assert_summary[-254:],
                                            description=phy_assert_description[:32767],
                                            customfield_10202={'value': phy_assert_product_at_fault},
                                            labels=phy_assert_labels_list,
                                            customfield_14900={'value': core_discovery_site},
                                            # customfield_10712={'value': 'Stability 2 Ues'},
                                            )
            return core_number
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def create_issue_link(self, jira, epic_core_number, defect_number):
        """
        This function responsible for create "issue link" to issue type "Epic" or "Core" on "CoreCare" project in
        Jira -> defect occurrence count

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "defect_number" - parameter need to be a string of defects (DEF-number)
                * for example: DEF-12345

        The function return 0 parameters
        """

        try:
            jira.create_issue_link('CoreCare', epic_core_number, defect_number)
            self.logger.info(f'{str(defect_number)} was linking to {str(epic_core_number)}')

        except JIRAError:
            self.logger.exception(f'{str(defect_number)} was not linking to {str(epic_core_number)}')

        except Exception:
            self.logger.error(f'{str(defect_number)} was not linking to {epic_core_number}')


class UpdateCoreCareClass:
    """ This class ("CreateCoreCareClass") responsible for updating on "CoreCare" project in Jira """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def update_core_discovery_site(self, jira, epic_core_number, core_discovery_site):
        """
        This function responsible for update the "Core Discovery Site" field in issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "core_discovery_site" - parameter need to be a string of the core discovery site (string type)

        The function return 0 parameters
        """

        try:
            issue_num = jira.issue(epic_core_number)
            issue_num.update(fields={"customfield_14900": {'value': str(core_discovery_site)}})
            self.logger.info(str(epic_core_number) + ' was update with "core_discovery_site"')
        except JIRAError:
            self.logger.exception(str(epic_core_number) + ' was not update with "core_discovery_site"')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "core_discovery_site"')

    def update_status_fields(self, jira, epic_core_number, new_status):
        """
        This function responsible for update the "status" field in issue type "Epic" or "Core" on "CoreCare" project
        in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "new_status" - parameter need to be a string of the current status (string type)

        The function return 0 parameters
        """

        try:
            jira.transition_issue(epic_core_number, transition=new_status)
            self.logger.info(str(epic_core_number) + ' was update with "status"')
        except JIRAError:
            self.logger.exception(str(epic_core_number) + ' was not update with "status"')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "status"')

    def update_labels(self, jira, epic_core_number, labels_list):
        """
        This function responsible for update/add "labels" field in issue type "Epic" or "Core" on "CoreCare" project
        in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "labels_list" - parameter need to be a list or string (without spaces) of the labels (list of string type)
                * for example: ['Avi', 'Zaguri'] or 'AviZaguri

        The function return 0 parameters
        """

        new_labels_list = []
        try:
            issue_num = jira.issue(jira, epic_core_number)
            current_labels_list = GetFromCoreCareClass().get_labels(jira, epic_core_number)
            if type(current_labels_list) is not list:
                new_labels_list.append(current_labels_list)
            else:
                new_labels_list = current_labels_list
            if type(labels_list) is not list:
                new_labels_list.append(labels_list)
            else:
                for labels in labels_list:
                    new_labels_list.append(labels)
            issue_num.update(fields={"labels": new_labels_list})
            self.logger.info(str(epic_core_number) + ' was update with "labels"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "labels"')
            self.logger.error(f"new_labels_list = {str(new_labels_list)}")

    def update_enb_software_version(self, jira, epic_core_number, enb_software_version):
        """
        This function responsible for update "eNB software version" field in issue type "Epic" or "Core"
        on "CoreCare" project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "enb_software_version" - the software version of the eNB (list of string type / string type)

        The function return 0 parameters
        """

        new_enb_software_version_list = []
        try:
            issue_num = jira.issue(epic_core_number)
            if current_enb_software_version := GetFromCoreCareClass().get_enb_software_version(jira, epic_core_number):
                if type(current_enb_software_version) is not list:
                    new_enb_software_version_list.append(current_enb_software_version)
                else:
                    new_enb_software_version_list = current_enb_software_version
            if type(enb_software_version) is not list:
                new_enb_software_version_list.append(enb_software_version)
            else:
                for labels in enb_software_version:
                    new_enb_software_version_list.append(labels)
            issue_num.update(fields={"customfield_13707": new_enb_software_version_list})
            self.logger.info(str(epic_core_number) + ' was update with "enb_software_version"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "new_enb_software_version_list"')
            self.logger.error(f"new_enb_software_version_list = {str(new_enb_software_version_list)}")

    def update_hyper_link(self, jira, epic_core_number, hyper_link=''):
        """
        This function responsible for update/add "hyper link" field in issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "hyper_link" - hyper link to specific path (string type)

        The function return 0 parameters
        """

        try:
            issue_num = jira.issue(epic_core_number)
            issue_num.update(fields={"customfield_12600": hyper_link})
            self.logger.info(str(epic_core_number) + ' was update with "hyper_link"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "hyper_link"')
            self.logger.error(f"hyper_link = {str(hyper_link)}")

    def update_core_occurrence_count(self, jira, epic_core_number):
        """
        This function responsible for update "core occurrence count" field in issue type "Epic" or "Core"
        on "CoreCare" project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 0 parameters
        """

        core_occurrence_count = 'error to get core_occurrence_count'
        try:
            core_occurrence_count = GetFromCoreCareClass().get_core_occurrence_count(jira, epic_core_number)
            issue_num = jira.issue(epic_core_number)
            issue_num.update(fields={"customfield_15000": core_occurrence_count})  # core occurrence count
            self.logger.info(str(epic_core_number) + ' was update with "core_occurrence_count"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "core_occurrence_count"')
            self.logger.error(f"core_occurrence_count = {str(core_occurrence_count)}")

    def update_core_layer_type(self, jira, epic_core_number, core_layer_type):
        """
        This function responsible for update/add "core layer type" field in issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "core_layer_type" - parameter need to be a string (without spaces) (string type)
                * for example:

        The function return 0 parameters
        """

        try:
            if core_layer_type and core_layer_type != '' and core_layer_type != 'N/A':
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_14800": {'value': str(core_layer_type)}})
                self.logger.info(str(epic_core_number) + ' was update with "core_layer_type"')
            else:
                self.logger.exception(str(epic_core_number) + ' was not update with "core_layer_type" - else')
        except JIRAError:
            self.logger.info('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "core_layer_type"')
            self.logger.error(f"core_layer_type = {str(core_layer_type)}")

    def update_bs_hardware_type(self, jira, epic_core_number, bs_hardware_type):
        """
        This function responsible for update/add "bs hardware type" field in issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "bs_hardware_type" - the hardware type eNB(without spaces) (string type from list on Jira)
                * for example: 2.5G, Air4G, etc..

        The function return 0 parameters
        """

        try:
            if bs_hardware_type and bs_hardware_type != '' and bs_hardware_type != 'Customer-Core':

                current_bs_hardware_type_list = GetFromCoreCareClass().get_bs_hardware_type(jira, epic_core_number)

                issue_num = jira.issue(epic_core_number)
                if current_bs_hardware_type_list:
                    bs_hardware_type_ = [{'value': i} for i in current_bs_hardware_type_list]
                    bs_hardware_type_.append({'value': bs_hardware_type})
                else:
                    bs_hardware_type_ = [{'value': bs_hardware_type}]
                issue_num.update(fields={"customfield_10800": bs_hardware_type_})
                self.logger.info(str(epic_core_number) + ' was update with "bs_hardware_type"')
            else:
                self.logger.info(str(epic_core_number) + ' was not update with "bs_hardware_type" - else')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "bs_hardware_type"')
            self.logger.error(f"bs_hardware_type = {str(bs_hardware_type)}")

    def update_radio_profile_bandwidth(self, jira, epic_core_number, radio_profile_bandwidth):
        """
        This function responsible for update/add "radio profile bandwidth" field in issue type "Epic" or "Core"
        on "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "radio_profile_bandwidth" - the bandwidth of the eNB (string type from list on Jira)
                * for example: 5MHz, 10MHz, 15MHz, 20MHz, 20+20Mhz, 15+15Mhz, 10+10Mhz, 5+5Mhz, 10+20Mhz, etc..

        The function return 0 parameters
        """

        try:
            if radio_profile_bandwidth and radio_profile_bandwidth != '' and radio_profile_bandwidth != 'None':
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_10513": {'value': str(radio_profile_bandwidth)}})
                self.logger.info(str(epic_core_number) + ' was update with "radio_profile_bandwidth"')
            else:
                self.logger.info(str(epic_core_number) + ' was not update with "radio_profile_bandwidth" - else')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "radio_profile_bandwidth"')
            self.logger.error(f"radio_profile_bandwidth = {str(radio_profile_bandwidth)}")

    def update_radio_profile_frame_config(self, jira, epic_core_number, radio_profile_frame_config):
        """
        This function responsible for update/add "radio profile frame config" field in issue type "Epic" or "Core"
        on "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "radio_profile_frame_config" - the frame config of the eNB (string type from list on Jira)
                * for example: FC1, FC2, FDD, etc..

        The function return 0 parameters
        """

        try:
            if radio_profile_frame_config and radio_profile_frame_config != '' \
                    and radio_profile_frame_config != 'None' and radio_profile_frame_config != []:
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_10512": {'value': str(radio_profile_frame_config)}})
                self.logger.info(str(epic_core_number) + ' was update with "radio_profile_frame_config"')
            else:
                self.logger.info(str(epic_core_number) + ' was not update with "radio_profile_frame_config" - else')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "radio_profile_frame_config"')
            self.logger.error(f"radio_profile_frame_config = {str(radio_profile_frame_config)}")

    def update_cell_configuration(self, jira, epic_core_number, cell_configuration):
        """
        This function responsible for update/add "cell configuration" field in issue type "Epic" or "Core"
        on "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "cell_configuration" - the cell configuration of the eNB (string type from list on Jira)
                * for example: LiteComp, MultiCell-Cont, MultiCell-NonCont, MultiCellCA-Cont, MultiCellCA-NonCont,
                               Single Cell-Sector1, Single Cell-Sector2, Dual cell, etc..

        The function return 0 parameters
        """

        try:
            if epic_core_number:
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_14500": {'value': str(cell_configuration)}})
                self.logger.info(str(epic_core_number) + ' was update with "cell_configuration"')
            else:
                self.logger.info(str(epic_core_number) + ' was not update with "cell_configuration" - else')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "cell_configuration"')
            self.logger.error(f"cell_configuration = {str(cell_configuration)}")

    def update_chip_set(self, jira, epic_core_number, chip_set):
        """
        This function responsible for update/add "chip-set" field in issue type "Epic" or "Core"
        on "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "chip_set" - the chip-set of the eNB (string type from list on Jira)
                * for example: DU-FSM, DU XLP, FSM, FSMv3, FSMv4, RelayEnodeB, UeRelay, XLP, etc..

        The function return 0 parameters
        """

        try:
            if chip_set and chip_set != 'N/A' and chip_set != '' and chip_set != 'None':
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_10510": {'value': str(chip_set)}})
                self.logger.info(str(epic_core_number) + ' was update with "chip_set"')
            else:
                self.logger.info(str(epic_core_number) + ' was not update with "chip_set" - else')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "chip_set"')
            self.logger.error(f"chip_set = {str(chip_set)}")

    def update_test_environments(self, jira, epic_core_number, test_environments):
        """
        This function responsible for update/add "test environments" field in issue type "Epic" or "Core"
        on "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "test_environments" - the hardware name of the eNB (without spaces) (string type)

        The function return 0 parameters
        """

        current_test_environments = 'error to get current_test_environments'
        try:
            current_test_environments = GetFromCoreCareClass().get_test_environments(jira, epic_core_number)
            if current_test_environments and current_test_environments != []:
                current_test_environments.append(test_environments)
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_11003": current_test_environments})
            else:
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_11003": [test_environments]})
            self.logger.info(str(epic_core_number) + ' was update with "test_environments"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "test_environments"')
            self.logger.error(f"test_environments = {str(test_environments)}")
            self.logger.error(f"current_test_environments = {str(current_test_environments)}")

    # "Epic Link" on "Core" issue type
    def update_core_link(self, jira, core_number, link):
        """
        This function responsible for update/add "link" field in issue type "Epic" or "Core"
        on "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "link" - the "Epic"/"Core" issue type for link (string type from issues type on Jira)

        The function return 0 parameters
        """

        try:
            if link:
                issue_num = jira.issue(core_number)
                issue_num.update(fields={"customfield_10000": str(link)})  # core
                self.logger.info(str(core_number) + ' was update with "link"')
            else:
                self.logger.info(str(core_number) + ' was not update with "link" - else')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(core_number) + ' was not update with "link"')
            self.logger.error(f"link = {str(link)}")

    def update_epic_link(self, jira, epic_core_number, link):
        """
        This function responsible for update/add "Epic link" field in issue type "Epic" or "Core"
        on "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "link" - the "Epic"/"Core" issue type for link (string type from issues type on Jira)

        The function return 0 parameters
        """

        try:
            if link:
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_10508": str(link)})  # epic
                self.logger.info(str(epic_core_number) + ' was update with "link"')
            else:
                self.logger.info(str(epic_core_number) + ' was not update with "link" - else')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "link"')
            self.logger.error(f"link = {str(link)}")

    def update_system_uptime(self, jira, epic_core_number, system_uptime):
        """
        This function responsible for update/add "system up-time" field in issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "system_uptime" - the number for system up-time (integer type)

        The function return 0 parameters
        """

        try:
            if system_uptime:
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_14801": int(system_uptime)})
                self.logger.info(str(epic_core_number) + ' was update with "system_uptime"')
            else:
                self.logger.info(str(epic_core_number) + ' was not update with "system_uptime" - else')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "system_uptime"')
            self.logger.error(f"system_uptime = {str(system_uptime)}")

    def update_core_system_uptime(self, jira, epic_core_number, core_system_uptime):
        """
        This function responsible for update/add "core system up-time" field in issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "core_system_uptime" - the number for system up-time (list of string /string type from list on Jira)
                * for example: <15min, 16-30min, 31-45min, 46-60min, 1-1.5hour, 1.5-2hour, 2-3hour, 3-4hour, 4-5hour,
                               5-6hour, 6-10hour, 10-15hour, 15-20hour, 20-25hour, 25-36hour, 36-48hour, 48-72hour,
                               >72hours, etc..

        The function return 0 parameters
        """

        new_core_system_uptime = []
        try:
            issue_num = jira.issue(epic_core_number)
            if current_core_system_uptime := GetFromCoreCareClass().get_core_system_uptime(jira, epic_core_number):
                if type(current_core_system_uptime) is not list:
                    new_core_system_uptime.append(current_core_system_uptime)
                else:
                    new_core_system_uptime = current_core_system_uptime
            if type(core_system_uptime) is not list:
                new_core_system_uptime.append(core_system_uptime)
            else:
                for index_core_system_uptime in core_system_uptime:
                    new_core_system_uptime.append(index_core_system_uptime)
            issue_num.update(fields={"customfield_14803": new_core_system_uptime})
            self.logger.info(str(epic_core_number) + ' was update with "core_system_uptime"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "core_system_uptime"')
            self.logger.error(f"core_system_uptime = {str(core_system_uptime)}")

    def update_core_crash_process(self, jira, epic_core_number, core_crash_process):
        """
        This function responsible for update/add "core crash process" field in issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "core_crash_process" - the name of the crash process (list type)

        The function return 0 parameters
        """

        new_core_crash_process = []
        try:
            issue_num = jira.issue(epic_core_number)
            if current_core_crash_process := GetFromCoreCareClass().get_core_crash_process(jira, epic_core_number):
                if type(current_core_crash_process) is not list:
                    new_core_crash_process.append(current_core_crash_process)
                else:
                    new_core_crash_process = current_core_crash_process
            if type(core_crash_process) is not list:
                new_core_crash_process.append(core_crash_process)
            else:
                for index_core_system_uptime in core_crash_process:
                    new_core_crash_process.append(index_core_system_uptime)
            issue_num.update(fields={"customfield_15001": new_core_crash_process})
            self.logger.info(str(epic_core_number) + ' was update with "core_crash_process"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "core_crash_process"')
            self.logger.error(f"core_crash_process = {str(core_crash_process)}")

    def update_enb_system_default(self, jira, epic_core_number, enb_system_default):
        """
        This function responsible for update/add "eNB system default" field in issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "enb_system_default" - the name of the enb system default (list of string type / string type)

        The function return 0 parameters
        """

        new_enb_system_default = []
        try:
            issue_num = jira.issue(epic_core_number)
            if current_enb_system_default := GetFromCoreCareClass().get_enb_system_default(jira, epic_core_number):
                if type(current_enb_system_default) is not list:
                    new_enb_system_default.append(current_enb_system_default)
                else:
                    new_enb_system_default = current_enb_system_default
            if type(enb_system_default) is not list:
                new_enb_system_default.append(enb_system_default)
            else:
                for index_core_system_uptime in enb_system_default:
                    new_enb_system_default.append(index_core_system_uptime)
            issue_num.update(fields={"customfield_13710": new_enb_system_default})
            self.logger.info(str(epic_core_number) + ' was update with "enb_system_default"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "enb_system_default"')
            self.logger.error(f"enb_system_default = {str(enb_system_default)}")

    def update_relay_system_default(self, jira, epic_core_number, relay_system_default):
        """
        This function responsible for update/add "relay system default" field in issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "relay_system_default" - the name of the relay system default (list of string type / string type)

        The function return 0 parameters
        """

        new_relay_system_default = []
        try:
            issue_num = jira.issue(epic_core_number)
            if current_relay_system_default := GetFromCoreCareClass().get_relay_system_default(jira, epic_core_number):
                if type(current_relay_system_default) is not list:
                    new_relay_system_default.append(current_relay_system_default)
                else:
                    new_relay_system_default = current_relay_system_default
            if type(relay_system_default) is not list:
                new_relay_system_default.append(relay_system_default)
            else:
                for index_relay_system_default in relay_system_default:
                    new_relay_system_default.append(index_relay_system_default)
            issue_num.update(fields={"customfield_13711": new_relay_system_default})
            self.logger.info(str(epic_core_number) + ' was update with "relay_system_default"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "relay_system_default"')
            self.logger.error(f"relay_system_default = {str(relay_system_default)}")

    def update_nms_software_version(self, jira, epic_core_number, nms_software_version):
        """
        This function responsible for update/add "nms software version" field in issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "nms_software_version" - the NMS version (list of string type / string type)

        The function return 0 parameters
        """

        new_nms_software_version = []
        try:
            issue_num = jira.issue(epic_core_number)
            if current_nms_software_version := GetFromCoreCareClass().get_nms_software_version(jira, epic_core_number):
                if type(current_nms_software_version) is not list:
                    new_nms_software_version.append(current_nms_software_version)
                else:
                    new_nms_software_version = current_nms_software_version
            if type(nms_software_version) is not list:
                new_nms_software_version.append(nms_software_version)
            else:
                for index_nms_software_version in nms_software_version:
                    new_nms_software_version.append(index_nms_software_version)
            issue_num.update(fields={"customfield_13709": new_nms_software_version})
            self.logger.info(str(epic_core_number) + ' was update with "nms_software_version"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "nms_software_version"')
            self.logger.error(f"nms_software_version = {str(nms_software_version)}")

    def update_relay_software_version(self, jira, epic_core_number, relay_software_version):
        """
        This function responsible for update/add "relay software version" field in issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "relay_software_version" - the relay version (list of string type / string type)

        The function return 0 parameters
        """

        new_relay_software_version = []
        try:
            issue_num = jira.issue(epic_core_number)
            if current_relay_software_version := GetFromCoreCareClass().get_relay_software_version(jira, epic_core_number):
                if type(current_relay_software_version) is not list:
                    new_relay_software_version.append(current_relay_software_version)
                else:
                    new_relay_software_version = current_relay_software_version
            if type(relay_software_version) is not list:
                new_relay_software_version.append(relay_software_version)
            else:
                for index_relay_software_version in relay_software_version:
                    new_relay_software_version.append(index_relay_software_version)
            issue_num.update(fields={"customfield_13708": new_relay_software_version})
            self.logger.info(str(epic_core_number) + ' was update with "relay_software_version"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "relay_software_version"')
            self.logger.error(f"relay_software_version = {str(relay_software_version)}")

    def update_enodeb_sw_version(self, jira, epic_core_number, new_enb_ver):
        """
        This function responsible for update/add "eNodeB SW version" field in issue type "DEF" on "CoreCare" project
        in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "new_enb_ver" - parameter need to be a string of the eNB version

        The function return 0 parameters
        """

        current_new_enb_ver = 'error to get new_enb_ver'
        try:
            current_new_enb_ver = GetFromCoreCareClass().get_enodeb_sw_version(jira, epic_core_number)
            if current_new_enb_ver and current_new_enb_ver != []:
                current_new_enb_ver.append(new_enb_ver)
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_13707": current_new_enb_ver})
            else:
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_13707": [new_enb_ver]})
            self.logger.info(str(epic_core_number) + ' was update with "enodeb_sw_version"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "new_enb_ver"')
            self.logger.error(f"new_enb_ver = {str(new_enb_ver)}")
            self.logger.error(f"current_new_enb_ver = {str(current_new_enb_ver)}")

    def update_core_customer_name(self, jira, epic_core_number, customer_name):
        """
        This function responsible for update/add "Core customer name" field in issue type "DEF" on "CoreCare" project
        in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "customer_name" - parameter need to be a string of the Core customer name

        The function return 0 parameters
        """

        current_customer_name = 'error to get current_customer_name'
        try:
            current_customer_name = GetFromCoreCareClass().get_core_customer_name(jira, epic_core_number)
            if current_customer_name and current_customer_name != []:
                current_customer_name.append(customer_name)
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_15900": current_customer_name})
            else:
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_15900": [customer_name]})
            self.logger.info(str(epic_core_number) + ' was update with "customer_name"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "customer_name"')
            self.logger.error(f"current_customer_name = {str(current_customer_name)}")
            self.logger.error(f"customer_name = {str(customer_name)}")

    def update_link_defect_string(self, jira, epic_core_number, defect_number):
        """
        This function responsible for update/add "link defect" field in issue type "DEF" on "CoreCare" project
        in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "defect_number" - parameter need to be DEF-number,
                * for example: DEF-12345

        The function return 0 parameters
        """

        try:
            if defect_number:
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"customfield_13512": str(defect_number)})
                self.logger.info(str(epic_core_number) + ' was update with "defect_number"')
            else:
                self.logger.info(str(epic_core_number) + ' was not update with "defect_number"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "defect_number"')
            self.logger.error('defect_number for update on customfield "link defect is: "' + str(defect_number))

    def update_fix_version(self, jira, epic_core_number, fix_ver):
        """
        This function responsible for update/add "link defect" field in issue type "DEF" on "CoreCare" project
        in Jira

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345
            - "fix_ver" - the fix version of the eNB (string type)

        The function return 0 parameters
        """

        try:
            current_fix_version = GetFromCoreCareClass().get_fix_version(jira, epic_core_number)
            if fix_ver:
                if type(current_fix_version) is list:
                    fix_versions_ = current_fix_version
                    fix_versions = [{'name': str(fix_version)} for fix_version in fix_versions_]
                    fix_versions.append({'name': str(fix_ver)})
                else:
                    fix_versions = [{'name': str(fix_ver)}]
                issue_num = jira.issue(epic_core_number)
                issue_num.update(fields={"fixVersions": fix_versions})
                self.logger.info(str(epic_core_number) + ' was update with "fixVersions"')
            else:
                self.logger.info(str(epic_core_number) + ' was not update with "fixVersions"')
        except JIRAError:
            self.logger.exception('')
        except Exception:
            self.logger.error(str(epic_core_number) + ' was not update with "fixVersions"')
            self.logger.error('fix_ver for update on customfield "fixVersions" is: ' + str(fix_ver))

    def update_epic_status_fields(self, jira, epic_number):
        try:
            issue_num = jira.issue(str(epic_number))
            if status_fields := issue_num.fields.status:
                if str(status_fields) == 'In Progress':
                    self.logger.info(f'The Epic {str(epic_number)}' + ' status is: "In Progress" ')
                elif str(status_fields) in {'Done', 'To Do'}:
                    jira.transition_issue(issue_num, transition='In Progress')
                    self.logger.info(f'The Epic {str(epic_number)}' + ' status update to "In Progress" ')

                else:
                    self.logger.info(f'The Epic {str(epic_number)} status was not changed, the current status is: {str(status_fields)}')

            else:
                self.logger.warning(colored(f'Error to Update {str(epic_number)}', 'red'))
        except JIRAError:
            self.logger.exception('')
        except Exception as err:
            self.logger.error(err)


class GetFromCoreCareClass:
    """ This class ("CreateCoreCareClass") responsible for get values from "CoreCare" project in Jira """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_status_fields(self, jira, epic_core_number):
        """
        This function responsible for get "status" field data from issue type "Epic" or "Core" on "CoreCare" project
        in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "current_epic_core_status" - the current status of "Epic" or "Core"
                * for example: TO DO, Pending, DONE, Fixed in R&D, Reopened, etc..
        """

        try:
            issue_num = jira.issue(epic_core_number)
            return issue_num.fields.status
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_labels(self, jira, epic_core_number):
        """
        This function responsible for get "labels" field data from issue type "Epic" or "Core" on "CoreCare" project
        in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "current_labels_list" - the current labels list of issue type (list of string type)
                * for example: ['Avi', 'Zaguri'] or 'AviZaguri
        """

        try:
            return jira.issue(str(epic_core_number), fields='labels').fields.labels
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_enb_software_version(self, jira, epic_core_number):
        """
        This function responsible for get "eNB software version" field data from issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "current_enb_new_enb_software_version_list_version" - parameter need to be a list or string
            (without spaces) of the labels (list of string type)
                * for example: ['Avi', 'Zaguri'] or 'AviZaguri
        """

        try:
            return jira.issue(str(epic_core_number), fields='customfield_13707').fields.customfield_13707

        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_core_occurrence_count(self, jira, epic_number):
        """
        This function responsible for get "core occurrence count" field data from issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "core_occurrence_count" - the core occurrence count that linked to issue type (string type)
        """

        try:
            list_core_occurrence_count = jira.search_issues(epic_number)
            return len(list_core_occurrence_count)
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_test_environments(self, jira, epic_core_number):
        """
        This function responsible for get "test environments" field data from issue type "Epic" or "Core" on"CoreCare"
        project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "current_test_environments" - the current test environments on issue type (list of string type)
        """

        try:
            issue_num = jira.issue(epic_core_number)
            return issue_num.fields.customfield_11003
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_core_system_uptime(self, jira, epic_core_number):
        """
        This function responsible for get "core system up-time" field data from issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "current_core_system_uptime" - parameter need to be a list or string (without spaces) of the labels
                                             (list of string type)
                * for example: ['Avi', 'Zaguri'] or 'AviZaguri
        """

        try:
            return jira.issue(str(epic_core_number), fields='customfield_14803').fields.customfield_14803

        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_core_crash_process(self, jira, epic_core_number):
        """
        This function responsible for get "core crash process" field data from issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "current_core_system_uptime" - parameter need to be a list or string (without spaces) of the labels
                                             (list of string type)
                * for example: ['Avi', 'Zaguri'] or 'AviZaguri
        """

        try:
            return jira.issue(str(epic_core_number), fields='customfield_15001').fields.customfield_15001

        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_enb_system_default(self, jira, epic_core_number):
        """
        This function responsible for get "eNB system default" field data from issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "current_enb_system_default" - the current system default of the enb (list of string type / string type)
        """

        try:
            return jira.issue(str(epic_core_number), fields='customfield_13710').fields.customfield_13710

        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_relay_system_default(self, jira, epic_core_number):
        """
        This function responsible for get "relay system default" field data from issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "current_relay_system_default" - the name of the current relay system default
                                               (list of string type / string type)
                * for example: ['Avi', 'Zaguri'] or 'AviZaguri
        """

        try:
            return jira.issue(str(epic_core_number), fields='customfield_13711').fields.customfield_13711

        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_nms_software_version(self, jira, epic_core_number):
        """
        This function responsible for get "nms software version" field data from issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "current_nms_software_version" - the NMS version (list of string type / string type)
        """

        try:
            return jira.issue(str(epic_core_number), fields='customfield_13709').fields.customfield_13709

        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_relay_software_version(self, jira, epic_core_number):
        """
        This function responsible for get "relay software version" field data from issue type "Epic" or "Core" on
        "CoreCare" project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_core_number" - parameter need to be CORE-number,
                * for example: CORE-12345

        The function return 1 parameters:
            - "relay_software_version" - the relay version (list of string type / string type)
                * for example: ['Avi', 'Zaguri'] or 'AviZaguri
        """

        try:
            return jira.issue(str(epic_core_number), fields='customfield_13708').fields.customfield_13708

        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_core_customer_name(self, jira, epic_core_number):
        """
        This function responsible for get "Core customer name" field data from issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "defect_number" - parameter need to be DEF-number,
                * for example: DEF-12345

        The function return 1 parameters:
            - "current_core_customer_name" - the current core_customer_name on issue type (list of string type)
        """

        try:
            issue_num = jira.issue(epic_core_number)
            return issue_num.fields.customfield_15900
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_enodeb_sw_version(self, jira, epic_core_number):
        """
        This function responsible for get "eNodeB SW version" field data from issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "defect_number" - parameter need to be DEF-number,
                * for example: DEF-12345

        The function return 1 parameters:
            - "current_test_environments" - the current test environments on issue type (list of string type)
        """

        try:
            issue_num = jira.issue(jira, epic_core_number)
            return issue_num.fields.customfield_13707
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_fix_version(self, jira, epic_core_number):
        """
        This function responsible for get "fix version" field data from issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "defect_number" - parameter need to be DEF-number,
                * for example: DEF-12345

        The function return 1 parameters:
            - "current_fix_version" - the current fix_version on issue type (list of dictionary type)
        """

        try:
            issue_num = jira.issue(epic_core_number)
            return issue_num.fields.fixVersions
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_bs_hardware_type(self, jira, epic_core_number):
        """
        This function responsible for get "fix version" field data from issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "defect_number" - parameter need to be DEF-number,
                * for example: DEF-12345

        The function return 1 parameters:
            - "current_fix_version" - the current fix_version on issue type (list of dictionary type)
        """

        try:
            issue_num = jira.issue(epic_core_number)
            current_bs_hardware_type = issue_num.fields.customfield_10800
            if not current_bs_hardware_type:
                return None
            return [str(bs_hardware_type) for bs_hardware_type in current_bs_hardware_type]
        except JIRAError:
            self.logger.exception('')
            return None
        except Exception as err:
            self.logger.error(err)
            return None

    def get_avg_system_uptime_min_for_all_links_cores_per_version(self, jira, epic_number, enb_version):
        """
        This function responsible for get "SystemUpTime (min)" field data from issue type "Epic" or "Core" on "CoreCare"
        project in Jira

        The function get 2 parameter:
            - "jira" - parameter need to be client of jira
            - "epic_number" - parameter need to be EPIC-number,
                * for example: EPIC-12345

        The function return 1 parameters:
            - "cores_sys_ut_min" - The sum of Core "SystemUpTime (min)" for all Cores that link
              to Epic (list of string type)
        """

        try:
            if type(enb_version) is str:
                filter_ = 'project = CORE AND ("Epic Link" = ' + str(epic_number) + ' OR Link ~ ' + str(epic_number) + \
                          ') AND issuetype = Core AND "Core SystemUpTime (min)" is not EMPTY ' \
                          'AND "g/eNodeB SW version" = ' + enb_version
            elif type(enb_version) is list:
                filter_ = 'project = CORE AND ("Epic Link" = ' + str(epic_number) + ' OR Link ~ ' + str(epic_number) + \
                          ') AND issuetype = Core AND "Core SystemUpTime (min)" is not EMPTY ' \
                          'AND ("g/eNodeB SW version" in ('
                for index, i in enumerate(enb_version, start=0):
                    filter_ += i
                    if index != len(enb_version) - 1:
                        filter_ += ', '
                filter_ += '))'
            else:
                return -1, -1, -1

            res = jira.search_issues(filter_)

            cores_system_uptime_avg = -1
            core_system_uptime_min = -1
            core_system_uptime_max = -1
            if res:
                for core_index, core_ in enumerate(res, start=0):
                    if core_index == 0:
                        core_system_uptime_min = core_.fields.customfield_14801
                        core_system_uptime_max = core_.fields.customfield_14801
                    core_system_uptime_avg = core_.fields.customfield_14801
                    cores_system_uptime_avg += int(core_system_uptime_avg)

                    if core_.fields.customfield_14801 < core_system_uptime_min and core_index != 0:
                        core_system_uptime_min = core_.fields.customfield_14801
                    elif core_.fields.customfield_14801 > core_system_uptime_max:
                        core_system_uptime_max = core_.fields.customfield_14801
                return cores_system_uptime_avg / len(res), core_system_uptime_min, core_system_uptime_max
            else:
                print(f'The filter_ is: {str(filter_)}')
                return cores_system_uptime_avg, core_system_uptime_min, core_system_uptime_max  # -1, -1, -1
        except JIRAError:
            self.logger.exception('')
            return -1, -1, -1
        except Exception as err:
            self.logger.error(err)
            return -1, -1, -1

    def get_cores_per_build_per_chipset(self, jira, version, chipset):
        if jira and version and chipset:
            search_result = jira.search_issues(
                f'type in (Core, PhyAssert) AND issuetype != Epic AND "g/eNodeB SW version" = {version} AND '
                f'Chipset = {chipset}', maxResults=5000)
        else:
            search_result = []
            self.logger.info('One of function arguments is None')

        return search_result
