import logging
import shutil


class FilesActions:
    """ This class ("IPAddressNetworkClass") responsible for IP related actions """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def copy_files_from_linux(self, full_path_file, dst_path):
        pass

    def copy_files_from_windows(self, full_path_file, dst_path):
        try:
            new_dst = shutil.copy(full_path_file, dst_path)
            self.logger.info(new_dst)
        except Exception:
            self.logger.exception('')

    def copy_files_per_platform(self, full_path_file, dst_path):
        try:
            from sys import platform
            if 'linux' in platform:
                self.copy_files_from_linux(full_path_file, dst_path)
            elif 'win' in platform:
                self.copy_files_from_windows(full_path_file, dst_path)
            else:
                self.logger.error('platform was not found')
        except Exception:
            self.logger.exception('')

    def move_files_from_linux(self, full_path_file, dst_path):
        pass

    def move_files_from_windows(self, full_path_file, dst_path):
        try:
            new_dst = shutil.move(full_path_file, dst_path)
            self.logger.info(new_dst)
        except Exception:
            self.logger.exception('')

    def move_files_per_platform(self, full_path_file, dst_path):
        try:
            from sys import platform
            if 'linux' in platform:
                self.move_files_from_linux(full_path_file, dst_path)
            elif 'win' in platform:
                self.move_files_from_windows(full_path_file, dst_path)
            else:
                self.logger.error('platform was not found')
        except Exception:
            self.logger.exception('')
