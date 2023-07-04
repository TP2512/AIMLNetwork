from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchForDashboard.ElasticSearchDashboard import SendDataForDashboard

if __name__ == '__main__':
    feature_global_information_doc = {'automation_manual': 'Automation', 'doc_id': '2022100816354710', 'feature_doc_id': '2022100816354710', 'ezlife_builder_id': None,
                                      'ezlife_builder_name': '[bobcat][AS2200]ACP_Sanity', 'jenkins_build_number': 'Build #7955', 'slave_name': 'ASIL-BOBCAT', 'ur_version': 'BackLOG', 'environment_config': None,
                                      'test_plan': None, 'test_set': 'SIR-47007', 'test_sir': None, 'feature_name': 'ACP_Sanity', 'feature_group_name': 'Initialization_and_SW_upgrade_process',
                                      'test_execution_list': ['SVGA-29767'], 'test_execution_list_str': 'SVGA-29767', 'test_plan_2': 'None', 'test_sir_2': 'None', 'test_plan_and_test_sir_2': 'None + None',
                                      'scenario_run_time': 13, 'scenario_status': 'FAIL', 'test_run_time': 1, 'gnb_test_status_list': ['FAIL'], 'run_test_in_loop': False, 'loop_count': False, 'gnb_type_list': ['AIO'],
                                      'gnb_type_list_str': 'AIO', 'fix_version_list': ['19.00', '19.50'], 'fix_version_list_str': '19.00, 19.50', 'cucp_fix_version_list': ['19.00'],
                                      'cucp_version_list': ['19.00-271-2.17'], 'cucp_version_list_str': '19.00-271-2.17', 'cuup_fix_version_list': ['19.00'], 'cuup_version_list': ['19.00-271-2.17'],
                                      'cuup_version_list_str': '19.00-271-2.17', 'du_fix_version_list': ['19.00'], 'du_version_list': ['19.00-383-1.105'], 'du_version_list_str': '19.00-383-1.105',
                                      'ru_fix_version_list': ['19.50'], 'ru_version_list': ['19.50-107-0.0'], 'ru_version_list_str': '19.50-107-0.0', 'aio_fix_version_list': ['19.00'],
                                      'aio_version_list': ['19.00-130-5.13'], 'aio_version_list_str': '19.00-130-5.13', 'xpu_fix_version_list': ['19.00'], 'xpu_version_list': ['19.00-175-1.27'],
                                      'xpu_version_list_str': '19.00-175-1.27', 'ems_fix_version_list': ['129.19.50.026'], 'ems_version_list': ['129.19.50.026'], 'ems_version_list_str': '129.19.50.026',
                                      'previous_cucp_fix_version_list': ['19.00'], 'previous_cucp_version_list': ['19.00-271-2.17'], 'previous_cucp_version_list_str': '19.00-271-2.17',
                                      'previous_cuup_fix_version_list': ['19.00'], 'previous_cuup_version_list': ['19.00-271-2.17'], 'previous_cuup_version_list_str': '19.00-271-2.17',
                                      'previous_du_fix_version_list': ['19.00'], 'previous_du_version_list': ['19.00-383-1.105'], 'previous_du_version_list_str': '19.00-383-1.105',
                                      'previous_ru_fix_version_list': ['19.50'], 'previous_ru_version_list': ['19.50-107-0.0'], 'previous_ru_version_list_str': '19.50-107-0.0',
                                      'previous_aio_fix_version_list': ['19.00'], 'previous_aio_version_list': ['19.00-130-5.13'], 'previous_aio_version_list_str': '19.00-130-5.13',
                                      'previous_xpu_fix_version_list': ['19.00'], 'previous_xpu_version_list': ['19.00-175-1.27'], 'previous_xpu_version_list_str': '19.00-175-1.27',
                                      'previous_ems_fix_version_list': ['129.19.50.026'], 'previous_ems_version_list': ['129.19.50.026'], 'previous_ems_version_list_str': '129.19.50.026', 'number_of_ues': 0,
                                      'core_files_name_list': [], 'core_files_name_list_str': '', 'defects_list': 'N/A', 'defects_list_str': 'N/A', 'traffic_transport_layer_protocol': 'UDP',
                                      'automation_traffic_direction': 'Bidi', 'traffic_testing_tool': 'IPERFv2', 'window_size': None, 'frame_size': '1300', 'threshold': None, 'dl_threshold': None, 'ul_threshold': None,
                                      'ul_avg': 0.0, 'dl_avg': 0.0, 'max_ul': 0.0, 'max_dl': 0.0, 'expected_dl': None, 'expected_ul': None, 'ho_type': None}

    elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch()
    list_of_docs = []
    send_data_for_dashboard = SendDataForDashboard()
    send_data_for_dashboard.fill_list_of_docs(
        list_of_docs=list_of_docs,
        index_name='new_dashboard_results_gnbs_production',
        doc=feature_global_information_doc
    )
    send_data_for_dashboard.set_list_of_docs(
        elk_client=elk_client,
        list_of_docs=list_of_docs
    )

    print()
