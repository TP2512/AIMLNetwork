import logging
import os
from datetime import datetime, timezone


class GitActions:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.branch_name = 'master'
        self.repo_path = None

    def git_add_commit_push(self, commit_message=None):
        if not commit_message:
            commit_message = datetime.now(timezone.utc).strftime('%Y/%m/%d - %H:%M:%S')

        if self.repo_path:
            commands = f'cd "{self.repo_path}" && git add . && git commit -m "{commit_message}" && git push --all'
        else:
            commands = f'git add . && git commit -m "{commit_message}" && git push --all'
        os.system(commands)


if __name__ == '__main__':
    g = GitActions()
    g.git_add_commit_push()
