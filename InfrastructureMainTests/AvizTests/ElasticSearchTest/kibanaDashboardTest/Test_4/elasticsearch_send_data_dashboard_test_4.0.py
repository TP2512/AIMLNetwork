import random
from datetime import datetime, timezone
from copy import deepcopy
from elasticsearch import helpers

from InfrastructureMainTests.AvizTests.ElasticSearchTest.kibanaDashboardTest.Test_4.data_to_elasticsearch_4 import gnb_type, version_list, slave_name_list, \
    ems_version_list, gnbs_configuration_list, ues_imsi_list, builds_data_dict


def generate_doc_id(index_version=None, index__feature=None):
    if index_version == 0 and index__feature == 0:
        return '2022042511321904'
    else:
        return datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%m')


def fill_list_of_docs(list_of_docs, index_name, doc):
    list_of_docs.append(
        {
            "_index": index_name,
            "_source": deepcopy(doc)
        }
    )


def set_list_of_docs(elk_client, list_of_docs):
    if list_of_docs:
        print(f'len(list_of_docs) is: {len(list_of_docs)}')
        print(f'list_of_docs is: {list_of_docs}')
        helpers.bulk(elk_client, list_of_docs)
    else:
        print('list_of_docs is empty')


def fill_global_information_doc(version, ems_version, slave_name, build_doc_id, test_plan, test_set, build_name, jenkins_build_number, time_list):
    return {
        "build_doc_id": build_doc_id,
        "test_plan": test_plan,
        "test_set": test_set,
        "build_name": build_name,
        "jenkins_build_number": jenkins_build_number,

        "slave_name": slave_name,

        "gnb_type": gnb_type,
        "Version": version,
        "Fix Version": version.split('-', 1)[0],
        "ems_version": ems_version,

        "time": time_list,  # ???
    }


def fill_feature_details_doc(list_of_docs, index_name, timestamp, global_information_doc,
                             feature_doc_id, test_sir, feature_group_name, feature_name, random_pass_fail, test_execution):
    feature_details_doc = {
        "timestamp": timestamp,

        "feature_doc_id": feature_doc_id,

        "test_sir": test_sir,
        "feature_name": feature_name,
        "feature_group_name": feature_group_name,

        "gnb_type": gnb_type,
        "dl_threshold": 90,

        "test_status": random_pass_fail,
        "test_status_bool": random_pass_fail == 'PASS',
        "test_status_1_2": int(random_pass_fail == 'PASS') + 1,
        "test_execution": test_execution,
    }
    feature_details_doc |= global_information_doc
    fill_list_of_docs(list_of_docs, index_name, feature_details_doc)


def fill_gnbs_docs(list_of_docs, index_name, timestamp, global_information_doc, build_doc_id, feature_doc_id, time_number, versions, feature_data, random_pass_fail):
    for index, (gnb_configuration_k, gnb_configuration_v) in enumerate(gnbs_configuration_list[1].items(), start=0):
        gnbs_docs = {
            "gnb": {
                "timestamp": timestamp,
                "build_doc_id": build_doc_id,
                "feature_doc_id": feature_doc_id,

                "gnb_number": gnb_configuration_k,
                "gnb_name": f'gNB_{gnb_configuration_k}',
                "gnb_serial_number": "gnb_serial_number",
                "time": time_number,

                "hardware": gnb_configuration_v['hardware'],
                "band": gnb_configuration_v['band'],
                "bw": gnb_configuration_v['bw'],
                "numerology": gnb_configuration_v['numerology'],
                "scs": gnb_configuration_v['scs'],

                "cucp_version": versions.get('cucps_under_test_versions', None),
                "cuup_version": versions.get('cuups_under_test_versions', None),
                "du_version": versions.get('dus_under_test_versions', None),
                "ru_version": versions.get('rus_under_test_versions', None),
                "aio_version": versions.get('aio_pack_vers_under_test_versions', None),
                "xpu_version": versions.get('xpus_under_test_versions', None),

                "test_status": random_pass_fail,
                "test_status_bool": random_pass_fail == 'PASS',
                "test_status_1_2": int(random_pass_fail == 'PASS') + 1,

                "expected_results": feature_data['Status'][random_pass_fail]['expected_results'],
                "actual_results": feature_data['Status'][random_pass_fail]['actual_results'],
                "gnb_configuration":
                    f"{gnb_configuration_v['hardware']}, {gnb_configuration_v['band']}, {gnb_configuration_v['bw']}, {gnb_configuration_v['numerology']}, {gnb_configuration_v['scs']}",
                f"{gnb_configuration_v['hardware']}, {gnb_configuration_v['band']}, {gnb_configuration_v['bw']}, {gnb_configuration_v['numerology']}, {gnb_configuration_v['scs']}":
                    f"Expected Results: {feature_data['Status'][random_pass_fail]['expected_results']}, Actual Results: {feature_data['Status'][random_pass_fail]['actual_results']}",
            }
        }
        gnbs_docs |= global_information_doc
        fill_list_of_docs(list_of_docs, index_name, gnbs_docs)


