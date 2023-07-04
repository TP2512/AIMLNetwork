import pandas as pd
from datetime import datetime, timezone

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.SendDataToElasticSearch2 import CreateELKDocument

if __name__ == '__main__':
    print('\nStart pandas to ELK\n')

    doc_index_name = 'robot_test_2'
    username = 'azaguri'
    timestamp = datetime.now(timezone.utc)
    doc_id = timestamp.strftime('%Y%m%d%H%M%S')

    columns = ['tp_test', 'time_test']

    tp_test = [9, 9, 60, 9, 90, 90, 90, 90, 100, 100]  # tp_test
    time_test = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # time_test
    row = [tp_test, time_test]

    # A = [55, 99, 57, 8]
    # B = [1, 2, 3, 4]
    # row = [A, B]
    dataframe = pd.DataFrame([row], columns=columns)

    elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch()

    doc = {}

    columns = dataframe.columns.tolist()
    if not timestamp.tzinfo:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    for index, row in dataframe.iterrows():
        # doc.update({'doc_id': doc_id, 'timestamp': timestamp})
        for column in columns:
            if type(row[column]) != list and pd.isnull(row[column]):
                row[column] = ''
                row[column] = None
            elif row[column] is True:
                row[column] = 'True'
            elif row[column] is False:
                row[column] = 'False'

            # self.logger.debug(f'{column}: {row[column]}')
            doc[column] = row[column]

        elk_info = elk_client.index(index=doc_index_name, document=doc)

    print(f'\n\ndoc_id_ is: {doc_id}')

    print()
