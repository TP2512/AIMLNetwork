import logging
import urllib.parse
import requests
import urllib


class UrlShortenTinyurl:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.URL = "http://tinyurl.com/api-create.php"

    def shorten(self, url_long):
        try:
            url = (f"{self.URL}?" + urllib.parse.urlencode({"url": url_long.replace('\\', '/')}))
            res = requests.get(url)
            # print("STATUS CODE:", res.status_code)
            # print("   LONG URL:", url_long)
            self.logger.info(res.text)
            return res.text
        except Exception:
            self.logger.error('Failed to create url')
