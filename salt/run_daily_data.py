import argparse
import pandas as pd
import daily_data
import datetime

# Command Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--listitems", action='store_true', help="List Unique Items")
parser.add_argument("-f", "--filename", help="Filename")
parser.add_argument("-o", "--output", action='store_true')
parser.add_argument("-a", "--automate", action='store_true') # Outputs a spreadsheet of unprocessed / dirty entries that can not be entered automatically
parser.add_argument("-m", "--manual", action='store_true') # Outputs a readable spreadsheet for data to be entered manually

args = parser.parse_args()

if not args.filename:
       print("ERROR: Please add a file to read by typing '-f' before your filename")
       quit()

start_time = datetime.datetime.now()

df = pd.read_excel(io=args.filename,
                     dtype={'': object,
                            'DoB': object,
                            'Client Name': object,
                            'HMIS ID': object,
                            'Race': object,
                            'Ethnicity': object,
                            'Verification of homeless': object,
                            'Gross monthly income': object,
                            'Service': object,
                            'Items': object})

dd = daily_data.DailyData(df, args.filename, args.automate, args.manual, args.output, args.listitems)
dd.read_and_process_data()
if args.manual:
       dd.export_manual_entry_data("~/Downloads/")

end_time = datetime.datetime.now()
difference = end_time - start_time
diff_in_seconds = difference.total_seconds()
diff_in_minutes = divmod(diff_in_seconds, 60)[0]
print("Total Automation Time: " + str(diff_in_minutes) + " minutes")