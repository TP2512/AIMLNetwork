import time
import pandas as pd

from InfrastructureSVG.EZLife.EZLifeTolls.EZLifeAndJira.EZLifeAndJira import EZLifeJira


def main(ezlife_jira_fn):
    path = _ezlife_jira_fn.global_class_and_functions.read_from_user_fn.read_str(question='Enter your csv path: '),
    # path = 'output\\ue_output.csv',

    _error_ues = []

    ue_dataframe = pd.read_csv(path)
    ue_dataframe.drop(columns='id', inplace=True)

    ue_exist_list = []
    for index, row in ue_dataframe.iterrows():
        status_code, setup_obj = ezlife_jira_fn.ezlife_method.ezlife_get.get_by_url(url=f'{ezlife_jira_fn.ezlife_method.base_url}/SetupApp/{row["setup"]}')
        if f'_[{setup_obj[0]["name"]}]' not in row["name"]:
            row["name"] = f'{row["name"]}_[{setup_obj[0]["name"]}]'

        status_code, obj = ezlife_jira_fn.ezlife_method.ezlife_get.get_by_url(url=f'{ezlife_jira_fn.ezlife_method.base_url}/UeApp/?name={row["name"]}')
        if obj:
            ue_exist_list.append(row["name"])

    if ue_exist_list:
        existing_ues = "\n".join(ue_exist_list)
        raise Exception(f'Some UEs are already exist:\n\n{existing_ues}\n')

    for index, row in ue_dataframe.iterrows():
        try:
            status_code, setup_obj = ezlife_jira_fn.ezlife_method.ezlife_get.get_by_url(url=f'{ezlife_jira_fn.ezlife_method.base_url}/SetupApp/{row["setup"]}')
            if f'_[{setup_obj[0]["name"]}]' not in row["name"]:
                row["name"] = f'{row["name"]}_[{setup_obj[0]["name"]}]'

            row['imsi'] = int(row.to_dict()['imsi'])
            status_code, ue_obj = ezlife_jira_fn.ezlife_method.ezlife_post.create_ue(data=row.to_dict())
            if status_code not in [200, 201]:
                if ue_obj.text:
                    logger.error(ue_obj.text)
                raise Exception('UE object was not created')
        except Exception:
            logger.exception('')
            _error_ues.append(row.to_dict()['name'])

    if _error_ues:
        error_ues = "\n".join(_error_ues)
        logger.error(f'The following UEs was not created: {error_ues}')


if __name__ == '__main__':
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger

    project_name, site = 'Import UEs From CSV', 'IL SVG'
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=True)

    _ezlife_jira_fn = EZLifeJira()

    try:
        main(
            ezlife_jira_fn=_ezlife_jira_fn,
        )
    except Exception:
        logger.exception('')
        time.sleep(0.2)

    _ = _ezlife_jira_fn.global_class_and_functions.read_from_user_fn.read_str(question='Press Enter to exit.')
