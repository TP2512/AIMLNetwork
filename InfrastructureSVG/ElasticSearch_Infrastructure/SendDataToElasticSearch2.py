import pandas as pd
import logging
from datetime import datetime, timezone


# import numpy as np
# import math


class CreateELKDocument:
    def __init__(self, elk_client):
        self.logger = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)
        self.doc = {}
        self.elk_client = elk_client

    def fill_elk_index(self, dataframe, doc_id, elk_client, doc_index_name, timestamp, date_and_time, username):
        columns = dataframe.columns.tolist()
        if not timestamp.tzinfo:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        if not date_and_time.tzinfo:
            date_and_time = date_and_time.replace(tzinfo=timezone.utc)

        for index, row in dataframe.iterrows():
            self.doc.update({'doc_id': doc_id, 'timestamp': timestamp})
            if date_and_time:
                self.doc['date_and_time'] = date_and_time
            if username:
                self.doc['username'] = username

            for column in columns:
                if type(row[column]) != list and pd.isnull(row[column]):  # if row[column] is np.nan or row[column] is None or pd.isnull(row[column]) or math.isnan(row[column]):
                    row[column] = ''
                    row[column] = None
                elif row[column] is True:
                    row[column] = 'True'
                elif row[column] is False:
                    row[column] = 'False'

                # self.logger.debug(f'{column}: {row[column]}')
                self.doc[column] = row[column]

            elk_info = elk_client.index(index=doc_index_name, document=self.doc)
            self.logger.info(elk_info)

    def fill_elk_index_by_csv(self, path, elk_client, elk_index_and_files_name_list, doc_id, timestamp, username=None):
        # elk_index_and_files_name_list = [
        #     {'file_name': 'tmp1.csv', 'doc_index_name': 'tmp1'},
        #     {'file_name': 'tmp2.csv', 'doc_index_name': 'tmp2'},
        # ]

        for elk_index_and_files_name in elk_index_and_files_name_list:
            self.logger.info(f'file_name is: {elk_index_and_files_name["file_name"]}')
            self.logger.info(f'doc_index_name is: {elk_index_and_files_name["doc_index_name"]}')

            dataframe_ = pd.read_csv(f'{path}\\{elk_index_and_files_name["file_name"]}')
            self.fill_elk_index(
                dataframe=dataframe_,
                elk_client=elk_client,
                doc_id=doc_id,
                doc_index_name=elk_index_and_files_name["doc_index_name"],
                timestamp=timestamp,
                date_and_time=timestamp,
                username=username,
            )
