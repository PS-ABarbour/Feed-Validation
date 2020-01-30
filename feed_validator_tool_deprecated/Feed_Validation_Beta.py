# Feed Validation tool that will handle PnG and all other Feeds (Beta Version 2.0)
# Program goal: To check for formating issues in uploaded feed.
# Output: Two files, One 'corrected feed' that will not have any blocking errors for importing a feed, and another that contains the errors found throughout the program. Errors will be separated by tabs. 
# To make into an executable, pip install pysintaller if you don't have module, then enter pyinstaller --windowed file.py in command prompt from the directory where the program is located. Will be in the 'dist' folder.
import pandas as pd
import csv
import os
import numpy as np
import validators
import requests
from urllib.request import *
from difflib import SequenceMatcher
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import *
from PIL import ImageTk, Image
import openpyxl
import xlrd

########################################################################################################################

def ref_files():
    country_codes = pd.read_excel('country_codes.xlsx')
    lDf = pd.read_excel('lang_codes.xlsx')


def browsefunc():
    global filename
    global directory
    directory = filedialog.askdirectory(initialdir=os.getcwd())
    os.chdir(directory)
    filename = filedialog.askopenfilename()
    head, tail = os.path.split(filename)
    pathlabel.config(text=tail)
    return tail

#######################################################################################################################


# Goal: iterate through all required columns in a excel and check for missing values (i.e. whitespace)

def getNaNs(feed,saved_feed):
    
    global Feed_Name
    global Feed_Errors_Name 
    global dummydf
    dummydf = pd.DataFrame()

    # Creating saved file name, reading in original feed, and potentially creating df for feed errors to pass to other functions.
    Feed_Input = saved_feed
    Feed_Name = Feed_Input + '.xlsx'
    Feed_Errors_Name = Feed_Input + '_Errors' + '.xlsx'
    df = pd.read_excel(feed, dtype={'sku': str})  
    df = df.replace("\n","",regex=True)
    

    # Will give rows that contain 'NaN' (empty values) anywhere in the file. Multiple try/excepts so no input from user is needed.
    try:
        dfbad = df.loc[df['country'].isna()]
    except KeyError:
        dfbad = df.loc[df['Country'].isna()]

    try:
        dfbad2 = df.loc[df['brandName'].isna()]
    except KeyError:
        dfbad2 = df.loc[df['manufacturerName'].isna()]

    try:
        dfbad3 = df.loc[df['sku'].isna()]
    except KeyError:
        dfbad3 = df.loc[df['SKU'].isna()]

    try:
        dfbad4 = df.loc[df['model'].isna()]
    except KeyError:
        dfbad4 = df.loc[df['Model'].isna()]

    dfbad5 = df.loc[df['productName'].isna()] # these column names are static for PnG feeds

    dfbad6 = df.loc[df['productGroup'].isna()]

    try:
        dfbad7 = df.loc[df['category'].isna()]
    except KeyError:
        dfbad7 = df.loc[df['Category'].isna()]


    
    # creating a full df with all bad data from required cols.
    dfbadfull = pd.concat([dfbad,dfbad2,dfbad3,dfbad4,dfbad5,dfbad6,dfbad7])
    dfbadfull_nan = dfbadfull.replace('nan','',regex=True)

    
    #creates a new data frame, and removes the 'bad data' from sheet
    dfgood = pd.concat([df, dfbadfull_nan]).drop_duplicates(keep=False)

    #Create an Errors sheet first, if no errors are found throughout program, delete it at the end of the program.
    if dfbadfull.empty:
        writer = pd.ExcelWriter(Feed_Errors_Name, engine='openpyxl', mode='w')
        dummydf.to_excel(writer, sheet_name = 'Sheet1', index = False)
        writer.save()
        writer.close()
    if not dfbadfull.empty:
        bad_data = file[file.index.isin(dfbadfull_nan.index)]
        writer = pd.ExcelWriter(Feed_Errors_Name, engine='openpyxl', mode='w')
        bad_data.to_excel(writer, sheet_name='Empty Cells in Required Columns', index = False)
        writer.save()
        writer.close()

    return dfgood, dfbadfull

