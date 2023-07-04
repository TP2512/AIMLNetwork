import hashlib

from InfrastructureSVG.Jira_Infrastructure.OpenObject.OpenObject_Infrastructure import CreateObjectOnJira
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger

jira_client = JiraActions(app_credentials='CoreCare')


def replace_to_hash(back_trace):
    """ Convert "Back Trace" to hash """

    try:
        # four_last_bt_list = back_trace.split(' -> ')[-4:]
        four_last_bt_list = back_trace.split(' -> ')[:4]
        print(four_last_bt_list)
        hash_object = hashlib.md5(str(four_last_bt_list).encode('utf-8'))
        hex_string = f'0x{hash_object.hexdigest()}'
        hex_int = int(hex_string, 16)
        new_int = abs(hex_int % (10 ** 8))
        back_trace_hash = str(new_int)
    except Exception:
        back_trace_hash = None

    return back_trace_hash


def update_hash_bt_on_defect(issue_id, summary, labels):
    """ Update "HashBT" """

    update_defect_data = {
        'set': [
            {'summary': [f'{summary}']},  # Hash BT
            {'labels': labels},  # Hash BT
        ],
        'add': []
    }

    jira_client.update_issue(issue_id=issue_id, data=update_defect_data)


def update_hash_bt_on_epic_core(issue_id, back_trace_hash):
    """ Update "HashBT" """

    update_defect_data = {
        'set': [
            {'customfield_18301': [f'{back_trace_hash}']},  # Hash BT
            {'labels': [f'{back_trace_hash}']},  # Hash BT
        ],
        'add': []
    }

    jira_client.update_issue(issue_id=issue_id, data=update_defect_data)


# sourcery no-metrics
if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    #

    create_object_on_jira = CreateObjectOnJira(jira_client=jira_client)

    # jira_filter_epic = 'project = CORE AND issuetype = Epic AND id = CORE-73547'
    jira_filter_epic = 'project = CORE AND issuetype = Epic AND created >= 2022-04-26 AND created <= 2022-05-23 AND reporter in (CoreCare-5G) ORDER BY created DESC'
    epic_list = create_object_on_jira.automation_helper.get_by_filter(str_filter=jira_filter_epic)
    for epic in epic_list:
        if "BT[" in epic.fields.summary:
            print('\n\n\n###################')
            print(f'Epic is: {epic}')
            print('-------------------\n')

            hash_bt_set = set()

            jira_filter_core = f'project = CoreCare AND issuetype = Core AND "Epic Link" = {epic} AND reporter in (CoreCare-5G) ORDER BY created DESC'
            core_list = create_object_on_jira.automation_helper.get_by_filter(str_filter=jira_filter_core)
            for index, core in enumerate(reversed(core_list), start=0):
                if "BT[" in core.fields.description:
                    print(f'Core is: {core}')

                    bt = f' -> BT[{core.fields.description.split("BT[", 1)[1]}'.replace('\n', ' -> ').split("{code}")[0]
                    back_trace_hash_ = replace_to_hash(bt)
                    hash_bt_set.add(back_trace_hash_)
                    # if back_trace_hash_ == core.fields.customfield_18301:
                    #     continue

                    if index == 0:
                        print(f'update Epic HashBT from {epic.fields.customfield_18301} to {back_trace_hash_}')
                        # update_hash_bt_on_epic_core(issue_id=epic.key, back_trace_hash=back_trace_hash_)

                        jira_filter_defect = f'project = "Defect Tracking" AND issuetype = Defect AND issue in linkedissues({epic}) ' \
                                             f'AND reporter in (CoreCare-5G) ORDER BY created DESC'
                        defect_list = create_object_on_jira.automation_helper.get_by_filter(str_filter=jira_filter_defect)
                        for defect in defect_list:
                            old_bt = defect.fields.summary.split('HashBT: [')[1].split(']', 1)[0]
                            summary = defect.fields.summary.replace(old_bt, back_trace_hash_)
                            labels = [i for i in defect.fields.labels if i != old_bt]
                            labels.append(back_trace_hash_)
                            # update_hash_bt_on_defect(issue_id=defect.key, summary=summary, labels=labels)
                    print(f'update Core HashBT from {core.fields.customfield_18301} to {back_trace_hash_}')
                    print()
                    # update_hash_bt_on_epic_core(issue_id=core.key, back_trace_hash=back_trace_hash_)
            if len(hash_bt_set) > 1:
                logger.error(f'xxx: {sorted(hash_bt_set)}')
            else:
                print(f'yyy: {sorted(hash_bt_set)}')
        print('######################################\n')
    print()
