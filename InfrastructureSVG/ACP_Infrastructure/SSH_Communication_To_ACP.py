import logging
import re
from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection
from scp import SCPClient


class SSHCommunicationToACP:
    """
    This class is responsible to communicate to ACP server.
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.acp_name = kwargs.get('acp_name')
        self.acp_username = kwargs.get('username')
        self.acp_password = kwargs.get('password')
        self.acp_commands = kwargs.get('commands')
        self.dest_path = kwargs.get('dest_path')
        self.source_path = kwargs.get('source_path')
        self.total_output = ''
        self.client_ssh = None
        self.remote_connect = None
        self.wait = None
        self.regex_pattern = None

    def send_commands_to_acp(self):
        """
        This function is responsible to send commands ACP linux server
        """
        ssh_obj = SSHConnection(
            ip_address=self.acp_name,
            username='spuser',
            password='sp_user9',
            )

        ssh_obj.ssh_connection()
        self.client_ssh = ssh_obj.client_ssh
        try:
            for command in self.acp_commands:
                self.logger.info(f'sending command: {command}')

                if 'copy sw version' in command:
                    process_msg = 'copy sw version...'
                    self.logger.info(f'Start {process_msg} ...')
                    if self.put_file_to_linux_directory():
                        self.wait = 3
                        continue
                    else:
                        self.logger.exception('')
                        return None
                elif '--delete-db' in command:
                    process_msg = 'uninstall NMS version'
                    self.logger.info(f'Start {process_msg} ...')
                    self.wait = 50
                elif '--start-services' in command:
                    process_msg = 'install NMS version'
                    self.logger.info(f'Start {process_msg} ...')
                    self.wait = 80
                else:
                    self.wait = 2
                ssh_obj.ssh_send_commands(commands=command, with_output=True, wait_before_output=self.wait,
                                          output_receive=50000000)

                self.total_output = self.total_output + ssh_obj.full_output

                if '--start-services' in command:
                    self.regex_pattern = 'NMS Installation completed'
                    self.validate_status()
                elif '--delete-db' in command:
                    self.regex_pattern = 'NMS uninstallation completed'
                    self.is_uninstall_completed()
        except Exception:
            self.logger.exception('')
            return None

    def is_uninstall_completed(self):
        """
        This function is responsible to if uninstall of NMS process is completed
        """
        if self.validate_status():
            self.logger.info('NMS Uninstallation completed successfully')
        else:
            self.logger.exception('Uninstall process failed!')

    def is_install_completed(self):
        """
        This function is responsible to if install of NMS process is completed
        """
        if self.validate_status():
            self.logger.info('NMS Installation completed successfully')
        else:
            self.logger.exception('Install process failed!')

    def validate_status(self):
        """
        This function is responsible to validate status
        """
        if self.regex_pattern.lower() in re.findall(self.regex_pattern, self.total_output)[0].lower():
            return True

    def put_file_to_linux_directory(self):
        try:
            scp = SCPClient(self.client_ssh.get_transport())

            scp.put(self.source_path, self.dest_path, preserve_times=True)

            self.logger.info('File was copied successfully!')
            return True
        except Exception:
            self.logger.exception('Specified target ACP version not found')
            return None
