import argparse
import daily_report

# Command Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--date")
parser.add_argument("-l", "--location") # TODO: if anything but downtown campus

args = parser.parse_args()
if not args.date:
       print("ERROR: Please add a date in format '-d MM-DD-YYYY'")
       quit()
    
report = daily_report.DailyReport(args.date, args.location)
report.download_report()