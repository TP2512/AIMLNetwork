import requests
from InfrastructureSVG.Jira_Infrastructure.App_Credentials.App_Credentials import Credentials
import logging


class DeletePageClass:
    user, password = Credentials().credentials_per_app('Dashboard_old')

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def delete_page(self, title, user, password):
        check_page_exists_data = requests.get(f"http://confluence-internal:8090/rest/api/content?title={title}&expand=history", headers={'Content-Type': 'application/json'}, auth=(user, password))

        request_json = check_page_exists_data.json()
        if request_json["results"] is not None:
            for results in request_json["results"]:
                page_id = (results["id"])
                requests.delete(f"http://confluence-internal:8090/rest/api/content/{page_id}", headers={'Content-Type': 'application/json'}, auth=(user, password))

        else:
            self.logger.info('Page does not exist')

    def clean_pages_from_space(self, confluence, space_key):
        """
        Remove all pages from trash for related space
        :param confluence:
        :param space_key:
        :return:
        """
        limit = 500
        flag = True
        step = 0
        while flag:
            values = confluence.get_all_pages_from_space_trash(space=space_key, start=0, limit=limit)
            step += 1
            if len(values) == 0:
                flag = False
                self.logger.info(f"For space {space_key} trash is empty")
            else:
                for value in values:
                    self.logger.info(value['title'])
                    confluence.remove_page_from_trash(value['id'])