#only function that will actually take in the name of the product feed:    


######################################################### DONE ##############################################################



# Image validation function
# Ensure provided image urls are actually URLs, and not broken. Caveat is some valid urls will get flagged. Validators.url() is not robust, but will work ~80% of the time. Other solutions have very long run times.

def badUrls(feed):
    
    file = feed
    file = file.astype(str)
    imageUrls = []
    fixedurls = []

# Image URLs Validation

    try:
        for url in file['imageURL']:
            fixedurls.append(url.replace(' ','%20'))

    except KeyError:
        for url in file['imageUrl']:
            fixedurls.append(url.replace(' ','%20'))

    for url in fixedurls:
        imageUrls.append(validators.url(url))

    imagedict ={'Image_Urls': imageUrls}
    imagedf = pd.DataFrame(imagedict,columns=['Image_Urls'])

# Pull out rows with non-valid urls in image 

    badiurls = imagedf[imagedf['Image_Urls'] != True]

# Here, match index from badiurls and main feed, pull all data in those rows into a bad data xslx file.
    bad_urls = file[file.index.isin(badiurls.index)]

#   dfgoodurls = pd.concat([file, bad_urls]).drop_duplicates(keep=False) # would drop invalid urls from main feed. Not needed at this point.
    
    if bad_urls.empty:
        pass      
        return file, bad_urls 
    if not bad_urls.empty:
        bad_urls_nan = file[file.index.isin(badiurls.index)].replace('nan','',regex=True)
        writer = pd.ExcelWriter(Feed_Errors_Name, engine='openpyxl', mode='a')
        bad_urls_nan.to_excel(writer, sheet_name='Invalid or Missing Image URLs', index = False)
        writer.save()
        writer.close()
        return file, bad_urls_nan

######################################################### DONE ##############################################################


# verifies upc is numeric and is 13-15 digits long. Takes in df and upc column name.
def upc_validation(df):
    badUPCs = []
    dataDict = df.to_dict('records')

    if 'UPC'.lower() in df.columns:
        try:
            upcColumnName = 'upc'
        except KeyError:
            upcColumnName = 'UPC'


        for x in dataDict:
            upcLen = len(str(x[upcColumnName]))
    #       append non numerical upc's to badUPCs
            try:
                x[upcColumnName] = int(float(x[upcColumnName]))
            except:
                badUPCs.append(x)
    #       verify length of upc
            if upcLen < 13 or upcLen > 15:
                if x not in badUPCs:
                    badUPCs.append(x)
                else:
                    pass
            else:
                pass
            
    #   remove upc's with nan or empty values. Since value is alound to be empty
        for item in badUPCs[:]:
            strUpc = str(item[upcColumnName])
            if strUpc == "nan" or strUpc == "":
                badUPCs.remove(item)
            else:
                pass
            
        for x in badUPCs:
            if x in dataDict[:]:
                dataDict.remove(x)
    #                 print(x)
            else:
                pass
            
    else:
        pass

    dfGood = pd.DataFrame(dataDict)
    dfBad =  pd.DataFrame(badUPCs)
    dfBad_nan = dfBad.replace('nan','',regex=True)


    if dfBad_nan.empty:
        pass
    if not dfBad_nan.empty:
        writer = pd.ExcelWriter(Feed_Errors_Name, engine='openpyxl', mode='a')
        dfBad_nan.to_excel(writer, sheet_name='Invalid UPCs', index = False)
        writer.save()
        writer.close() 


    return dfGood, dfBad

######################################################### DONE ##############################################################



# finds duplicate skus,altskus, or upc against country or lang. Accepts dataframe and column name as string
def dup_validation(df,thirdColumn=None):
    dataDict = df.to_dict('records')
