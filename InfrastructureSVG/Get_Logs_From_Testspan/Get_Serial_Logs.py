from scp import SCPClient, SCPException
from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection
import logging
from InfrastructureSVG.Files_Infrastructure.ZIP_Files.ZIP_Files_Infrastructure import ZIPFilesReadClass


class GetSerialLogsFromTestspan:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_serial_logs_by_uid_list(self, uid_list, exec_id, path):
        try:
            client = SSHConnection(ip_address='asil-svg-testspan',
                                   username='root', password='Testsp@n')
            client.ssh_connection()
            scp = SCPClient(client.client_ssh.get_transport())
            ftp = client.client_ssh.open_sftp()
            if not uid_list:
                return False

            for i in uid_list:
                try:
                    for f in ftp.listdir(f'/home/difido/difido-server/docRoot/reports/exec_{exec_id}/tests/test_{i}'):

                        if '.log' in f and '.zip' not in f:
                            if '.csv' not in f and '.html' not in f and '.js' not in f:
                                try:
                                    scp.get(f'/home/difido/difido-server/docRoot/reports/exec_{exec_id}/tests/test_{i}/{f}',
                                            path, preserve_times=True)
                                except (SCPException, FileNotFoundError):
                                    continue
                        elif '.zip' in f:
                            scp.get(f'/home/difido/difido-server/docRoot/reports/exec_{exec_id}/tests/test_{i}/{f}',
                                    path, preserve_times=True)
                            ZIPFilesReadClass().extract_archive_folder_to_zip(f'{path}/{f}', path)
                except FileNotFoundError:
                    continue
            return True
        except Exception:
            self.logger.exception('')
