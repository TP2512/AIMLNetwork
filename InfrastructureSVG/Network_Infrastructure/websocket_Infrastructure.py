import logging
import time

import websocket
import websockets


# from websocket import create_connection


class WebSocketActions:
    def __init__(self, web_socket_ip_address: str, web_socket_port: str) -> None:
        self.logger = logging.getLogger(
            f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.web_socket = None
        self.web_socket_url = f'ws://{web_socket_ip_address}:{web_socket_port}'
        self.full_output = ''
        self.last_output = ''

    def get_output(self) -> None:
        output = self.web_socket.recv()
        self.full_output += output
        self.last_output = output

    def web_socket_connection(self, timeout: int = None) -> None:
        self.web_socket = websocket.create_connection(url=self.web_socket_url, timeout=timeout)
        self.get_output()

    def send_command(self, command: str, time_before_output: int = 1) -> None:
         """
        This function responsible to send one command (return output)

        The function get 2 parameter:
            - "commands" - the command (one command!) that need to send (string/list type)
            - "time_before_output" - the time before taking output (integer type) [Optional]
        """

        self.web_socket.send('{"message": "ue_get"}')
        self.web_socket.send(command)
        time.sleep(time_before_output)
        self.get_output()

    async def async_send_params(self, param):
        async with websockets.connect(self.web_socket_url, max_size=None) as ws:
            await ws.send(f"{param}")
            while True:
                return await ws.recv()
                # return pickle.loads(msg)


if __name__ == '__main__':
    mme_aio = 'ws://172.20.63.14:9062/'