# evaluates all possible col case sensitivity in try/except blocks.
    try:
        for columnName in df.columns.values:
            if columnName == 'SKU':
                dupColumnName = 'SKU'
            if columnName == 'sku':
                dupColumnName = 'sku'
            if columnName == 'Country':
                againstColumnName = 'Country'
            if columnName == 'country':
                againstColumnName = 'country'
        colNameList = [dupColumnName, againstColumnName]

    except UnboundLocalError:
        dupColumnName = 'sku'
        againstColumnName = 'Country'
        colNameList = [dupColumnName, againstColumnName]

    except KeyError:
        dupColumnName = 'sku'
        againstColumnName = 'Country'
        colNameList = [dupColumnName, againstColumnName]


    # colNameList = [dupColumnName, againstColumnName]

    
#   adds third column to list if needed
    if thirdColumn != None:
        colNameList.append(thirdColumn)
    
#   duplicated returns second instance of value as pd.series
    dup = df.duplicated(colNameList)
    
#   list of indexes to use in loc
    indexList = []
    
#   iterate through boolean duplicate data to return indexs of dups
    for key, value in dup.items():
        if value == True:
            indexList.append(key)
            
    dfClean = df.drop(df.index[indexList])
    
#   df of dups pulled by in dup
    dupDF = df.iloc[indexList]
    
    
######################################################################################################################
# logic to remove all instaces of dups. 

# #   Send df sku column to list
#     sku_list = dupDF[dupColumnName].tolist()
    
#     dupList = []
    
# #   find the dup and the original from df and append to list
#     for x in dataDict:
#         if x[dupColumnName] in sku_list:
#             dupList.append(x)


#     dfBaddup =  pd.DataFrame(dupList)           
######################################################################################################################

    dfGood = dfClean
    dfBad = dupDF.replace('nan','',regex=True) # changed from dupDF.replace

    if dfBad.empty:
        pass
        
    if not dfBad.empty:
        writer = pd.ExcelWriter(Feed_Errors_Name, engine='openpyxl', mode='a')
        dfBad.to_excel(writer, sheet_name='Duplicate Values', index = False)
        writer.save()
        writer.close()
                
    return dfGood, dfBad
    
######################################################### DONE ##############################################################




# takes in a list of good brands and a list of questionable brands and spits out a Dict of brands to replace
def comparison_swap(good, questionable):
    
    gthreshold = []
    qthreshold = [] 
    ratioDict = []

    
#   Creates two lists of the same len that are aligned via index based on character similarity.
    for g in list(good):
        for q in questionable:
            ratiothresh = SequenceMatcher(None, g, q).ratio()
            if ratiothresh > 0.50:
                gthreshold.append(g)
                qthreshold.append(q)
            else:
                pass
#     print(gthreshold,qthreshold,"\n")

#   Send to lowercasee for case insensitive comparison
    gL = (word.lower() for word in gthreshold)
    qL = (word.lower() for word in qthreshold)
    
#   loop grab ratio of each pair and change if necessary
    for index, (wordg, wordq) in enumerate(zip(gL,qL)):
#       check if values are the same before attempting the switch
        if qthreshold[index] is gthreshold[index]:
            same = True
        else:
            same = False
        
        ratio = SequenceMatcher(None, wordg, wordq).ratio()
        
#       switch the questionable brand to the good brand
        if ratio > 0.80 and same == False:
            replaced = qthreshold[index]
            qthreshold[index] = gthreshold[index]
        else:
            replaced = "N/A"
            
            
        ratioDict.append({
            "ratio": ratio, 
            "examined": gthreshold[index],
            "replaced": replaced,
            "with": qthreshold[index]})
    
    return ratioDict

#######################################################################################################################

# *** NOT A NECESSARY FUNCTION PER THE USER, NOT ADDED INTO FINAL FUNCTION ***

#  Potential problem here is that it will classify a one off category as an outlier and remove it, add this to potential errors.

def outlier_detect(df):

    dataDict = df.to_dict('records')
    q_brands = []
    g_brands = []
    brandDict = []

    try:
        brandColumnName = 'Category'
        #   count frequency of brands
        brandCounts = df[brandColumnName].value_counts()
    except KeyError:
        brandColumnName = 'category'
        #   count frequency of brands
        brandCounts = df[brandColumnName].value_counts()
    
