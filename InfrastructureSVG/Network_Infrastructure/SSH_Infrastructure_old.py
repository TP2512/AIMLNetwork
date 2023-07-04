import time
import paramiko
import logging

from InfrastructureSVG.General_Actions_Infrastructure.General_Actions_Infrastructure import GeneralActionsClass
from InfrastructureSVG.Network_Infrastructure.IP_Address_Network_Infrastructure import IPAddressNetworkClass

""" 
In this py file have 2 class
    - SSHConnectionClass
    - SSHSendCommandsClass
"""


class SSHConnectionClass:
    """ This class ("SSHConnectionClass") responsible for SSH connection """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def ssh_connection(self, ip_address, username, password, port=22):
        """
        This function responsible to create ssh connection

        The function get 4 parameter:
            - "ip_address" - the ip address for connection (string type)
            - "username" - the username for connection (string type)
            - "password" - the password for connection (string type)
            - "port" - the port for connection (string type) [Optional]

        The function return 2 parameters:
            - "client_SSH" - client of SSH
            - "remote_conn" - client of SSH
        """

        try:
            client_ssh = paramiko.SSHClient()
            client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client_ssh.connect(hostname=ip_address, port=port, username=username, password=password)
            # client_SSH.connect(hostname=ip, username=username, password=password)
            remote_connect = client_ssh.invoke_shell()
            self.logger.info(f"Interactive session established with {ip_address}")
            return client_ssh, remote_connect
        except ValueError:
            return None, None
        except Exception:
            self.logger.exception('')
            return None, None

    def ssh_reconnect(self, ip_address, username, password, port=22, count=1, loop_count=3, time_to_sleep=3):
        try:
            while count < loop_count:
                if IPAddressNetworkClass().check_ping_status():
                    # self.logger.debug('Network Active')
                    client_ssh_connect, remote_connect = SSHConnectionClass(). \
                        ssh_connection(ip_address, username, password, port)
                    if SSHConnectionClass(). \
                            check_ssh_status(client_ssh_connect, remote_connect):
                        return client_ssh_connect, remote_connect
                time.sleep(time_to_sleep)
                if loop_count is True:
                    count = 0
                else:
                    count += 1
            return None, None
        except Exception:
            self.logger.exception('')

    def ssh_reconnect_(self, ip_address, username, password, port=22):
        """
        This function responsible to reconnect ssh session

        The function get 4 parameter:
            - "ip_address" - the ip address for reconnect (string type)
            - "username" - the username for reconnect (string type)
            - "password" - the password for reconnect (string type)
            - "port" - the port for reconnect (string type) [Optional]

        The function return 2 parameters:
            - "client_ssh_reconnect" - client of SSH
            - "remote_reconnect" - client of SSH
        """

        try:
            client_ssh_reconnect, remote_reconnect = SSHConnectionClass().ssh_connection(ip_address, username, password,
                                                                                         port)
            time.sleep(1)
            if SSHConnectionClass().check_ssh_status(client_ssh_reconnect, remote_reconnect):
                print("\nReconnection was successful")
            else:
                print("\nReconnection was not successful")
            return client_ssh_reconnect, remote_reconnect
        except Exception:
            self.logger.exception("")

    def check_ssh_status(self, client_ssh, remote_connect):
        try:
            if client_ssh and remote_connect:  # if client exist
                return remote_connect.get_transport() is not None and client_ssh.get_transport() is not None

            else:
                return False
        except Exception:
            self.logger.exception('')
            return False


class SSHSendCommandsClass:
    """ This class ("SSHSendCommandsClass") responsible for send SSH commands """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def ssh_send_commands_with_output(self, commands, client_ssh_connect, remote_connect, ip_address, username,
                                      password, port=22, wait_before_output=1, output_receive=10000,
                                      count=1, loop_count=5, time_to_sleep=3):
        """
        This function responsible to send one command (return output)

        The function get 9 parameter:
            - "commands" - the command (one command!) that need to send (string type)
            - "client_ssh_connect" - client of SSH
            - "remote_connect" - client of SSH
            - "ip_address" - the ip address for connect (string type)
            - "username" - the username for connect (string type)
            - "password" - the password for connect (string type)
            - "port" - the port for connect (string type) [Optional]
            - "wait_before_output" - the time before taking output (integer type) [Optional]
            - "output_receive" - the output that receive from the ssh connection (string type) [Optional]

        The function return 3 parameters:
            - "client_ssh_connect" - client of SSH
            - "remote_connect" - client of SSH
            - "output" - client of SSH
        """
        try:
            if type(commands) is str:
                commands = [commands]
            output = None
            for command in commands:
                for _ in range(1, 3):
                    if SSHConnectionClass().check_ssh_status(client_ssh_connect, remote_connect):
                        remote_connect.send(f'{command}\n')
                        time.sleep(wait_before_output)
                        try:
                            output = remote_connect.recv(output_receive)
                            output = output.decode('utf-8')
                        except UnicodeDecodeError:
                            output = GeneralActionsClass().byte_to_string_error_decode(output)
                        break
                    else:
                        client_ssh_connect, remote_connect = SSHConnectionClass(). \
                            ssh_reconnect(ip_address, username, password, port, count, loop_count, time_to_sleep)
            return client_ssh_connect, remote_connect, output
        except Exception:
            self.logger.exception('')

    def ssh_send_commands_without_output(self, commands, client_ssh_connect, remote_connect, ip_address, username,
                                         password, port=22, wait_between_commands=1):
        """
        This function responsible to send one command (not return output)

        The function get 9 parameter:
            - "commands" - the command (one command!) that need to send (string type)
            - "client_ssh_connect" - client of SSH
            - "remote_connect" - client of SSH
            - "ip_address" - the ip address for connect (string type)
            - "username" - the username for connect (string type)
            - "password" - the password for connect (string type)
            - "port" - the port for connect (string type) [Optional]
            - "wait_before_output" - the time before taking output (integer type) [Optional]

        The function return 3 parameters:
            - "client_ssh_connect" - client of SSH
            - "remote_connect" - client of SSH
            - "output" - client of SSH
        """

        # print("the command is: " + commands)
        try:
            for _ in range(3):
                if SSHConnectionClass().check_ssh_status(client_ssh_connect, remote_connect):
                    remote_connect.send('\n' + commands + '\n')
                    time.sleep(wait_between_commands)
                    break
                else:
                    client_ssh_connect, remote_connect = SSHConnectionClass().ssh_reconnect(ip_address, username,
                                                                                            password, port)
            return client_ssh_connect, remote_connect

        except Exception:
            self.logger.exception('')
