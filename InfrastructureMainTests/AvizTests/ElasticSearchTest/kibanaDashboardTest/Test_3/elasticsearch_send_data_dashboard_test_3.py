import random
from datetime import datetime, timezone
from copy import deepcopy

from InfrastructureMainTests.AvizTests.ElasticSearchTest.kibanaDashboardTest.Test_3.data_to_elasticsearch_3 import gnb_type, version_list, slave_name_list, \
    ems_version_list, gnbs_configuration_list, ues_imsi_list, features_data_dict


def generate_doc_id(index_1, index_3):
    if index_1 == 0 and index_3 == 0:
        return '2022042511321904'
    else:
        return datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%m')


def fill_global_information_doc(list_of_docs, index_name, timestamp, version, index):
    general_info_doc = {
        "timestamp": "timestamp",
        "slave_name": "slave_name",

        "gnb_type": "AIO / FlexRAN",
        "version": "version",
        "fix_version": "'version.split('-', 1)[0]'",
        "ems_version": "ems_version",
    }

    global_information_doc = {
        "timestamp": timestamp,
        "slave_name": slave_name_list[index],

        "gnb_type": gnb_type,
        "Version": version,
        "Fix Version": version.split('-', 1)[0],
        "ems_version": ems_version_list[index],
    }
    fill_list_of_docs(list_of_docs, index_name, global_information_doc)


def fill_enbs_docs(list_of_docs, index_name, gnbs_docs, timestamp, feature_data, feature_data_index):
    gnb_info_doc = {
        "gnb_number": "gnb_number",
        "gnb_serial_number": "gnb_serial_number",

        "gnb_hardware": "gnb_hardware",
        "gnb_band": "gnb_band",
        "gnb_bw": "gnb_bw",
        "gnb_numerology": "gnb_numerology",
        "gnb_scs": "gnb_scs",

        "gnb_configuration": "gnb_hardware" + "gnb_band" + "gnb_bw" + "gnb_numerology" + "gnb_scs",
        "gnb_hardware" + "gnb_band" + "gnb_bw" + "gnb_numerology" + "gnb_scs": "Expected Results: 'expected_results', Actual Results: 'actual_results'"
    }

    for index, (gnb_configuration_k, gnb_configuration_v) in enumerate(gnbs_configuration_list[1].items(), start=0):
        random_pass_fail = 'PASS' if bool(random.randint(0, 1)) else 'FAIL'
        gnbs_docs.update(
            {
                f"gNB{gnb_configuration_k}": {
                    "timestamp": timestamp,
                    "gnb_number": gnb_configuration_k,
                    "gnb_serial_number": "gnb_serial_number",

                    "Hardware": gnb_configuration_v['hardware'],
                    "BAND": gnb_configuration_v['band'],
                    "BW": gnb_configuration_v['bw'],
                    "Numerology": gnb_configuration_v['numerology'],
                    "SCS": gnb_configuration_v['scs'],

                    "expected_results": list(feature_data.values())[feature_data_index]['Status'][random_pass_fail]['expected_results'],
                    "actual_results": list(feature_data.values())[feature_data_index]['Status'][random_pass_fail]['actual_results'],
                    "gnb_configuration": f"{gnb_configuration_v['hardware']}, {gnb_configuration_v['band']}, {gnb_configuration_v['bw']}, {gnb_configuration_v['numerology']}, {gnb_configuration_v['scs']}",
                    f"{gnb_configuration_v['hardware']}, {gnb_configuration_v['band']}, {gnb_configuration_v['bw']}, {gnb_configuration_v['numerology']}, {gnb_configuration_v['scs']}":
                        f"Expected Results: {list(feature_data.values())[feature_data_index]['Status'][random_pass_fail]['expected_results']}, Actual Results: {list(feature_data.values())[feature_data_index]['Status'][random_pass_fail]['actual_results']}"
                }
            }
        )
        fill_list_of_docs(list_of_docs, index_name, gnbs_docs)