# #   count frequency of brands
#     brandCounts = df[brandColumnName].value_counts()
    
#   stats for determining outliers
    mean = np.mean(brandCounts)
    cut_off = 0.10 * mean
    

#   append brand names to q_brand that appear less than 5 times in feed.
    for key, value in brandCounts.items():
        if value < cut_off:
            q_brands.append(key)
        else:
            g_brands.append(key)
            
#   See similar_brand_switch       
    flagged_brands = comparison_swap(g_brands, q_brands)
    
#   create list of rows that contain the question brand names.
    for x in dataDict:
        if x[brandColumnName] in q_brands:
            brandDict.append(x)
            
#   Replace brands in dataDict that have been id'd in flagged_brands for replacement
    for y in brandDict:
        for z in flagged_brands:
            if y[brandColumnName] == z["replaced"]:         
                y[brandColumnName] = z["with"]
                
    
    branddf = pd.DataFrame(dataDict)  
    
#   get value counts again. Send any stragglers to error df
    brandCounts2 = branddf[brandColumnName].value_counts()
    
    lowCountIndex = []
    
    for key, value in brandCounts2.items():
        if value < 2:
            indx = branddf.index[branddf[brandColumnName] == key].tolist()
            lowCountIndex.append(indx)  

#   flatten lowCountIndex that comes back as a 1x2 list
    flatList = []
    
    for sublist in lowCountIndex:
        for indx in sublist:
            flatList.append(indx)
            
    uncorrected = branddf.iloc[flatList].replace('nan','',regex=True)
    
    branddf = branddf.drop(flatList)


    if not uncorrected.empty:
        writer = pd.ExcelWriter(Feed_Errors_Name, engine='openpyxl', mode='a')
        uncorrected.to_excel(writer, sheet_name='Outlying Categories', index = False)
        writer.save()
        writer.close()

    if uncorrected.empty:
        pass
    
    return branddf, uncorrected
        

#######################################################################################################################

# verify country code are accurate and formated correctly. Returns good and bad df. Corrects code if not capitalized.

def country_code_validation(df):

    feed_path = os.path.join(directory,'Feed_Validator')
    feed_dir = os.chdir(feed_path)
    ccdf = pd.read_excel('country_codes.xlsx') # Code here is to call country and language code spreadsheets from the Feed Validator directory, switches back to choosen directory after files have been read.
    backdir = os.chdir(directory)

    dataDict = df.to_dict('records')
    badCountries = []
    
#   send the df columns to lists
    cCodes = ccdf["Code"].tolist()
    cNames = ccdf["Name"].tolist()
    
    for index, x in enumerate(dataDict):
        try:
            country = x["Country"]
        except KeyError:
            country = x["country"]

        CapitalTest = country.isupper()
        
#       Capitalizes names in order to make a match against cNames
        if CapitalTest == False and len(country) > 2:
            country = country.capitalize()
            
#       makes sure country codes are uppercased
        if len(country) == 2:
            x["Country"] = country.upper()
            
            # reassign country after the switch for later use       
            country = x["Country"]
            
#       change country name to country code if name in CNames   
        if country in cNames:
            nameIndex = cNames.index(country)
            x["Country"] = cCodes[nameIndex]
            
#       Send x to badCountries if not in cCodes and cNames
        elif country not in cCodes:
            badCountries.append(x)
            dataDict.remove(x)
            
    goodDf = pd.DataFrame(dataDict) 
    badDf = pd.DataFrame(badCountries).replace('nan','',regex=True)
   
    if not badDf.empty:
        writer = pd.ExcelWriter(Feed_Errors_Name, engine='openpyxl', mode='a')
        badDf.to_excel(writer, sheet_name='Invalid Country Codes', index = False)
        writer.save()
        writer.close()
    if badDf.empty:
        pass
  
    return goodDf, badDf

