import hashlib
import ctypes
import datetime
from datetime import date
import calendar
import logging


class GeneralActionsClass:
    """ This class ("JiraConnectionClass") responsible for do any general action """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def byte_to_string_error_decode(self, byte_string):
        """
        This function responsible to convert byte to string according to decoding error

        The function get 1 parameter:
            - "byte_string" - the byte parameter (byte type)

        The function return 1 parameters:
            - "output" - string parameter (string type - utf-8)
        """

        output = ''
        try:
            output_ = str(byte_string).encode("ascii").decode("utf-8")[2:][:-1]
            for i_line in output_.split("\\r\\n"):
                # print(i_line.replace("\\r", ""))
                output = output + i_line.replace("\\r", "") + "\n"
        except Exception:
            self.logger.exception('')
        return output

    def to_hash(self, string_value):
        """
        This function responsible for convert string value to hash number

        The function get 3 parameter:
            - "jira" - parameter need to be client of jira
            - "defect_number" - parameter need to be a string of defects (DEF-number)
                * for example: DEF-12345
            - "new_status" - parameter need to be a string string of the current status (string type)

        The function return 0 parameters
        """
        try:
            hash_object = hashlib.md5(str(string_value).encode('utf-8'))
            hex_string = f'0x{hash_object.hexdigest()}'
            hex_int = int(hex_string, 16)
            new_int = abs(hex_int % (10 ** 8))
            return str(new_int)

        except Exception:
            self.logger.exception('')

    def popup(self, message_name_type, message_number_type):
        """
        This function responsible for return the specific current date (in format: Y-m-d)

        The function get 2 parameter:
            - "message_name_type" the message name type (int type)
                * For example: info, error, etc.
            - "message_number_type" the message number type (string type)
                * For example: 0, 1, 2, 3, etc.

        The function return 1 parameters:
            - "result" the result from the popup (int type)
        """
        try:
            return ctypes.windll.user32.MessageBoxW(0, "That's an error", message_name_type, message_number_type)

        except Exception:
            self.logger.exception('')

    def get_current_date(self):
        """
        This function responsible for return the specific current date (in format: Y-m-d)

        The function get 0 parameter:

        The function return 1 parameters:
            - "current_date" the current date (string type)
        """
        try:

            return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            self.logger.exception('')

    def get_current_time(self):
        """
        This function responsible for return the specific current time (in format: H:M)

        The function get 0 parameter:

        The function return 1 parameters:
            - "current_time" the current time (string type)
        """
        try:
            return datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")

        except Exception:
            self.logger.exception('')

    def get_current_day_name(self):
        """
        This function responsible for return the specific current day name

        The function get 0 parameter:

        The function return 1 parameters:
            - "current_day_name" the current day name (string type)
        """
        try:
            current_day = date.today()
            return calendar.day_name[current_day.weekday()]
        except Exception:
            self.logger.exception('')
