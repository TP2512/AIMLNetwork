import pandas as pd
from datetime import datetime, timezone
import random
from datetime import datetime, timezone

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.SendDataToElasticSearch2 import CreateELKDocument


if __name__ == '__main__':
    print(f'start time is: {datetime.now(timezone.utc)}')

    print('\nStart pandas to ELK\n')

    doc_index_name = 'robot_test'
    username = 'azaguri'
    timestamp = datetime.now(timezone.utc)
    doc_id = timestamp.strftime('%Y%m%d%H%M%S')

    columns = ['time_test', 'tp_test']

    tp_test_per_time = [{'time_test': i, 'tp_test': random.randint(1, 100)} for i in range(3600)]

    # tp_test_per_time = [
    #     {'time_test': 1, 'tp_test': 100},
    #     {'time_test': 2, 'tp_test': 100},
    #     {'time_test': 3, 'tp_test': 6},
    #     {'time_test': 4, 'tp_test': 6},
    #     {'time_test': 5, 'tp_test': 6},
    #     {'time_test': 6, 'tp_test': 60},
    #     {'time_test': 7, 'tp_test': 60},
    #     {'time_test': 8, 'tp_test': 100},
    #     {'time_test': 9, 'tp_test': 100},
    #     {'time_test': 10, 'tp_test': 100}
    # ]

    dataframe = pd.DataFrame(tp_test_per_time, columns=columns)

    elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch()

    CreateELKDocument(elk_client=elk_client).fill_elk_index(
        dataframe=dataframe,
        doc_id=doc_id,
        elk_client=elk_client,
        doc_index_name=doc_index_name,
        timestamp=timestamp,
        date_and_time=timestamp,
        username=username
    )

    print(f'\n\ndoc_id_ is: {doc_id}\n')
    print(f'end time is: {datetime.now(timezone.utc)}')

    print()
