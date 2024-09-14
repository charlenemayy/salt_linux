from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import traceback
import time

class Driver:

    # Global Variables
    wait_time = 3

    def __init__(self):
        desired = DesiredCapabilities.FIREFOX
        
        firefox_options = Options()
        firefox_options.desired = desired

        # added for linux build
        firefox_options.add_argument("--headless")

        self.browser = webdriver.Firefox(options=firefox_options, service=FirefoxService(GeckoDriverManager().install()))

    def open_saltwebapp(self, location):
        if location == "ORL": 
            self.browser.get('https://saltoutreachapp.com/')
        else:
            self.browser.get('https://sanford.saltoutreachapp.com/')

    def login_saltwebapp_native(self, username, password):
        try:
            WebDriverWait(self.browser, self.wait_time).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="email"]'))
            )
            field_username = self.browser.find_element(By.XPATH, '//input[@type="email"]')
            field_password = self.browser.find_element(By.XPATH, '//input[@type="password"]')

            field_username.send_keys(username)
            field_password.send_keys(password)
            field_password.send_keys(Keys.RETURN)
        except Exception as e:
            print("Couldn't login with SALT username and password")
            print(e)
            return False


    def login_saltwebapp_google(self, username, password):
        try:
            WebDriverWait(self.browser, self.wait_time).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="text-center"]/a'))
            )
            button_google_login = self.browser.find_element(By.XPATH, '//div[@class="text-center"]/a')
            button_google_login.click()
        except Exception as e:
            print("Couldn't click Google login button")
            print(e)
            return False
 
        try:
            WebDriverWait(self.browser, self.wait_time).until(
                EC.presence_of_element_located((By.ID, 'identifierId'))
            )
            field_username = self.browser.find_element(By.ID, 'identifierId')
            field_username.send_keys(username)
            field_username.send_keys(Keys.RETURN)
        except Exception as e:
            print("Couldn't enter Google username")
            print(e)
            return False

        try:
            WebDriverWait(self.browser, self.wait_time).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]'))
            )
            field_password = self.browser.find_element(By.XPATH, '//input[@type="password"]')
            field_password.click()
            field_password.send_keys(password)
            field_password.send_keys(Keys.RETURN)
        except Exception as e:
            print("Couldn't enter Google password")
            print(e)
            return False

        # wait for salt page to be loaded and ready
        self.__wait_until_page_fully_loaded('SALT Homepage')
        time.sleep(3)
        self.browser.save_screenshot('screenshot.png')
        print("SAVED SCREENSHOT")
        time.sleep(40)
        try:
            WebDriverWait(self.browser, self.wait_time).until(
                EC.visibility_of_element_located((By.ID, 'navbar'))
            )
        except Exception as e:
            print("Login didn't navigate back to SALT web app")
            print(e)
            return False
        return True

    # date format: YYYY-MM-DD
    def navigate_to_daily_data_by_client(self, date):
        self.__wait_until_page_fully_loaded('SALT Homepage')
        try:
            WebDriverWait(self.browser, self.wait_time).until(
                EC.element_to_be_clickable((By.ID, 'formdate'))
            )
            input_date = self.browser.find_element(By.ID, 'formdate')
            input_date.send_keys(date)
            input_date.send_keys(Keys.RETURN)
        except Exception as e:
            print("Couldn't load daily numbers for client")
            print(e)
            return False
        return True
    
    def download_daily_report_by_client(self, location):
        self.__wait_until_page_fully_loaded('SALT Homepage')
        if location == "ORL":
            download_url = "https://saltoutreachapp.com/dashboard/export"
            time.sleep(20)
        else:
            download_url = "https://sanford.saltoutreachapp.com/dashboard/export"
            time.sleep(3)
        try:
            WebDriverWait(self.browser, self.wait_time).until(
                EC.element_to_be_clickable((By.XPATH, '//form[@action="{}"]/button'.format(download_url)))
            )
            button_export = self.browser.find_element(By.XPATH, '//form[@action="{}"]/button'.format(download_url))
            button_export.click()
            print("Downloading Report...")
        except Exception as e:
            print("Couldn't download daily report")
            print(traceback.format_exc())
            return False
        print("Success! Daily report downloaded")
        self.__wait_until_page_fully_loaded('SALT Homepage')
        # self.browser.quit()
        return True
    '''
    ------------------------ HELPER ------------------------
    '''
    # Waits until a page is fully loaded before continuing
    # @param: [str] page_name: the name of the page to be printed in output to make debug easier
    def __wait_until_page_fully_loaded(self, page_name):
        try:
            WebDriverWait(self.browser, self.wait_time).until(
                lambda browser: browser.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            print("Error loading " + page_name + " page")
            print(traceback.format_exc())
