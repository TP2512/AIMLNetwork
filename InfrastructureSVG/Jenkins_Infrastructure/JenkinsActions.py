import logging


class JenkinsActions:
    def __init__(self, jenkins_agent):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jenkins_agent = jenkins_agent

    def get_nodes(self) -> list:
        return [j['name'] for j in self.jenkins_agent.get_nodes()]

    def get_jenkins_version(self):
        return self.jenkins_agent.get_version()


if __name__ == '__main__':
    from InfrastructureSVG.Jenkins_Infrastructure.Jenkins_Connection import JenkinsConnection
    from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials

    jenkins_url = 'https://jenkins.airspan.labs'
    username, password = Credentials().credentials_per_app('jenkins')

    jenkins_agent = JenkinsActions(
        jenkins_agent=JenkinsConnection(baseurl=jenkins_url, username=username, password=password).jenkins_connection()
    )

    jenkins_version = jenkins_agent.get_jenkins_version()
    print(jenkins_version)

    print()
