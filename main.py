import pandas as pd
import lib.argumentcli as argcli
import lib.rules as rule


# TODO: should main print statements or should it be done in the functions?

# NOTE: read excel file
# open file as a string
# open file using file name, option to choose sheet, option to ignore commented lines
# returns string as a DataFrame
def readFileAsObject(fileName, sheetName = 0, comment = None):
    df = pd.read_excel(fileName)
    df.columns = [x.lower() for x in df.columns]
    return df
    
def main():  
    args = argcli.getParser()

    if args.file:
        file = readFileAsObject(args.file)
    
    #TODO: better print statements
    rule.processHeaders(file)
    rule.processFields(file)

    return

main()