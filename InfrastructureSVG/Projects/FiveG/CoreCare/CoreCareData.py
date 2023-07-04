import tarfile
# from datetime import datetime, timezone
import collections

# from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging

# Global Logger Configuration
PROJECT_NAME = 'CoreCare 5G Application'

COLUMNS = [
    'Date Line',
    'Date Uploading Crash',
    'Crash Type',
    'Version Type',
    'gNB Version',
    'Crash Version',
    'IP Address',
    'Setup Name',
    'Setup Owner',
    'Link To Crash Folder',
    'Crash File Name',
    'Back Trace hash',
    'Back Trace',
    'System Runtime',
    'PID',
    'Crash Timestamp',
    'Core TTI',
    'Customer Name',
    'Full BT',
    'Old BT',
    'Old Back Trace hash',
    'Core Validation Timestamp',
]

DEFECT_OPEN_STATUS_LIST_JIRA_SYNTAX = [
    '"Pending"',
    '"Processing"',
    '"Parked"',
    '"To Reproduce"',
    '"Fixed in R&D"',
    '"Ready for Verification"',
    '"Need more Info"',
    '"Verify Fail"',
    '"Screening"',
    '"Assigned to 3rd Party"',
]

DEFECT_CLOSE_STATUS_LIST_JIRA_SYNTAX = [
    '"Duplicate "',
    '"Closed "',
    '"VERIFY PASS"',
]

PROCESS_LIST = [
    'bbupool',
    'phy_proc_mng',
    'l1app',
    'dpdk-pdump',
    'PHY_RECV',
    'WORKER_',
    'gnb_du_',
    'fm_proc',
    'pmServerProc',
    'sysrepod',
    'systemd-journal',
    'netopeer',
    'kernel',
    '_fsm_',
]

PHY_PROCESS_LIST = [
    'bbupool',
    'phy_proc_mng',
    'l1app',
    'dpdk-pdump',
    'PHY_RECV ',
    '_lcore-worker',
]

cucp_core_files_mandatory = [
    'core_info',
    'core_mem_info',
    'exec_path',
    'systemerror',
    'systeminfo',
    'pid_file',
    'version.txt',
    'PersistentFileLogs',
    'severity.txt',
]

cuup_core_files_mandatory = [
    'core_info',
    'core_mem_info',
    'exec_path',
    'systemerror',
    'systeminfo',
    'pid_file',
    'version.txt',
    'PersistentFileLogs',
    'severity.txt',
]

du_core_files_mandatory = [
    'core_info',
    'core_mem_info',
    'exec_path',
    'systemerror',
    'systeminfo',
    'pid_file',
    'version.txt',
    'airspan-hard-reset.xml',
    'cell_sw_pvt_cfg.xml',
    'du_sw_pvt_cfg.xml',
    'gnb_vs_config.xml',
    '_3gpp-common-managed-element.xml',
    'severity_monolithic.txt',
]

ru_core_files_mandatory = [
    'core_info',
    'core_mem_info',
    'exec_path',
    'systemerror',
    'pid_file',
    'version.txt',
]

xpu_core_files_mandatory = [
    'core_info',
    'core_mem_info',
    'exec_path',
    'systemerror',
    'pid_file',
    'LogEvents',
    'PersistentFileLogs.txt',
    'version.txt',
    'airspan-o-ran-uplane-conf.xml',
    'rf_manager.xml',
]


def validate_data_crash_from_csv(crash_details: dict):
    if not crash_details.get('type_crash_name'):  # Type Crash Name
        return False
    elif not crash_details.get('ip_address'):  # IP Address
        return False
    elif not crash_details.get('setup_name'):  # Setup Name
        return False
    elif not crash_details.get('setup_owner'):  # Setup Owner
        return False
    elif not crash_details.get('link_to_core'):  # Link To Core
        return False
    elif not crash_details.get('core_file_name'):  # Core File Name
        return False
    elif not crash_details.get('back_trace_hash'):  # Back Trace hash
        return False
    elif not crash_details.get('back_trace'):  # Back Trace
        return False
    elif not crash_details.get('core_timestamp'):  # Core Timestamp
        return False
    elif not crash_details.get('core_tti'):  # Core TTI
        return False
    elif not crash_details.get('system_runtime'):  # System Runtime
        return False
    elif not crash_details.get('customer_name'):  # System Runtime
        return False
    else:
        return True


def get_tar_gz_file(back_trace_file_path: str):
    tar = None
    try:
        tar = tarfile.open(back_trace_file_path, encoding='utf-8')
        get_members = tar.getmembers()
    except Exception:
        if tar:
            tar.close()
        raise
    return tar, get_members


def read_tar_gz_file(tar, get_members, tr_gz_file_name: str, entity=None):
    fp_read = None
    if tr_gz_file_name_list := [
        tr_gz_name for tr_gz_name in get_members if
        (not tr_gz_name.name.startswith('.') and not tr_gz_name.name.endswith('.swp')) and
        ((entity and entity in tr_gz_name.name and tr_gz_file_name in tr_gz_name.name) or (not entity and tr_gz_file_name in tr_gz_name.name))
    ]:
        tr_gz_file_name = collections.OrderedDict(sorted({i.mtime: i for i in tr_gz_file_name_list}.items()))
        tr_gz_file_name = tr_gz_file_name[list(tr_gz_file_name.keys())[-1]]
        fp = tar.extractfile(tr_gz_file_name)
        fp_read = fp.read()
    return fp_read


def extract_specific_file(tar: tarfile, tar_members: list[tarfile], tr_gz_file_name: str, to_path: str, entity=None) -> [str, None]:
    if tr_gz_file_name_list := [
        tr_gz_name for tr_gz_name in tar_members if
        (not tr_gz_name.name.startswith('.') and not tr_gz_name.name.endswith('.swp')) and
        ((entity and entity in tr_gz_name.name and tr_gz_file_name in tr_gz_name.name) or (not entity and tr_gz_file_name in tr_gz_name.name))
    ]:
        tr_gz_file_name = collections.OrderedDict(sorted({i.mtime: i for i in tr_gz_file_name_list}.items()))
        tar.extractall(to_path, list(tr_gz_file_name.values()))
        return f'{to_path}\\var\\crash'
    else:
        return None


def close_tar_gz_file_reader(tar):
    if tar:
        tar.close()
