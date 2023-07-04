from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials
from InfrastructureSVG.Jenkins_Infrastructure.Jenkins_Connection import JenkinsConnection
# from InfrastructureSVG.Jenkins_Infrastructure.Cancel_Queue import CancelQueue

# curl http://asil-sv-ez4u:8080/job/RobotFrameworkSVG/buildWithParameters --user spuser:113bdc6f51d20873a68b7f46f15f8a3238
# --data "SLAVE=ASIL-JAGUAR&TEST_PLAN=SVGA-6585&SELECTED_TESTS=2

if __name__ == '__main__':
    job_name = 'RobotFrameworkSVG'
    jenkins_url = 'http://asil-sv-ez4u:8080'
    username, password = Credentials().credentials_per_app('spuser')

    node_name = 'ASIL-JAGUAR'

    jenkins = JenkinsConnection(baseurl=jenkins_url, username=username, password=password).jenkins_connection()

    build_id = None
    for build_obj in jenkins.get_job_info(job_name)['builds']:
        build_id = build_obj['number']

        if jenkins.get_build_info(job_name, build_id)['building'] and jenkins.get_build_info(job_name, build_id)['builtOn'] == node_name:
            print(f'Build id is: {build_id} and the Slave name is: {node_name}')
            break

    print()
    if job_name and build_id:
        jenkins.stop_build(job_name, build_id)

    print()
