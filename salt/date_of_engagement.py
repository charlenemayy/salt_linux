import pandas as pd
import json
import hmis_driver
import os

class DateOfEngagement:
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_excel(io=filename,
                             dtype={'clientid': object,
                                    'Name': object,
                                    'ProgramName': object})
        if self.df.empty:
            print("No data to process, closing now")
            quit()
        
        self.failed_df = self.df.copy()

        try:
            filename = "./salt/settings.json"
            f = open(filename)
            data = json.load(f)
        except Exception as e:
            print("ERROR: 'settings.json' file cannot be found, please see README for details")
            quit()

        settings = data["data"][0]
        self.username = settings["hmis_username"]
        self.password = settings["hmis_password"]
        self.output_path = settings["output_path"]

    # Clean and prepare data for automation and build client dicts
    def read_and_process_data(self):
        self.__open_clienttrack()

        for row_index in range(0, len(self.df)):
            client_dict = {}
            row = self.df.iloc[row_index]

            # split name into first and last
            string_list = row['Name'].rsplit(', ', 1)
            if len(string_list) > 1:
                client_dict['First Name'] = string_list[1]
            else:
                client_dict['First Name'] = ''
            client_dict['Last Name'] = string_list[0]

            # add clientid to dict
            client_dict['Client ID'] = row['clientid']

            self.__delete_date_of_engagement(client_dict, row_index)

    # Open and login to HMIS Clienttrack
    def __open_clienttrack(self):
        self.driver = hmis_driver.Driver()
        self.driver.open_clienttrack()
        if not self.driver.login_clienttrack(self.username, self.password):
            print("Could not login successfully, closing now")
            quit()
    
    def __delete_date_of_engagement(self, client_dict, row_index):
        # STEP ONE: SEARCH FOR CLIENT
        print("\nNEW CLIENT: Deleting Date of Engagement for Client " + client_dict['First Name'] + ' ' + client_dict['Last Name'])
        if not isinstance(client_dict['Client ID'], float) and client_dict['Client ID'] != "":
            success = self.driver.search_client_by_ID(client_dict['Client ID'], client_dict['First Name'], client_dict['Last Name'])
        else:
            print("Not enough data provided to search for client:")
            print(client_dict)
            return

        if not success:
            print("Client could not be found in the system:")
            print(client_dict)
            return

        # STEP TWO: DELETE CLIENT'S DATE OF ENGAGEMENT
        success = self.driver.delete_date_of_engagement() # look at 'update_date_of_engagement'
        if not success:
            print("Date of engagement could not be deleted for client:")
            print(client_dict)
            return # keep client on failed entry list and move on to next client
        else:
            # remove client from list of failed entries
            self.failed_df = self.failed_df.drop([row_index])
            print("Success! " + str(len(self.failed_df.index)) + " entries remaining\n")
            self.__export_failed_automation_data()

    # Export a sheet of the failed automated entries in their original format
    # This way we can keep looping the failed entries and try again
    def __export_failed_automation_data(self):
        # get date from original file and output into new excel sheet
        output_name = ("Remaining_" + os.path.basename(self.filename))
        # create sheet for remaining clients that need to be entered and could not be automated
        self.failed_df.to_excel(self.output_path + output_name, sheet_name = "Failed Entries Report - " + output_name)