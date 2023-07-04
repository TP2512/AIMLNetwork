import re
import socket
import requests
from jenkinsapi.jenkins import Jenkins
# import jenkins  # pip install python-jenkins

if __name__ == '__main__':
    hostname = socket.gethostname()
    url = 'asil-sv-ez4u'
    port = '8080'
    username = 'spuser'
    token = '113bdc6f51d20873a68b7f46f15f8a3238'

    jenkins_agent = Jenkins(baseurl=f'http://{url}:{port}', username=username, password=token)

    jenkins_agent.create_node(name=hostname, num_executors=1, remote_fs='c:\\jenkins')
    if hostname in jenkins_agent.nodes.keys():
        jenkins_requests = requests.get(f'http://{username}:{token}@{url}:{port}/computer/{hostname}/')
        if jenkins_requests.status_code in [200, 201]:
            jenkins_requests_text = jenkins_requests.text

            secret_file_regex = r'(?<=echo )(.*)(?= > secret-file)'
            secret_file = re.search(secret_file_regex, jenkins_requests_text, re.I).group()
            print(f' The secret_file is: {secret_file}')

            with open('path', 'w') as f:
                f.write(f"""
echo Connect to Jenkins

java -jar C:\\jenkins\\agent.jar -jnlpUrl http://{url}:{port}/computer/{hostname}/jenkins-agent.jnlp -secret {secret_file} -workDir "C:\\jenkins"

PAUSE
                """)
        else:
            print(f'status_code is: {jenkins_requests.status_code}')
    else:
        print(f'The hostname "{hostname} not exist')

    print()
