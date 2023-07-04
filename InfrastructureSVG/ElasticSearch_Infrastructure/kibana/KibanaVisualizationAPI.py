import datetime
import json
import requests
import numpy as np


class KibanaVisualizationAPI:
    def __init__(self):
        self.headers = {
            "kbn-xsrf": "true",
            'Content-Type': 'application/json'
        }

    @staticmethod
    def get_vis_saved_object(vis_name, vis_state):
        return {
            "visualization": {
              "title": vis_name,
              "visState": json.dumps(vis_state, sort_keys=True, indent=4, separators=(',', ': ')),
              "uiStateJSON": "{}",
              "description": "",
              "version": 1,
              "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                  "query": {
                    "language": "kuery",
                    "query": ""
                  },
                  "filter": []
                }),
              }
            },
            "type": "visualization",
            "references": [],
            "migrationVersion": {
              "visualization": "7.7.0"
            },
            "updated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        }

    def save_vega_lite_vis(self, client, index, vis_name, altair_chart, result_size=100, time_field=True):
        chart_json = json.loads(altair_chart.to_json())
        chart_json['data']['url'] = {
            "%context%": True,
            "index": index,
            "body": {
                "size": result_size
            }
        }

        if time_field:
            chart_json['data']['url']['%timefield%'] = "timestamp"

        vis_state = {
          "type": "vega",
          "aggs": [],
          "params": {
            "spec": json.dumps(chart_json, sort_keys=True, indent=4, separators=(',', ': ')),
          },
          "title": vis_name
        }

        return client.index(index='.kibana', id=f'visualization:{vis_name}', body=self.get_vis_saved_object(vis_name, vis_state))

    def save_vega_vis(self, client, index, vis_name, altair_chart, time_field=False):
        chart_json = json.loads(altair_chart.to_json())
        chart_json['spec'] = {'data': {}}
        chart_json['spec']['data']['url'] = {
            "%context%": True,
            "index": index,
        }

        if time_field:
            chart_json['spec']['data']['url']['%timefield%'] = "timestamp"

        vis_state = {
          "type": "vega",
          "aggs": [],
          "params": {
            "spec": json.dumps(chart_json, sort_keys=True, indent=4, separators=(',', ': ')),
          },
          "title": vis_name,
        }

        client.index(index='.kibana', id=f'visualization:{vis_name}', body=self.get_vis_saved_object(vis_name, vis_state))

    def create_and_set_tags(self, elasticsearch_url, kibana_port, tag_list, chart_name):
        existing_tag_list = self.get_existing_tag_list(elasticsearch_url, kibana_port)
        non_existing_tag_list = []
        tag_not_exist = False
        for tag in tag_list:
            try:
                next(tag for existing_tag in existing_tag_list if existing_tag["name"] == tag['tag_name'])
            except StopIteration:
                tag_not_exist = True
                non_existing_tag_list.append(tag)
                self.create_tag(elasticsearch_url, kibana_port, tag)
        if tag_not_exist:
            existing_tag_list = self.get_existing_tag_list(elasticsearch_url, kibana_port)
        self.add_tag_to_visualization(elasticsearch_url, kibana_port, tag_list, existing_tag_list, chart_name)

    def get_existing_tag_list(self, elasticsearch_url, kibana_port):
        uri = f"{elasticsearch_url}:{kibana_port}/api/saved_objects_tagging/tags"
        response = requests.get(uri, headers=self.headers).json()
        return response['tags']

    def create_tag(self, elasticsearch_url, kibana_port, tag):
        color = tuple(np.random.choice(range(256), size=3))
        hex_color = '#%02x%02x%02x' % color
        query = json.dumps({"name": tag['tag_name'], "description": "", "color": hex_color})
        uri = f"{elasticsearch_url}:{kibana_port}/api/saved_objects_tagging/tags/create"
        requests.post(uri, headers=self.headers, data=query).json()

    def add_tag_to_visualization(self, elasticsearch_url, kibana_port, tag_list, existing_tag_list, chart_name):
        tag_ids = []
        for tag in tag_list:
            existing_tag = next(existing_tag for existing_tag in existing_tag_list if existing_tag["name"] == tag['tag_name'])
            tag_ids.append(existing_tag['id'])
        query = json.dumps({"tags": tag_ids,
                            "assign": [{"type": "visualization",
                                        "id": chart_name}],
                            "unassign": []})
        uri = f"{elasticsearch_url}:{kibana_port}/api/saved_objects_tagging/assignments/update_by_tags"
        requests.post(uri, headers=self.headers, data=query).json()
