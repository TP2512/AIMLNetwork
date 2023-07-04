import logging
import re
import time
from colorama import Fore

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


class SwImageUpload:
    JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width >> 1)),
          y = rect.top + (offsetY || (rect.height >> 1)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
"""
    TOTAL_PROGRESS = 100
    BAR_WIDTH = 50

    def __init__(self, acp_ip, sw_image_path):
        self.error_message = None
        self.success_message = None
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
        self.acp_ip = acp_ip
        self.sw_image_path = sw_image_path
        service = Service('\\\\192.168.127.231\\LabShare\\Automation\\SeleniumDriver\\geckodriver.exe')
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(service=service, options=options)
        self.is_success_visible = None
        self.is_error_visible = None
        self.prev_bar_width = None

    def open_website(self):
        self.driver.get(f'https://{self.acp_ip}/')
        self.driver.maximize_window()
        self.driver.implicitly_wait(15)
        self.driver.set_script_timeout(10)

    def login(self, username, password):
        username_input = self.driver.find_element(by=By.ID, value="txtUsername")
        password_input = self.driver.find_element(by=By.ID, value="txtPassword")
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button = self.driver.find_element(by=By.XPATH, value="/html/body/div/div[1]/div[3]/div[1]/form/input[5]")
        submit_button.click()
        time.sleep(2)

    def navigate_to_software_images(self):
        self.navigate_to("Software", 1)
        self.navigate_to("Software Images", 2)

    def navigate_to(self, value, arg1):
        link_software = self.driver.find_element(by=By.LINK_TEXT, value=value)
        link_software.click()
        time.sleep(arg1)

    def switch_to_frame(self):
        frame_element = self.driver.find_element(by=By.XPATH, value="//iframe[@name='Main']")
        self.driver.switch_to.frame(frame_element)

    def upload_file(self):
        add_image_to_list_button = self.driver.find_element(by=By.XPATH, value='//*[@id="SoftwareImageList"]/div[2]/div[4]/div[2]/div[6]/div/button[1]')
        add_image_to_list_button.click()
        time.sleep(2)
        upload_application_button = self.driver.find_element(by=By.XPATH, value='//*[@id="SoftwareImageEdit"]/div[2]/div[4]/div[2]/div[4]/div[2]/button')
        upload_application_button.click()
        time.sleep(2)
        image_upload_form = self.driver.find_element(by=By.ID, value='aioImageForm')
        file_explorer = self.driver.execute_script(self.JS_DROP_FILE, image_upload_form, 0, 0)
        file_explorer.send_keys(self.sw_image_path)
        upload_button = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div[6]/div/div/div[3]/button[1]')
        upload_button.click()

    def get_progress_info_and_value(self):
        progress_info = self.driver.find_element(by=By.XPATH, value='//*[@id="progressInfo"]').get_attribute('innerHTML').split('<br>')[0]
        pattern = r'(.+?)\s+\d+%$'
        regex_result = re.search(pattern, progress_info)
        progress_info = regex_result[1] if regex_result else progress_info
        progress_value = int(self.driver.find_element(by=By.XPATH, value='//*[@id="progressBar"]').get_attribute('aria-valuenow'))
        return progress_info, progress_value

    def is_success_or_error_visible(self):
        return self.success_message.is_displayed(), self.error_message.is_displayed()

    def track_progress(self):
        self.success_message = self.driver.find_element(by=By.XPATH, value='//*[@id="SoftwareImageEdit"]/div[2]/div[9]')
        self.error_message = self.driver.find_element(by=By.XPATH, value='//*[@id="SoftwareImageEdit"]/div[2]/div[8]')
        prev_progress_info = None
        prev_progress_value = None
        start_time = time.time()

        while True:
            self.is_success_visible, self.is_error_visible = self.is_success_or_error_visible()
            progress_info, progress_value = self.get_progress_info_and_value()

            if prev_progress_info != progress_info:
                prev_progress_info = progress_info
                prev_progress_value = None
                self.logger.info(f'{progress_info}:')

            if prev_progress_value != progress_value:
                prev_progress_value = progress_value
                progress = progress_value / self.TOTAL_PROGRESS
                if prev_progress_value is None:
                    self.print_progress_bar(0, self.BAR_WIDTH)
                self.print_progress_bar(progress, self.BAR_WIDTH)

            if self.is_success_visible or self.is_error_visible or time.time() - start_time >= 900:
                break
            else:
                time.sleep(1)

    def close(self):
        self.driver.close()

    def print_progress_bar(self, progress, bar_width):
        filled_width = int(progress * bar_width)
        if filled_width != self.prev_bar_width:
            self.prev_bar_width = filled_width
            bar = '#' * filled_width + '-' * (bar_width - filled_width)
            self.logger.info(f'{Fore.MAGENTA}|{bar}| {progress:.1%}')

    def check_for_errors(self):
        if self.is_error_visible:
            error_list_item_element = self.driver.find_element(by=By.XPATH, value='//*[@id="SoftwareImageEdit"]/div[2]/div[8]/div[2]/ul/li')
            error_message = error_list_item_element.get_attribute('innerHTML')
            self.logger.info(error_message)
            return error_message

    def click_save_on_success_upload(self):
        if self.is_success_visible:
            save_image_button = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div[10]/button[1]')
            save_image_button.click()
            time.sleep(2)
            if self.error_message.is_displayed():
                error_list_item_element = self.driver.find_element(by=By.XPATH, value='//*[@id="SoftwareImageEdit"]/div[2]/div[8]/div[2]/ul/li')
                error_message = error_list_item_element.get_attribute('innerHTML')
                self.logger.error(error_message)
                return False
            else:
                agree_version = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[3]/div/div/div[3]/button[1]')
                agree_version.click()
                return True

    def start_image_upload(self):
        self.open_website()
        self.login('admin', 'password')
        self.navigate_to_software_images()
        self.switch_to_frame()
        self.upload_file()
        self.track_progress()
        errors = self.check_for_errors()
        status = False if errors else self.click_save_on_success_upload()
        self.close()
        return status
