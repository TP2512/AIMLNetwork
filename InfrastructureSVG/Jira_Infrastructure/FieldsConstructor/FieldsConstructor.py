import json
from dataclasses import dataclass, asdict


@dataclass
class IssueFieldsConstructor:
    # Customfield Name:
    ASSIGNEE: str = "assignee"
    DESCRIPTION: str = "description"
    FIX_VERSIONS: str = "fixVersions"
    ISSUE_LINKS: str = "issuelinks"
    KEY: str = 'key'
    LABELS: str = "labels"
    PROJECT: str = "project"
    REPORTER: str = "reporter"
    SUMMARY: str = "summary"
    STATUS: str = "status"
    UPDATED: str = "updated"
    AFFECTED_VERSIONS: str = "versions"

    # Customfield Number:
    EPIC_LINK: str = "customfield_10000"
    EPIC_NAME: str = "customfield_10002"
    REPORTED_IN_RELEASE: str = "customfield_10200"
    REPRODUCIBILITY_FREQUENCY: str = "customfield_10201"
    PRODUCT_AT_FAULT: str = "customfield_10202"
    SEVERITY: str = "customfield_10406"
    LINK: str = "customfield_10508"
    CHIPSET: str = "customfield_10510"
    BAND: str = "customfield_10511"
    BW: str = "customfield_10513"
    DEFECT_MODULE_SUB_FEATURE: str = "customfield_10712"
    DOCUMENT_REFERENCE_NAME: str = "customfield_10713"
    TARGET_RELEASE: str = "customfield_10715"
    ENB_CD_DU_SW: str = "customfield_10726"
    EMS_TYPE: str = "customfield_10731"
    BANDWIDTH: str = "customfield_10734"
    DISCOVERY_SITE_CUSTOMER: str = "customfield_10736"
    EMS_SOFTWARE_VERSION: str = "customfield_10737"
    HW_TYPE: str = "customfield_10800"
    NOTES: str = "customfield_10975"
    TEST_SIR: str = "customfield_10993"
    TEST_ENVIRONMENT: str = "customfield_11003"
    TEST_PLAN: str = "customfield_11005"
    BACKHAUL: str = "customfield_11500"
    SHOWSTOPPER: str = "customfield_11200"
    DEFECT_IMPACT: str = "customfield_11449"
    FEATURE_NAME: str = "customfield_11801"
    LOGS_PATH: str = "customfield_12600"
    FRAME_SIZE: str = "customfield_12607"
    RUN_TIME: str = "customfield_12623"
    MIN_RUN_TIME: str = "customfield_12652"
    MAX_RUN_TIME: str = "customfield_12667"
    REPORT_LINK: str = "customfield_12818"
    CUSTOMER_NAME: str = "customfield_13300"
    DL: str = "customfield_13514"
    UL: str = "customfield_13515"
    # ENB_SW_VERSION: str = "customfield_13707"
    GNB_VERSION: str = "customfield_13707"
    UE_RELAY_SW_VERSION: str = "customfield_13708"
    ACP_VERSION: str = "customfield_13709"
    GNB_SYSTEM_DEFAULT_PROFILE_VERSION: str = "customfield_13710"
    RELAY_SYSTEM_DEFAULT_PROFILE_VERSION: str = "customfield_13711"
    AUTOMATION_SETUP_NAME: str = "customfield_13712"
    AUTOMATION_BUILD_NAME: str = "customfield_13713"
    NUMBER_OF_UES: str = "customfield_13716"
    TRAFFIC_TRANSPORT_LAYER: str = "customfield_13816"
    TP_CALCULATOR_LABEL: str = "customfield_13817"
    UDP_TRAFFIC_AVG_LATENCY: str = "customfield_13818"
    PING_AVG_LATENCY: str = "customfield_13819"
    HO_SUCCESS_RATE: str = "customfield_13820"
    HO_TYPE: str = "customfield_13821"
    AUTOMATION_TEST_SET_KEY: str = "customfield_13822"
    TRAFFIC_DIRECTION: str = "customfield_13834"
    TRAFFIC_TESTING_TOOL: str = "customfield_13900"
    AUTOMATION_ERROR_MESSAGE: str = "customfield_14100"
    TCP_WINDOW_SIZE: str = "customfield_14300"
    CELL_CARRIER: str = "customfield_14500"
    CORE_SYSTEM_UP_TIME: str = "customfield_14801"
    CORE_SYSTEM_UPTIME: str = "customfield_14803"
    CORE_DISCOVERY_SITE: str = "customfield_14900"
    ACTUAL_RESULT: str = "customfield_14915"
    CORE_OCCURRENCE_COUNT: str = "customfield_15000"
    FAILURE_REASON: str = "customfield_15701"
    DU_VERSION: str = "customfield_16200"
    RU_VERSION: str = "customfield_16203"
    TIME_TO_FIRST_CRASH: str = "customfield_16400"
    SCENARIO_RUN_TIME: str = "customfield_16500"
    KPI: str = "customfield_16600"
    MTBF_CORE_OCCURRENCE_COUNT: str = "customfield_16700"
    CUCP_VERSION: str = "customfield_16800"
    CUUP_VERSION: str = "customfield_16801"
    NUMEROLOGY: str = "customfield_16900"
    FORMAT: str = "customfield_17300"
    DL_LAYERS: str = "customfield_17301"
    UL_LAYERS: str = "customfield_17302"
    DL_CA: str = "customfield_20800"
    UL_CA: str = "customfield_20801"
    TDD_SPLIT: str = "customfield_20400"
    FC: str = "customfield_10512"
    PRODUCT_SUPPORT: str = "customfield_20401"
    HASH_BT: str = "customfield_18301"
    CRASH_PID: str = "customfield_18302"
    LAST_OCCURRED_GNB_VERSIONS: str = "customfield_18401"
    TOTAL_CORE_OCCURRENCE_COUNT: str = "customfield_19201"
    MAX_DL: str = "customfield_19400"
    MAX_UL: str = "customfield_19401"
    PING_LOSS: str = "customfield_19402"
    XPU_VERSION: str = "customfield_19404"
    AUTOMATION_FILE_NAME: str = "customfield_19406"
    CORE_FILE_NAMES: str = "customfield_19502"
    GROUP_NAME: str = "customfield_19601"
    TEST_CYCLE_ID: str = "customfield_20700"
    TEST_SETUP_TYPE: str = "customfield_20802"

    def print_sorted_constructor_by_value(self):
        # sourcery skip: identity-comprehension
        fields_constructor_dict = {k: v for k, v in sorted(self.__dict__.items(), key=lambda item: item[1])}
        print(
            f'fields_constructor is:\n'
            f'{json.dumps(fields_constructor_dict, indent=2, separators=(", ", " = "))}'
            f'\n'
        )


def get_full_field_list(*args):
    return list(args) + sorted(list(IssueFieldsConstructor().__dict__.values()))


def get_basic_field_list(*args):
    return sorted(
        list(args) + [
            "assignee",
            "created",
            "description",
            "fixVersions",
            "issuelinks",
            "key",
            "labels",
            "project",
            "reporter",
            "summary",
            "status",
            "updated",
            "versions"
        ]
    )


if __name__ == '__main__':
    issue_fields_constructor_fn = IssueFieldsConstructor()
    print()
    issue_fields_constructor_fn.print_sorted_constructor_by_value()

    fields_dict = issue_fields_constructor_fn.__dict__
    fields_asdict = asdict(issue_fields_constructor_fn)

    fields_dict_list = list(fields_dict.values())
    fields_asdict_list = list(fields_asdict.values())

    print()
