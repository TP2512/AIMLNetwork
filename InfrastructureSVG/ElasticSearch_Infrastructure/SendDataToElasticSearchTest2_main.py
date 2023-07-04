from datetime import datetime, timezone

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from InfrastructureSVG.ElasticSearch_Infrastructure.SendDataToElasticSearch2 import CreateELKDocument

if __name__ == '__main__':
    print(f'\nStart pandas to ELK\n')

    username = 'azaguri'
    timestamp = datetime.now(timezone.utc)
    doc_id = timestamp.strftime('%Y%m%d%H%M%S')
    path = 'C:\\Users\\Administrator\\Desktop\\Files2'

    elk_client = ElasticSearchConnection().connect_to_svg_elasticsearch_dev()

    elk_index_and_files_name_list = [
        {'file_name': 'downlink_packets.csv', 'doc_index_name': 'ws_dl_analyzer'},
        {'file_name': 'uplink_packets.csv', 'doc_index_name': 'ws_ul_analyzer'},
        {'file_name': 'error_packets.csv', 'doc_index_name': 'ws_error_analyzer'},
        {'file_name': 'csirs.csv', 'doc_index_name': 'ws_csirs_analyzer'},
        {'file_name': 'ssb.csv', 'doc_index_name': 'ws_ssb_analyzer'},
    ]

    CreateDocument(elk_client=elk_client).fill_elk_index_by_csv(
        path=path,
        elk_client=elk_client,
        elk_index_and_files_name_list=elk_index_and_files_name_list,
        doc_id=doc_id,
        timestamp=timestamp,
        username=username
    )

    print(f'\n\ndoc_id_ is: {doc_id}')

    print()