##################################################################################################################################################



def leading_zeros(df,baddf):

    try:
        for columnName in df.columns:
            if columnName == 'SKU':
                skuColumnName = 'SKU'
            if columnName == 'sku':
                skuColumnName = 'sku'
    except KeyError:
        skuColumnName = 'sku'
   
    
#   declared here so that when the function is not triggered the original df is returned
    lzDf = df
    
    dataDict = df.to_dict('records')
    
#   grab total number of rows
    skuCount = len(dataDict)
    
#   set threshold to trigger function
    triggerThreshold = skuCount * 0.60
    
    counter = 0

#   count num of skus with leading zeros
    for x in dataDict:
        
        sku = x[skuColumnName]
        
        skuLen = len(sku) - len(sku.lstrip('0'))
        
        if skuLen != 0:
            counter +=1
            
#   trigger function if counter exceeds thresh       
    if counter > triggerThreshold:
        
    #   get len counts
        lenCounts = df[skuColumnName].apply(len).value_counts()

    #   grab max count for len
        avLenMax = lenCounts.values.max()

    #   grab key for max count. This will be the actual len
        for key, value in lenCounts.items():
            if value == avLenMax:
                actualSkuLen = key

    #   add zeros to skus up to actualSkuLen. commentted out since this alters the df directly
#         lzdf[skuColumnName]= list(map(lambda x: x.zfill(actualSkuLen), lzdf[skuColumnName]))

    #   adds zeros to skus up to acutalSkuLen   
        for x in dataDict:
            sku = x[skuColumnName]
            sku = sku.zfill(actualSkuLen)
            x[skuColumnName] = sku
            
        lzDf = pd.DataFrame(dataDict)
        
    else:
        pass
    
    
    return lzDf, baddf

##################################################################################################################################################

# P&G specific block

# verify country code are accurate and formated correctly. Returns good and bad df
def lang_code_validation(df):

    feed_path = os.path.join(directory,'Feed_Validator')
    feed_dir = os.chdir(feed_path)
    lcdf = pd.read_excel('lang_codes.xlsx')    # Code here is to call country and language code spreadsheets from the Feed Validator directory, switches back to choosen directory after files have been read.
    backdir = os.chdir(directory)

    dataDict = df.to_dict('records')
    badCountries = []
    errors_df = pd.read_excel(Feed_Errors_Name)

    lCodes = lcdf["639-1"].tolist()
    lNames = lcdf["ISO language name"].tolist()
    
    lCodes = [x.upper() for x in lCodes]
    
    for index, x in enumerate(dataDict):
        
        lang = x["resourceLanguage"]
        
        CapitalTest = lang.isupper()
        
#       Capitalizes names in order to make a match against cNames
        if CapitalTest == False and len(lang) > 2:
            lang = lang.capitalize()
            
#       makes sure country codes are uppercased
        if len(lang) == 2:
            x["resourceLanguage"] = lang.upper()
            
            # reassingn country after the switch for later use       
            lang = x["resourceLanguage"]
            
#       change country name to country code if name in CNames   
        if lang in lNames:
            nameIndex = lNames.index(lang)
            x["resourceLanguage"] = lCodes[nameIndex]
            
#       Send x to badCountries if not in cCodes and cNames
        elif lang not in lCodes:
            badCountries.append(x)
            dataDict.remove(x)
            
    goodDf = pd.DataFrame(dataDict) 
    badDf = pd.DataFrame(badCountries).replace('nan','',regex=True)
    if badDf.empty:
        pass
    if not badDf.empty:
        writer = pd.ExcelWriter(Feed_Errors_Name, engine='openpyxl', mode='a')
        badDf.to_excel(writer, sheet_name='Invalid Language Codes', index = False)
        writer.save()
        writer.close()
   
        
   
    return goodDf, badDf


##################################################################################################################################################

# P&G specific block

