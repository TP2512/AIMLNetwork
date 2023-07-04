import contextlib
from typing import Dict, List

import pandas as pd
from zeep.helpers import serialize_object


def try_convert_to_float(val):
    with contextlib.suppress(ValueError):
        return int(val)


def select_columns(df: pd.DataFrame, columns: List) -> pd.DataFrame:
    return df[columns]


def serialize_soap_response(response) -> Dict:
    return serialize_object(response)


def add_kpi_to_data_frame(kpis, columns) -> pd.DataFrame:
    if hasattr(kpis, 'StatisticsResult'):
        df = pd.DataFrame(serialize_soap_response(kpis.StatisticsResult[0].LteHoStatsRow)).dropna(how='all', axis=1)
        df = select_columns(df, columns)
        df = df.applymap(try_convert_to_float)
        return df.groupby(level=0).sum()
    return pd.DataFrame()
