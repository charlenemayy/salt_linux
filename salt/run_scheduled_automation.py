from datetime import date
from datetime import timedelta
from datetime import datetime
import os
import subprocess
import json
import time
import argparse

'''
Downloads yesterday's daily report from the SALT Web App and enters its data into HMIS
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
parser.add_argument("-l", "--lockwhendone", action="store_true")

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
    print("Downloading yesterday's report from the SALT Web App")
    subprocess.run(["/usr/bin/python3 salt/run_daily_report.py -d {0}".format(date_str)], shell=True)
    time.sleep(5)

# double check that report has been downloaded / exists
report_path = output_path + report_filename
if not os.path.exists(report_path):
    print("ERROR: Downloaded report from SALT cannot be found")
    quit()

# download pretty xlsx file to upload to drive
print("Processing simplified report file")
subprocess.run(["/usr/bin/python3 salt/run_daily_data.py -f {0} -m".format(report_path)], shell=True)

# start first run of automation
if not args.skipfirstrun:
    print("Starting first run of automation")
    subprocess.run(["/usr/bin/python3 salt/run_daily_data.py -f {0} -a".format(report_path)], shell=True)

# run the failed entries three more times
failed_report_filename = "Failed_entries_" + date_str + ".xlsx"
failed_report_path = output_path + failed_report_filename

print(failed_report_path)

if not os.path.exists(failed_report_path):
    print("ERROR: Failed entry report from SALT cannot be found")
    quit()

for i in range(run_count):
    print("Automating failed entries, {0} more rounds to go".format(run_count-1-i))
    subprocess.run(["/usr/bin/python3 salt/run_daily_data.py -f {0} -a".format(failed_report_path)], shell=True)

print("SUCCESS: Finished running scheduled automation!")

if args.lockwhendone: # good for scheduled runs late at night
    os.system("pmset displaysleepnow")