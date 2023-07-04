import logging

"""
In this py file have 1 class
    - ConfluenceCreateAndUpdateClass
"""


class ConfluenceCreateAndUpdateClass:
    """ This class ("ConfluenceCreateAndUpdateClass") responsible for create and update page """
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def update_page(self, confluence, confluence_page_id, confluence_page_name, page_body):
        """
        This function responsible Create "confluence Html title" as part of confluence page

        The function get 2 parameter:
            - "confluence" - client of confluence (real)
            - "confluence_page_id" - parameter need to be the number of the confluence id page (string type)
            - "confluence_page_name" - parameter need to be the name of the confluence page (string type)
            - "page_body" - The full html page of the confluence page (string type)

        The function return 0 parameters:
        """

        try:
            confluence.update_or_create(confluence_page_id, confluence_page_name, page_body, representation='storage')
        except Exception:
            self.logger.exception('')
            return None
