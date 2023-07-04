from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchForDashboard.ElasticSearchURVersion.ElasticSearchURVersion import ElasticSearchURVersion
from elasticsearch_dsl import Search, UpdateByQuery

if __name__ == '__main__':
    elastic_search_ur_version_ins = ElasticSearchURVersion()
    data = elastic_search_ur_version_ins.search_for_test_plan(ur_version='SR19.00_UR7.2', test_plan='SVGA-21093')

    for document in data:
        print(f'id = {document.meta.id}')
        query = {'query': {'match': {'_id': f'{document.meta.id}'}}}
        script_source = "ctx._source.automation_manual = \"Automation\";"
        ubq = UpdateByQuery(using=elastic_search_ur_version_ins.elk_client, index=document.meta.index).update_from_dict(query).script(source=script_source)
        ubq.execute()
        print()
    print()
