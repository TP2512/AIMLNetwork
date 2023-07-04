import subprocess
import logging
import ipaddr

""" 
In this py file have 1 class
    - IPAddressNetworkClass
"""


class IPAddressNetworkClass:
    """ This class ("IPAddressNetworkClass") responsible for IP related actions """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.ip_address = kwargs.get('ip_address')
        self.number_of_ping = kwargs.get('number_of_ping')
        if not self.number_of_ping:
            self.number_of_ping = 1

    def validate_ip_address(self, ip_address):
        """
        This function responsible to check for validate IP address and IP version (IPv4 or IPv6)

        The function get 1 parameter: 
            - "ip_address" - parameter need to be IP from string type

        The function return 2 parameters:
            - "ip_validate" - string that equal to "correct IP address" or "wrong value"
            - "ip_version" - string that equal to "IPv4", "IPv6" or None (if exception)
        """
        ip_version = ''
        if ip_address:
            try:
                ip = ipaddr.IPAddress(ip_address)
                ip_version = f'IPv{ip.version}'
                ip_validate = 'correct IP address'
                # self.logger.info(IP_ver)
                # self.logger.info('%s is a correct IP%s address.' % (ip, ip.version))

            except ValueError:
                # print('Wrong value, reenter the IP address')
                ip_validate = 'wrong value'
                return ip_validate, None
            except Exception:
                ip_validate = 'wrong value'
                self.logger.exception('')
                return ip_validate, None
        else:
            self.logger.warning('ip_address parameter is empty')
            ip_validate = 'wrong value'

        return ip_validate, ip_version

    def check_ping_status(self):
        try:
            from sys import platform
            if 'linux' in platform:
                return self.check_ping_status_from_linux()
            elif 'win' in platform:
                return self.check_ping_status_from_windows()
            else:
                return None
        except Exception:
            self.logger.exception('')
            return None

    def check_ping_status_from_linux(self):
        try:
            response = subprocess.Popen(f"ping -c {self.number_of_ping} {self.ip_address}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = response.communicate()

            if response.returncode == 0:
                return True
            self.logger.debug(out.decode('utf-8'))
            self.logger.debug(err.decode('utf-8'))
            return False
        except Exception:
            self.logger.exception('check_ping_status')
            return None

    def check_ping_status_from_windows(self):
        try:
            response = subprocess.Popen(f"ping -n {self.number_of_ping} {self.ip_address}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = response.communicate(timeout=5)

            if response.returncode == 0:
                return True
            self.logger.info(f'There is no Ping to {self.ip_address}')
            self.logger.debug(out.decode('utf-8'))
            self.logger.debug(err.decode('utf-8'))
            return False
        except subprocess.TimeoutExpired:
            self.logger.info(f'There is no Ping to {self.ip_address}')
            return None
