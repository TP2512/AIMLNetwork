# def create_defect2(self, defect_obj: Union[JiraParameters, Defect]):
#     defect_data = [
#         # Required fields
#         {'reporter': [f'{self.username}']},  # reporter
#         {'assignee': [f'{defect_obj.assignee}']},  # assignee
#         {'summary': [f'{defect_obj.summary}'[-254:]]},  # summary
#         {'customfield_10736': [{'value': f'{defect_obj.site.split(" ")[0]}', 'child': f'{defect_obj.site.split(" ")[1]}'}]},  # Discovery Site / Customer
#         {'customfield_10200': [f'SR{defect_obj.entity_version.split("-", 1)[0]}']},  # Reported In Release (eNB)
#         {'customfield_10202': [f'{defect_obj.product_at_fault}']},  # product at fault
#         {'customfield_10800': [f'{defect_obj.bs_hardware_type}']},  # BS Hardware Type
#         # {'customfield_10201': [f'{self.get_reproducibility_frequency()}']},  # Reproducibility/Frequency
#         {'customfield_10201': [f'Always']},  # Reproducibility/Frequency
#         {'customfield_10406': [f'{defect_obj.severity}']},  # Severity
#
#         # Other fields
#         {'versions': [f'SR{defect_obj.entity_version.split("-", 1)[0]}']},  # Affects Version/s
#         {'fixVersions': [f'SR{defect_obj.entity_version.split("-", 1)[0]}']},  # SR Versions
#         {'customfield_13300': defect_obj.customer_name},  # Customer name
#         {'customfield_10731': [f'{defect_obj.ems_type}']},  # EMS Type
#         # {'customfield_10726': [f'{defect_obj.entity_version}']},  # eNB /CD/DU - SW
#         {'customfield_10737': [f'{defect_obj.ems_software_version}']},  # EMS Software Version
#         {'description': [f'{defect_obj.description}']},  # description
#         {'customfield_11449': [f'{defect_obj.impact}']},  # Defect Impact
#         {'customfield_10712': [{'value': 'Stability 2 Ues', 'child': 'small automation setups'}]},  # Defect Module / Sub-feature
#         {'customfield_10704': [f'{defect_obj.frequency_band}']},  # Frequency Band
#         {'customfield_10734': [f'{defect_obj.bandwidth}']},  # Bandwidth
#         {'labels': defect_obj.labels},  # labels
#         {'customfield_11200': [f'TBD']},  # Showstopper
#         {'customfield_10975': [f'{defect_obj.notes}']},  # Notes
#         # Core Occurrence count
#         # Core SystemUpTime (min)
#         {'customfield_10715': [f'SR{defect_obj.entity_version.split("-", 1)[0]}']},  # Target Release
#         {'customfield_13707': [f'{defect_obj.entity_version}']},  # g/eNodeB SW version
#         # {'customfield_10725': [defect_obj.entity_version]},  # Last Occurred BS Software Version
#         {'customfield_18401': [f'{defect_obj.entity_version}']},  # Last Occurred GNB Versions
#         {'customfield_12682': [f'{defect_obj.linux_kernel}']},  # Linux Kernel
#         {'customfield_16800': [f'{defect_obj.cucp_version}']},  # 5G_CUCP_Ver
#         {'customfield_16801': [f'{defect_obj.cuup_version}']},  # 5G_CUUP_Ver
#         {'customfield_16200': [f'{defect_obj.du_version}']},  # 5G_DU_Ver
#         {'customfield_16203': [f'{defect_obj.ru_version}']},  # 5G_RU_Ver
#         {'customfield_11003': defect_obj.test_environments},  # test environments
#         #
#
#         # {'customfield_15000': [self.get_last_version_core_occurrence_count_by_filter(defect_obj.entity_version)]},  # Occurrence count
#         # {'customfield_14801': [self.get_core_system_uptime_min(defect_obj.entity_version)]},  # Core SystemUpTime (min)
#         # {'customfield_14803': [self.get_core_system_uptime_for_defect(defect_obj.entity_version)]},  # core system uptime
#
#         # {'customfield_14803': [f'{self.get_core_system_uptime()}']},  # core system uptime
#         # {'customfield_14803': [self.get_core_system_uptime_for_defect(defect_obj.entity_version)]},  # core system uptime
#         # {'customfield_14801': [int(self.get_system_runtime_minutes())]},  # Core SystemUpTime (min)
#         # {'customfield_14801': [self.get_core_system_uptime_min(defect_obj.entity_version)]},  # Core SystemUpTime (min)
#
#     ]
#     defect = self.jira_client.create_issue(project='DEF', issue_type='Defect', data=defect_data)
#
#     if defect:
#         self.logger.info(f'Defect was created')
#         self.logger.info(f'Defect key is: {defect}\n')
#         self.update_defect_after_created()
#     else:
#         self.logger.error(f'Defect was not created')
#
#     return defect


