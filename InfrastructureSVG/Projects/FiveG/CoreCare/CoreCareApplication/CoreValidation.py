import logging
import re
from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection
from InfrastructureSVG.Files_Infrastructure.SCP_Files.SCP_Infrastructure import SCPActionsClass

LINUX_IP = '192.168.124.93'
LINUX_USER_NAME = 'spuser'
LINUX_PASSWORD = 'sp_user9'
LINUX_CORE_VALIDATION_PATH = '/CoreCare/core_validation/'


class CoreValidation:
    def __init__(self, core_file_path, binary_timestamp):
        self.logger = logging.getLogger(
            f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.core_file_path = core_file_path
        self.binary_timestamp = int(binary_timestamp)
        self.save_on_path = LINUX_CORE_VALIDATION_PATH
        self.lib_path = f'{LINUX_CORE_VALIDATION_PATH}lib'
        self.ssh_obj = SSHConnection(
            ip_address=LINUX_IP,
            username=LINUX_USER_NAME,
            password=LINUX_PASSWORD)

        self.ssh_obj.ssh_connection()

    def __del__(self):
        self.ssh_obj.ssh_close_connection()

    def extract_gz_file(self, gz_file_path):
        extract_command = [
            f'gzip -dk {gz_file_path} && echo finish'
        ]
        self.ssh_obj.ssh_send_commands(commands=extract_command, clean_output=True, timeout=600)

    def clear_linux_dirs(self):
        clear_command = [
            f'rm -rf {self.save_on_path}/{self.binary_timestamp}'
        ]
        self.ssh_obj.ssh_send_commands(commands=clear_command)

    @staticmethod
    def bt_is_valid(bt):
        if bt:
            double_question_mark_count = bt.count("??")
            frames_count = bt.count("#")
            # Check if there are 3 or more valid frames
            if frames_count - double_question_mark_count >= 3:
                return True
        return False

    def run_gdb(self, binary_path, core_file_path):
        gdb_commands = [f'gdb {binary_path} {core_file_path}', 'c', f'set solib-search-path {self.lib_path}', 'c']
        self.ssh_obj.ssh_send_commands(commands=gdb_commands, with_output=True, wait_before_output=10, wait_between_commands=10, timeout=100)
        return self.ssh_obj.last_session_output

    @staticmethod
    def get_num_of_threads(gdb_output):
        return gdb_output.count("New LWP")

    @staticmethod
    def core_file_is_truncated(gdb_output):
        return gdb_output.count("truncated")

    def get_bt(self, thread_idx):
        thread_command = [f'thread {thread_idx}']
        self.ssh_obj.ssh_send_commands(commands=thread_command, with_output=True, timeout=20)
        bt_command = ['bt']
        self.ssh_obj.ssh_send_commands(commands=bt_command, with_output=True, timeout=20)
        return self.ssh_obj.last_session_output

    def gdb_validation(self, binary_path, core_file_path):
        # Run gdb
        gdb_output = self.run_gdb(binary_path=binary_path, core_file_path=core_file_path)
        if not gdb_output:
            mass = 'There is no "gdb_output"'
            self.logger.error(mass)
            return False, mass

        # Check if the core file is truncated
        if not self.core_file_is_truncated(gdb_output):
            self.logger.debug("The core is not truncated")
        self.logger.info("The core is truncated")

        # Go through the threads and check for a valid backtrace
        num_of_threads = self.get_num_of_threads(gdb_output)
        if not num_of_threads:
            self.logger.debug("num_of_threads count is 0")

        for thread_idx in range(1, num_of_threads + 1):
            backtrace = self.get_bt(thread_idx)
            if self.bt_is_valid(backtrace):
                mass = f'Valid BT was found in thread ID: {thread_idx}'
                self.logger.info(mass)
                return True, mass
        mass = 'The Core is not valid, there is no thread with valid BT'
        return False, mass

    def copy_core_to_remote_linux_machine(self):
        scp_action_ins = SCPActionsClass()
        return scp_action_ins.put_file_by_scp(
            ip_address=LINUX_IP,
            username=LINUX_USER_NAME,
            password=LINUX_PASSWORD,
            from_full_path=self.core_file_path.replace("_test", ""),
            to_full_path=f'{self.save_on_path}{self.binary_timestamp}',
        )

    def get_core_file_name(self):
        parsed_core_file_full_name = re.findall('airspaninfo.*gz', self.core_file_path)
        if len(parsed_core_file_full_name) == 0:
            return None
        core_file_full_name = parsed_core_file_full_name[0]
        return core_file_full_name.replace('.gz', '')

    @staticmethod
    def remove_new_line_char_from_string(string):
        return string.replace("\n", "")

    def get_binary_name(self):
        ls_command = f'ls -l {self.save_on_path}/{self.binary_timestamp}'
        awk_command = "awk '{print $9}'"
        grep_command = f'grep {self.binary_timestamp}'
        command = [f'{ls_command} | {awk_command} | {grep_command}']
        self.ssh_obj.ssh_send_commands(commands=command, clean_output=True, with_output=True)
        binary_name = self.remove_new_line_char_from_string(self.ssh_obj.last_session_output)
        return binary_name if f'_{self.binary_timestamp}' in binary_name else None

    def check_if_binary_file_exists(self):
        self.logger.debug('Start to check if binary file exists')
        ls_command = f'ls -l {self.save_on_path}/{self.binary_timestamp}'
        awk_command = "awk '{print $9}'"
        grep_command = f'grep {self.binary_timestamp}'
        command = [f'{ls_command} | {awk_command} | {grep_command}']
        self.ssh_obj.ssh_send_commands(commands=command, clean_output=True, with_output=True)
        binary_name = self.remove_new_line_char_from_string(self.ssh_obj.last_session_output)
        if f'_{self.binary_timestamp}' in binary_name:
            binary_file_linux_path = f'{self.save_on_path}{self.binary_timestamp}/{binary_name}'
            return True, binary_file_linux_path
        return False, None

    def core_validation(self, debug=False):
        # sourcery skip: extract-duplicate-method, extract-method, use-fstring-for-concatenation
        try:
            # Check for binary file
            binary_file_exists, binary_file_linux_path = self.check_if_binary_file_exists()
            if not binary_file_exists:
                mass = "Error - Binary not found"
                self.logger.error(mass)
                return False, mass

            # Get core file name
            core_file_name = self.get_core_file_name()
            if not core_file_name:
                mass = "Error - Core file name is incorrect"
                self.logger.error(mass)
                return False, mass

            # Copy the core file to linux machine for gdb validation
            if not debug:
                self.logger.debug('Start to copy the core file to linux machine for gdb validation')
                if not self.copy_core_to_remote_linux_machine():
                    mass = "Error - Copy core file to the linux machine failed"
                    self.logger.error(mass)
                    return False, mass

            core_file_linux_path = f'{self.save_on_path}{self.binary_timestamp}/{core_file_name}'

            # Extract the gz core file in the linux machine
            if not debug:
                self.logger.debug('Start to extract the gz core file in the linux machine')
                self.extract_gz_file(core_file_linux_path + '.gz')

            # GDB validation
            self.logger.debug('Start gdb validation')
            gdb_validation_bool, mass = self.gdb_validation(binary_file_linux_path, core_file_linux_path)
            if not gdb_validation_bool:
                self.logger.error(mass)
                return False, mass
            return True, mass

        except Exception as err:
            self.logger.exception(err)
            return False, err
        finally:
            self.logger.info('Start to clear linux dirs')
            self.clear_linux_dirs()


def main():
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger

    project_name, site = 'CoreValidation', None
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    core_validation_ins = CoreValidation(
        core_file_path='\\\\192.168.127.247\\cores\\SVG\\2023_04_03\\20.50-36-0.0\\test\\var\\crash\\'
                       'airspaninfo_EAB869009EC0_du-at2200-eab869009ec0-1-deployment-74cc85bbcf-bhp5q_gnb_du_371_26266_11_1681627216.gz',
        binary_timestamp='1681626830'
    )

    _t_f, _mass = core_validation_ins.core_validation(debug=True)
    if _t_f:
        logger.info('PASS')
    else:
        logger.error('FAIL')
        logger.error(_mass)


if __name__ == '__main__':
    main()
