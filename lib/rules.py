import pandas as pd
import lib.messages as msg
import re
import json

# NOTE: check headers of file against our sample feed.

# TODO: Add check against attributes in processHeaders
def processHeaders(file):
    headerRule = checkHeaders(file)

    if len(headerRule) > 0:
        msg.printWarning("These are not proper headers (doesn't check attribute names): ", headerRule)
    else:
        msg.printOkay("All columns passed.")

    return

#NOTE: iterates through skus once
#TODO: since itertuples gives us everything we should think about looping through it all once then checking (in the case that we have to process way too many products)
# break sku check into it's own function
def processFields(file):
    msg.printHeader("Missing SKU Check")
    items = list(file.itertuples())
    
    # NOTE: Sku processing lists
    # sku indexes that are empty
    skuIsEmpty = list()
    for item in items:
        # checking if sku is empty
        if (pd.isna(item.sku)):
            skuIsEmpty.append(item.Index)

    # once loop is done check our lists and print messages
    if len(skuIsEmpty) > 0:
        msg.printStop("MISSING: missing skus at these lines ", skuIsEmpty)
    else:
        msg.printOkay("No missing Skus")

    return

# if we add attributes check within this function we probably don't need the function, and we can just put the logic directly up
def checkHeaders(file):
    msg.printHeader("Header Check")
    headerSet = set(['country', 'brandname', 'sku', 'altsku', 'model', 'productname', 'upc', 'releasedate', 'productpageurl', 'imageurl', 'productgroup', 'category', 'map', 'tempmap', 'tempmapstartdate', 'tempmapenddate'])
    notProperHeader = list()

    for header in file.columns.values:
        if header not in headerSet:
            notProperHeader.append(header)
    
    return notProperHeader

# verifies data is in first sheet and checks if data exists in other sheets
def sheetCheck(filename):
    msg.printHeader("Sheet Data Check")
    file = pd.ExcelFile(filename)
    sheets = pd.ExcelFile(filename).sheet_names
    
    if file.parse(sheets[0]).empty:
        msg.printStop('The first excel sheet is empty.', f'Sheet Name: {sheets[0]}')  
    else: 
        msg.printOkay("The first sheet contains data.")
    
    if len(sheets) > 1:
        for sheet in sheets[1:]:
            if not file.parse(sheet).empty:
                msg.printStop('Data found outside of first sheet.', f'Sheet Name: {sheet}')  


# reads in json files and returns raw JSON
def readJSON(path):
    with open(path) as x:
        JSON = json.load(x)
    return JSON

# find column name using regex
def findColumnName(file, regex):
    columns = file.columns.values
    r = re.compile(regex)
    matches = list(filter(r.search, columns))
    return matches

#NOTE: Verifies country codes are valid
#TODO: adjust to also check lang codes
def checkCountryCodes(file):
    msg.printHeader("Country Code Check")
    LibccCodes = set(readJSON('data/code.json')["countryCodes"])
    feedccCodes = file[findColumnName(file, "country.*")[0]].tolist()
    invalidList = list()
    
    for i, x in enumerate(feedccCodes):
        x = x.lower()
        if x not in LibccCodes:
            invalidList.append(f"row {i + 2}: {x}")
            
    if invalidList:
        # Looks like we follow ISO 3166-2 with a few exceptions. I think I've seen UK used instead of GB       
        msg.printWarning("Currently ISO 3166-2 two letter codes are supported.", "Please see https://en.wikipedia.org/wiki/ISO_3166-2")
        msg.printStop(f'Ivalid country codes found:', "\n ".join(invalidList))
    if not invalidList: 
         msg.printOkay("Country codes are valid")

# finds duplicate skus within the columns provided. Used in dupCheck
def findDups(columns, file):
    skuHeader = findColumnName(file, "(sku)")[0]
    dups = file.duplicated(columns,keep=False)
    dupList = list()

    for key, value in dups.items():
        if value:
            dup = file.iloc[key][skuHeader]
            dupList.append(f"row {key + 2}: {dup}")        

    if dupList:
        msg.printStop(f'Duplicate skus found:', "\n ".join(dupList))
    if not dupList: 
         msg.printOkay("No duplicate skus found.")

# detects duplicates with in the specified fields
def dupCheck(file):
    msg.printHeader("Dup SKU Check")
    columns = findColumnName(file, "(country.*|brand.*|manufacturer|sku)")
    lang = findColumnName(file, "lang.*")
   
    if lang:
        columns.append(lang[0])
        findDups(columns, file)
                    
    if not lang:
        findDups(columns, file)

# checks that the imgs include http or https and are in a supported file format (jpg,jpeg,png)
def imageCheck(file):
    msg.printHeader("Image Check")
    imageColumn = findColumnName(file, "image.*")
    imageURLs = file[imageColumn[0]].tolist()
    httpErrors = list()
    typeErrors = list()
    
    for i, x in enumerate(imageURLs):
        try:           
            if not re.search("(http:\/\/|https:\/\/)", x):
                httpErrors.append(f"row {i + 2}: {x}") 
            if not re.search("(\.jpg|\.jpeg|\.png)", x):
                typeErrors.append(f"row {i + 2}: {x}") 
        except:
            # pass on nans
            pass
        
    if httpErrors:
        msg.printStop(f'Invalid or missing http:// or https://', "\n ".join(httpErrors))
            
    if typeErrors:
        msg.printStop(f'Invalid file format:', "\n ".join(typeErrors))
        msg.printWarning("Supported file formats jpg, jpeg, and png.")
        
    if not typeErrors and not httpErrors: 
         msg.printOkay("All images include http:// or https:// and are in a supported file format")

# prints list unique product groups for review
def productGroupReview(file):
    msg.printHeader("Product Group Check")
    PGcolumn = findColumnName(file, ".*group")[0]
    uniquePG = file[PGcolumn].unique()
    
    msg.printWarning('Please review the following products groups for accuracy.', 
                     "These product groups affect the functionality of the Where to Buy.\n Please notify your account manager when adding new product groups to the feed.")
    msg.printWarning(f'Current product groups:', "\n ".join(uniquePG))