def fill_ues_docs(list_of_docs, index_name, timestamp, global_information_doc, feature_doc_id, build_doc_id, time_number, ues_number):
    for ue_number in range(1, ues_number + 1):
        ues_docs = {
            "ue": {
                "timestamp": timestamp,
                "build_doc_id": build_doc_id,
                "feature_doc_id": feature_doc_id,

                "ue_number": ue_number,
                "ue_name": f'UE_{ue_number}',
                "time": time_number,

                "imsi": f'{ues_imsi_list[ue_number - 1]}',
                "rnti": f'{random.randint(1, 100)}',
                "ue_id": f'{random.randint(1, 100)}',
                "cell_id": f'{random.randint(0, 1)}',
                "pcell_id": f'{random.randint(0, 1)}',
                "connected_time_min": random.randint(0, 10000),

                "256qam_actv": bool(random.getrandbits(1)),  # true / false
                "256qam_alloc": bool(random.getrandbits(1)),  # true / false
                "mesa_active": bool(random.getrandbits(1)),  # true / false
                "meas_gap_active": bool(random.getrandbits(1)),  # true / false

                "dl_tpt_mb": random.randint(700, 1000),
                "ul_tpt_mb": random.randint(0, 100),

                "dl_threshold": 990,
                "ul_threshold": 100,
                # "dl_threshold": [990, 990, 990, 990, 990],
                # "ul_threshold": [100, 100, 100, 100, 100],

                'dl_bler_cw_0': random.randint(0, 12),
                'dl_bler_cw_1': 0,
                'ri_rx': random.randint(1, 2),
                'ri_ul': 1,
                'ri_dl': random.randint(1, 2),
                'dl_cqi_cw_0': random.randint(1, 15),
                'dl_cqi_cw_1': 0,
                'dl_mcs_cw_0': random.randint(23, 28),
                'dl_mcs_cw_1': 0,
                'ul_bler_crc_per': random.randint(1, 3),
                'ul_cqi_cw_0': 0,
                'ul_cqi_cw_1': 0,
                'ul_mcs_cw_0': random.randint(23, 28),
                'ul_mcs_cw_1': 0,
                'c2i': random.randint(24, 31),

                'dl_pkt_rx': 0,
                'rlc_dl_tpt_mb': 0,
                'rlc_ul_tpt_mb': 0,
                'mac_dl-_tpt _mb': 0,
                'mac_ul_tpt_mb': 0,
                'cl_dl_tpt_mb': 0,
                'cl_ul_tpt_mb': 0,
                'ul_pkt_tx': 0,
                'num-sr': 8,

                "rsrp": random.randint(-85, -75),
                "rssi": random.randint(-85, -75),
                "rsrq": random.randint(-15, -10),
                "snr": random.randint(25, 35),
            },
        }
        ues_docs |= global_information_doc
        fill_list_of_docs(list_of_docs, index_name, ues_docs)


