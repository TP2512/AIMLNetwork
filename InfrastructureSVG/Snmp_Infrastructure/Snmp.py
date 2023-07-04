import logging

from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from InfrastructureSVG.Files_Infrastructure.XLSX_Files.Read_From_XLSX_File_Infrastructure import ReadFromXLSXFileClass
from pysnmp.proto import rfc1902
from robot.api.deco import keyword
from InfrastructureSVG.Regex_Infrastructure.Regex_Actions import RegexClass


class SNMP:

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{__name__}')

    @keyword(name='Get Mib Info By Name')
    def get_mib_info_by_name(self, mib_name):
        mib_info = {}
        """ read data from xlsx"""
        mib_file_full_path = '\\\\fs4\\DATA\\SVG\\Automation\\Python Projects\\Mibs\\5G\\UEs_MIBs.xlsx'
        df = ReadFromXLSXFileClass().read_xlsx_by_sheet_name(mib_file_full_path, sheetname=0)
        check_for_value = df['Name'] == mib_name
        row_with_mib_name = df[check_for_value]
        if len(row_with_mib_name.index) == 1:
            mib_info["oid"] = row_with_mib_name['OID'].values.tolist()[0]
            mib_info["type"] = row_with_mib_name['Type'].values.tolist()[0]
        else:
            self.logger.info(f"No mib found with name{mib_name}")
        return mib_info

    @keyword(name='Get Value By OID')
    def get_value_by_oid(self, **data):
        """
        This function responsible to perform "GET" action for value by oid MIB

        The function get 2 parameters:
            'host_ip' - target ip address (string type)
            'oid' - object identification for desired value (String type)

        The function return 1 parameter:
            '[oid_value]' - list contain oids and values (list of list of string type)
                * only for single instances
        """

        try:
            host_ip = data["host"]
            oid = data["oid"]
            read_community = data["read_community"]
            port = data["port"]
            error_indication, error_status, error_index, var_binds = next(
                getCmd(SnmpEngine(),
                       CommunityData(read_community),
                       UdpTransportTarget((host_ip, port)),
                       ContextData(),
                       ObjectType(ObjectIdentity(oid))))

            if error_indication:
                self.logger.warning(error_indication)
                return None
            elif error_status:
                self.logger.warning('%s at %s' % (error_status.prettyPrint(), error_index and
                                                  var_binds[int(error_index) - 1][0] or '?'))
                return None
            else:
                oid_value = []
                for varBind in var_binds:
                    for oid_value_ in varBind:
                        if not str(oid_value_):
                            oid_value_ = 'NoSuchInstance'
                        oid_value.append(str(oid_value_))
                return [oid_value]
        except Exception:
            self.logger.exception('')
            return None

    @keyword(name='Get Next Value By Oid')
    def get_next_value_by_oid(self, **data):
        """
        This function responsible to perform "GET-NEXT" action for value by oid MIB

        The function get 4 parameters:
            'host_ip' - target ip address (string type)
            'oid' - object identification for desired value (String type)
            'replace_ - this parameter control on replacing string to 'root_tree_oid' (Boolean type) [optional]
                * in case of "True" - perform replace
                * in case of "False" - do not perform replace
            'root_tree_oid' - first oid of oid tree (as part of standard mib tree) (String type) [optional]
                * work only if "replace_" = True

        The function return 1 parameter:
            'instance_list' - list of list contain oids and values (list of list of string type)
                * only for multi instances
        """
        host_ip = data["host"]
        oid = data["oid"]
        replace_ = data["replace"]
        root_tree_oid = data["root_tree_oid"]
        port = data["port"]
        read_community = data["read_community"]
        error_indication, error_status, error_index, var_bind_table = cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData(read_community),
            cmdgen.UdpTransportTarget((host_ip, port)), oid)

        if error_indication:
            self.logger.info(error_indication)
        else:
            instance_list = []
            if error_status:
                self.logger.info('%s at %s\n' % (
                    error_status.prettyPrint(), error_index and var_bind_table[-1][int(error_index) - 1] or '?'
                ))
            else:
                reg_pattern = r'(^[^.]*?[^.](?=\.))'  # Find first dot(.) char in string
                for index, name_ in enumerate(var_bind_table, start=0):
                    value_from_regex = RegexClass().regex_on_string_find_all(str(name_[0]), reg_pattern)
                    if replace_:
                        instance_list.append(str(name_[0]).replace(value_from_regex[0], root_tree_oid).split(" = "))
                    else:
                        instance_list.append(str(name_[0]).split(" = "))

            return instance_list

    @keyword(name='Set Value By Oid')
    def set_value_by_oid(self, **data):

        """ This function responsible to perform "SET" action by oid MIB

        The function get 4 parameters:
            'host_ip' - target ip address (string type)
            'oid' - object identification for desired value (String type)
            'value_type' - The value type during perform SET actions (string type)
                * for example: Integer, Octetstring, etc.
            'new_value' - new value to set (string type)

        The function return 1 parameter:
            'oid_value' - The updated value after the SET action (string type)
        """

        try:
            host_ip = data["host"]
            oid = data["oid"]
            value_type = self.get_type(data["type"])
            new_value = data["value"]
            port = data["port"]
            read_community = data["read_community"]
            write_community = data.get("write_community")
            if value_type:
                if write_community:
                    error_indication, error_status, error_index, var_binds = cmdgen.CommandGenerator().setCmd(
                        cmdgen.CommunityData(read_community, write_community, 1),
                        cmdgen.UdpTransportTarget((host_ip, port), timeout=7.0, retries=5),
                        (oid, value_type(new_value))
                    )
                else:
                    error_indication, error_status, error_index, var_binds = cmdgen.CommandGenerator().setCmd(
                        cmdgen.CommunityData(read_community, mpModel=1),
                        cmdgen.UdpTransportTarget((host_ip, port), timeout=7.0, retries=5),
                        (oid, value_type(new_value))
                    )
                    # Check for errors and print out results
                if error_indication:
                    self.logger.warning(error_indication)
                    return None
                else:
                    if error_status:
                        self.logger.info(
                            f"{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1] or '?'}"
                        )

                        return None
                    else:
                        self.logger.info(f'Oid ${str(oid)} Successfully set to ${str(new_value)}')
                        return ''
            else:
                self.logger.info("unknown value type")
                return None

        except Exception:
            self.logger.exception('')
            return None

    @staticmethod
    def get_type(name):
        if "integer" in name.lower():
            return rfc1902.Integer
        elif "string" in name.lower():
            return rfc1902.OctetString
        else:
            return False

    @keyword(name='Walk Over All Values By Oid')
    def walk_over_all_values_by_oid(self, **data):
        """
        This function responsible to perform "WALK"" action for value by oid MIB

        The function get 4 parameters:
            'host_ip' - target ip address (string type)
            'oid' - object identification for desired value (String type)
            'replace_ - this parameter control on replacing string to 'root_tree_oid' (Boolean type) [optional]
                * in case of "True" - perform replace
                * in case of "False" - do not perform replace
            'root_tree_oid' - first oid of oid tree (as part of standard mib tree) (String type) [optional]
                * work only if "replace_" = T

        The function return 1 parameter:
            'list_for_oid' - list of list contain oids and values (list of list of string type)
                * only for multi instances
        """

        try:
            host_ip = data["host"]
            oid = data["oid"]
            port = data["port"]
            read_community = data["read_community"]
            replace_ = data["replace"]
            root_tree_oid = data["root_tree_oid"]
            list_for_oid = []
            for (errorIndication,
                 errorStatus,
                 errorIndex,
                 varBinds) in nextCmd(SnmpEngine(),
                                      CommunityData(read_community),
                                      UdpTransportTarget((host_ip, port)),
                                      ContextData(),
                                      ObjectType(ObjectIdentity(oid)),
                                      lookupMib=True,
                                      maxRows=False,
                                      maxCalls=False,
                                      lexicographicMode=False):
                if errorIndication:
                    self.logger.info(errorIndication)
                    break

                elif errorStatus:
                    self.logger.info('%s at %s' % (errorStatus.prettyPrint(), errorIndex and
                                                   varBinds[int(errorIndex) - 1][0] or '?'))
                    break

                else:
                    list_for_oid.extend(str(varBind) for varBind in varBinds)
            reg_pattern = r'(^[^.]*?[^.](?=\.))'  # Find first dot(.) char in string
            for i, name_ in enumerate(list_for_oid, start=0):
                value_from_regex = RegexClass().regex_on_string_find_all(str(name_), reg_pattern)
                if replace_:
                    list_for_oid[i] = str(list_for_oid[i]).replace(value_from_regex[0], root_tree_oid).split(" = ")
            return list_for_oid
        except Exception:
            self.logger.exception('')
            return None
