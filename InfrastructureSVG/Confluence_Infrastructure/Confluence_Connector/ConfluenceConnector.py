from atlassian import Confluence
import logging

from atlassian.errors import ApiPermissionError
from atlassian.rest_client import AtlassianRestAPI
from requests import HTTPError


""" 
In this py file have 1 class
    - ConfluenceConnectionClass
"""


class ConfluenceConnectionClass:
    """ This class ("ConfluenceConnectionClass") responsible for connections to Confluence server """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def confluence_connection(self, user_name, password):
        """
        This function responsible for connections to Confluence real server

        The function get 2 parameter:
            - "user" - The user name for connection (string type)
            - "password" - The password for connection (string type)

        The function return 1 parameters:
            - "confluence" - client of confluence (real)
        """

        try:
            confluence = ConfluenceSvg(
                # url='https://confluence.airspan.com/',
                # url='http://confluence-internal:8090/',
                url='https://airspan-il.atlassian.net/',
                username=user_name,
                password=password,
                timeout=580)
            return confluence
        except Exception:
            self.logger.exception('')


class ConfluenceSvg(Confluence):
    def __init__(self, url, *args, **kwargs):
        if ("atlassian.net" in url or "jira.com" in url) and ("/wiki" not in url):
            url = AtlassianRestAPI.url_joiner(url, "/wiki")
            if "cloud" not in kwargs:
                kwargs["cloud"] = True
        super(Confluence, self).__init__(url, *args, **kwargs)
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def create_page(
        self,
        space,
        title,
        body,
        parent_id=None,
        type="page",
        representation="storage",
        editor=None,
        full_width=False,
    ):
        """
        Create page from scratch
        :param space:
        :param title:
        :param body:
        :param parent_id:
        :param type:
        :param representation: OPTIONAL: either Confluence 'storage' or 'wiki' markup format
        :param editor: OPTIONAL: v2 to be created in the new editor
        :return:
        """
        self.logger.info('Creating {type} "{space}" -> "{title}"'.format(space=space, title=title, type=type))
        url = "rest/api/content/"
        data = {
            "type": type,
            "title": title,
            "space": {"key": space},
            "body": self._create_body(body, representation),
        }
        if parent_id:
            data["ancestors"] = [{"type": type, "id": parent_id}]
        if editor is not None and editor in ["v1", "v2"]:
            data["metadata"] = {
                "properties": {
                    "editor": {"value": editor},
                    "content-appearance-draft": {"value": 'full-width'},
                    "content-appearance-published": {"value": 'full-width'},
                }
            }
        try:
            response = self.post(url, data=data)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise ApiPermissionError("The calling user does not have permission to view the content", reason=e) from e

            raise
        return response
