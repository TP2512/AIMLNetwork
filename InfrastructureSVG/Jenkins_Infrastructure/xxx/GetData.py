# from Exceptions.Python_Exceptions import Exceptions
# from Network.SSH_Infrastructure import SSHConnectionClass, SSHSendCommandsClass
#
#
# class GetLogsFromTestSpan:
#
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def get_log_file_from_testspan_server(uid, exec_id):
#         """
#         func to get UESHOWRATE.log file from testspan server by uid # and exec_id
#         :param uid: int
#         :param exec_id:  int
#         :return: string that contain content of ueshowrate.log file
#         """
#         try:
#             commands = 'ls ' + '/home/difido/difido-server/docRoot/reports/exec_' + exec_id + '/tests/test_' + uid
#             client_ssh, remote_connect = SSHConnectionClass.ssh_connection('asil-svg-testspan', 'root', 'Testsp@n')
#             client_ssh_reconnect, remote_reconnect, output = \
#                 SSHSendCommandsClass.ssh_send_commands_with_output(commands, client_ssh, remote_connect,
#                                                                    'asil-svg-testspan', 'root', 'Testsp@n')
#             log_file = ""
#             # print(output)
#             output = output.split("\r\n")
#             for line in output:
#                 if 'UeShowRate.log' in line or 'ue_show_link_and_rate_logs1.log' in line:
#                     print("Log file: " + line + " Found")
#                     print(commands)
#                     cat_cmd = "cat " + '/home/difido/difido-server/docRoot/reports/exec_' + exec_id + '/tests/test_' \
#                               + uid + "/" + line
#                     client_ssh_reconnect, remote_reconnect, log_file = \
#                         SSHSendCommandsClass.ssh_send_commands_with_output(cat_cmd, client_ssh, remote_connect,
#                                                                            'asil-svg-testspan',
#                                                                            'root', 'Testsp@n', 22, 5, 1000000)
#             return log_file
#         except Exception as err:
#             print("Can't read from txt file")
#             Exceptions.common_exceptiom(err)
#             return None
