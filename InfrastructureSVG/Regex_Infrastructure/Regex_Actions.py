import logging
import re


class RegexClass:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def regex_on_freason(self, freason, feature=None):
        """
           This function responsible for extracting Throughput results from Jira_Infrastructure failure reason

           The function get 1 parameter:
               - "freason" -  parameter need to be a string

           The function return Throughput results failure reason
        """
        reg = ''
        if freason:
            if feature:
                if 'UpLink' in feature:
                    reg = r"UL port level AvgRate\(Mbps\): Expected: ([0-9]+.[0-9]+)"
                elif 'DownLink' in feature:
                    reg = r"DL port level AvgRate\(Mbps\): Expected: ([0-9]+.[0-9]+)"
            elif 'Expected:' in freason:
                reg = r"Expected: [0-9]+.[0-9]+ Mbps"
            elif 'expected' in freason:
                reg = r"expected: [0-9]+.[0-9]+"
            elif 'Failed to get value from CLI' in freason:
                reg = r"(Failure:Couldn't get eNodeB information. Failed to get value from CLI)"
            elif 'dl actual' in freason:
                reg = r"dl actual: ([0-9]+.[0-9]+)"
            elif 'ul actual' in freason:
                reg = r"ul actual: ([0-9]+.[0-9]+)"
            else:
                reg = r"threshold was [0-9]+.[0-9]+"
            return re.findall(reg, freason, re.I)
        else:
            self.logger.warning('freason parameter is empty')
            return None

    def regex_on_sir(self, filter_string):
        """
           This function responsible for extracting SIR id from Jira_Infrastructure filter string

           The function get 1 parameter:
               - "filter_string" -  parameter need to be a string

           The function return SIR number (SIR-12345)
        """
        if filter_string:
            reg = r"SIR-[0-9]+"
            sir_ = re.findall(reg, str(filter_string), re.I)
            sir = ''.join(sir_)
        else:
            sir = ''
            self.logger.warning('filter_string parameter is empty')

        return sir

    def regex_on_cell_carrier(self, filter_string):
        """
           This function responsible for extracting Cell Carrier type from Jira_Infrastructure filter string

           The function get 1 parameter:
               - "filter_string" -  parameter need to be a string

           The function return Cell Carrier
        """

        try:
            if filter_string:
                reg = r"\"Cell/Carrier Config\" = \"(.+?)\""
                cell_carrier_ = re.findall(reg, str(filter_string), re.I)
                return ''.join(cell_carrier_)
            else:
                return ''
        except Exception:
            self.logger.exception("")

    def regex_on_backhaul(self, filter_string):
        """
           This function responsible for extracting Backhaul configuration from Jira_Infrastructure filter string

           The function get 1 parameter:
               - "filter_string" -  parameter need to be a string

           The function return Backhaul type
        """

        if filter_string:
            reg = r"Backhaul = \"(.+?)\""
            backhaul_ = re.findall(reg, str(filter_string), re.I)
            backhaul = ''.join(backhaul_)
        else:
            backhaul = ''
            self.logger.warning('filter_string parameter is empty')

        return backhaul

    def regex_on_bandwidth(self, filter_string):
        """
           This function responsible for extracting Bandwidth configuration from Jira_Infrastructure filter string

           The function get 1 parameter:
               - "filter_string" -  parameter need to be a string

           The function return Bandwidth type
        """
        if filter_string:
            reg = r"BW = ([0-9]+.+Mhz)"
            bandwidth_ = re.findall(reg, str(filter_string), re.I)
            bandwidth = ''.join(bandwidth_)
        else:
            bandwidth = ''
            self.logger.warning('filter_string parameter is empty')

        return bandwidth

    def regex_on_fc(self, filter_string):
        """
           This function responsible for extracting FC configuration from Jira_Infrastructure filter string

           The function get 1 parameter:
               - "filter_string" -  parameter need to be a string

           The function return FC configuration
        """
        if filter_string:
            reg = r"FC = ([A-Z]+[0-9])"
            fc_ = re.findall(reg, str(filter_string), re.I)
            fc = ''.join(fc_)
        else:
            fc = ''
            self.logger.warning('filter_string parameter is empty')

        return fc

    def regex_version(self, filter_string):
        """
           This function responsible for extracting version from Jira_Infrastructure filter string

           The function get 1 parameter:
               - "filter_string" -  parameter need to be a string

           The function return version
        """
        if filter_string:
            reg = r"in \((.*?)\)"
            version_ = re.findall(reg, str(filter_string), re.I)
            version = ''.join(version_)
        else:
            version = ''
            self.logger.warning('filter_string parameter is empty')

        return version

    def regex_hw_type(self, filter_string):
        """
           This function responsible for extracting Hardware Type from Jira_Infrastructure filter string

           The function get 1 parameter:
               - "filter_string" -  parameter need to be a string

           The function return Hardware Type
        """
        if filter_string:
            reg = r"\"BS Hardware Type\" = \"(.+?)\""
            hw_type_ = re.findall(reg, str(filter_string), re.I)
            hw_ = ''.join(hw_type_)
            hw = "\"" + hw_ + "\""
        else:
            hw = ''
            self.logger.warning('filter_string parameter is empty')

        return hw

    def regex_get_build_number_from_execution_summary(self, summary):
        """
           This function responsible for extracting Build Number from
           Jira_Infrastructure Test Execution Summary string

           The function get 1 parameter:
               - "Test Execution Summary" -  parameter need to be a string

           The function return Build Number
        """
        if summary:
            reg = r"Jenkins_Infrastructure \((.*?)\)"
            build_num_ = re.findall(reg, str(summary), re.I)
            build_num = ''.join(build_num_)
        else:
            build_num = ''
            self.logger.warning('summary parameter is empty')

        return build_num

    def regex_get_date_and_time(self, string_to_parse):
        """
           This function responsible for extracting TimeStamp from
           Jira_Infrastructure Test Execution failure reason string

           The function get 1 parameter:
               - "Test Execution Summary" -  parameter need to be a string

           The function return TimeStamp
        """

        if string_to_parse:
            reg = r"(?:[0-9]{4}/)(?:[0-9]{2}/)(?:[0-9]{2}) (?:[0-9]{2}:)(?:[0-9]{2}:)(?:[0-9]{2})"
            date_string_ = re.findall(reg, str(string_to_parse), re.I)
            # date_time = ''.join(date_string_)
        else:
            date_string_ = ''
            self.logger.warning('string_to_parse parameter is empty')

        return date_string_

    def regex_on_string_find_all(self, string_to_parse, pattern):
        """
           This function responsible for extracting any object from string by using "findall"
           method

           The function get 2 parameters:
               - "string_to_parse" -
               - pattern - Regex_Infrastructure pattern, parameter need to be a string

           The function return list of found objects
        """
        if string_to_parse and pattern:
            try:
                string_to_return = re.findall(pattern, str(string_to_parse), re.I)

            except Exception:
                return None
        else:
            string_to_return = None
            self.logger.warning('pattern parameter is empty')
        return string_to_return

    def regex_on_string_search(self, string_to_parse, pattern, group=None, find_all=None):
        """
           This function responsible for extracting any object from string by using "findall"
           method

           The function get 2 parameters:
               - "string_to_parse" -
               - pattern - Regex_Infrastructure pattern, parameter need to be a string

           The function return list of found objects
        """

        if string_to_parse and pattern:
            try:
                if not group and not find_all:
                    string_to_return = re.search(pattern, str(string_to_parse), re.I).group()
                elif find_all:
                    string_to_return = re.findall(pattern, str(string_to_parse), re.I)
                else:
                    string_to_return = re.search(pattern, str(string_to_parse), re.I)[int(group)]

            except Exception:
                return None
        else:
            string_to_return = None
            self.logger.warning('pattern parameter is empty')

        return string_to_return
