import pandas as pd
import lib.messages as msg
import re

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
    headerSet = set(['country', 'brandname', 'sku', 'altsku', 'model', 'productname', 'upc', 'releasedate', 'productpageurl', 'imageurl', 'productgroup', 'category', 'map', 'tempmap', 'tempmapstartdate', 'tempmapenddate'])
    notProperHeader = list()

    for header in file.columns.values:
        if header not in headerSet:
            notProperHeader.append(header)
    
    return notProperHeader