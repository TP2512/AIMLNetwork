from InfrastructureSVG.EZLife.EZLifeTolls.EZLifeAndJira.EZLifeAndJira import EZLifeJira


def main():
    ezlife_jira_fn = EZLifeJira()

    ezlife_url = f'{ezlife_jira_fn.ezlife_method_fn.ezlife_get.base_url}/TreeApp/?name&setup_name__name&test_plan'
    status_code, tree_obj_list = ezlife_jira_fn.ezlife_method_fn.ezlife_get.get_by_url(ezlife_url)
    logger.debug(f'status code is: {status_code}')

    for tree_obj in tree_obj_list:
        test_plan = f"{tree_obj['test_plan']}"
        setup_name = f"{tree_obj['setup_name__name']}"

        try:
            if tree_obj['test_plan']:
                logger.info(f'{test_plan} - {setup_name}')
                test_plan_obj = ezlife_jira_fn.jira_client.search_by_filter(
                    str_filter=f'key = {test_plan}',
                    fields=ezlife_jira_fn.global_parameters.field_list
                )
                if test_plan_obj and setup_name not in test_plan_obj[0].fields.customfield_11003:
                    update_data = {
                        'set': [
                            {'customfield_11003': [f'{setup_name}']},  # test environments
                        ],
                        'add': []
                    }
                    ezlife_jira_fn.jira_client.update_issue(issue_id=test_plan_obj[0].key, data=update_data)
        except Exception as err:
            logger.exception('')
            logger.debug(test_plan)


if __name__ == '__main__':
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger

    project_name, site = 'Test', 'IL SVG'
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    main()
