import argparse
import pandas as pd
import daily_data

# Command Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--listitems", action='store_true', help="List Unique Items")
parser.add_argument("-f", "--filename", help="Filename")
parser.add_argument("-o", "--output", action='store_true')
parser.add_argument("-d", "--rundriver", action='store_true')

args = parser.parse_args()

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

dd = daily_data.DailyData(df, args.rundriver, args.output, args.listitems)
dd.clean_data()
dd.read_and_enter_data()
dd.combine_service_and_item_columns()
dd.export_data(args.filename, "~/Desktop/SALT/output/")