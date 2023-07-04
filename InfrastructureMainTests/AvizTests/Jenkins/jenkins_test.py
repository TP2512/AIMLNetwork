from InfrastructureSVG.Jenkins_Infrastructure.Cancel_Queue import CancelQueue
from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials
from InfrastructureSVG.Jenkins_Infrastructure.Jenkins_Connection import JenkinsConnection

if __name__ == '__main__':
    # username, password = Credentials().credentials_per_app('EZlife')
    username, password = Credentials().credentials_per_app('spuser')
    jenkins_url = 'http://asil-sv-ez4u:8080/'

    jenkins_agent = JenkinsConnection(baseurl=jenkins_url, username=username, password=password).jenkins_connection()
    jenkins_modes = [j['name'] for j in jenkins_agent.get_nodes()]
    print(jenkins_modes)

    CancelQueue(jenkins=jenkins_agent).cancel_all_queue_for_all_setups_per_job_name(job_name='RobotFrameworkSVG', setup_name='ASIL-JAGUAR')

    print()
