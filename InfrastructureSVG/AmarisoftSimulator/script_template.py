import re


class AmarisoftUeSimulator:
    def __init__(self, **kwargs):
        self.cell_count = int(kwargs.get('cell_count')) if kwargs.get('cell_count') else 1
        self.open_dict = '{'
        self.close_dict = '}'
        self.open_list = '['
        self.close_list = ']'
        self.chanel = int(kwargs.get('chanel')) if kwargs.get('chanel') else 1
        self.rx_antenna = kwargs.get('rx_antenna') or True
        self.n_antenna_dl = kwargs.get('n_antenna_dl') or 2
        self.n_antenna_ul = kwargs.get('n_antenna_ul') or 1
        self.tx_gain = kwargs.get('tx_gain') or 55
        self.rx_gain = kwargs.get('rx_gain') or 82
        self.chanel_sim = kwargs.get('chanel_sim') or 'true'
        self.ip = kwargs.get('ip') or '172.20.63.236'
        self.port = kwargs.get('port') or '9002'
        self.power_on_off_list = kwargs.get('power_on_off_list')
        self.file_name = kwargs.get('file_name')
        self.imsi_list = kwargs.get('imsi_list')
        self.kwargs = kwargs

    def create_server(self):
        return f'  log_options: "all.level=error,all.max_size=0,nas.level=debug,nas.max_size=1,rrc.level=debug,rrc.max_size=1,time=sec",\n' \
               f'  //log_options: "all.level=none,all.max_size=1",\n' \
               f'  log_filename: "/tmp/ue0.log",\n\n' \
               f'  /* Enable remote API and Web interface */\n' \
               f'  com_addr: "{self.ip}:{self.port}",\n'

    def get_rf_driver(self):
        args = ''
        devices_comment = "  /* list of devices. 'dev0' is always the master. */\n"
        rf_driver_comment = '  /* RF driver configuration */\n'
        rf_driver = f'rf_driver: {self.open_dict}\n' \
                    f'\t\tname: "sdr",\n\n' \
                    f'\t{devices_comment}'

        if self.chanel == 1:
            args = '\targs: "dev0=/dev/sdr0",\n'
        elif self.chanel == 11:
            args = '\targs: "dev0=/dev/sdr1",\n'
        elif self.chanel == 13:
            args = '\targs: "dev0=/dev/sdr2",\n'
        elif self.chanel == 14:
            args = '\targs: "dev1=/dev/sdr3",\n'
        elif self.chanel in [2, 212]:
            args = '\targs: "dev0=/dev/sdr0,dev1=/dev/sdr1",\n'
        elif self.chanel in [202, 234]:
            args = '\targs: "dev0=/dev/sdr2,dev1=/dev/sdr3",\n'
        elif self.chanel == 213:
            args = '\targs: "dev0=/dev/sdr0,dev1=/dev/sdr2",\n'
        elif self.chanel == 223:
            args = '\targs: "dev0=/dev/sdr1,dev1=/dev/sdr2",\n'
        elif self.chanel == 3:
            args = '\targs: "dev0=/dev/sdr0,dev1=/dev/sdr1,dev2=/dev/sdr2"\n'
        elif self.chanel == 4:
            args = '\targs: "dev0=/dev/sdr0,dev1=/dev/sdr1,dev2=/dev/sdr2,dev3=/dev/sdr3",\n'
        elif self.chanel == 6:
            args = '\targs: "dev0=/dev/sdr0,dev1=/dev/sdr1,dev2=/dev/sdr2,dev3=/dev/sdr3,dev4=/dev/sdr4,dev5=/dev/sdr5",\n'
        antenna = '\trx_antenna:"rx",\n' if self.rx_antenna else '\t// rx_antenna:"rx",\n'

        return f'{rf_driver_comment}' \
               f'\t{rf_driver}' \
               f'\t{args}' \
               f'\t{antenna}' \
               f'\t{self.close_dict},\n\n'

    @staticmethod
    def script_header():
        return '/* UE simulator configuration file version 2018-04-01\n' \
               '* Copyright (C) 2015-2018 Amarisoft\n' \
               '*/\n'

    def get_gain(self):
        return f'  rx_gain: {self.rx_gain},\n' \
               f'  tx_gain: {self.tx_gain},\n'

    def cell_groups(self):
        return f'  cell_groups: {self.open_list}\n' \
               f'  {self.open_dict}\n' \
               f'    group_type: "nr",\n' \
               f'    multi_ue: 1,\n' \
               f'    channel_sim: {self.chanel_sim},\n\n' \
               f'    cells: [\n'

    def configure_cell(self):
        return ''.join(
            f'\t{self.open_dict}\n'
            f'\t  rf_port: {0 if self.cell_count == 1 else cell_index},\n'
            f'\t  bandwidth: {self.kwargs.get(f"cell_{cell_index}_bandwidth")},\n'
            f'\t  rx_to_tx_latency: {self.kwargs.get(f"cell_{cell_index}_rx_to_tx_latency") or 3},\n'
            f'\t  band: {self.kwargs.get(f"cell_{cell_index}_band")},\n'
            f'\t  dl_nr_arfcn: {self.kwargs.get(f"cell_{cell_index}_dl_nr_arfcn")},\n'
            f'\t  ssb_nr_arfcn: {self.kwargs.get(f"cell_{cell_index}_ssb_nr_arfcn")},\n'
            f'\t  ssb_subcarrier_spacing: {self.kwargs.get(f"cell_{cell_index}_ssb_subcarrier_spacing") or 30}, /* KHz */\n'
            f'\t  subcarrier_spacing: {self.kwargs.get(f"cell_{cell_index}_subcarrier_spacing") or 30}, /* kHz */\n'
            f'\t  n_antenna_dl: {self.kwargs.get(f"cell_{cell_index}_n_antenna_dl") or 2}, /* 1-8 */\n'
            f'\t  n_antenna_ul: {self.kwargs.get(f"cell_{cell_index}_n_antenna_ul") or 1}, /* 1-8 */\n'
            f'\t  global_timing_advance: {self.kwargs.get(f"cell_{cell_index}_global_timing_advance") or -1}, /* in 1/(1.92*2^mu) us units */\n'
            f'\t{self.get_chanel(cell_index, cell_index + 1)}'
            f'\t{self.close_dict},\n' for cell_index in range(self.kwargs.get('start') or 0, self.cell_count + self.kwargs['start'] if self.kwargs.get('start') else self.cell_count))

    def ues_list(self):
        return f'ue_list: {self.open_list}\n'

    def get_chanel(self, j, i):
        return f'  position: [{self.kwargs.get(f"position{j + i}") or 130},{self.kwargs.get(f"position{2 * i}") or 130}],\n' \
               f'\t  ref_signal_power: {self.kwargs.get("ref_signal_power") or 1}, /* in dBm */\n' \
               f'\t  ul_power_attenuation: {self.kwargs.get("ul_power_attenuation") or 128},\n' \
               f'\t  /* Attenuation between the UE TX and eNodeB RX in dB. */\n' \
               f'\t  antenna: {self.open_dict}\n \t\ttype: "{self.kwargs.get("antenna_type") or "isotropic"}"\n \t\t{self.close_dict},\n'

    def create_ue(self):
        ue = ''
        count = 1
        imsi_count = 0
        start_time = float(self.kwargs.get("start_time"))
        num_of_pings = self.kwargs.get("num_of_pings")
        dest_ip_addr = self.kwargs.get("dest_ip_addr")
        cell_index = self.kwargs.get("cell_index")
        new_time = 0
        for key in sorted(list(set(re.findall(r'cell_\d', ''.join(list(self.kwargs.keys())))))):
            for _ in range(1, int(f'{self.kwargs[f"{key}_ue"]}') + 1):
                new_time += start_time

                position_count = count * 2 - 1
                ue += f'\t{self.open_dict}\n' \
                      f'\t  sim_algo: "milenage",\n' \
                      f'\t  imsi: "{self.imsi_list[imsi_count]}",\n' \
                      f'\t  K: "5C95978B5E89488CB7DB44381E237809",\n' \
                      f'\t  op: "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",\n\n' \
                      f'\t  cell_index: {cell_index or key.replace("cell_", "")},\n\n' \
                      f'\t  /* UE channel simulator parameters */\n' \
                      f'\t\tposition: [{int(self.kwargs.get(f"ue_position{position_count}") or 90)}, ' \
                      f'{self.kwargs.get(f"ue_position{position_count}") or 90}],' \
                      f'\t/* starting position in meters */\n' \
                      f'\t\tinitial_radius: 0,  /* random position inside this radius centered on "position" */\n' \
                      f'\t\tspeed: 0, \t\t\t/* speed km/h default = 0 */\n' \
                      f'\t\tdirection: 0, \t\t/* direction in degrees default = 0 */\n' \
                      f'\t\t\tchannel: {self.open_dict}\n' \
                      f'\t\t\t\ttype: "awgn",\n' \
                      f'\t\t\t{self.close_dict},\n' \
                      f'\t\tpower_control_enabled: {self.kwargs.get("power_control_enabled") or "true"},\n' \
                      f'\t/******/\n\n' \
                      f'\t/* UE capabilities */\n' \
                      f'\tas_release: 15,\n' \
                      f'\tue_category: "nr",\n\n' \
                      f'\ttun_setup_script: "ue-ifup_new",\n\n' \
                      f'\tapn: "{self.kwargs.get("apn")}",\n\n\n' \
                      f'\tsim_events: {self.open_list}\n' \
                      f'\t\t{self.open_dict}\n' \
                      f'\t\t\tevent: "{self.power_on_off_list[imsi_count]}",\n' \
                      f'\t\t\tstart_time: {start_time if count == 1 else new_time},\n' \
                      f'\t\t{self.close_dict},\n' \
                      f'\t\t{self.open_dict}\n' \
                      f'\t\t\tevent: "ext_app",\n' \
                      f'\t\t\tprog: "ext_app.sh",\n' \
                      f'\t\t\targs: ["ping -i 5 -c", {num_of_pings} , "{dest_ip_addr}"],\n' \
                      f'\t\t{self.close_dict}\n' \
                      f'\t  {self.close_list}\n' \
                      f'\t{self.close_dict},\n'

                count += 1
                imsi_count += 1
        return ue

    def create_script(self):
        with open(self.file_name, "w") as file:
            file.write(f'{self.script_header()}\n'
                       f'{self.open_dict}\n'
                       f'{self.create_server()}\n'
                       f'{self.get_rf_driver()}\n'
                       f'{self.get_gain()}\n'
                       f'{self.cell_groups()}'
                       f'{self.configure_cell()}'
                       f'  {self.close_list},\n'
                       f' {self.close_dict}\n'
                       f' {self.close_list},\n\n'
                       f'  {self.ues_list()}\n'
                       f'{self.create_ue()}'
                       f'  {self.close_list},\n'
                       f'{self.close_dict}')


if __name__ == '__main__':
    AmarisoftUeSimulator(cell_count=2,
                         cell_0_bandwidth='20',
                         cell_1_bandwidth='20',
                         cell_0_band='48',
                         cell_1_band='48',
                         cell_0_dl_nr_arfcn='641064',
                         cell_1_dl_nr_arfcn='641064',
                         cell_0_ssb_nr_arfcn='640992',
                         cell_1_ssb_nr_arfcn='640992',
                         position1='130',
                         position2='130',
                         apn='tel3',
                         chanel=2,
                         cell_0_ue=5,
                         cell_1_ue=5,
                         start_time='0.25', file_name='C:\\tmp\\Amarisoft_UE_Simulator.cfg_Template.cfg',
                         imsi_list=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
                         start=1).create_script()
