# Feed-Validation

Program goal: To check for formatting issues in uploaded feed.
Output: Two files, One 'corrected feed' that will ideally have no blocking errors for importing a feed, and another that contains the errors found throughout the program.

Requirements for Optimal Use:

Feed_Validation directory contains 7 files:
1) _pycache_
2) build
3) Application_Files
4) country_codes.xlsx
5) lang_codes.xlsx
6) Feed_Validation_Beta > actual .exe
7) Feed_Validation_Beta.spec

All of these files MUST be within the Feed_Validator file (or whatever you choose to name the file) in order for the program to function properly. If files are not within this directory you may get a "Required files not found" error, or no output at all.

The actual .exe will be located within Application_Files > Feed_Validation_Beta > Feed_Validation_Beta.exe (file type is Application). For easier access, pin this application to your taskbar.

The Feed_Validation directory can be placed anywhere on your computer. When you select a file, the output files (if any), will be exported to the directory where your selected file is.

How to use:

1) Choose a feed (.xlsx) file to upload to the program via the browse button. 
2) In "Save Feeds As:" enter a name you wish to save the feeds under.
3) Hit Validate!
4) If there are any errors, the two files will be exported to the directory where your choosen file lives. They will be named after what you inputted in 2). The error file name will be called Saved_File_name_Errors.

That's it!

