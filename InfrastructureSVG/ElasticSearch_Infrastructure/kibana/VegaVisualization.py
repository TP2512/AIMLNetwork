import pandas as pd
import altair as alt
from InfrastructureSVG.ElasticSearch_Infrastructure.kibana.KibanaVisualizationAPI import KibanaVisualizationAPI

import logging
from InfrastructureSVG.ElasticSearch_Infrastructure.validation.kibana_visualization_validation import KibanaVisualizationValidation
from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection

alt.data_transformers.disable_max_rows()


class VegaVisualizations:

    def __init__(self):
        self.logger = logging.getLogger('MLSystemAnalyzerSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)
        self.elasticSearchConnection = ElasticSearchConnection()
        self.elastic_client = self.elasticSearchConnection.connect_to_svg_elasticsearch()
        self.elasticsearch_url = self.elasticSearchConnection.elasticsearch_url
        self.kibana_port = self.elasticSearchConnection.kibana_port
        self.index_name = "robotautomation"
        self.kibana_visualization_api = KibanaVisualizationAPI()
        self.kibana_visualization_validation = KibanaVisualizationValidation()

    def get_data(self, fields_definition, doc_id, traffic_direction):
        query_body = {
            "query": {
                "terms": {
                    "_id": [doc_id]
                }
            }
        }
        result = self.elastic_client.search(index=self.index_name, body=query_body)
        df = pd.DataFrame()
        independent_vars_list = []
        for field_definition in fields_definition:
            df[field_definition['field_title']] = result['hits']['hits'][0]['_source'][field_definition['field_name']]
            independent_vars_list.append(field_definition['field_title'])
        df['TP'] = result['hits']['hits'][0]['_source'][f"{traffic_direction} TP List"]
        bs_hardware_types = set(result['hits']['hits'][0]['_source']['BS Hardware Type'])
        tag_list = [{'tag_type_name': 'BSHardwareType', 'tag_name': bs_hardware_type} for bs_hardware_type in bs_hardware_types]

        tag_list.extend(({'tag_type_name': 'G5_CUUP_Ver', 'tag_name': f"CUUP_ver_{result['hits']['hits'][0]['_source']['G5_CUUP_Ver']}"}, {'tag_type_name': 'G5_CUCP_Ver', 'tag_name': f"CUCP_ver_{result['hits']['hits'][0]['_source']['G5_CUCP_Ver']}"},
                         {'tag_type_name': 'G5_RU_Ver', 'tag_name': f"RU_ver_{result['hits']['hits'][0]['_source']['G5_RU_Ver']}"}, {'tag_type_name': 'G5_DU_Ver', 'tag_name': f"DU_ver_{result['hits']['hits'][0]['_source']['G5_DU_Ver']}"}))

        dependent_var = 'TP'
        return df.astype(str), dependent_var, independent_vars_list, tag_list

    @staticmethod
    def prepare_chart(df, dependent_var, independent_vars_list, fields_definition):
        selection = alt.selection_single(fields=['independent_var'],
                                         bind='legend',
                                         empty='none',
                                         init={'independent_var': independent_vars_list[0]})
        color_list = [
            '#4363d8',  # Blue
            '#3cb44b',  # Green
            '#911eb4',  # Purple
            '#f58231',  # Orange
            '#e6194B',  # Red
            '#f032e6',  # Magenta
            '#42d4f4',  # Cyan
            '#bfef45',  # Lime
            '#000075',  # Navy
            '#469990',  # Teal
            '#9A6324',  # Brown
            '#00fa9a',  # mediumspringgreen
            '#800000',  # Maroon
            '#ff1493',  # deeppink
            '#fa8072',  # salmon
            '#4169e1',  # royalblue
            '#808000',  # Olive
            '#da70d6',  # orchid
            '#8fbc8f',  # darkseagreen
            '#dc143c',  # crimson
        ]

        independent_vars_color_list = [color_list[field_index + 15] for field_index, field_dict in enumerate(fields_definition)]

        independent_vars_title_list = [field_dict['field_title'] for field_dict in fields_definition]

        base = alt.Chart(df).transform_fold(independent_vars_list, as_=['independent_var', 'metrics']). \
            mark_line().encode(x=alt.X('metrics', sort='descending', type='ordinal', title=None),
                               y=alt.Y(dependent_var, type='quantitative', title='Throughput'),
                               color=alt.Opacity('independent_var:O', legend=alt.Legend(title="metrics", orient="none", legendX=1170, legendY=150),
                                                 scale=alt.Scale(range=independent_vars_color_list, domain=independent_vars_list))).add_selection(selection).transform_filter(selection)

        df_independent_vars = pd.DataFrame({'independent_var_names': independent_vars_list})
        text = alt.Chart(df_independent_vars).transform_fold(
            independent_vars_list,
            as_=['independent_var', 'metrics']
        ).mark_text(dy=270, fontSize=15).encode(text='_var_name:O',).transform_filter(selection).transform_calculate(_var_name=alt.datum.independent_var)
        chart = base + text
        return chart.properties(width=1300, height=700, padding={"right": 150, "top": 50}, autosize="none").configure_legend(titleFontSize=15, labelFontSize=15)

    def create_visualization_by_id(self, doc_id, chart_name, fields_definition, traffic_direction):
        if self.kibana_visualization_validation.validate_fields_definition(fields_definition):
            self.logger.info('input validation passed')
            df, dependent_var, independent_vars_list, tag_list = self.get_data(fields_definition, doc_id, traffic_direction)
            chart = self.prepare_chart(df, dependent_var, independent_vars_list, fields_definition)
            self.kibana_visualization_api.save_vega_vis(self.elastic_client,
                                                        self.index_name,
                                                        chart_name,
                                                        chart)
            self.kibana_visualization_api.create_and_set_tags(self.elasticsearch_url,
                                                              self.kibana_port,
                                                              tag_list,
                                                              chart_name)
        else:
            self.logger.error('input validation error')


if __name__ == "__main__":
    _doc_id = 'GoxV4H8BWRleWQJT0IOG'
    _chart_name = 'vega_visualisation_GoxV4H8BWRleWQJT0IOG'
    _fields_definition = [{'field_name': 'MCS', 'field_title': 'MCS'},
                          {'field_name': 'RSRP', 'field_title': 'RSRP'},
                          {'field_name': 'RSSI', 'field_title': 'RSSI'},
                          {'field_name': 'RSRQ', 'field_title': 'RSRQ'},
                          {'field_name': 'SINR', 'field_title': 'SINR'}]
    vega_visualizations = VegaVisualizations()
    vega_visualizations.create_visualization_by_id(_doc_id, _chart_name, _fields_definition, 'DL')
