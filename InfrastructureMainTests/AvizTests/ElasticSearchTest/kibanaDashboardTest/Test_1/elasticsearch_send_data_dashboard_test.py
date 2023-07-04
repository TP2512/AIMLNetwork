import random
from datetime import datetime, timezone
from elasticsearch import helpers
from copy import deepcopy

from InfrastructureMainTests.AvizTests.ElasticSearchTest.kibanaDashboardTest.Test_1.data_to_elasticsearch import gnb_type, version_list, ems_version_list, configuration_dict, \
    features_data_dict, warning_list, error_list


def main(elk_client, index_name, ues_number, timestamp) -> None:  # sourcery skip: dict-assign-update-to-union, low-code-quality
    list_of_docs = []
    for index_1, version in enumerate(version_list, start=0):
        print('\n\n')
        print(f'- Version: {version}')

        doc = {
            "timestamp": timestamp,

            "gnb_type": gnb_type,
            "Version": version,
            "Fix Version": version.split('-', 1)[0],
            "ACP Version": ems_version_list[index_1],
        }
        for builder_profile_k, builder_profile_v in features_data_dict.items():
            print(f'-- Builder Profile Name: {builder_profile_k}')

            doc["builder_name"] = builder_profile_k
            for configuration_v in configuration_dict:
                doc.update(
                    {
                        "slave_name": configuration_v['slave_name'],
                        "Hardware": configuration_v['hardware'],
                        "BAND": configuration_v['band'],
                        "BW": configuration_v['bw'],
                        "Numerology": configuration_v['numerology'],
                        "SCS": configuration_v['scs'],
                    }
                )

                configuration = f"{configuration_v['hardware']}, " \
                                f"{configuration_v['band']}, " \
                                f"{configuration_v['bw']}, " \
                                f"Numerology={configuration_v['numerology']}, " \
                                f"SCS={configuration_v['scs']}"
                for feature_k, feature_v in builder_profile_v.items():
                    print(f'--- Feature Name: {feature_k}')

                    random_pass_fail = 'PASS' if bool(random.randint(0, 1)) else 'FAIL'
                    for index_3, (feature_scenario_k, feature_scenario_v) in enumerate(feature_v['Status'].items()):
                        if feature_scenario_k != random_pass_fail:
                            continue

                        if index_1 == 0 and index_3 == 0:
                            doc_id = '2022042511321904'
                        else:
                            doc_id = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%m')

                        doc.update(
                            {
                                "doc_id": f'{doc_id}',
                                "Feature Group Name": feature_v['Feature Group Name'],
                                "Feature Name": feature_k,
                                "test_plan_number": feature_v['Test Plan Number'],
                                "sir_number": feature_v['SIR Number'],
                                "test_execution": f'SVGA-{random.randint(100, 199)}',

                                "build_id": int(int(index_3) + 58),
                                "jenkins_build_number": int(index_3) + 1,

                                "Test Status": feature_scenario_k,
                                "Test Status Bool": feature_scenario_k == 'PASS',
                                "Test Status 1/2": int(feature_scenario_k == 'PASS') + 1,

                                "UL_threshold": 100,
                                "DL_threshold": 990,

                                'Warning': warning_list[index_3],
                                'Error': error_list[index_3],

                                "Expected Results": feature_scenario_v['expected_results'],
                                "Actual Results": feature_scenario_v['actual_results'],

                                "Configuration": configuration,
                                configuration: f"Expected Results: {feature_scenario_v['expected_results']}, Actual Results: {feature_scenario_v['actual_results']}",
                            }
                        )
                        for time_index in range(5):
                            print(f'--- Time: {time_index}')

                            doc.update(
                                {
                                    "Time": time_index,
                                    "UE_RES": {},
                                }
                            )
                            for ue_number in range(1, ues_number + 1):
                                doc["UE_RES"].update(
                                    {
                                        f"UE{ue_number}": {

                                            "IMSI": int(str(configuration_v['imsi']) + str(ue_number)),
                                            # "IMSI": random.randint(200010001016226, 200010001016526),
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

                                        "Test_333":
                                            [
                                                {'UE 1 ': random.randint(9, 100)},
                                                {'UE 2 ': random.randint(9, 100)},
                                                {'UE 3 ': random.randint(9, 100)},
                                                {'UE 4 ': random.randint(9, 100)},
                                                {'UE 5 ': random.randint(9, 100)},
                                            ]
                                        ,

                                "Test_123": [
                                    {
                                        'list_of_UEs ': ['UE 1', 'UE 2', 'UE 3', 'UE 4', 'UE 5'],
                                        "list_of_TP": [random.randint(9, 100), random.randint(7, 80), random.randint(6, 70), random.randint(9, 10), random.randint(9, 10)]
                                    }
                                ],
                                }
                                )

                                # time.sleep(0.3)
                                # elk_client.index(index=index_name, document=doc)

                                list_of_docs.append(
                                    {
                                        "_index": index_name,
                                        "_source": deepcopy(doc)
                                    }
                                )
                    print()
            print()
        if list_of_docs:
            helpers.bulk(elk_client, list_of_docs)
        else:
            print('list_of_docs is empty')
        print()
