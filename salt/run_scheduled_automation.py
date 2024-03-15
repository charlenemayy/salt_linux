from datetime import date
from datetime import timedelta
from datetime import datetime
import os
import subprocess
import json
import time
import argparse
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

'''
Automates the entire daily data process, from downloading the report in the SALT Web app to 
inputting into HMIS, including running the failed entries several times. This is meant to be 
run late at night, every night. 

This was developed based on my personal environment in MacOS and will not work in other operating systems.
'''
# SETTINGS
run_count = 3 # amount of times to run the failed entry automation


# grab output path from settings.json
try:
    filename = "./salt/settings.json"
    f = open(filename)
    data = json.load(f)
except Exception as e:
    print("ERROR: 'settings.json' file cannot be found, please see README for details")
    quit()
settings = data["data"][0]
output_path = settings["output_path"]

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--date")
parser.add_argument("-sfr", "--skipfirstrun", action="store_true")
parser.add_argument("-lu", "--leaveunlocked", action="store_true")

args = parser.parse_args()
if args.date:
    date_str = args.date
else:
    # get yesterday's date
    yesterday = date.today() - timedelta(days=1)
    date_str = datetime.fromordinal(yesterday.toordinal()).strftime("%m-%d-%Y")

# check if report has already been downloaded
files = os.listdir(output_path)
report_filename = "Report_by_client_" + date_str + ".xlsx"

# download yesterday's report
if report_filename not in files:
    print("RUNNING: Downloading yesterday's report from the SALT Web App")
    subprocess.run(["/usr/bin/python3 salt/run_daily_report.py -d {0}".format(date_str)], shell=True)
    time.sleep(5)

# double check that report has been downloaded / exists
report_path = output_path + report_filename
if not os.path.exists(report_path):
    print("ERROR: Downloaded report from SALT cannot be found")
    quit()

# download pretty xlsx file to upload to drive
print("RUNNING: Processing simplified report file")
subprocess.run(["/usr/bin/python3 salt/run_daily_data.py -f {0} -m".format(report_path)], shell=True)

# start first run of automation
if not args.skipfirstrun:
    print("RUNNING: Starting first run of automation")
    subprocess.run(["/usr/bin/python3 salt/run_daily_data.py -f {0} -a".format(report_path)], shell=True)

# run the failed entries three more times
failed_report_filename = "Failed_entries_" + date_str + ".xlsx"
failed_report_path = output_path + failed_report_filename

if not os.path.exists(failed_report_path):
    print("ERROR: Failed entry report from SALT cannot be found")
    quit()

for i in range(run_count):
    print("\nRUNNING: Automating failed entries, {0} more round(s) to go".format(run_count-1-i))
    subprocess.run(["/usr/bin/python3 salt/run_daily_data.py -f {0} -a".format(failed_report_path)], shell=True)

# upload final instance of the failed entry report to drive
gauth = GoogleAuth() 
drive = GoogleDrive(gauth)

gfile = drive.CreateFile({'parents': [{'id': '15sT6EeVyeUsMd_vinRYgSpncosPW7B2s'}], 'title': failed_report_filename}) 
gfile.SetContentFile(failed_report_path)
gfile.Upload()

print("SUCCESS: Finished running scheduled automation!")
if not args.leaveunlocked:
    os.system("pmset displaysleepnow") # locks mac when done