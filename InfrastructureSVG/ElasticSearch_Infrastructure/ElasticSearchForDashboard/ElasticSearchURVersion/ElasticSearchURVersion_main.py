import time

from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchForDashboard.ElasticSearchURVersion.ElasticSearchURVersion import ElasticSearchURVersion


def main(ur_version):
    logger.info('Start the process\n\n')

    fill_ur_version_on_elk = ElasticSearchURVersion()
    time.sleep(1)

    try:
        fill_ur_version_on_elk.delete_automation_and_manual_ur_version(
            ur_version=ur_version.replace('.', '_')
        )
    except Exception:
        logger.exception('exception in function "delete_automation_and_manual_ur_version"')

    try:
        existing = fill_ur_version_on_elk.get_existing_docs(
            ur_version=ur_version.replace('.', '_')
        )
        list_of_existing_docs = [i['_source'] for i in existing.hits.hits._l_]
        set_list_of_existing_docs = {i['execute_environment_config_and_test_sir'] for i in list_of_existing_docs if 'None' not in i['execute_environment_config_and_test_sir']}
        set_list_of_existing_docs = {i['execute_environment_config_and_test_sir'] for i in list_of_existing_docs}
    except Exception:
        logger.exception('exception in function "delete_automation_and_manual_ur_version"')
        set_list_of_existing_docs = None

    try:
        fill_ur_version_on_elk.build_new_ur_version_on_elk(
            ur_version=ur_version,
            manual=False,
            set_list_of_existing_docs=set_list_of_existing_docs
        )
    except Exception:
        logger.exception('exception in function "build_new_ur_version_on_elk"')

        time.sleep(1)


if __name__ == '__main__':
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import BuildLogger, print_before_logger

    PROJECT_NAME = 'ELK Add and Delete Automation and Manual UR Version'
    site = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=site)
    logger = BuildLogger(project_name=PROJECT_NAME, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    time.sleep(1)
    print('\n#####################################################')
    print('PAY ATTENTION !!!')
    print('You Must To Be Connecting To Net 60 (172.20.63.0) !!!')
    print('#####################################################\n')

    # _ur_version = 'SVG_SR19.50_UR1'
    # _ur_version = 'SR20.00 GA'
    # _ur_version = 'SR19.50_UR1'
    # _ur_version = 'SVG_SR20.00 GA'
    _ur_version = 'SR20.00 GA'
    if not _ur_version:
        _ur_version = input('Please enter the relevant UR version: ')

    main(ur_version=_ur_version)

    # _ = input('\n\n\nPlease press enter to exit')
