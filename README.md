# List of Features to Implement for an Excel Product Feed Validator
These should be typical checks that the validator can handle before having user input.

- [x] Create list!
- [x] Check column names against the default feed
- [] Check data is appearing in first Sheet
- [] Check country codes are valid abbreviations
- [] Check `sku` column is text field (if possible with pandas)
- [x] Check `sku` is present in all rows
- [] Check `sku` has no delimiters (i.e. commas, pipe, etc.)
- [] Check `upc` is valid format (can copy over rule from importer)
- [] Check if product image is of `jpg`, `jpeg`, `png` format
- [] Check if product image includes `https://` or `http://`
- [] If `action` column is present, check if every product has an action value
- [] Check for excel `Number` fields and spit out warning (should be Text field)
- [] Check `sku` has no duplicates within the feed (except when we have translations or different countries)
- [] Check all fields don't have new lines (if possible)
- [] Check against typical selectors ? (how do we get the right name unless we standardize a feed)
    - [] gather a list of typical selectors ? (based on data in system)
- [] Check that if a product has a selector value then all product rows after should have a value
- [] Should print out a list of unique product groups for the user to verify against Widget in Affiliate Portal ? (not sure yet since product group can change depending on the ask)

# How To Run

To start the virtual environment

`$ source venv/bin/activate .`

Then it should read

`(venv) My-Laptop-Name:Feed-Validation username$`

Install dependencies in the virtual environment

`(venv) $ pip3 install -r requirements.txt`

To end the virtual environment

`$ deactivate`
