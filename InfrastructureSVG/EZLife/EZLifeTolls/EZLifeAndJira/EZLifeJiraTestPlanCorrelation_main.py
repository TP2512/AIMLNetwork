import json

from InfrastructureSVG.EZLife.EZLifeTolls.EZLifeAndJira.EZLifeAndJira import EZLifeJiraTestPlanCorrelation


def print_jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict():
    ezlife_fn = EZLifeJiraTestPlanCorrelation()

    jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict = ezlife_fn.get_jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter()
    logger.info(json.dumps(jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict, indent=4, sort_keys=True))


def print_tree_ezlife_not_exist_on_jira_test_plan_list_per_reporter_dict():
    ezlife_fn = EZLifeJiraTestPlanCorrelation()

    jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict = ezlife_fn.get_ezlife_tree_test_plan_list_not_exist_on_jira()
    logger.info(json.dumps(jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict, indent=4, sort_keys=True))


if __name__ == '__main__':
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger

    project_name, site = 'EZLifeJira', 'IL'
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    # print_jira_test_plan_list_not_exist_on_tree_ezlife_per_reporter_dict()
    print_tree_ezlife_not_exist_on_jira_test_plan_list_per_reporter_dict()
