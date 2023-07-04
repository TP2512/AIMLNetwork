from InfrastructureSVG.TP_Calculator_Infrastructure_New.TP_Calc import Tpcalc

if __name__ == "__main__":
    data_from_jira = {
        'slot_format': 'Format 6 - DL 71% : UL 0%',
        'sub_carrier_spacing': 'Numerology=1,SCS=30Khz',
        'dl_layers': 2,
        'ul_layers': 1,
        'frequency_band': 'n48',
        'dl_max_modulation': 'DL256QAM',
        'ul_max_modulation': 'UL64QAM',
        'cyclic_prefix': 'Normal',
        'bw': '40',
        'dl_splite': 70,
        'ul_splite': 20,
        'ssf_splite': 10,
        'dl_ca': 2,
        'ul_ca': 1,
        'pucch': 2,
        'limitation_by_sw_version': '19.5',
        'packet_size': '1300',
        'measurement_gap_': 'NO',
    }

    # data_from_jira = {"frequency_band": "n51", "bw": "100MHz", "slot_format": "Format 2 - DL 0% : UL 0%",
    #                   "dl_layers": "2",
    #                   "ul_layers": "1",
    #                   "ul_max_modulation": "256QAM", "dl_max_modulation": "64QAM",
    #                   "sub_carrier_spacing": "Numerology=1,SCS=30Khz",
    #                   "cyclic_prefix": "Normal",
    #                   "dl_splite": 80, "ul_splite": 30, "ssf_splite": 50, "mcs": "0", "PUCCH": "2"}
    xxx = Tpcalc()
    xxx.get_tp_result(max_tp=True, **data_from_jira)
    print(xxx.Throughput)
