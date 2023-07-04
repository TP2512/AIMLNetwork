import logging
import requests
import time


class TestSpanStudioApi:

    def __init__(self):
        self.logger = logging.getLogger(
            'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)

    def update_testspan_studio_via_api(self, param_dict, sir):
        """
        function to update testspan studio params via Api
        :param param_dict: get dict with key and value to update the function
        example : { "XLP_SW_BUILD": "fsm.15_17_00_1180.enc2" }
        :param sir: get sir to update
        :return:
        """
        try:
            sir_url = 'http://asil-svg-testspan:8050/test-set-config/' + str(sir)
            post_url = 'http://asil-svg-testspan:8050/update-test-set-parameters/'
            data = None
            update = None
            for i in range(0, 2):
                try:
                    data = requests.get(url=sir_url, timeout=600).json()
                    break
                except Exception as err:
                    self.logger.info("Cant update testspan studio will try again in 30 seconds")
                    self.logger.exception(err)
                    time.sleep(30)
                    continue
            if data:
                for i in data['globalParams']:
                    for key, value in param_dict.items():
                        if i['key'] == str(key):
                            i['value'] = value
                            self.logger.info(f"update: {str(i['key'])} with {str(i['value'])}")
                for i in range(0, 2):
                    try:
                        update = requests.post(url=post_url, json=data, timeout=240)
                        break
                    except Exception as err:
                        self.logger.info("Cant update testspan studio will try again in 30 seconds")
                        self.logger.exception(err)
                        time.sleep(30)
                        continue
                if update.status_code == 200:
                    self.logger.info(f"{str(sir)} updated in testspan studio")
                else:
                    self.logger.info(f"failed to update testspan studio error code: {str(update.status_code)}")
            else:
                self.logger.info("no data received from testpspan studio")
        except Exception as err:
            self.logger.exception(err)
