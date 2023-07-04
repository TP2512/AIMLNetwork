import os
import time
import zipfile
import tarfile
import logging
import subprocess

from InfrastructureSVG.Files_Infrastructure.Actions_On_Files_And_Folders.Active_actions_files_and_folders \
    import GeneralActionClass

""" 
In this py file have 3 class
    - ZIPFilesReadClass
    - ZIPFilesWriteClass
    - TARGZFilesWriteClass
"""


class ZIPFilesReadClass:
    """ This class ("RARFilesClass") responsible for RAR files related actions """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def extract_archive_folder_to_zip(self, full_path_file, directory_to_extract):
        try:
            time.sleep(1)
            check_if_directory_exist_t_f_ = GeneralActionClass().check_if_directory_exist(directory_to_extract)
            if not check_if_directory_exist_t_f_:
                os.system(f'mkdir {directory_to_extract}')
            with zipfile.ZipFile(full_path_file, 'r') as zip_ref:
                zip_ref.extractall(directory_to_extract)
        except Exception:
            self.logger.exception("")


class ZIPFilesWriteClass:
    """ This class ("RARFilesClass") responsible for zip files related actions """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def create_archive_folder_to_zip(self, full_path):
        """
        This function responsible to create zip files to specific file folder

        The function get 1 parameter:
            - "full_path" - parameter need to be the path location (string type) of the folder to archive
                * for example: C:\\Users\\username\\New_folder
        The function return 1 parameters:
            - "zip_path" - the full path of the zip file (string type)
                * for example: C:\\Users\\username\\Desktop\\New_folder.zip
        """

        fantasy_zip = zipfile.ZipFile(f"{full_path}.zip", 'w')
        zip_path = f"{full_path}.zip"
        try:
            for folder, sub_folders, files in os.walk(full_path):

                for file in files:
                    if file.endswith(''):
                        fantasy_zip.write(os.path.join(folder, file),
                                          os.path.relpath(os.path.join(folder, file), full_path),
                                          compress_type=zipfile.ZIP_DEFLATED)
            fantasy_zip.close()
            return zip_path
        except FileNotFoundError:
            self.logger.debug("[WinError 2] The system cannot find the file specified")
            return None
        except OSError:
            self.logger.debug("OSError: [Err no 28] No space left on device")
            return None
        except Exception:
            self.logger.debug("Can't read CSV file from Pycharm folder")
            self.logger.exception('')
            return None

    def create_archive_folder_to_zip_to_path(self, src_folder_path, dst_path):
        """
        This function responsible to create zip files to specific folder

        The function get 1 parameter:
            - "src_folder_path" - parameter need to be the path location of the folder to archive of the folder to
                                  archive (string type)
                * for example: C:\\Users\\username\\New_folder

            - "dst_path" - parameter need to be the path location of save the zip file of the folder to archive
                           (string type)
                * for example: C:\\Users\\username\\New_folder

        The function return 0 parameters:
        """

        zf = zipfile.ZipFile(f"{dst_path}.zip", "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(src_folder_path)
        for dir_name, sub_dirs, files in os.walk(src_folder_path):
            for filename in files:
                abs_name = os.path.abspath(os.path.join(dir_name, filename))
                arc_name = abs_name[len(abs_src) + 1:]
                self.logger.info(f'zipping {os.path.join(dir_name, filename)} as {arc_name}')
                zf.write(abs_name, arc_name)
        zf.close()


class TARGZFilesWriteClass:
    """ This class ("TARGZFilesWriteClass") responsible for convert tar.gz file to zip """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def convert_tar_gz_to_zip(self, folder_path, file_name_tar, directory_to_extract):
        """
        This function responsible to convert .tar.gz file to .zip file

        The function get 2 parameter:
            - "folder_path" - parameter need to be the path location of the folder file.tar.gz (string type)
                * for example: C:\\Users\\username\\New_folder
            - "file_name_tar" - parameter need to be the name of the file.tar.gz (string type)
                * for example: name123.tar.gz
        The function return 0 parameters:
        """
        try:
            if folder_path[len(folder_path)-1] != '\\':
                folder_path = folder_path + '\\'
            file_name_zip = file_name_tar.replace(".tar.gz", "_new.zip")
            tar_file = tarfile.open(name=folder_path + file_name_tar, mode='r|gz')
            zip_file = zipfile.ZipFile(file=f'{directory_to_extract}\\{file_name_zip}',
                                       mode='a', compression=zipfile.ZIP_DEFLATED)
            for m in tar_file:
                try:
                    f = tar_file.extractfile(m)
                    fl = f.read()
                    fn = m.name
                    zip_file.writestr(fn, fl)
                except Exception:
                    pass
            tar_file.close()
            zip_file.close()

        except Exception:
            self.logger.exception('')

    def convert_tar_tar_bz2_to_zip(self, folder_path, file_name_tar, directory_to_extract):
        """
        This function responsible to convert .tar.bz2 file to .zip file

        The function get 2 parameter:
            - "folder_path" - parameter need to be the path location of the folder file.tar.bz2 (string type)
                * for example: C:\\Users\\username\\New_folder
            - "file_name_tar" - parameter need to be the name of the file.tar.bz2 (string type)
                * for example: name123.tar.gz
        The function return 0 parameters:
        """
        try:
            if folder_path[len(folder_path) - 1] != '\\':
                folder_path = folder_path + '\\'
            file_name_zip = file_name_tar.replace(".tar.bz2", "_new.zip")
            tar_file = tarfile.open(name=folder_path + file_name_tar, mode='r|bz2')
            zip_file = zipfile.ZipFile(file=directory_to_extract + "\\" + file_name_zip,
                                       mode='a', compression=zipfile.ZIP_DEFLATED)
            for m in tar_file:
                try:
                    f = tar_file.extractfile(m)
                    fl = f.read()
                    fn = m.name
                    zip_file.writestr(fn, fl)
                except Exception:
                    pass
            tar_file.close()
            zip_file.close()

        except Exception:
            self.logger.exception('')

    def online_untar(self, tar_path, file_name):
        try:
            tar = tarfile.open(tar_path, encoding='utf-8')

            fp_read_list = None
            tr_gz_name = None
            for tr_gz_name in tar.getmembers():
                if file_name in tr_gz_name.name:
                    fp = tar.extractfile(tr_gz_name)
                    fp_read = fp.read()
                    fp_read_list = fp_read.decode("UTF-8").split("\n")
                    break
            tar.close()
            if not tr_gz_name:
                self.logger.error(f'{tr_gz_name} is not exist')

            return fp_read_list
        except Exception:
            self.logger.exception('')
            return False

    def untar(self, tar_path, extract_to=None):
        if not extract_to:
            extract_to = tar_path

        try:
            tar = tarfile.open(tar_path, encoding='utf-8')

            tar.extractall(path=extract_to)
            tar.close()
            return True
        except Exception:
            self.logger.exception('')
            return False

    def untar_and_wait_untill(self, tar_path, extract_to=None, new_folder_name=None):
        try:
            tar_path_split = tar_path.split("\\")
            if not extract_to:
                extract_to = '\\'.join(tar_path_split[:-1])

            if not new_folder_name:
                file_name = tar_path_split[-1]
                new_folder = '.'.join(file_name.split(".")[:-1])
                extract_to = f'{extract_to}\\{new_folder}'
            else:
                extract_to = f'{extract_to}\\{new_folder_name}'
            os.system(f'mkdir "{extract_to}"')

            command = f'tar -zxvf "{tar_path}" -C "{extract_to}"'
            process = subprocess.Popen(command, shell=True)
            process.wait()
        except Exception:
            self.logger.exception('')
