from datetime import datetime, timezone

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureMainTests.AvizTests.ElasticSearchTest.kibanaDashboardTest.Test_4.elasticsearch_send_data_dashboard_test_4 import main


if __name__ == '__main__':
    _elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch_dev()

    index = 1
    main(
        elk_client=_elk_client,
        index_name={
            'dashboard_results_setup': f'new_dashboard_results_setup_test_{index}',
            'dashboard_results_feature_details': f'new_dashboard_results_feature_details_test_{index}',
            'dashboard_results_gnbs': f'new_dashboard_results_gnbs_test_{index}',
            'dashboard_results_ues': f'new_dashboard_results_ues_test_{index}',
            'dashboard_results_execution': f'new_dashboard_results_execution_test_{index}',
            'dashboard_results_error_and_warning_list': f'new_dashboard_results_error_and_warning_list_test_{index}',
        },
        ues_number=5,
        run_time=5,
    )

    print()
