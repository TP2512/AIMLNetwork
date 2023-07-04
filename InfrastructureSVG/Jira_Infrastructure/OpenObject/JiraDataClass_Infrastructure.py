from dataclasses import dataclass, field
from typing import List
import json
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions


def get_schema_fields():
    jira_client = JiraActions(app_credentials='EZlife')
    return jira_client._jira_connection.createmeta(projectKeys=['DEF'], expand='projects.issuetypes.fields')['projects'][0]['issuetypes'][0]['fields']


def get_product_at_fault_allowed_values(schema_fields):
    return [i['value'] for i in schema_fields['customfield_10202']['allowedValues']]


def get_bs_hardware_type_allowed_values(schema_fields):
    return [i['value'] for i in schema_fields['customfield_10800']['allowedValues']]


def get_reproducibility_frequency_allowed_values(schema_fields):
    return [i['value'] for i in schema_fields['customfield_10201']['allowedValues']]


@dataclass()
class JiraParameters:
    """
        - set_default: bool = False,
            * Set "True" to fill default values in all Jira parameters
            * set "False" to fill required fields + relevant fields (will be filled only the parameters that will pass, other parameters will be "None")

        - print_as_json: bool = False,
            * Set "True" to print the "JiraParameters" as json

        - Under each parameter have a comment that represents  "customfield_name ; customfield_number"
        - Pay attention to Required fields
            * There is no default value:
                - site: str  # Discovery Site / Customer ; customfield_10736
                - entity_version: str

            * Have a default value:
                - assignee: str  # assignee ; assignee
                - summary: str  # summary ; summary
                - product_at_fault: str  # product at fault ; customfield_10202
                - bs_hardware_type: str  # BS Hardware Type ; customfield_10800
                - severity: str  # Severity ; customfield_10406
                - epic_name: str  # Epic Name ; customfield_10002
    """

    # Required fields
    site: str  # Discovery Site / Customer ; customfield_10736
    entity_version: str

    assignee: str = 'akimiagarov'  # assignee ; assignee
    summary: str = 'There is no summary'  # summary ; summary
    product_at_fault: str = 'Unknown'  # from allowed values  # product at fault ; customfield_10202
    bs_hardware_type: list = field(default_factory=lambda: ['undefined'])  # from allowed values  # BS Hardware Type ; customfield_10800
    severity: str = 'Unknown'  # Severity ; customfield_10406
    epic_name: str = None  # Epic Name ; customfield_10002

    # Additional fields
    print_as_json: bool = False
    set_default: bool = False

    description: str = ' ' if set_default else None  # description ; description
    labels: List = field(default_factory=lambda: [])  # labels ; labels
    defect_module_sub_feature: dict = {'value': 'Stability 2 Ues', 'child': 'small automation setups'} if set_default else None
    show_stopper: str = 'TBD' if set_default else None
    reproducibility_frequency: str = 'Always'  # from allowed values  # Reproducibility/Frequency ; customfield_10201
    frequency_band: str = 'N/A' if set_default else None  # Frequency Band ; customfield_10704
    ems_type: str = 'Unknown' if set_default else None  # EMS Type ; customfield_10731
    bandwidth: str = '-1' if set_default else None  # Bandwidth ; customfield_10734
    ems_software_version: str = ' ' if set_default else None  # EMS Software Version ; customfield_10737
    notes: str = ' ' if set_default else None  # Notes ; customfield_10975
    test_environments: list = field(default_factory=lambda: [])  # test environments ; customfield_11003
    impact: str = 'Service disruption' if set_default else None  # Defect Impact ; customfield_11449
    path: str = ' ' if set_default else None  # Path ; customfield_12600
    linux_kernel: str = ' ' if set_default else None  # Linux Kernel ; customfield_12682
    customer_name: list = field(default_factory=lambda: ['TBD'])  # from allowed values  # Customer name ; customfield_13300
    core_layer_type: str = None  # Core Layer Type ; customfield_14800
    core_system_uptime_min: int = 0 if set_default else None  # Core SystemUpTime (min) ; customfield_14801
    system_runtime: dict = field(default_factory=lambda: {'Hours': 0, 'Minutes': 0, 'Seconds': 1})  # CoreSysUpTime ; customfield_14803
    core_occurrence_count: int = -1 if set_default else None  # Occurrence count ; customfield_15000
    core_crashed_process: list = field(default_factory=lambda: [])  # Core Crashed Process ; customfield_15001
    core_customer_name: list = field(default_factory=lambda: [])  # Core Customer Name ; customfield_15900
    du_version: str = ' ' if set_default else None  # 5G_DU_Ver ; customfield_16200
    ru_version: str = ' ' if set_default else None  # 5G_RU_Ver ; customfield_16203
    cucp_version: str = ' ' if set_default else None  # 5G_CUCP_Ver ; customfield_16800
    cuup_version: str = ' ' if set_default else None  # 5G_CUUP_Ver ; customfield_16801
    hash_bt: str = ' ' if set_default else None  # Hash BT ; customfield_18301
    back_trace: str = 'There is no BT' if set_default else None
    crash_pid: list = field(default_factory=lambda: [])  # Crash PID ; customfield_18302
    last_occurred_gnb_versions: list = field(default_factory=lambda: [])  # Last Occurred GNB Versions ; customfield_18401

    # Additional general fields
    fix_versions: List = field(default_factory=lambda: ['unknown'])  # from allowed values
    g_enodeb_sw_version: list = field(default_factory=lambda: [])
    core_sys_uptime: list = field(default_factory=lambda: ['N/A'])  # from allowed values
    actual: str = ' ' if set_default else None
    expected: str = ' ' if set_default else None

    # _schema_fields: dict = field(init=False, repr=False, default_factory=lambda: get_schema_fields())
    _schema_fields: dict = field(init=False, repr=False, default_factory=dict)

    # core_layer_type: str = None

    # def __init__(self, *args, **kwargs):
    #     self.kwargs = {}
    #     self.args = []
    #     names = set([f.name for f in dataclasses.fields(self)])
    #
    #     for k, v in kwargs.items():
    #         if k in names:
    #             setattr(self, k, v)
    #         else:
    #             self.kwargs[k] = v
    #
    #     for v in args:
    #         setattr(self.args, v)
    #     print()

    def __post_init__(self):
        if not self.epic_name:
            self.epic_name: str = self.summary
        self._schema_fields = get_schema_fields()  # New function
        self.product_at_fault = self.get_product_at_fault()
        self.bs_hardware_type = self.get_bs_hardware_type()
        self.reproducibility_frequency = self.get_reproducibility_frequency()
        self.sr_version = f'SR{self.entity_version.split("-", 1)[0]}' if len(self.entity_version.split("-", 1)) > 1 else 'Unknown'

        if self.print_as_json:
            print(f'Jira Parameters:\n{json.dumps(self.__dict__, default=lambda _schema_fields: "<not serializable>", indent=2, separators=(", ", " = "))}\n')

    def get_product_at_fault(self):
        if self.product_at_fault.upper() == 'CUCP':
            return 'vCU-CP'
        elif self.product_at_fault.upper() == 'CUUP':
            return 'vCU-UP'
        elif self.product_at_fault.upper() == 'DU':
            return 'vDU'
        elif self.product_at_fault.upper() == 'RU':
            return 'RU'
        elif self.product_at_fault in get_product_at_fault_allowed_values(self._schema_fields):
            return self.product_at_fault
        else:
            return 'Unknown'

    def get_bs_hardware_type(self):
        bs_hardware_type_list = [
            bs_hardware_type if bs_hardware_type in get_bs_hardware_type_allowed_values(self._schema_fields)
            else 'undefined'
            for bs_hardware_type in self.bs_hardware_type
        ]

        return bs_hardware_type_list or ['undefined']

    def get_reproducibility_frequency(self):
        if self.reproducibility_frequency in get_reproducibility_frequency_allowed_values(self._schema_fields):
            return self.reproducibility_frequency
        else:
            return 'Always'
