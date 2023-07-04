import asyncio
import contextlib

from InfrastructureSVG.Jenkins_Infrastructure.Jenkins_Connection import JenkinsConnection
from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials
from pathlib import Path
import datetime
from datetimerange import DateTimeRange
from aioshutil import rmtree
from colorama import Fore

from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger

ROOT_PATH = '\\\\192.168.127.231\\AutomationResults\\old_runs'


class Cleaner:

    @staticmethod
    def get_jenkins_slaves():
        username, password = Credentials().credentials_per_app('jenkins')
        jenkins_agent = JenkinsConnection(baseurl='https://jenkins.airspan.labs/', username=username, password=password).jenkins_connection()
        return [j['name'] for j in jenkins_agent.get_nodes()]

    @staticmethod
    def get_time_range():
        now = datetime.datetime.now()
        three_month_range = now - datetime.timedelta(days=60)
        return DateTimeRange(three_month_range, now)

    @staticmethod
    def collect_paths(jenkins_slaves, time_range):
        tmp = []
        for slave in jenkins_slaves:
            path = Path(f'{ROOT_PATH}\\{slave}')
            if path.exists():
                if old_runs := [
                    x
                    for x in path.iterdir()
                    if x.is_dir()
                    and datetime.datetime.fromtimestamp(x.stat().st_ctime)
                    not in time_range
                ]:
                    tmp.extend(iter(old_runs))
        return tmp

    @staticmethod
    async def delete_old_runs(path_list):
        for path in path_list:
            print(f'{Fore.GREEN}Deleting old runs from {path}')
            with contextlib.suppress(PermissionError):
                await rmtree(path)


async def main():
    cleaner = Cleaner()
    path_l = cleaner.collect_paths(cleaner.get_jenkins_slaves(), cleaner.get_time_range())
    await cleaner.delete_old_runs(path_l)


if __name__ == '__main__':
    project_name, site = 'Old Runs Cleaner', 'IL SVG'
    print_before_logger(project_name=project_name, site=site)
    asyncio.run(main())
