import logging
from datetime import datetime, timezone

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging
from InfrastructureSVG.ACP_Infrastructure.General_Actions import GeneralSshACPActions
from InfrastructureSVG.ACP_Infrastructure.SSH_Communication_To_ACP import SSHCommunicationToACP
from InfrastructureSVG.VMWare_Infrastructure.Communication_To_VM_ware import CommunicateToVMware

from robot.api.deco import keyword
# from robot.libraries.BuiltIn import BuiltIn


class ACPUpdater:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    @keyword(name='ACP Updater Main')
    def acp_updater_main(self, acp_name, target_acp_version, vcenter_ip, vcenter_user, vcenter_password, vm_name):
        current_active_acp_version = GeneralSshACPActions().get_acp_release_version(acp_name=acp_name)[4:]

        try:
            if current_active_acp_version >= target_acp_version:
                raise Exception(
                    f'Active build version "{current_active_acp_version}" must be lower than'
                    f' Target build version "{target_acp_version}"')
            # active_sr_version = current_active_acp_version[0:4]
            # active_build_version = current_active_acp_version.split('.')[2]

            target_sr_version = target_acp_version[0:4]
            target_build_version = target_acp_version.split('.')[2]

            src_path_to_target_build_ver = f'\\\\fs23\\SoftwareReleases\\NMS\\SR{target_sr_version}\\' \
                                           f'Build {target_build_version}\\NMS (Linux)\\' \
                                           f'InstallNMS_129.{target_acp_version}'

            src_path_to_target_build_ver = f'T:\\SVG\\Automation\\~Semyon~\\ACP_Updater_test\\' \
                                           f'InstallNMS_129.{target_acp_version}'

            dst_acp_build_path = f'/root/ACP_Installations/'

            vsphere_params = {'vcenter_ip': f'{vcenter_ip}',
                              'vcenter_user': f'{vcenter_user}',
                              'vcenter_password': f'{vcenter_password}',
                              'vm_name': f'{vm_name}',
                              'operation': 'create',  # Static parameter
                              'snapshot_name': f'{current_active_acp_version}',
                              }

            acp_params = {'acp_name': acp_name,
                          'username': 'spuser',
                          'password': 'sp_user9',
                          'commands': ['sudo su', 'sp_user9',
                                       f'mkdir {dst_acp_build_path}{target_acp_version}/',  # create new directory
                                       f'chmod -R 777 {dst_acp_build_path}{target_acp_version}/',
                                       'copy sw version',  # using as flag to trigger put_file function

                                       # set r/wr for target version
                                       f'chmod 777 {dst_acp_build_path}{target_acp_version}/'
                                       f'InstallNMS_129.{target_acp_version}',

                                       # uninstall active version
                                       f'{dst_acp_build_path}{current_active_acp_version}/'
                                       f'InstallNMS_129.{current_active_acp_version} uninstall --delete-db false',

                                       f'{dst_acp_build_path}{target_acp_version}/InstallNMS_129.{target_acp_version}'
                                       f' install -s 127.0.0.1'
                                       ' -u sa -p SVG_5g12 -a /opt/nms_data -d /var/opt/mssql/sql_data'
                                       ' --start-services true'
                                       ' --auto-services true --licence-agreed true'],  # install target version

                          'source_path': src_path_to_target_build_ver,
                          # path/directory which has an origin file
                          'dest_path': f'{dst_acp_build_path}{target_acp_version}'
                          # path/directory which should get/receive a file
                          }

            vm_snapshot = CommunicateToVMware(**vsphere_params)
            if vm_snapshot.create_snapshot():
                self.logger.info('Snapshot process is completed!')

                get_target_acp_version = SSHCommunicationToACP(**acp_params)
                if get_target_acp_version.send_commands_to_acp():
                    self.logger.info('Copy new file, Uninstall, Install was completed!')
                self.logger.info('End of Script!')
        except Exception:
            self.logger.exception('')


if __name__ == '__main__':
    active_date_time = datetime.now(timezone.utc)
    time_string = active_date_time.strftime("%HT%MT%S")
    date_string = active_date_time.strftime("%Y.%m.%d")
    log_path = '\\\\fs4\\data\\SVG\\Automation\\Python Projects\\Files_for_Python_projects\\ACP_Updater\\Logs'
    print("Is the program executed from IL(Israel) site?")

    log_file_name = time_string + ' ' + date_string
    logger = ProjectsLogging('ACP_Updater', path=log_path, file_name=log_file_name).project_logging()
    logger.info(f'FYI - Logs session will be placed on this path: {log_path}')

    try:
        ACPUpdater().acp_updater_main(acp_name='asil-svg-acp5',
                                      target_acp_version='18.50.035',
                                      # vsphere_ip_old='192.168.56.17',
                                      vcenter_ip='192.168.63.91',
                                      # vsphere_user_old='autosvg@cs.local',
                                      vcenter_user='spuser',
                                      # vsphere_password_old='Autosvg1',
                                      vcenter_password='sp_user9',
                                      vm_name='5G_ACP_5_1')
    except Exception as err:
        print(err)
    #     input("The program failed due to an exception error!\nPress enter to exit")
    # input("The program executed fine!\nPress enter to exit")
