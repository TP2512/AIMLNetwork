from Confluence_Infrastructure.Confluence_Connector.ConfluenceConnector import ConfluenceConnectionClass
import logging

"""
In this py file have 1 class
    - ConfluencePageGetterClass
"""


class ConfluencePageGetterClass:
    """ This class ("PageGetterClass") responsible for get page info """
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def get_page(self, confluence, confluence_space, confluence_page_name):
        """
        This function responsible Create "confluence Html title" as part of confluence page

        The function get 2 parameter:
            - "confluence" - client of confluence (real)
            - "confluence_space" - parameter need to be the name of the confluence space (string type)
            - "confluence_page_name" - parameter need to be the name of the confluence page (string type)

        The function return 1 parameters:
            - "confluence_page_name_html" - The full HTML of the confluence page ( type)
        """

        try:
            return confluence.get_page_by_title(confluence_space, confluence_page_name, expand='body.storage')

        except Exception:
            self.logger.exception('')
            return None

    def get_page_version(self, page_id, user_name, password):
        """
           This function responsible retrieving confluence page version

           The function get 1 parameter:
            - "page_id" - parameter need to be the page id (string type)
            - "user_name" - parameter need to be the user name (string type)
            - "password" - parameter need to be the password (string type)

           The function return 1 parameters:
               - "page_version" - The version of the Confluence page
           """

        try:
            get_version = ConfluenceConnectionClass().confluence_connection(user_name, password).\
                get_page_by_id(page_id, expand='version')
            return get_version.get('version', {}).get('number')
        except Exception:
            self.logger.exception('')
            return None
