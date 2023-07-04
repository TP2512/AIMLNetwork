import logging


class Iperf2Actions:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.network_side_interfaces_commands_list = []
        self.user_side_interfaces_commands_list = []

        self.network_side_run_commands_list = []
        self.user_side_run_commands_list = []

    def build_interface_command(self, **kwargs):
        interface_command = None

        interface_name = kwargs.get('interface_name')
        dl_vlan = kwargs.get('dl_vlan')
        dl_ip_address = kwargs.get('dl_ip_address')
        ul_vlan = kwargs.get('ul_vlan')
        ul_ip_address = kwargs.get('ul_ip_address')
        route_ip_address = kwargs.get('route_ip_address')
        default_gateway = kwargs.get('default_gateway')
        netmask = kwargs.get('netmask')
        prefix = kwargs.get('prefix')
        try:
            if dl_vlan and dl_ip_address:
                vlan = dl_vlan
                vlan_ip_address = dl_ip_address
            elif ul_vlan and ul_ip_address:
                vlan = ul_vlan
                vlan_ip_address = ul_ip_address
            else:
                return None
            interface_command = [
                f'vconfig add {interface_name} {vlan}',
                f'ifconfig {interface_name}.{vlan} {vlan_ip_address} netmask {netmask} up',
                f'ip route add {route_ip_address}/{prefix} via {default_gateway} dev '
                f'{interface_name}.{vlan}'
            ]
        except Exception:
            self.logger.exception('')
        finally:
            return interface_command

    def print_message(self, traffic_direction, network_side_command, user_side_command):
        self.logger.info('*********************************************************')
        self.logger.info(f'Commands for {traffic_direction} direction')
        self.logger.info(f'Network Side command: {network_side_command}')
        self.logger.info(f'User Side command: {user_side_command}')
        self.logger.info('*********************************************************')

    def build_tcp_run_commands(self, traffic_direction, window_size, tcp_udp_port, run_time,
                               iperf_sessions_number, dl_ip_address=None, user_wan_ip_address=None, **kwargs):
        network_side_command = []
        user_side_command = []
        try:
            if traffic_direction == 'UL':
                network_side_command = f"iperf -s -i1 -w {window_size}B -p {tcp_udp_port} -f m"
                user_side_command = f"iperf -c {dl_ip_address} -w {window_size}B -p {tcp_udp_port} " \
                                    f"-t{run_time} -P {iperf_sessions_number} -f m"
            elif traffic_direction == 'DL':
                user_side_command = f"iperf -s -i1 -w {window_size}B -p {tcp_udp_port} -f m"
                network_side_command = f"iperf -c {user_wan_ip_address} -w {window_size}B -p {tcp_udp_port} " \
                                       f"-t{run_time} -P {iperf_sessions_number} -f m"
            else:
                self.logger.info(
                    'The "traffic direction" (customfield_13834) is not equal "UL" and not equal "DL"')
        except Exception:
            self.logger.exception('')
        finally:
            self.print_message(traffic_direction, network_side_command, user_side_command)
            return network_side_command, user_side_command

    def build_udp_run_commands(self, traffic_direction, frame_size, tcp_udp_port, run_time, rate, dl_ip_address=None,
                               user_wan_ip_address=None, **kwargs):
        network_side_command = []
        user_side_command = []
        try:
            if traffic_direction == 'UL':
                network_side_command = f"iperf -s -u -i1 -p {tcp_udp_port} -f m"
                user_side_command = f"iperf -u -c {dl_ip_address} -t{run_time} -i1 " \
                                    f"-l{frame_size} -f m -b{rate}M -p {tcp_udp_port}"
            elif traffic_direction == 'DL':
                user_side_command = f"iperf -s -u -i1 -p {tcp_udp_port} -f m"
                network_side_command = f"iperf -u -c {user_wan_ip_address} -t{run_time} -i1 " \
                                       f"-l{frame_size} -f m -b{rate}M -p {tcp_udp_port}"
            else:
                self.logger.info(
                    'The "traffic direction" (customfield_13834) is not equal "UL" and not equal "DL"')
        except Exception:
            self.logger.exception('')
        finally:
            self.print_message(traffic_direction, network_side_command, user_side_command)
            return network_side_command, user_side_command
            # return {'user_side_command': user_side_command, 'network_side_command': network_side_command}
