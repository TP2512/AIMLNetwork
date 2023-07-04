import os
import time
from cryptography.fernet import Fernet
import logging


""" 
In this py file have 3 class
    - GeneralActionClass
    - ActionOnFilesClass
    - ActionOnFoldersClass
"""


class GeneralActionClass:
    """ This class ("ActionOnFilesClass") responsible to do actions on folder and\\or files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def copy_to_folder(self, from_path, to_path):
        """
        This function responsible to copy files\folder from one folder to another folder

        The function get 2 parameter:
            - "from_path" - parameter need to be the current full path location of the file include the file name
              (string type)
            - "to_path" - parameter need to be the current full path of new location (string type)

        The function return 0 parameters
        """

        # to_path = '\\\\fs4\\PRT_Attachments\\' + str(defect_number)
        os.system(f'mkdir {to_path}')
        time.sleep(1)
        # print("from_path is: " + str(from_path))
        # print("to_path is: " + str(to_path))
        try:
            file_copied = os.system(f'copy {from_path} {to_path}')
            if file_copied == 0:  # copy
                self.logger.info(f"The file was copied to {to_path}\n")
            if file_copied == 1:  # not copy
                self.logger.warning("The file was not copied - (There is not enough space on the disk)\n")
        except TypeError:
            self.logger.exception("The file was not copied - (The path is broken)\n")
        except Exception:
            self.logger.exception("The file of was not copied - (Unknown reason)\n")
            return None

    def check_if_directory_exist(self, specific_directory_path):
        """
        This function responsible to check if specific directory is exists

        The function get 1 parameter:
            - "specific_directory_path" - parameter need to be the full path location of the file\folder (string type)

        The function return 1 parameters
            - "True"\"False" - the answer if the file\folder is exists
                * True - exist
                * False - not exist
        """

        try:
            if not os.path.exists(specific_directory_path):
                self.logger.info("directory not exists")
                return False
            else:
                self.logger.info("directory already exists")
                return True
        except FileExistsError:
            self.logger.debug("directory not exists")
            return None
        except Exception:
            self.logger.exception('')
            return None


class ActionOnFilesClass:
    """ This class ("ActionOnFilesClass") responsible to do actions on files """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def encryption_file(self, file_path):
        """
        This function responsible to encryption file

        The function get 1 parameter:
            - "file_path" - parameter need to be the full path location of the file (string type)

        The function return 1 parameters
            - "key" - the key for decrypted file (byte type)
        """

        try:
            # Get key
            key = Fernet.generate_key()
            # print(key)

            # Open the file to encrypt
            filename = file_path
            with open(filename, 'rb') as f:
                data = f.read()

            for_enc = Fernet(key)
            encrypted = for_enc.encrypt(data)

            # Write the encrypted file
            with open(f"{filename}.encrypted", 'wb') as f:
                f.write(encrypted)
            return key
        except Exception:
            self.logger.exception('')
            return None

    def decryption_file(self, file_path_enc, key):
        """
        This function responsible to decryption file

        The function get 1 parameter:
            - "file_path" - parameter need to be the full path location of the file (string type)
            - "key" - parameter need to be the relevant key for decryption the file

        The function return 1 parameters
            - "decryption_data" - the key for decrypted file (byte type)
        """

        try:
            # Open the file to encrypt
            filename = file_path_enc
            with open(filename, 'rb') as f:
                data = f.read()

            # decrypt file
            fernet = Fernet(key)
            return (fernet.decrypt(data)).decode()
        except Exception:
            self.logger.exception('')
            return None


class ActionOnFoldersClass:
    """ This class ("ActionOnFilesClass") responsible to do actions on folders """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
