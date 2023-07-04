import logging
import paramiko
from paramiko import SSHClient
from scp import SCPClient

""" 
In this py file have 1 class
    - SCPActions
"""


class SCPActionsClass:
    """ This class ("ReadFromTXTFileClass") responsible for read data from txt files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_file_by_scp(self, ip_address, username, password, from_full_path, to_full_path, preserve_times=True, recursive=False):
        """
        :param ip_address:
        :param username:
        :param password:
        :param from_full_path:
        :param to_full_path:
        :param preserve_times:
        :param recursive: False for file, True for folder
        :return:
        """
        scp = None
        try:
            ssh = SSHClient()
            # ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip_address, username=username, password=password)

            # SCP client takes a paramiko transport as an argument
            scp = SCPClient(ssh.get_transport())

            scp.get(from_full_path, to_full_path, preserve_times=preserve_times, recursive=recursive)

            self.logger.info('File was copied successfully!')
            return True
        except Exception:
            self.logger.exception('')
            return None
        finally:
            if scp:
                scp.close()

    def put_file_by_scp(self, ip_address, username, password, from_full_path, to_full_path, preserve_times=True,
                        recursive=False):
        """
        :param ip_address:
        :param username:
        :param password:
        :param from_full_path:
        :param to_full_path:
        :param preserve_times:
        :param recursive: False for file, True for folder
        :return:
        """
        scp = None
        try:
            ssh = SSHClient()
            # ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip_address, username=username, password=password)

            # SCP client takes a paramiko transport as an argument
            scp = SCPClient(ssh.get_transport())

            scp.put(from_full_path, to_full_path, preserve_times=preserve_times, recursive=recursive)

            self.logger.info('File was copied successfully!')
            return True
        except Exception:
            self.logger.exception('')
            return None
        finally:
            if scp:
                scp.close()
