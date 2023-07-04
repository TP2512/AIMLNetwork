from datetime import datetime, timezone

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureMainTests.AvizTests.ElasticSearchTest.kibanaDashboardTest.Test_3.elasticsearch_send_data_dashboard_test_3 import main


if __name__ == '__main__':
    _elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch_dev()

    index = 1
    main(
        elk_client=_elk_client,
        # index_name='dashboard_results__test_1',
        index_name={
            'dashboard_results_setup': f'dashboard_results_setup_test_{index}',
            'dashboard_results_enbs': f'dashboard_results_enbs_test_{index}',
            'dashboard_results_ues': f'dashboard_results_ues_test_{index}'
        },
        ues_number=5,
        timestamp=datetime.now(timezone.utc),
    )

    print()
