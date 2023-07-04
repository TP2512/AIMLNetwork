import copy
import time
import logging
import datetime

from colorama import Fore

from InfrastructureSVG.General_Actions_Infrastructure.General_Actions_Infrastructure import GeneralActionsClass
from InfrastructureSVG.Network_Infrastructure.IP_Address_Network_Infrastructure import IPAddressNetworkClass
from InfrastructureSVG.ProgressBar.ProgressBarPrinter import ProgressBar

""" 
In this py file have 2 class
    - _SSHSendCommands
    - SSHConnection
"""


class WrongInstanceException(Exception):
    pass


class _SSHSendCommands:
    """
    This class ("SSHSendCommandsClass") responsible for send SSH commands (with or without output)
    Only for inheritance to "SSHConnection" Class
    """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        if not isinstance(self, SSHConnection):
            raise WrongInstanceException('Cannot call constructor, use the "SSHConnection" Class')

        self.full_output = ''
        self.last_session_output = ''
        self.return_code = None
        self.is_connected = None

    def with_output_collector(self, output_from_command, print_output, command):
        try:
            output_from_command = output_from_command.decode('utf-8')
            if print_output:
                string_to_replace = '\r'
                self.logger.info(f"The output for command {command} is:\n{output_from_command.replace(string_to_replace, '')}")
        except UnicodeDecodeError:
            # self.logger.info('Failed to decode output to utf-8, trying to encode("ascii") and decode("utf-8")')
            output_from_command = \
                GeneralActionsClass().byte_to_string_error_decode(output_from_command)
        self.last_session_output += output_from_command
        self.full_output += output_from_command

    def clean_output_collector(self, data):
        output = ""
        for line in data:
            output = output + line
        if output != "":
            self.last_session_output += output
            self.full_output += output

    def lines_reader(self, stdout, err=False):
        if err:
            stderr = stdout.readlines()
            self.clean_output_collector(stderr)
        elif stdout.channel.exit_status_ready():
            stdout = stdout.readlines()
            self.clean_output_collector(stdout)

    def wait_for_output_with_timeout(self, stdin, stdout, timeout):
        bar = ProgressBar()
        start_time = datetime.datetime.now(tz=datetime.timezone.utc)
        eta = start_time + datetime.timedelta(seconds=timeout)
        eta = datetime.datetime.strftime(eta, "%H:%M:%S")
        countdown = copy.deepcopy(timeout)
        for _ in range(timeout):
            if not stdout.channel.exit_status_ready():
                time.sleep(1)
                mins, secs = divmod(countdown, 60)
                hours, mins = divmod(mins, 60)
                timer = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
                bar.print_progress_bar(_ + 1, timeout, prefix='Progress until timeout:', suffix=f'Complete, {timer} Remained, ETA {eta}', length=50)
                countdown -= 1
            elif stdout.channel.exit_status_ready() and stdin.channel.eof_received:
                self.lines_reader(stdout)
                self.return_code = 0
                break
        if self.return_code is None and not stdin.channel.eof_received and not stdout.channel.exit_status_ready():
            self.return_code = 1
            self.logger.warning('Failed to get output from command, consider to increase timeout')
            # self.lines_reader(stderr, True)

    def with_clean_output(self, stdin, stdout, timeout):
        # https://stackoverflow.com/questions/28485647/wait-until-task-is-completed-on-remote-machine-through-python
        self.wait_for_output_with_timeout(stdin, stdout, timeout)

    def no_ping_logger(self, ip_address):
        self.last_session_output += f'\nThere is no ping to {ip_address} ' \
                                    f'or problem to connect over SSH ' \
                                    f'=> Commands not send\n'
        self.full_output += self.last_session_output
        self.is_connected = False

    def connection_loss_logger(self, ip_address, err):
        self.logger.exception(f'exception for {ip_address}')
        self.last_session_output += f'\nSSH session on {ip_address} is disconnected\n The exception error is:\n {err}\n'
        self.is_connected = False
        self.full_output += self.last_session_output

    def validate_connection(self):
        if isinstance(self, SSHConnection) and IPAddressNetworkClass(ip_address=self.ip_address).check_ping_status() and not self.check_ssh_status():
            self.last_session_output += f'\nHave ping but SSH session on {self.ip_address} is disconnected\n'
            self.full_output += self.last_session_output
            self.is_connected = False
            self.ssh_reconnect()

    def ssh_send_commands(self, commands, with_output=False, clean_output=False, wait_before_output=1, wait_between_commands=1,
                          output_receive=10000, end_line='\n', print_output=False, timeout=300):
        """
        This function responsible to send one command (return output)

        The function get 4 parameter:
            - "commands" - the command (one command!) that need to send (string/list type)
            - "with_output" - choose to get or not an output (integer type) [Default is False]
            - "wait_before_output" - the time before taking output (integer type) [Optional]
            - "output_receive" - the output that receive from the ssh connection (string type) [Optional]
        """

        self.last_session_output = ''
        try:
            if type(commands) is str:
                commands = [commands]

            if isinstance(self, SSHConnection):
                self.validate_connection()
                if IPAddressNetworkClass(ip_address=self.ip_address).check_ping_status() and self.check_ssh_status():
                    self.is_connected = True
                    for command in commands:
                        time.sleep(wait_between_commands)
                        if clean_output:
                            stdin, stdout, stderr = self.client_ssh.exec_command(f'{command}{end_line}', timeout=timeout)
                            self.with_clean_output(stdin, stdout, timeout)
                        elif self.check_ssh_status():
                            if not self.thread_flag:
                                self.set_time_out(self.timeout or 5)
                            self.remote_ssh.send(f'{command}{end_line}')
                            if with_output:
                                time.sleep(wait_before_output)
                                try:
                                    output_from_command = self.remote_ssh.recv(output_receive)
                                    self.with_output_collector(output_from_command, print_output, command)
                                except TimeoutError:
                                    self.return_code = 1
                else:
                    self.no_ping_logger(self.ip_address)
            else:
                self.last_session_output += '\nSSHConnection is no instance of self\n'
                self.full_output += self.last_session_output
        except Exception as err:
            self.connection_loss_logger(self.ip_address, err)

    # not relevant - Do not use with this function - the relevant function is: "ssh_send_commands"
    def ssh_send_commands_with_output(self, commands, wait_before_output=1, output_receive=10000):
        """
        This function responsible to send one command (return output)

        The function get 9 parameter:
            - "commands" - the command (one command!) that need to send (string type)
            - "wait_before_output" - the time before taking output (integer type) [Optional]
            - "output_receive" - the output that receive from the ssh connection (string type) [Optional]

        The function return 3 parameters:
            - "output" - client of SSH
        """

        output = ''
        try:
            if type(commands) is str:
                commands = [commands]
            if isinstance(self, SSHConnection):
                if IPAddressNetworkClass(ip_address=self.ip_address).check_ping_status() and self.check_ssh_status():
                    self.is_connected = True
                    for command in commands:
                        self.remote_ssh.send(f'{command}\n')
                        time.sleep(wait_before_output)
                        try:
                            output_from_command = self.remote_ssh.recv(output_receive).decode('utf-8')
                        except UnicodeDecodeError:
                            output_from_command = GeneralActionsClass().byte_to_string_error_decode(output)
                        output += output_from_command
                else:
                    output += f'\nSSH session on {self.ip_address} is disconnected\n'
                    self.is_connected = False
                    self.ssh_reconnect()
            else:
                output += '\nSSHConnection is no instance of self\n'
            return output
        except Exception as err:
            self.logger.exception(f'exception for {self.ip_address}')
            output += f'\nSSH session on {self.ip_address} is disconnected\n'
            output += f'The exception error is:\n {err}\n'
            return output

    # not relevant - Do not use with this function - the relevant function is: "ssh_send_commands"
    def ssh_send_commands_without_output(self, commands):
        """
        This function responsible to send one command (return output)

        The function get 9 parameter:
            - "commands" - the command (one command!) that need to send (string type)
        """

        try:
            if type(commands) is str:
                commands = [commands]
            if isinstance(self, SSHConnection):
                if IPAddressNetworkClass(ip_address=self.ip_address).check_ping_status():
                    self.is_connected = True
                    for command in commands:
                        self.remote_ssh.send(f'{command}\n')
                    return
                else:
                    self.is_connected = False
                    self.ssh_reconnect()
        except Exception:
            self.logger.exception(f'exception for {self.ip_address}')


