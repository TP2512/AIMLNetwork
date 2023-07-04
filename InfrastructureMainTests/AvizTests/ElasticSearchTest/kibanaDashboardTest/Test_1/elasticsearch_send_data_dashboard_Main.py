from datetime import datetime, timezone

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureMainTests.AvizTests.ElasticSearchTest.kibanaDashboardTest.Test_1.elasticsearch_send_data_dashboard_test import main


if __name__ == '__main__':
    _elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch_dev()

    index = 1
    main(
        elk_client=_elk_client,
        index_name=f'dashboard_results__test_{index}',
        ues_number=5,
        timestamp=datetime.now(timezone.utc),
    )

    print()