def fill_error_and_warning_list(list_of_docs, index_name, timestamp, global_information_doc):
    for _ in range(20):
        warning_int = random.randint(0, 100)
        error_int = random.randint(0, 100)

        error_and_warning_list = {
            "timestamp": timestamp,

            "warning_message_int": warning_int,
            "warning_message": f'warning {warning_int}',

            "error_message_int": error_int,
            "error_message": f'error {error_int}',
        }
        error_and_warning_list |= global_information_doc
        fill_list_of_docs(list_of_docs, index_name, error_and_warning_list)


def process(elk_client, index_name, ues_number, run_time, index_fix_version, fix_version_list) -> None:
    for index_version, version in enumerate(fix_version_list, start=0):
        print(f'version is: {version}\n{"="*25}\n')
        for index_build, (build_data_k, build_data_v) in enumerate(builds_data_dict.items(), start=0):
            print(f'index_build is: {index_build}')

            list_of_docs = []
            build_doc_id = generate_doc_id()
            jenkins_build_number = f'Build #{random.randint(5000 , 6000)}'

            global_information_doc = fill_global_information_doc(
                version=version,
                slave_name=slave_name_list[index_version],
                ems_version=ems_version_list[index_fix_version][index_version],
                build_doc_id=build_doc_id,
                test_plan=build_data_v['Test Plan Number'],
                test_set=build_data_v['Test Set Number'],
                build_name=build_data_k,
                jenkins_build_number=jenkins_build_number,
                time_list=list(range(run_time)),
            )

            for index_feature, (feature_data_k, feature_data_v) in enumerate(build_data_v.items(), start=0):
                if feature_data_k in ['Test Plan Number', 'Test Set Number']:
                    continue

                feature_doc_id = generate_doc_id()
                test_execution = f'SVGA-{random.randint(100, 300)}'
                random_pass_fail = 'PASS' if bool(random.randint(0, 1)) else 'FAIL'

                fill_feature_details_doc(
                    list_of_docs=list_of_docs,
                    index_name=index_name['dashboard_results_feature_details'],
                    timestamp=datetime.now(timezone.utc),
                    global_information_doc=global_information_doc,

                    feature_doc_id=feature_doc_id,
                    test_sir=feature_data_v['SIR Number'],
                    feature_name=feature_data_k,
                    feature_group_name=feature_data_v['Feature Group Name'],
                    random_pass_fail=random_pass_fail,
                    test_execution=test_execution,
                )
                for time_number in range(run_time):
                    fill_gnbs_docs(
                        list_of_docs=list_of_docs,
                        index_name=index_name['dashboard_results_gnbs'],
                        timestamp=datetime.now(timezone.utc),
                        global_information_doc=global_information_doc,

                        build_doc_id=build_doc_id,
                        feature_doc_id=feature_doc_id,
                        time_number=time_number,
                        feature_data=feature_data_v,
                        random_pass_fail=random_pass_fail,
                    )
                    fill_ues_docs(
                        list_of_docs=list_of_docs,
                        index_name=index_name['dashboard_results_ues'],
                        timestamp=datetime.now(timezone.utc),
                        global_information_doc=global_information_doc,

                        build_doc_id=build_doc_id,
                        feature_doc_id=feature_doc_id,
                        time_number=time_number,
                        ues_number=ues_number,
                    )
                    fill_error_and_warning_list(
                        list_of_docs=list_of_docs,
                        index_name=index_name['dashboard_results_error_and_warning_list'],
                        timestamp=datetime.now(timezone.utc),
                        global_information_doc=global_information_doc,
                    )
                    print()
            set_list_of_docs(elk_client, list_of_docs)
    print()


def main(elk_client, index_name, ues_number, run_time) -> None:
    for index_fix_version, fix_version_list in enumerate(version_list, start=0):
        process(elk_client, index_name, ues_number, run_time, index_fix_version, fix_version_list)
