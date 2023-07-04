from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.OpenObject.JiraDataClass_Infrastructure import JiraParameters
from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger


def process(jira_client, jira_parameters_obj: JiraParameters):
    create_object_on_jira = CreateObjectOnJira(jira_client=jira_client)

    # Initialization process and Data
    print('Initialization process and Data')

    # Real process
    jira_parameters_obj.labels.append(jira_parameters_obj.hash_bt)
    if epic := create_object_on_jira.corecare_helper.found_epic(type_crash_name=jira_parameters_obj.product_at_fault, back_trace_hash=jira_parameters_obj.hash_bt):
        create_object_on_jira.update_epic(epic=epic, epic_obj=jira_parameters_obj)
    else:
        epic = create_object_on_jira.create_epic(epic_obj=jira_parameters_obj, summary=jira_parameters_obj.back_trace)

    core = create_object_on_jira.create_core(core_obj=jira_parameters_obj, summary=jira_parameters_obj.back_trace)
    create_object_on_jira.create_link_between_core_and_epic(epic=epic, core=core)
    create_object_on_jira.update_epic_core_occurrence_count(epic=epic)

    print()

    if 'Customer' in jira_parameters_obj.site:
        jira_parameters_obj.site = f"Customer {jira_parameters_obj.customer_name}"

    if defect := create_object_on_jira.corecare_helper.found_defect(epic=epic):
        defect_summary = create_object_on_jira.corecare_helper.update_summary_for_defect(defect=defect, jira_parameters_obj=jira_parameters_obj, epic=epic)
        create_object_on_jira.update_defect(defect=defect, defect_obj=jira_parameters_obj, summary=defect_summary, epic=epic, core=core)
        print()
    elif create_object_on_jira.check_if_need_to_create_new_defect_for_corecare(epic=epic, entity_type_name=jira_parameters_obj.product_at_fault,
                                                                               current_ver=jira_parameters_obj.entity_version):
        defect_summary = create_object_on_jira.corecare_helper.build_summary_for_defect(jira_parameters_obj=jira_parameters_obj, epic=epic)
        defect = create_object_on_jira.create_defect(defect_obj=jira_parameters_obj, summary=defect_summary, epic=epic)
        # create_object_on_jira.update_defect_document_reference_name(src_path=jira_parameters_obj.path, defect=defect)
        create_object_on_jira.create_link_between_defect_and_epic(defect=defect, epic=epic)
        print()
    else:
        create_object_on_jira.logger.info('Not need to create / update defect')

    print()


if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    jira_client_ = JiraActions(app_credentials='TestspanAuto')
    jira_parameters_obj_ = JiraParameters(
        print_as_json=True,
        site='IL SVG',
        # entity_version='19.00-271-0.0',
        entity_version='19.00-306-1.5',
        # entity_version='19.00-306-1.6',
        product_at_fault='DU',
        labels=['AvizTest', 'Created_by_Automation_Dev_SVG'],
        hash_bt='007',
        cucp_version='airspan_cu_19.00-125-0.0',
        cuup_version='airspan_cu_19.00-125-0.0',
        du_version='19.00-306-1.5',
        ru_version='airspan_A5G57_19_00-44-1_1',
    )
    process(jira_client_, jira_parameters_obj=jira_parameters_obj_)

    print()
