import time
import telnetlib
import logging

from InfrastructureSVG.General_Actions_Infrastructure.General_Actions_Infrastructure import GeneralActionsClass

""" 
In this py file have 2 class
    - TelnetConnectionClass
    - TelnetSendCommandsClass
"""


class TelnetConnectionClass:
    """ This class ("TelnetConnectionClass().) responsible for Telnet connection """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def telnet_connection(self, ip_address, username_and_password=None, port=23):
        """
        This function responsible to create Telnet connection

        The function get 3 parameter:
            - "ip_address" - the ip address for connection (string type)
            - "username_and_password" - username and password for connection (list of byte type) [Optional]
            - "port" - the port for connection (string type) [Optional]

        The function return 1 parameters:
            - "client_telnet_connect" - client of Telnet
        """

        try:
            client_telnet_connect = telnetlib.Telnet(ip_address, port)
            self.logger.info("Interactive session established with {0}".format(ip_address))
            if username_and_password:
                for command in username_and_password:
                    client_telnet_connect.write(b"\n" + command + b"\n")
            return client_telnet_connect
        except ValueError:
            self.logger.exception('')
            return None
        except ConnectionRefusedError:
            self.logger.exception('Telnet connection experience:\nError: Connection RefusedError')
        except Exception:
            self.logger.exception('')
            return None

    def telnet_reconnect(self, ip_address, username_and_password=None, port=23):
        """
        This function responsible to reconnect Telnet session

        The function get 2 parameter:
            - "ip_address" - the ip address for connection (string type)
            - "username_and_password" - username and password for connection (list of byte type) [Optional]
            - "port" - the port for connection (string type) [Optional]

        The function return 1 parameters:
            - "client_telnet_reconnect" - client of telnet
        """

        client_telnet_reconnect = TelnetConnectionClass().telnet_connection(ip_address, username_and_password, port)
        time.sleep(1)
        try:
            client_telnet_reconnect.write(b"\n")
        except ConnectionRefusedError:
            self.logger.exception('Telnet connection experience:\nError: Connection RefusedError')
            client_telnet_reconnect = TelnetConnectionClass().telnet_connection(ip_address, username_and_password, port)
        if client_telnet_reconnect:
            self.logger.info("\nReconnection was successful")
        else:
            self.logger.debug("\nReconnection was not successful")
        return client_telnet_reconnect


class TelnetSendCommandsClass:
    """ This class ("TelnetSendCommandsClass") responsible for send Telnet commands """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def telnet_send_commands_with_output(self, commands, client_telnet_connect, ip_address, username_and_password=None,
                                         port=23, wait_before_output=1, timeout_output_receive=3):
        """
        This function responsible to send one command (return output)

        The function get 7 parameter:
            - "commands" - the command (one command!) that need to send (byte type)
            - "client_telnet_connect" - client of Telnet
            - "ip_address" - parameter need to be IP from (string type)
            - "username_and_password" - username and password for connection (list of byte type) [Optional]
            - "port" - parameter need to be the port number for connection (integer type) [Optional]
            - "wait_before_output" - the time before taking output (integer type) [Optional]
            - "timeout_output_receive" - the time for output that receive from the telnet connection (string type)
              [Optional]

        The function return 2 parameters:
            - "client_telnet_connect" - client of telnet
            - "output" - client of telnet
        """

        output = ''
        # print("the command is: " + commands)
        for _ in range(3):
            try:
                if client_telnet_connect and commands:
                    client_telnet_connect.write(commands + b"\n")
                    time.sleep(wait_before_output)
                    try:
                        output = client_telnet_connect.read_until(b'!23', timeout_output_receive)
                        output = output.decode('utf-8')
                    except UnicodeDecodeError:
                        output = GeneralActionsClass().byte_to_string_error_decode(output)
                # print(output)
                break
            except ConnectionRefusedError:
                self.logger.exception('Telnet connection experience:\nError: Connection RefusedError')
                client_telnet_connect = TelnetConnectionClass().telnet_connection(ip_address, username_and_password,
                                                                                  port)
            except Exception:
                self.logger.exception('')
                return output

        return client_telnet_connect, output

    def telnet_send_commands_without_output(self, commands, client_telnet_reconnect, ip_address, username_and_password,
                                            port=23, wait_before_output=1):
        """
        This function responsible to send one command (not return output)

        The function get 6 parameter:
            - "commands" - the command (one command!) that need to send (byte type)
            - "client_telnet_connect" - client of Telnet
            - "ip_address" - the ip address for connection (string type)
            - "username_and_password" - the username and password for connection (list of byte type) [Optional]
            - "port" - the port for connection (string type) [Optional]
            - "wait_before_output" - the time before taking output (integer type) [Optional]

        The function return 1 parameters:
            - "client_telnet_reconnect" - client of telnet
        """

        # print("the command is: " + commands)
        for _ in range(3):
            try:
                if commands:
                    client_telnet_reconnect.write(b"\n" + commands + b"\n")
                    time.sleep(wait_before_output)
                break
            except ConnectionRefusedError:
                self.logger.exception('Telnet connection experience:\nError: Connection RefusedError')
                client_telnet_reconnect = TelnetConnectionClass().telnet_connection(ip_address, username_and_password,
                                                                                    port)
            except Exception:
                self.logger.exception('')
                return None
        return client_telnet_reconnect
