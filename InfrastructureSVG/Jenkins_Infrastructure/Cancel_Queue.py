import logging
import re
import time


class CancelQueue:
    def __init__(self, jenkins):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.jenkins = jenkins
        self.jobs = self.jenkins.get_all_jobs()
        self.queue_info = self.jenkins.get_queue_info()

    def cancel_all_queue_for_all_setups_per_job_name(self, job_name, setup_name):
        for j in self.jobs:
            if job_name == j['fullname']:
                for queue in self.queue_info:
                    slave_name = re.search(r'(?<=SLAVE=)(.*)(?=])', queue['params'], re.I).group()
                    if slave_name == setup_name:
                        queue_id = queue['id']
                        self.jenkins.cancel_queue(queue_id)
                        self.logger.info(f'The queue ({queue_id}) was canceled')
                        time.sleep(1)

    def cancel_all_queue_for_per_setup_per_job_name(self, job_name):
        for j in self.jobs:
            if job_name == j['fullname']:
                for queue in self.queue_info:
                    queue_id = queue['id']
                    self.jenkins.cancel_queue(queue_id)
                    self.logger.info(f'The queue ({queue_id}) was canceled')
                    time.sleep(1)

    def test(self, job_name):
        for j in self.jobs:
            if job_name == j['fullname']:
                last_build_number = self.jenkins.get_job_info(job_name)

                build_id = last_build_number['lastBuild']['number']
                self.logger.debug(f"The build id is: {build_id}")

                build_result = self.jenkins.get_build_info(job_name, build_id)['result']
                self.logger.debug(f"The build result is: {build_result}")

                build_status = self.jenkins.get_build_info(job_name, build_id)['building']
                self.logger.debug(f"The build status (active=True/not active=False) is: {build_status}")

                queue_id = self.jenkins.get_build_info(job_name, build_id)['queueId']
                self.logger.debug(f"The queue id (active=True/not active=False) is: {queue_id}")