# validate product group, specific to PG. Most likely optional for other clients.
def productGroup_validation(df, columnName, brandColumnName):
    
    dataDict = df.to_dict('records')
    errors_df = pd.read_excel(Feed_Errors_Name)

    badPG = []
    
    for x in dataDict:
        pg = x[columnName]
        country = x["Country"]
        brand = x[brandColumnName]
        countryBrand = f"{country} {brand}"
       
        if pg != countryBrand:
            badPG.append(x)
            
    for y in badPG:
        if y in dataDict:
            dataDict.remove(y)
                
    
    goodpg = pd.DataFrame(dataDict)
    badPG = pd.DataFrame(badPG).replace('nan','',regex=True)

    if badPG.empty:
        pass
    if not badPG.empty:
        writer = pd.ExcelWriter(Feed_Errors_Name, engine='openpyxl', mode='a')
        badPG.to_excel(writer, sheet_name='Invalid Product Groups', index = False)
        writer.save()
        writer.close()

    
    return goodpg, badPG
##################################################################################################################################################
##################################################################################################################################################
# General feed validation function


def General_Feed_Validation(feed,saved_feed):
    
    goodfeed, badfeed = getNaNs(feed,saved_feed)
    goodfeed2, badfeed2 = badUrls(goodfeed)
    goodfeed3, badfeed3 = upc_validation(goodfeed2)
    goodfeed4, badfeed4 = dup_validation(goodfeed3,thirdColumn=None)
    goodfeed5, badfeed5 = leading_zeros(goodfeed4,badfeed4) # function doesn't need do anything to badfeed4, just there to avoid errors. Badfeed5 is ultimately skipped as it is the same as badfeed4.
    goodfeed6, badfeed6 = country_code_validation(goodfeed5)

    dfbadfull = pd.concat([badfeed,badfeed2,badfeed3,badfeed4,badfeed6])


# Final Feed Conditional:

    if not dfbadfull.empty:

        cols = goodfeed.columns.tolist()
     
        if cols[0] != 'Country':
            message = 'Errors found, please review exported files.\nCountry is not the first column in the feed\nor is lowercase.'
        
        else:
            message = 'Errors found, please review exported files.'

        Feed_Corrected = goodfeed6
        Feed_Corrected_nan = Feed_Corrected.replace('nan','',regex=True)
        writer = pd.ExcelWriter(Feed_Name, engine='openpyxl', mode='w')
        Feed_Corrected_nan.to_excel(writer, sheet_name='Sheet1', index = False)
        writer.save()
        writer.close()

        # Removing dummy sheet1 when there are errors present within the sheet.
        wb = openpyxl.load_workbook(Feed_Errors_Name)
        names = wb.get_sheet_names()
        for name in names:
            if name == 'Sheet1':
                rmvs = wb.get_sheet_by_name(name)
                wb.remove_sheet(rmvs)
                wb.save(Feed_Errors_Name)
            else:
                pass

# If no errors found within the program, get rid of the error dummy file.
    if dfbadfull.empty:
        os.remove(Feed_Errors_Name)
        message ='No errors found in feed.'

    result['text'] = message

##################################################################################################################################################
# P&G feed validation function

def PNG_Feed_Validation(feed,saved_feed):

    goodfeed, badfeed = getNaNs(feed,saved_feed)
    goodfeed2, badfeed2 = badUrls(goodfeed)
    goodfeed3, badfeed3 = upc_validation(goodfeed2)
    goodfeed4, badfeed4 = dup_validation(goodfeed3, thirdColumn=None)
    goodfeed5, badfeed5 = country_code_validation(goodfeed4)
    goodfeed6, badfeed6 = lang_code_validation(goodfeed5)
    goodfeed7, badfeed7 = productGroup_validation(goodfeed6, "productGroup", "manufacturerName")

    dfbadfull = pd.concat([badfeed,badfeed2,badfeed3,badfeed4,badfeed5,badfeed6,badfeed7])

