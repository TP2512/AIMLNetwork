# from dataclasses import dataclass, field
# from beartype.typing import List
# import json
# from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
#
#
# def get_schema_fields():
#     jira_client = JiraActions(app_credentials='Automation_Dev')
#     return jira_client._jira_connection.createmeta(projectKeys=['DEF'], expand='projects.issuetypes.fields')['projects'][0]['issuetypes'][0]['fields']
#
#
# def get_product_at_fault_allowed_values():
#     schema_fields = get_schema_fields()
#     return [i['value'] for i in schema_fields['customfield_10202']['allowedValues']]
#
#
# def get_bs_hardware_type_allowed_values():
#     schema_fields = get_schema_fields()
#     return [i['value'] for i in schema_fields['customfield_10800']['allowedValues']]
#
#
# @dataclass()
# class JiraParameters:  # customfield_name ; customfield_number
#     # required fields
#     site: str  # Discovery Site / Customer ; customfield_10736
#     entity_version: str
#
#     default: bool = field(repr=False, default=False)
#
#     assignee: str = 'akimiagarov'  # assignee ; assignee
#     summary: str = 'There is no summary'  # summary ; summary
#     product_at_fault: str = ''  # product at fault ; customfield_10202
#     bs_hardware_type: str = ''  # BS Hardware Type ; customfield_10800
#     severity: str = 'Unknown'  # Severity ; customfield_10406
#     epic_name: str = field(init=False, repr=True)  # Epic Name ; customfield_10002
#
#     # Additional fields
#     description2: str = None  # description ; description
#     description: str = ' ' if default else None  # description ; description
#     labels: List = field(default_factory=lambda: [''])  # labels ; labels
#
#     frequency_band: str = 'N/A'  # Frequency Band ; customfield_10704
#     ems_type: str = 'Unknown'  # EMS Type ; customfield_10731
#     bandwidth: str = '-1'  # Bandwidth ; customfield_10734
#     ems_software_version: str = ' '  # EMS Software Version ; customfield_10737
#     notes: str = ' '  # Notes ; customfield_10975
#     test_environments: list = field(default_factory=lambda: [''])  # test environments ; customfield_11003
#     impact: str = 'Service disruption'  # Defect Impact ; customfield_11449
#     path: str = ' '  # Path ; customfield_12600
#     linux_kernel: str = ' '  # Linux Kernel ; customfield_12682
#     customer_name: list = field(default_factory=lambda: ['TBD'])  # from allowed values  # Customer name ; customfield_13300
#     core_layer_type: str = None  # Core Layer Type ; customfield_14800
#     core_system_uptime_min: int = 0  # Core SystemUpTime (min) ; customfield_14801
#     system_runtime: dict = field(default_factory=lambda: {'Hours': 0, 'Minutes': 0, 'Seconds': 1})  # CoreSysUpTime ; customfield_14803
#     core_occurrence_count: str = -1  # Occurrence count ; customfield_15000
#     core_crashed_process: list = field(default_factory=lambda: [''])  # Core Crashed Process ; customfield_15001
#     core_customer_name: list = field(default_factory=lambda: [''])  # Core Customer Name ; customfield_15900
#     du_version: str = ' '  # 5G_DU_Ver ; customfield_16200
#     ru_version: str = ' '  # 5G_RU_Ver ; customfield_16203
#     cucp_version: str = ' '  # 5G_CUCP_Ver ; customfield_16800
#     cuup_version: str = ' '  # 5G_CUUP_Ver ; customfield_16801
#     hash_bt: str = ' '  # Hash BT ; customfield_18301
#     crash_pid: list = field(default_factory=lambda: [''])  # Crash PID ; customfield_18302
#     last_occurred_gnb_versions: list = field(default_factory=lambda: [''])  # Last Occurred GNB Versions ; customfield_18401
#
#     # Additional general fields
#     fix_versions: List = field(default_factory=lambda: ['unknown'])  # from allowed values
#     g_enodeb_sw_version: list = field(default_factory=lambda: [''])
#     core_sys_uptime: list = field(default_factory=lambda: ['N/A'])  # from allowed values
#
#     # core_layer_type: str = None
#
#     # def __init__(self, *args, **kwargs):
#     #     self.kwargs = {}
#     #     self.args = []
#     #     names = set([f.name for f in dataclasses.fields(self)])
#     #
#     #     for k, v in kwargs.items():
#     #         if k in names:
#     #             setattr(self, k, v)
#     #         else:
#     #             self.kwargs[k] = v
#     #
#     #     for v in args:
#     #         setattr(self.args, v)
#     #     print()
#
#     def __post_init__(self):
#         self.epic_name: str = self.summary
#         self.product_at_fault = self.get_product_at_fault()
#         self.bs_hardware_type = self.get_bs_hardware_type()
#
#         print(f'Jira Parameters:\n{json.dumps(self.__dict__, indent=2, separators=(", ", " = "))}\n')
#
#     def get_product_at_fault(self):
#         if self.product_at_fault.upper() == 'CUCP':
#             return 'vCU-CP'
#         elif self.product_at_fault.upper() == 'CUUP':
#             return 'vCU-UP'
#         elif self.product_at_fault.upper() == 'DU':
#             return 'vDU'
#         elif self.product_at_fault.upper() == 'RU':
#             return 'RU'
#         elif self.product_at_fault in get_product_at_fault_allowed_values():
#             return self.product_at_fault
#         else:
#             return 'Unknown'
#
#     def get_bs_hardware_type(self):
#         if self.bs_hardware_type in get_bs_hardware_type_allowed_values():
#             return self.product_at_fault
#         else:
#             return 'undefined'
