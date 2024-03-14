import argparse
import daily_report

# Command Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--date")

args = parser.parse_args()
if not args.date:
       print("ERROR: Please add a date in format '-d MM-DD-YYYY'")
       quit()
    
report = daily_report.DailyReport(args.date)
report.download_report()