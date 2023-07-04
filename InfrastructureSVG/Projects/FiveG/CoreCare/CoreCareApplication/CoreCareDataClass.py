from typing import Union
import pandas as pd
from dataclasses import dataclass


def get_entity_crash_name(type_crash_name: str):
    if 'cp' in type_crash_name.lower():
        return 'CUCP'
    elif 'up' in type_crash_name.lower():
        return 'CUUP'
    elif 'du' in type_crash_name.lower():
        return 'DU_L2'
    elif 'ru' in type_crash_name.lower():
        return 'RU'
    elif 'xpu' in type_crash_name.lower():
        return 'XPU'
    else:
        return ''


@dataclass(frozen=True)
class GlobalConfiguration:
    PATTERNS: list
    PROJECT_NAME: str
    HOST_NAME: str
    SERVER_PATH: str
    LAST_ROW_INDEX_PATH: str


@dataclass(frozen=True)
class ListenerConfiguration:
    RECURSIVE: bool
    days_before: int
    old_size: int


@dataclass()
class ProcessConfiguration:
    OPEN_DEFECT: bool
    LINK_TO_LAST_DEFECT: list
    REPLACE_TEST_ENVIRONMENTS: dict


@dataclass()
class CrashParameters:
    row: pd.DataFrame
    site: str
    test_flag: Union[str, bool, None]

    def __post_init__(self):
        self.date_uploading_core: str = '' if pd.isnull(self.row.get('Date Uploading Crash', '')) else self.row.get('Date Uploading Crash', '')
        self.type_crash_name: str = '' if pd.isnull(self.row.get('Crash Type', '')) else self.row.get('Crash Type', '')
        self.entity_crash_name: str = get_entity_crash_name(self.type_crash_name)
        self.version_type: str = 'undefined' if pd.isnull(self.row.get('Version Type', '')) else self.row.get('Version Type', '')
        self.gnb_version: str = '' if pd.isnull(self.row.get('gNB Version', '')) else self.row.get('gNB Version', '')
        self.crash_version: str = '' if pd.isnull(self.row.get('Crash Version', '')) else self.row.get('Crash Version', '')
        self.ip_address: str = '' if pd.isnull(self.row.get('IP Address', '')) else self.row.get('IP Address', '')
        self.setup_name: str = '' if pd.isnull(self.row.get('Setup Name', '')) else self.row.get('Setup Name', '')
        self.setup_owner: str = 'akimiagarov' if pd.isnull(self.row.get('Setup Owner', '')) else self.row.get('Setup Owner', '')
        self.link_to_core: str = '' if pd.isnull(self.row.get('Link To Crash Folder', '')) else self.row.get('Link To Crash Folder', '')
        self.core_file_name: str = '' if pd.isnull(self.row.get('Crash File Name', '')) else self.row.get('Crash File Name', '')
        self.back_trace_hash: str = '' if pd.isnull(self.row.get('Back Trace hash', '')) else int(self.row.get('Back Trace hash', ''))
        self.back_trace: str = '' if pd.isnull(self.row.get('Back Trace', '')) else self.row.get('Back Trace', '')
        self.system_runtime: str = '' if pd.isnull(self.row.get('System Runtime', '')) else self.row.get('System Runtime', '')
        self.core_timestamp: str = '' if pd.isnull(self.row.get('Crash Timestamp', '')) else self.row.get('Crash Timestamp', '')
        self.core_pid: str = '' if pd.isnull(self.row.get('PID', '')) else self.row.get('PID', '')
        self.core_tti: str = '' if pd.isnull(self.row.get('Core TTI', '')) else self.row.get('Core TTI', '')
        self.customer_name: str = '' if pd.isnull(self.row.get('Customer Name', '')) else self.row.get('Customer Name', '')
        self.full_bt: str = '' if pd.isnull(self.row.get('Full BT', '')) else self.row.get('Full BT', '')
        self.old_bt: str = '' if pd.isnull(self.row.get('Old BT', '')) else self.row.get('Old BT', '')
        self.old_back_trace_hash: str = '' if pd.isnull(self.row.get('Old Back Trace hash', '')) else int(self.row.get('Old Back Trace hash', ''))
        self.core_validation_timestamp: str = '' if pd.isnull(self.row.get('Core Validation Timestamp', '')) else self.row.get('Core Validation Timestamp', '')
