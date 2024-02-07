from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import difflib

class Driver:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        self.browser = Chrome(options=chrome_options)

    # Setup
    def open_clienttrack(self):
        self.browser.get('https://clienttrack.eccovia.com/login/HSNCFL')

    # Login to Client Track
    def login_clienttrack(self, username, password):
        field_username = self.browser.find_element(By.ID, "UserName")
        field_password = self.browser.find_element(By.ID, "Password")

        field_username.send_keys(username)
        field_password.send_keys(password)
        field_password.send_keys(Keys.RETURN)
    
    # Focus on iframe with given ID
    def __switch_to_iframe(self, iframe_id):
        try:
            WebDriverWait(self.browser, 30).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, iframe_id))
            )
        except Exception as e:
            print("Couldn't focus on iframe")
    
    # Navigate to 'Find Client' page
    def navigate_to_find_client(self):
        button_nav_clients_page_id = "ws_2_tab"
        button_nav_find_clients_page_id = "o1000000037"
        inner_iframe_id = "TabFrame_2"

        # find 'Clients' button on left sidebar
        try:
            WebDriverWait(self.browser, 30).until(
                EC.element_to_be_clickable((By.ID, button_nav_clients_page_id))
            )
            button_clients = self.browser.find_element(By.ID, button_nav_clients_page_id)
            button_clients.click()
        except Exception as e:
            print("Couldn't navigate to 'Clients' page")
            return False
        
        # find 'Find Client' button on left sidebar after waiting for client dashboard to fully load
        try:
            WebDriverWait(self.browser, 30).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, inner_iframe_id))
            ) 
            self.browser.switch_to.default_content()
            WebDriverWait(self.browser, 30).until(
                EC.element_to_be_clickable((By.ID, button_nav_find_clients_page_id))
            )
            button_find_client = self.browser.find_element(By.ID, button_nav_find_clients_page_id)
            button_find_client.click()
        except Exception as e:
            print("Couldn't open 'Find Client' page")
            return False

    # Search for a Client by their ID number
    def search_client_by_ID(self, id, first_name, last_name):
        self.navigate_to_find_client()

        field_client_id_id = "1000005942_Renderer"
        button_search_id = "Renderer_SEARCH"
        inner_iframe_id = "TabFrame_2"
        label_client_name_xpath = "//span[@class = 'entity-info-value'][@aria-label = 'Name']"

        # enter id into client id field
        self.__switch_to_iframe(inner_iframe_id)
        try:
            WebDriverWait(self.browser, 30).until(
                EC.element_to_be_clickable((By.ID, field_client_id_id))
            )
            field_client_id = self.browser.find_element(By.ID, field_client_id_id)        
            field_client_id.click()
            field_client_id.send_keys(id)

            button_search_id = self.browser.find_element(By.ID, button_search_id)
            button_search_id.click()
        except Exception as e:
            print("Couldn't find 'Client ID' field")
            return False

        # check that name matches client data and id
        # should load directly to client dashboard
        self.browser.switch_to.default_content()
        try:
            WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.XPATH, label_client_name_xpath))
            )
            dashboard_name = self.browser.find_element(By.XPATH, label_client_name_xpath).text
            dashboard_first_name = dashboard_name.split(" ", 1)[0]
            dashboard_last_name = dashboard_name.split(" ", 1)[1]

            # sometimes first and last names are swapped, check both scenarios
            if self.__similar(dashboard_first_name, first_name, 0.9) and self.__similar(dashboard_last_name, last_name, 0.9):
                return True
            # sometimes the first and last names are flipped
            elif self.__similar(dashboard_first_name, last_name, 0.9) and self.__similar(dashboard_last_name, first_name, 0.9):
                return True
        except Exception as e:
            print("Couldn't find correct Client Name")
            return False

    def search_client_by_birthdate(self, birthdate, first_name, last_name):
        self.navigate_to_find_client()

        inner_iframe_id = "TabFrame_2"
        field_birthdate_id = "1000005939_Renderer"
        button_search_id = "Renderer_SEARCH"
        table_search_results_rows_xpath = "//table[@id='RendererResultSet']//tbody/tr"

        self.__switch_to_iframe(inner_iframe_id)
        try:
            WebDriverWait(self.browser, 30).until(
                EC.element_to_be_clickable((By.ID, field_birthdate_id))
            )
            # enter birthday to field
            field_birthdate = self.browser.find_element(By.ID, field_birthdate_id)        
            field_birthdate.click()
            field_birthdate.send_keys(birthdate)

            button_search_id = self.browser.find_element(By.ID, button_search_id)
            button_search_id.click()
        except Exception as e:
            print("Couldn't find 'Birth Date' field")
            return False

        try:
            WebDriverWait(self.browser, 30).until(
                EC.visibility_of_all_elements_located((By.XPATH, table_search_results_rows_xpath))
            )
            # search through rows in tables
            table_search_results = self.browser.find_elements(By.XPATH, table_search_results_rows_xpath)
            for result in table_search_results:
                result_first_name = result.find_element(By.XPATH, "td[2]").text
                result_last_name = result.find_element(By.XPATH, "td[3]").text
                if self.__similar(result_first_name, first_name, 0.9) and self.__similar(result_last_name, last_name, 0.9):
                    result.click()
                    break
                # sometimes the first and last names are flipped
                elif self.__similar(result_first_name, last_name, 0.9) and self.__similar(result_last_name, first_name, 0.9):
                    result.click()
                    break
        except Exception as e:
            print("Couldn't find client name among results")
            return False
    
    # Returns a ratio showing how similar two strings are
    def __similar(self, a, b, min_score):
        print(difflib.SequenceMatcher(a=a.lower(), b=b.lower()).ratio())
        return difflib.SequenceMatcher(a=a.lower(), b=b.lower()).ratio() > min_score