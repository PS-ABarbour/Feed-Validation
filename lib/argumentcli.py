import argparse
# NOTE: main function runs all our test functions
# TODO: create function that reads in excel file from command line argument

# NOTE: read command line arguments
parser = argparse.ArgumentParser()
group = parser.add_argument("file", help="the name of the excel file")
# group = parser.add_argument("-sh", "--sheet", help="the name of the sheet program will read")

def getParser():
 return parser.parse_args()