def fill_ues_docs(list_of_docs, index_name, ues_docs, timestamp, ues_number):
    ue_info_doc = {
        "ue_id": "ue_id",
        "ue_imsi": "ue_imsi",
        "ue_rnti": "ue_rnti",
        "ue_hardware": "ue_hardware",
        "ue_band": "ue_band",
        "ue_bw": "ue_bw",

        "UE-ID": "UE-ID",
        "CELL-ID": "CELL-ID",
        "PCELL-ID": "PCELL-ID",
        "Connected Time(Min)": "Connected Time(Min)",

        "256QAM ACTV": "256QAM ACTV",  # True / False
        "256QAM Alloc": "256QAM Alloc",  # True / False
        "MEASGAP ACTIVE": "MEASGAP ACTIVE",  # True / False
        "MEAS GAP ACTIVE": "MEAS GAP ACTIVE",  # True / False

        "DL-TPT (Mb)": "DL-TPT (Mb)",
        "UL-TPT (Mb)": "UL-TPT (Mb)",

        'DL-BLER %CW-0': 'DL-BLER %CW-0',
        'DL-BLER %CW-1': 'DL-BLER %CW-1',
        'RI RX': 'RI RX',
        'RI UL': 'RI UL',
        'RI DL': 'RI DL',
        'DL-CQI CW-0': 'DL-CQI CW-0',
        'DL-CQI CW-1': 'DL-CQI CW-1',
        'DL-MCS CW-0': 'DL-MCS CW-0',
        'DL-MCS CW-1': 'DL-MCS CW-1',
        'UL-BLER-CRC %PER': 'UL-BLER-CRC %PER',
        'UL-CQI CW-0': 'UL-CQI CW-0',
        'UL-CQI CW-1': 'UL-CQI CW-1',
        'UL-MCS CW-0': 'UL-MCS CW-0',
        'UL-MCS CW-1': 'UL-MCS CW-1',
        'C2I': 'C2I',
        'DL-PKT-RX': 'DL-PKT-RX',
        'RLC-DL-TPT (Mb)': 'RLC-DL-TPT (Mb)',
        'RLC-UL-TPT (Mb)': 'RLC-UL-TPT (Mb)',
        'MAC-DL-TPT (Mb)': 'MAC-DL-TPT (Mb)',
        'MAC-UL-TPT (Mb)': 'MAC-UL-TPT (Mb)',
        'CL-DL-TPT (Mb)': 'CL-DL-TPT (Mb)',
        'CL-UL-TPT (Mb)': 'CL-UL-TPT (Mb)',
        'UL-PKT-TX': 'UL-PKT-TX',
        'NUM-SR': 'NUM-SR',

        "RSRP": "RSRP",
        "RSSI": "RSSI",
        "RSRQ": "RSRQ",
        "SNR": "SNR",
    }

    for ue_number in range(1, ues_number + 1):
        ues_docs.update(
            {
                f"UE{ue_number}": {
                    "timestamp": timestamp,

                    # "IMSI": random.randint(200010001016226, 200010001016526),
                    "IMSI": ues_imsi_list[ue_number-1],
                    "RNTI": random.randint(1, 100),
                    "UE-ID": random.randint(1, 100),
                    "CELL-ID": random.randint(0, 1),
                    "PCELL-ID": random.randint(0, 1),
                    "Connected Time(Min)": random.randint(0, 10000),

                    "256QAM ACTV": bool(random.getrandbits(1)),  # True / False
                    "256QAM Alloc": bool(random.getrandbits(1)),  # True / False
                    "MEASGAP ACTIVE": bool(random.getrandbits(1)),  # True / False
                    "MEAS GAP ACTIVE": bool(random.getrandbits(1)),  # True / False

                    "DL-TPT (Mb)": random.randint(900, 1000),
                    "UL-TPT (Mb)": random.randint(0, 100),

                    'DL-BLER %CW-0': [2],
                    'DL-BLER %CW-1': [0],
                    'RI RX': [2],
                    'RI UL': [1],
                    'RI DL': [2],
                    'DL-CQI CW-0': ['15'],
                    'DL-CQI CW-1': ['0'],
                    'DL-MCS CW-0': [28],
                    'DL-MCS CW-1': [0],
                    'UL-BLER-CRC %PER': [1],
                    'UL-CQI CW-0': ['0'],
                    'UL-CQI CW-1': ['0'],
                    'UL-MCS CW-0': [27],
                    'UL-MCS CW-1': [0],
                    'C2I': [24.4],
                    'DL-PKT-RX': ['11'],
                    'RLC-DL-TPT (Mb)': ['0.13'],
                    'RLC-UL-TPT (Mb)': ['0.00'],
                    'MAC-DL-TPT (Mb)': ['0.14'],
                    'MAC-UL-TPT (Mb)': ['0.00'],
                    'CL-DL-TPT (Mb)': ['46.25'],
                    'CL-UL-TPT (Mb)': ['0.00'],
                    'UL-PKT-TX': ['0'],
                    'NUM-SR': ['8'],

                    "RSRP": random.randint(-80, -75),
                    "RSSI": random.randint(-80, -75),
                    "RSRQ": random.randint(-80, -75),
                    "SNR": random.randint(-80, -75),
                },
            }
        )
        fill_list_of_docs(list_of_docs, index_name, ues_docs)


def fill_list_of_docs(list_of_docs, index_name, doc):
    list_of_docs.append(
        {
            "_index": index_name,
            "_source": deepcopy(doc)
        }
    )


def main(elk_client, index_name, ues_number, timestamp) -> None:
    list_of_docs = []

    for index_1, version in enumerate(version_list, start=0):
        fill_global_information_doc(list_of_docs=list_of_docs, index_name=index_name['dashboard_results_setup'], timestamp=timestamp, version=version, index=index_1)

        for index_2, (feature_data_k, feature_data_v) in enumerate(features_data_dict.items(), start=0):
            fill_enbs_docs(list_of_docs=list_of_docs, index_name=index_name['dashboard_results_enbs'], gnbs_docs={}, timestamp=timestamp, feature_data=feature_data_v, feature_data_index=index_2)
            print()

            fill_ues_docs(list_of_docs=list_of_docs, index_name=index_name['dashboard_results_ues'], ues_docs={}, timestamp=timestamp, ues_number=ues_number)
            print()

    print()
