import pandas as pd
import argparse

# NOTE: main function runs all our test functions
# TODO: create function that reads in excel file from command line argument

# TODO: read command line arguments
parser = argparse.ArgumentParser()
group = parser.add_argument("file", help="the name of the excel file")
group = parser.add_argument("-sh", "--sheet", help="the name of the sheet program will read")
args = parser.parse_args()

# TODO: read excel file
# open file as a string
# open file using file name, option to choose sheet, option to ignore commented lines
# returns string as a DataFrame
def readFileAsObject(fileName, sheetName = 0, comment = None):
    return pd.read_excel(fileName, sheetName, comment)


    
def main():
    print(args)
    
    if args.file:
        file = readFileAsObject(args.file)
    print(file)

    return

main()