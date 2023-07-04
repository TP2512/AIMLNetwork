from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from datetime import datetime, timezone
import pandas as pd
# import numpy as np
# import math


def fill_elk_index(dataframe, doc_id, elk_client, doc_index_name, timestamp, date_and_time, username):
    columns = dataframe.columns.tolist()
    for index, row in dataframe.iterrows():
        doc = {'doc_id': doc_id, 'timestamp': timestamp}
        if date_and_time:
            doc['date_and_time'] = date_and_time
        if username:
            doc['username'] = username

        for column in columns:
            if pd.isnull(row[column]):
                row[column] = ''
                row[column] = None
            elif row[column] is True:
                row[column] = 'True'
            elif row[column] is False:
                row[column] = 'False'

            print(f'{column}: {row[column]}')
            doc[column] = row[column]

        elk_info = elk_client.index(index=doc_index_name, document=doc)
        print(elk_info)


def fill_elk_index_by_csv(path, elk_client, elk_index_and_files_name_list, doc_id, timestamp, username):
    # elk_index_and_files_name_list = [
    #     {'file_name': 'tmp1.csv', 'doc_index_name': 'tmp1'},
    #     {'file_name': 'tmp2.csv', 'doc_index_name': 'tmp2'},
    # ]

    for elk_index_and_files_name in elk_index_and_files_name_list:
        print(f'file_name is: {elk_index_and_files_name["file_name"]}')
        print(f'doc_index_name is: {elk_index_and_files_name["doc_index_name"]}')

        dataframe_ = pd.read_csv(f'{path}\\{elk_index_and_files_name["file_name"]}')
        fill_elk_index(
            dataframe=dataframe_,
            elk_client=elk_client,
            doc_id=doc_id,
            doc_index_name=elk_index_and_files_name["doc_index_name"],
            timestamp=timestamp,
            date_and_time=timestamp,
            username=username,
        )
