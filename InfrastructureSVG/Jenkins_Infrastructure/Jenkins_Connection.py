import logging
import os

import jenkins  # pip install python-jenkins
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.requester import Requester

from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials


class JenkinsConnection:
    def __init__(self, baseurl, username, password):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.baseurl = baseurl
        self.username = username
        self.password = password

    def jenkins_connection(self):
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        jenkins_agent = jenkins.Jenkins(
            self.baseurl,
            self.username,
            self.password,
        )

        jenkins_agent.get_nodes()
        return jenkins_agent

    def jenkins_connection2(self):
        return Jenkins(
            self.baseurl,
            self.username,
            self.password,
            requester=Requester(
                self.username,
                self.password,
                ssl_verify=False
            )
        )


def main(jenkins_url, username, password):
    jenkins_agent = JenkinsConnection(baseurl=jenkins_url, username=username, password=password).jenkins_connection()
    print(jenkins_agent.get_whoami())
    print(jenkins_agent.get_jobs())
    print()


if __name__ == '__main__':
    _jenkins_url = 'https://jenkins.airspan.labs'
    _username, _password = Credentials().credentials_per_app('jenkins')

    main(jenkins_url=_jenkins_url, username=_username, password=_password)
