import copy
import threading
import time
import logging
import datetime
import pssh
from pssh import exceptions
from pssh.clients import SSHClient
from termcolor import colored

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


class _ParallelSSHSendCommands:
    """
    This class ("SSHSendCommandsClass") responsible for send SSH commands (with or without output)
    Only for inheritance to "SSHConnection" Class
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        if not isinstance(self, ParallelSSHConnection):
            raise WrongInstanceException('Cannot call constructor, use the "SSHConnection" Class')

        self.full_output = ''
        self.last_session_output = ''
        self.return_code = None

    def with_output_collector(self, output_from_command, print_output, command):
        try:
            output_from_command = output_from_command
            if print_output:
                string_to_replace = '\r'
                self.logger.info(
                    f"The output for command {command} is:\n{output_from_command.replace(string_to_replace, '')}")
        except UnicodeDecodeError:
            self.logger.info('Failed to decode output to utf-8, trying to encode("ascii") and decode("utf-8")')
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
            return
        stdout = "\n".join(stdout)
        self.clean_output_collector(stdout)

    def wait_for_output_with_timeout(self, timeout, hostoutput):
        event = threading.Event
        event = threading.Event()
        thread = threading.Thread(target=self.progress_bar, args=(timeout, event))
        thread.start()
        output = []
        try:
            for line in hostoutput.stdout:
                output.append(line)
                self.logger.info(line)
            event.set()
            time.sleep(0.5)
            self.lines_reader(output)
            self.logger.info("\nCommand Finished")

        except pssh.exceptions.Timeout:
            event.set()
            time.sleep(0.5)
            self.logger.info("\nCommand failed, try increasing the timeout")

    @staticmethod
    def progress_bar(dur, event):
        time.sleep(1)
        bar = ProgressBar()
        start_time = datetime.datetime.now(tz=datetime.timezone.utc)
        eta = start_time + datetime.timedelta(seconds=dur)
        countdown = copy.deepcopy(dur)
        for _ in range(dur):
            if not event.is_set():
                time.sleep(1)
                mins, secs = divmod(countdown, 60)
                hours, mins = divmod(mins, 60)
                timer = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
                bar.print_progress_bar(_ + 1, dur, prefix='Progress until timeout:',
                                       suffix=f'Complete, {timer} Remained, ETA {eta}', length=50)
                countdown -= 1

    def with_clean_output(self, timeout, host):
        # https://stackoverflow.com/questions/28485647/wait-until-task-is-completed-on-remote-machine-through-python
        self.wait_for_output_with_timeout(timeout, host)

    def no_ping_logger(self, ip_address):
        self.last_session_output += f'\nThere is no ping to {ip_address} ' \
                                    f'or problem to connect over SSH ' \
                                    f'=> Commands not send\n'

        self.full_output += self.last_session_output

    def connection_loss_logger(self, ip_address, err):
        self.logger.exception(f'exception for {ip_address}')
        self.last_session_output += f'\nSSH session on {ip_address} is disconnected\n The exception error is:\n {err}\n'

        self.full_output += self.last_session_output

    def validate_connection(self):
        if isinstance(self, ParallelSSHConnection) and IPAddressNetworkClass(
                ip_address=self.ip_address).check_ping_status() and not self.check_ssh_status():
            self.last_session_output += f'\nHave ping but SSH session on {self.ip_address} is disconnected\n'
            self.full_output += self.last_session_output
            self.ssh_reconnect()

    def ssh_send_commands(self, commands, with_output=False, clean_output=False, wait_before_output=1,
                          wait_between_commands=1,
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
        output_from_command = ''
        try:
            if isinstance(self, ParallelSSHConnection):
                self.validate_connection()
                if IPAddressNetworkClass(ip_address=self.ip_address).check_ping_status() and self.check_ssh_status():
                    for command in commands:
                        time.sleep(wait_between_commands)
                        if clean_output:
                            host_output = self.client_ssh.run_command(f'{command}{end_line}')
                            self.with_clean_output(timeout, host_output)
                        elif self.check_ssh_status():
                            if not self.thread_flag:
                                # cant put timeout on shell commands
                                self.set_time_out(self.timeout or 5)
                            self.remote_ssh.run(f'{command}{end_line}')
                            self.remote_ssh.close()
                            if with_output:
                                time.sleep(wait_before_output)
                                try:
                                    output = []
                                    for line in self.remote_ssh.stdout:
                                        output.append(line)
                                        output_from_command = "\n".join(output)
                                    # output_from_command = self.remote_ssh.stdout
                                    self.with_output_collector(output_from_command, print_output, command)
                                except TimeoutError:
                                    self.return_code = 1
                                    # self.logger.warning(f'Failed to get output after timeout of {self.timeout or 300} seconds, consider to increase timeout')

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
            if isinstance(self, ParallelSSHConnection):
                if IPAddressNetworkClass(ip_address=self.ip_address).check_ping_status() and self.check_ssh_status():
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
            if isinstance(self, ParallelSSHConnection):
                if IPAddressNetworkClass(ip_address=self.ip_address).check_ping_status():
                    for command in commands:
                        self.remote_ssh.send(f'{command}\n')
                    return
                else:
                    self.ssh_reconnect()
        except Exception:
            self.logger.exception(f'exception for {self.ip_address}')


class ParallelSSHConnection(_ParallelSSHSendCommands):
    """
    This class ("SSHConnectionClass") responsible for SSH connection
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(
            f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        super(ParallelSSHConnection, self).__init__()

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

        try:
            client_ssh = SSHClient(self.ip_address, user=self.username, password=self.password, port=self.port,
                                   timeout=60)
            remote_ssh = client_ssh.open_shell()
            self.logger.info(f"Interactive session established with {self.ip_address}")
            setattr(self, 'client_ssh', client_ssh)
            setattr(self, 'remote_ssh', remote_ssh)
            self.flag = {'t_f': True, 'count': 0}

        except Exception as e:
            self.logger.info(
                colored(f'Interactive session not established with {self.ip_address}, reconnecting...', 'yellow'))

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
                self.logger.info(colored(f"Attempt {self.flag['count']} out of {self.retries_count}", 'yellow'))
                self.ssh_connection()
        else:
            self.logger.info(
                colored(f"Failed to establish SSH connection after {self.retries_count} retries", 'yellow'))
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
            self.client_ssh = SSHClient(self.ip_address, user=self.username, password=self.password, port=self.port,
                                        timeout=5)
            self.remote_ssh = self.client_ssh.open_shell()
            return bool(self.client_ssh and self.remote_ssh)
        except Exception:
            self.logger.exception('"check_ssh_status" is fail')
            return False

    def ssh_close_connection(self):
        try:
            if self.check_ssh_status():
                self.client_ssh.disconnect()
                self.logger.info(f'Connection to {self.ip_address} was closed successfully')
            else:
                self.logger.info(f'Connection to {self.ip_address} was NOT closed successfully')
        except Exception:
            self.logger.exception('"ssh_close_connection" is fail')

    def set_time_out(self, set_time=5):
        self.timeout = set_time

    def paramiko_set_time_out(self, set_time=5):
        self.remote_ssh.settimeout(set_time)

