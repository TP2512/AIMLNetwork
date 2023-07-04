import time
import pandas as pd

from InfrastructureSVG.EZLife.EZLifeTolls.EZLifeAndJira.EZLifeAndJira import EZLifeJira


def main(ezlife_jira_fn, index_list, save_in_path, file_name='ue_output.csv', list_ignor=None):
    if not list_ignor:
        list_ignor = []

    ue_object_list = []
    for index in index_list:
        status_code, obj = ezlife_jira_fn.ezlife_method.ezlife_get.get_by_url(url=f'{ezlife_jira_fn.ezlife_method.base_url}/UeApp/{index}/')
        ue_object_list.extend(
            [{k: [v['id']] if type(v) is dict else [v] for k, v in obj[0].items() if k not in list_ignor} for _ in obj]
        )

    ue_dataframe = pd.DataFrame()
    for ue_object in ue_object_list:
        ue_dataframe = pd.concat([ue_dataframe, pd.DataFrame.from_dict(ue_object)])

    ue_dataframe.to_csv(f'{save_in_path}\\{file_name}', index=False)


if __name__ == '__main__':
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger

    project_name, site = 'Export UEs To CSV', 'IL SVG'
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=True)

    list_ignor_ = [
        'en_dis',
        'created_at',
        'updated_at',
        'ue_hardware_type_upload_file',

        'rack_switch',
        'serial_terminal',
        'snmp_managed_devices'
    ]

    _ezlife_jira_fn = EZLifeJira()
    try:
        main(
            ezlife_jira_fn=_ezlife_jira_fn,
            index_list='1',
            save_in_path='output',
            file_name='ue_output.csv',
            list_ignor=list_ignor_,
        )
    except Exception:
        logger.exception('')
        time.sleep(0.2)
    _ = _ezlife_jira_fn.global_class_and_functions.read_from_user_fn.read_str(question='Press Enter to exit.')
