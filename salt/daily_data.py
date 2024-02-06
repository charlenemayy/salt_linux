import re
from datetime import datetime
import automation_driver

class DailyData:
    # Item Keys
    service_item_codes = ['Shower', 'Laundry']
    clothing_item_codes = ['TOP', 'BTM', 'UND', 'SKS', 'SHO', 'BXR', 'Diabetic Socks']
    grooming_item_codes = ['DDR', 'TBR', 'TPS', 'Razors', 'Adult Depends']
    food_item_codes = ['SBG']
    bedding_item_codes = ['Blankets']

    # Login Info
    username = "charlene@saltoutreach.org"
    password = "1ntsygtmtir!CL"

    # Enrollment Codes
    enroll_orl_street_code = "255537" #value
    enroll_orn_street_code = "234901" # lol jk it changes all the time

    def __init__(self, df, run_driver, show_output, list_items):
        self.df = df
        self.run_driver = run_driver
        self.show_output = show_output
        self.list_items = list_items
        self.unique_items = set()
                
        if self.run_driver:
            self.driver = automation_driver.Driver()
            self.driver.open_clienttrack()
            self.driver.login_clienttrack(DailyData.username, DailyData.password)

    # Remove unecessary columns and reorganize for easier entry
    def clean_data(self):
        self.df = self.df.drop(columns=['Race', 'Ethnicity', 'Verification of homeless', 'Gross monthly income'], axis=1)
        reorder = ['', 'HMIS ID', 'Client Name', 'Service', 'Items', 'DoB']
        self.df = self.df.reindex(columns=reorder)

    # Parse each row (panda series data type) and collect item totals,
    # reorganize birth dates and enter data into clienttrack
    def read_and_enter_data(self):
        for row_index in range(0, len(self.df)):
            # build dictionary datatype for client to pass into automation
            client_dict = {}

            row = self.df.iloc[row_index]

            # rearrange birthday and update row
            date = row['DoB']
            day = date[0:3]
            month = date[3:6]
            result = month + day + date[6:(len(date))]
            self.df.at[row_index, 'DoB'] = result
            client_dict['DoB'] = result

            # get total number of services and items
            service_and_items_dict = {}

            services_dict = self.__get_service_totals(row, row_index)
            items_dict = self.__count_item_totals(row, row_index, services_dict)
            client_dict['Services'] = {**services_dict, **items_dict}

            # split name into first and last
            string_list = row['Client Name'].split(' ')
            client_dict['First Name'] = string_list[1]
            client_dict['Last Name'] = string_list[0]

            # add remaining client info
            client_dict['Client ID'] = row['HMIS ID']

            if self.show_output:
                print()
                print("Final Dictionary Output:")
                print(client_dict)
                print("-----------------------------")

            # automate data entry for current client (as represented by the current row)
            if self.run_driver:
                client_fullname = client_dict['First Name'] + " " + client_dict['Last Name']
                if client_dict['Client ID']:
                    self.driver.search_client_by_ID(client_dict['Client ID'], client_fullname)
                elif client_dict['DoB']:
                    self.driver.search_client_by_birthdate(client_dict['DoB'].replace("-", ""))
                elif client_dict['First Name'] and client_dict['Last Name']:
                    self.driver.search_client_by_name(client_dict['First Name'], client_dict['Last Name'])
                else:
                    print("Not enough client data provided for search")
                    #TODO: add note to excel sheet
                self.driver.enter_client_service(client_dict)

        if self.list_items:
            print(self.unique_items)
    
    # Convert row values to proper data types and return a dictionary
    def __get_service_totals(self, row, row_index):
        services_dict = {}

        if isinstance(row['Service'], float):
            self.df.at[row_index, 'Service'] = ""
        else:
            index = row['Service'].find('Shower')
            if index >= 0:
                # find num value attributed to shower
                string_list = row['Service'].split('Shower')
                substring = string_list[1]

                # get first ':' following 'Shower'
                i = substring.index(':')
                services_dict['Shower'] = int(substring[i+2])

            index = row['Service'].find('Laundry')
            if index >= 0:
                # find num value attributed to laundry
                string_list = row['Service'].split('Laundry')
                substring = string_list[1]

                # get first ':' following 'Laundry' ()
                # multiply laundry x2 (one wash, one dry)
                i = substring.index(':')
                services_dict['Laundry'] = int(substring[i+2]) * 2

        return services_dict

    # Collect total number of items under each category for each client
    # and store all items into a dictionary
    def __count_item_totals(self, row, row_index, services_dict):
        items_dict = {}
        row_items = row['Items']

        if self.show_output:
            print("Raw Excel Data:")
            print("SERVICES")
            print(row['Service'])
            print("ITEMS")
            print(row_items)
            print()
            print("Processed Item Counts:")

        if not isinstance(row_items, float):
            # OPTIONAL: collect all unique keys for items i.e. SHO, TOP, etc.
            if self.list_items:
                li = list(row_items.split(" "))
                for item in li:
                    if item.isalpha():
                        self.unique_items.add(item)

            items_string = ""

            # Clothing 
            clothing_count = 0
            for item in DailyData.clothing_item_codes:
                index = row_items.find(item)
                if index >= 0:
                    # find num value attributed to item code
                    string_list = row_items.split(item)
                    substring = string_list[1]

                    # get first ':' following item code
                    i = substring.index(':')
                    clothing_count += int(substring[i+2])
            if clothing_count > 0:
                items_string = (items_string + "Clothing: " + str(clothing_count) + "\n")
                items_dict['Clothing'] = clothing_count
            if self.show_output:
                print("Clothing: " + str(clothing_count))

            # Grooming/Hygiene 
            grooming_count = 0
            for item in DailyData.grooming_item_codes:
                index = row_items.find(item)
                if index >= 0:
                    # find num value attributed to item code
                    string_list = row_items.split(item)
                    substring = string_list[1]

                    # get first ':' following item code
                    i = substring.index(':')
                    grooming_count += int(substring[i+2])
            # add body wash + shampoo for each shower
            if 'Shower' in services_dict:
                grooming_count += (services_dict['Shower'] * 2)
            # add detergent for each laundry run (wash + dry)
            if 'Laundry' in services_dict:
                grooming_count += int(services_dict['Laundry'] / 2)
            if grooming_count > 0:
                items_string = (items_string + "Grooming: " + str(grooming_count) + "\n")
                items_dict['Grooming'] = grooming_count
            if self.show_output:
                print("Grooming: " + str(grooming_count))

            # Food 
            food_count = 0
            for item in DailyData.food_item_codes:
                index = row_items.find(item)
                if index >= 0:
                    # find num value attributed to item code
                    string_list = row_items.split(item)
                    substring = string_list[1]

                    # get first ':' following item code
                    i = substring.index(':')
                    food_count += int(substring[i+2])
            if food_count > 0:
                items_string = (items_string + "Food: " + str(food_count) + "\n")
                items_dict['Food'] = food_count
            if self.show_output: 
                print("Food: " + str(food_count))

            # Bedding 
            bedding_count = 0
            for item in DailyData.bedding_item_codes:
                index = row_items.find(item)
                if index >= 0:
                    # find num value attributed to item code
                    string_list = row_items.split(item)
                    substring = string_list[1]

                    # get first ':' following item code
                    i = substring.index(':')
                    bedding_count += int(substring[i+2])
            if bedding_count > 0:
                items_string = (items_string + "Bedding: " + str(bedding_count) + "\n")
                items_dict['Bedding'] = bedding_count
            if self.show_output: 
                print("Bedding: " + str(bedding_count))

            # set updated items value to excel sheet
            self.df.at[row_index, 'Items'] = items_string
        # if there are no items in the item column but in the service column
        elif (services_dict): 
            items_string = ""
            grooming_count = 0
            if 'Shower' in services_dict:
                grooming_count += (services_dict['Shower'] * 2)
            # add detergent for each laundry run (wash + dry)
            if 'Laundry' in services_dict:
                grooming_count += int(services_dict['Laundry'] / 2)
            if grooming_count > 0:
                items_string = (items_string + "Grooming: " + str(grooming_count) + "\n")
                items_dict['Grooming'] = grooming_count
            if self.show_output:
                print("Grooming: " + str(grooming_count))
        else:
            # if 'NaN' value set to empty string
            self.df.at[row_index, 'Items'] = ""

        return items_dict

    # Make data more readable for manual data entry
    def combine_service_and_item_columns(self):
        # combine service columns into one
        self.df['Services'] = self.df['Service'].astype(str) + self.df['Items'].astype(str)
        self.df = self.df.drop(['Service', 'Items'], axis=1)
        reorder = ['', 'HMIS ID', 'Client Name', 'Services', 'DoB']
        self.df = self.df.reindex(columns=reorder)


    # Export data to new spreadsheet in output folder
    def export_data(self, filename, output_path):
        # get date from original file and output into new excel sheet
        date_string = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", filename)
        date = datetime.strptime(date_string[0], '%m-%d-%Y')
        output_name = str(date.strftime('%d')) + ' ' + str(date.strftime('%b')) + ' ' + str(date.strftime('%Y'))
        self.df.to_excel(output_path + output_name + ".xlsx", sheet_name=output_name)