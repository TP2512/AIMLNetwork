import os
import sys
import time
import logging


class GitHubReleasesVersion:
    def __init__(self, version):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.venv_activate_command = f'{os.path.join(os.path.dirname(sys.executable))}\\activate.bat'
        self.version = version

    def execute_command_via_venv(self, command):
        os.system(f'{self.venv_activate_command} & {command}')

    def create_git_tag(self):
        command = f'git tag {self.version}'
        self.execute_command_via_venv(command)

    def git_push_version(self):
        command = f'git push origin {self.version}'
        self.execute_command_via_venv(command)

    def delete_git_tag(self):
        command = f'git tag -d {self.version}'
        self.execute_command_via_venv(command)

    def delete_git_push(self):
        command = f'git push origin --delete {self.version}'
        self.execute_command_via_venv(command)


if __name__ == '__main__':
    infrastructure_svg_version = 'v2.31.0'
    github_releases_version = GitHubReleasesVersion(version=infrastructure_svg_version)

    github_releases_version.delete_git_tag()
    github_releases_version.delete_git_push()
    time.sleep(1)
    github_releases_version.create_git_tag()
    github_releases_version.git_push_version()

    print()
