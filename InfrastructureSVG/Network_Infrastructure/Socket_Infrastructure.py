import logging
import socket


""" 
In this py file have 1 class
    - SocketConnectionClass
"""


class SocketConnectionClass:
    """ This class ("SSHConnectionClass") responsible for socket connection """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def socket_sender_connection(self, server_address, server_port):
        """
        This function responsible to create ssh connection

        The function get 4 parameter:
            - "server_address" - the ip address for connection (string type)
            - "server_port" - the port for connection (string type) [Optional]

        The function return 2 parameters:
            - "socket_client" - client of socket
        """
        socket_client = None
        if server_address:
            if server_port:
                try:
                    # Create a TCP/IP socket
                    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    socket_client.bind((server_address, server_port))
                    self.logger.info('starting up on {} port {}'.format(*(server_address, server_port)) + '\n')

                except socket.error:
                    self.logger.exception('Socket error, Trying to reconnect')
                except Exception:
                    self.logger.exception('')
                    return None
            else:
                self.logger.warning('server_port parameter is empty')
        else:
            self.logger.warning('server_address parameter is empty')

        return socket_client

    def socket_receiver_connection(self, server_address, server_port):
        """
        This function responsible to create ssh connection

        The function get 4 parameter:
            - "server_address" - the ip address for connection (string type)
            - "server_port" - the port for connection (string type) [Optional]

        The function return 2 parameters:
            - "socket_client" - client of socket
        """

        socket_client = None
        if server_address:
            if server_port:
                try:
                    # Create a TCP/IP socket
                    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket_client.connect((server_address, server_port))
                    # socket_client.connect(server_address)
                    self.logger.info('connecting to {} port {}'.format(*(server_address, server_port)) + '\n')

                except Exception:
                    self.logger.exception('')
                    return None
            else:
                self.logger.warning('server_port parameter is empty')
        else:
            self.logger.warning('server_address parameter is empty')

        return socket_client
