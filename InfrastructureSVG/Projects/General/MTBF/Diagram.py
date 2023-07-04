import logging
import os

import plotly.express as px
from pandasticsearch import DataFrame


class Diagram:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    @staticmethod
    def create_line_diagram(data: DataFrame, title: str, y_label: str, x_label: str, menu: str, execution_id: str, diagram_path: str):
        fig = px.line(data, x=x_label, y=y_label, color=menu, title=title)
        fig.update_traces(textposition="bottom right")
        path = os.path.join(diagram_path, f'{execution_id}.html')
        fig.write_html(path)
