import logging
from github import Github
import github3


class GithubActions:
    def __init__(self, repository_name=None):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.token = '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'

        self.github_client = None
        self.owner = 'airspansvg'
        self.repository_name = repository_name or 'RobotFrameworkSVG'
        self.repository_details = None

        self.release_details = []

    def login_to_github(self):
        self.github_client = Github(self.token)

    def get_repository_details(self):
        self.repository_details = self.github_client.get_repo(f'{self.owner}/{self.repository_name}')

    def get_release_details(self):
        self.release_details = self.repository_details.get_releases()

    def get_release_list(self):
        self.get_release_details()
        return [release.title for release in self.release_details]

    def get_latest_release(self):
        self.get_release_details()
        for release in self.release_details:
            # print(f'title is: {release.title}')
            # print(f'prerelease is: {release.prerelease}')
            if not release.prerelease and not release.draft:
                return release.title

    def login_to_github2(self):
        self.github_client = github3.login(token=self.token)

    def get_repository_details2(self):
        self.repository_details = self.github_client.repository(owner=self.owner, repository=self.repository_name)

    def get_get_release_details2(self):
        self.release_details = self.repository_details.tags()

    def get_release_list2(self):
        self.login_to_github2()
        self.get_repository_details2()
        self.get_get_release_details2()
        return [release.name for release in self.release_details]


if __name__ == '__main__':
    github_actions = GithubActions()

    github_actions.login_to_github()
    github_actions.get_repository_details()
    print(f'release list is: {github_actions.get_release_list()}')
    print(f'latest release is: {github_actions.get_latest_release()}')
    releases_dict = {
        'release_list': github_actions.get_release_list(),
        'latest_release': github_actions.get_latest_release(),
    }
    print(f'releases_dict is: {releases_dict}')
    print()

    github_actions.login_to_github2()
    github_actions.get_repository_details2()
    print(f'release list 2 is: {github_actions.get_release_list2()}')
    print()
