import logging

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger
from InfrastructureSVG.Jira_Infrastructure.Update_Create_Issues.New_Jira_Infra import JiraActions
from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import get_basic_field_list


class GetSubTaskS:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jira_client = JiraActions(app_credentials='EZlife')

    @staticmethod
    def get_param(sub_task):
        if sub_task.fields.customfield_10800:
            bs_hardware_type = sub_task.fields.customfield_10800[0].value
        else:
            bs_hardware_type = None

        if sub_task.fields.customfield_16900:
            numerology_scs = sub_task.fields.customfield_16900[0].value
        else:
            numerology_scs = None

        if sub_task.fields.customfield_17300:
            format_ssf = sub_task.fields.customfield_17300[0].value
        else:
            format_ssf = None

        if sub_task.fields.customfield_10511:
            band = sub_task.fields.customfield_10511.value
        else:
            band = None

        if sub_task.fields.customfield_10513:
            bw = sub_task.fields.customfield_10513.value
        else:
            bw = None

        return {
            'key': sub_task.key,
            'summary': sub_task.fields.summary,
            'bs_hardware_type': bs_hardware_type,
            'numerology_scs': numerology_scs,
            'format_ssf': format_ssf,
            'band': band,
            'bw': bw,
            'ezlife_summary': f'{sub_task.key} - {sub_task.fields.customfield_10800[0].value if sub_task.fields.customfield_10800 else None}',
            # 'TP QAM config': sub_task_client.fields.customfield_16000,
            'sub_task_key': sub_task.key,
        }

    def get_sub_tasks_dict(self, env_config_name):
        cucp_sub_tasks_dict = []
        cuup_sub_tasks_dict = []
        du_sub_tasks_dict = []
        ru_sub_tasks_dict = []
        other_device_sub_tasks_dict = []

        # self.jira_client.get_issue(env_config_name)
        # env_config_obj = self.jira_client.issues[env_config_name].issue
        env_config_obj = self.jira_client.search_by_filter(str_filter=f'issuekey = {env_config_name}', fields=['summary', 'subtasks'])[0]

        if not hasattr(env_config_obj.fields, 'subtasks'):
            return '"subtasks" is no hasattr'

        sub_task_filter = f'project = SVGA AND issuetype = Sub-task AND parent = "{env_config_name}"'
        sub_task_list = self.jira_client.search_by_filter(str_filter=sub_task_filter, fields=get_basic_field_list(
            'customfield_10800',  # bs_hardware_type
            'customfield_16900',  # numerology_scs
            'customfield_17300',  # format_ssf
            'customfield_10511',  # band
            'customfield_10513',  # bw
            'customfield_10202',  # Product At Fault
        ))

        env_config_dict = {
            'summary': env_config_obj.fields.summary
        }

        for sub_task in sub_task_list:
            sub_task_name = sub_task.fields.customfield_10202.value

            if sub_task_name == 'vCU-CP':
                cucp_sub_tasks_dict.append(self.get_param(sub_task))
            elif sub_task_name == 'vCU-UP':
                cuup_sub_tasks_dict.append(self.get_param(sub_task))
            elif sub_task_name == 'vDU':
                du_sub_tasks_dict.append(self.get_param(sub_task))
            elif sub_task_name in ['RU', 'RIU-D']:
                ru_sub_tasks_dict.append(self.get_param(sub_task))
            else:
                other_device_sub_tasks_dict.append(self.get_param(sub_task))

        response_tmp = {
            'env_config_dict': env_config_dict,
            'cucp_sub_tasks': cucp_sub_tasks_dict,
            'cuup_sub_tasks': cuup_sub_tasks_dict,
            'du_sub_tasks': du_sub_tasks_dict,
            'ru_sub_tasks': ru_sub_tasks_dict,
            'other_device_sub_tasks': other_device_sub_tasks_dict
        }
        return dict(response_tmp)


if __name__ == '__main__':
    PROJECT_NAME = 'Jira'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    get_sub_tasks_ins = GetSubTaskS()
    res = get_sub_tasks_ins.get_sub_tasks_dict(env_config_name='SVGA-6')

    print()
