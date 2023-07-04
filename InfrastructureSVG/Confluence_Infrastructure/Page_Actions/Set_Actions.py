import requests
import json
from requests.auth import HTTPBasicAuth
import logging

class PageSetterClass:
    def __init__(self):
        self.logger = logging.getLogger(
            'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)

    def update_page(self, body, page_id, space, version, page_version):
        # set auth token and get the basic auth code
        auth = HTTPBasicAuth("TestspanAuto", "air_auto1")
        # Set the title and content of the page to create
        page_html = body
        url = f"https://confluence.airspan.com/rest/api/content/{page_id}"

        # get the confluence home page url for your organization {confluence_home_page}

        data = {
            "id": page_id,
            "type": "page",
            "title": version,
            "space": {
                "key": space
            },
            "body": {
                "storage": {
                    "value": "\"" + page_html + "\"",
                    "representation": "storage"
                }
            },
            "version": {
                "number": page_version
            }
        }
        # Request Headers
        headers = {
            "Content-Type": "application/json"
        }

        try:

            r = requests.put(url=url, data=json.dumps(data), headers=headers, auth=auth)

            # Consider any status other than 2xx an error
            if r.status_code // 100 != 2:
                self.logger.debug(f"Error: Unexpected response {r}")
            else:
                self.logger.warning("Page Updated!")

        except requests.exceptions.RequestException as e:
            self.logger.exception("Error: {}".format(e))