# Final Feed Conditionals:

    if not dfbadfull.empty:

        cols = goodfeed.columns.tolist()
     
        if cols[0] != 'Country':
            message = 'Errors found, please review exported files.\nCountry is not the first column in the feed\nor is lowercase.'
        
        else:
            message = 'Errors found, please review exported files.'

        Feed_Corrected = goodfeed7
        Feed_Corrected_nan = Feed_Corrected.replace('nan','',regex=True)

        writer = pd.ExcelWriter(Feed_Name, engine='openpyxl', mode='w')
        Feed_Corrected_nan.to_excel(writer, sheet_name='Sheet1', index = False)
        writer.save()
        writer.close()

        # Removing dummy sheet1 when there are errors present within the sheet.
        wb = openpyxl.load_workbook(Feed_Errors_Name)
        names = wb.get_sheet_names()
        for name in names:
            if name == 'Sheet1':
                rmvs = wb.get_sheet_by_name(name)
                wb.remove_sheet(rmvs)
                wb.save(Feed_Errors_Name)
            else:
                pass

# If no errors found within the program, get rid of the error dummy file.
    if dfbadfull.empty:
        os.remove(Feed_Errors_Name)
        message ='No errors found in feed.'

    result['text'] = message

##################################################################################################################################################

# Main()

def Validate_Feed(feed, saved_feed):

    try:
        if 'PnG' in feed:
            PNG_Feed_Validation(feed,saved_feed)
        else:
            General_Feed_Validation(feed,saved_feed)


    except KeyError:
        result['text'] = 'Error reading uploaded file.\nUnidentified column name.'
    except UnboundLocalError:
        result['text'] = 'Error reading uploaded file.\nFile may be corrupt.'
    except xlrd.XLRDError:
        result['text'] = 'Unsupported file type or corrupt file.'
    except FileNotFoundError:
        result['text'] = 'Required files not found in current directory.'



##################################################################################################################################################
# Initial GUI

root = Tk()
root.configure(bg='#6f7b91') 
root.title('Feed Validator')
canvas = Canvas(root, width=1000, height=1000,bg='#6f7b91')

# Main Frame
frame = Frame(root,bg='#6f7b91',width=10, height=10) 
frame.place(relx=0.5, rely=0.1,relwidth=0.8,relheight=0.8, anchor=N)

File_name = Label(frame, text='Choose File (.xlsx): ', font=('Helvetica',11), fg='white' ,bg='#6f7b91')
File_name.grid(row=1,column=0,padx=25,pady=5)

pathlabel = Label(frame,font=('Helvetica',9),anchor=NW,fg='white' ,bg='#6f7b91')
pathlabel.place(relx=0.3,rely=0.04,relwidth=1,relheight=0.2) 

browsebutton = Button(frame, text="        Browse        ",font=('Helvetica',11),fg='white' ,bg='#7f8fa4', command=lambda: browsefunc())
browsebutton.place(relx=0.77,rely=0.1)

saved_name = Label(frame, text='Save Feeds As: ',font=('Helvetica',11),anchor=NW,fg='white' ,bg='#6f7b91')
saved_name.grid(row=2,column=0,padx=5,pady=5)

saved_name_entry = Entry(frame,font=('Helvetica',11), fg='white',bg='#b8b7b7')
saved_name_entry.config(insertbackground='white')
saved_name_entry.grid(row=2,column=1)

run_button = Button(frame, text='    Validate Feed   ',font=('Helvetica',11),fg='white' ,bg='#7f8fa4',command=lambda: Validate_Feed(filename,saved_name_entry.get()))
run_button.place(relx=0.77,rely=0.4)

result_box = Label(frame, text='Result: ',font=('Helvetica',11),fg='white' ,bg='#6f7b91')
result_box.grid(row=3,column=0)

result = Label(frame,font=('Helvetica',10), anchor=NW, justify='left',bd=4,fg='white' ,bg='#6f7b91')
result.place(relx=0.3, rely=0.45)

tm_label = Label(root, text='© PriceSpider 2005-2019',font=('Helvetica',8),fg='white' ,bg='#6f7b91')
tm_label.place(relx=0,rely=1,anchor=SW)

root.geometry('720x175')
root.mainloop()