class SSHConnection(_SSHSendCommands):
    """
    This class ("SSHConnectionClass") responsible for SSH connection
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(SSHConnection, self).__init__()

        self.client_ssh = None
        self.remote_ssh = None

        self.flag = {
            't_f': True,
            'count': 0
        }

        self.thread_flag = kwargs.get('thread_flag')
        self.max_reconnect_time = kwargs.get('max_reconnect_time')
        self.timeout = kwargs.get('timeout')

        self.ip_address = kwargs.get('ip_address')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.port = kwargs.get('port')
        self.retries_count = kwargs.get('retries_count') or 3

        if not self.port:
            self.port = 22

        if not self.ip_address or not self.username or not self.password:
            return

        if not self.max_reconnect_time:
            self.max_reconnect_time = 630

    def ssh_connection(self):
        """
        This function responsible to create ssh connection
        """
        import paramiko

        try:
            client_ssh = paramiko.SSHClient()
            # client_ssh.load_host_keys(f'{Path.home()}\\.ssh\\known_hosts')
            # client_ssh.load_system_host_keys()
            client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client_ssh.connect(hostname=self.ip_address, username=self.username, password=self.password, port=self.port, timeout=10)
            remote_ssh = client_ssh.invoke_shell()
            self.logger.info(f"Interactive session established with {self.ip_address}")
            setattr(self, 'client_ssh', client_ssh)
            setattr(self, 'remote_ssh', remote_ssh)

            self.flag = {'t_f': True, 'count': 0}
            self.is_connected = True

        except paramiko.AuthenticationException as error:
            self.logger.error(f'User is: {self.username}')
            self.logger.error(f'Password is: {self.password}')
            self.logger.error(error)
            raise paramiko.AuthenticationException from error
        except Exception as e:
            self.logger.info(
                f'{Fore.YELLOW}Interactive session not established with {self.ip_address}, reconnecting...'
            )
            self.is_connected = False

            self.ssh_reconnect()
            if not self.flag['t_f']:
                win_error, strerror = getattr(e, 'winerror', None), getattr(e, 'strerror', None)

                if win_error and strerror:
                    if hasattr(e, 'winerror') and hasattr(e, 'strerror'):
                        setattr(self, 'exception', f'WinError {e.winerror} {e.strerror}')
                elif not win_error and strerror:
                    if hasattr(e, 'strerror'):
                        setattr(self, 'exception', e.strerror)
                else:
                    setattr(self, 'exception', e)

    def ssh_reconnect(self):
        """
        This function responsible to create ssh reconnection
        """

        if self.thread_flag or (self.check_if_available() and self.flag['t_f']):
            if self.thread_flag:
                self.flag['t_f'] = True
                self.ssh_connection()
            elif self.flag['count'] == self.retries_count:
                self.flag['t_f'] = False
            else:
                self.flag['count'] += 1
                self.logger.info(f"{Fore.YELLOW}Attempt {self.flag['count']} out of {self.retries_count}")
                self.ssh_connection()
        else:
            self.logger.info(f"{Fore.YELLOW}Failed to establish SSH connection after {self.retries_count} retries")
            setattr(self, 'client_ssh', None)
            setattr(self, 'remote_ssh', None)

    def check_if_available(self):
        """
        This function responsible to check if the ssh session is available
        """

        try:
            t_f_available = IPAddressNetworkClass(ip_address=self.ip_address).check_ping_status()
            i = 0
            while self.thread_flag and not t_f_available and i < 100:
                t_f_available = IPAddressNetworkClass(ip_address=self.ip_address).check_ping_status()
                time.sleep(self.max_reconnect_time / 100)
                i += 1
            return t_f_available
        except Exception:
            self.logger.exception('"check_if_available" is fail')
            return False

    def check_ssh_status(self):
        """
        This function responsible to check if the ssh status (check the "client_ssh" and "remote_ssh" parameters)
        """

        try:
            if self.client_ssh and self.remote_ssh:
                return bool(
                    self.client_ssh.get_transport() is not None
                    and self.remote_ssh.get_transport() is not None
                    and getattr(self.client_ssh, '_transport').active
                    and not self.remote_ssh.closed
                )

            else:
                return False
        except Exception:
            self.logger.exception('"check_ssh_status" is fail')
            return False

    def ssh_close_connection(self):
        try:
            if self.check_ssh_status():
                self.client_ssh.close()
                self.logger.info(f'Connection to {self.ip_address} was closed successfully')
            else:
                self.logger.info(f'Connection to {self.ip_address} was NOT closed successfully')
        except Exception:
            self.logger.exception('"ssh_close_connection" is fail')

    def set_time_out(self, set_time=5):
        self.remote_ssh.settimeout(set_time)
