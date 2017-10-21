# My Solution Details

## Technology

I was informed by my recruiter that I could use **Python (3.\*)** (my primary language) if I wanted to. I have not written Java in a few years and didn't want to waste too much time relearning best practises to complete this challenge.

The code uses no 3rd party libraries. 

## How to Run the Code

1. Install some version of Python3. I am using 3.5.3
2. Run `python data_normaliser.py` from the `lorica_challenge` folder
3. Output files will appear in the root folder. Copies of the output can be found in `lorica_challenge/outputfiles`
4. Unittests - `python -m unittest`

## Command Line Output 

This is the output from my command line when I run the code. It informs the user which records had invalid data in it and why.

```
ashwinramesh@Ashwins-MBP  ~/Projects/lorica_challenge   master ●✚  python data_normaliser.py
ERROR - Error converting record to Transaction (Error: Invalid value for FundCoverAmount): Row 11
ERROR - Errors: 1
CSV file created - ABC-normalised.csv
 
 
ERROR - Error converting record to Transaction (Error: Invalid value for FundCover): Row 11
ERROR - Error converting record to Transaction (Error: Invalid value for LastName): Row 18
ERROR - Error converting record to Transaction (Error: Invalid value for FirstName): Row 20
ERROR - Error converting record to Transaction (Error: Invalid value for DateClaimed): Row 25
ERROR - Errors: 4
CSV file created - Coverall-normalised.csv
```

## Architecture of my Solution

### Transaction

The `Transaction` object was implemented to hold the valid state of a normalised record. This meant that all fields would be of the correct data type (date, str, int, float) and needed no further validation.

### TransactionsCSVWriter

The `TransactionsCSVWriter` had the role of formatting `Transaction` sets into valid output strings and create a CSV file.

The implementation of this class was designed to allow for future configuration in the event that data formats change (i.e dates) or ordering for fields in the CSV change.

The class takes a list of `Transaction` objects, which have been constructed from raw customer data and write rows of CSV data into a user given file.

### AbstractCustomerToTransactionCSVConverter

The `AbstractCustomerToTransactionCSVConverter` was the most challenging part of this task. I had to reimplement parts of my solution until I was satisfied with my solution.

The main goal of this class is to take any CSV row (raw) and be able to extract out field information, perform validation and finally create a `Transaction` object as an output (if the data was valid).

Additionally, I wanted to notify users on what row number and what field errors occured. This allows the programmer, in the future, to see what edge cases were not dealt with in writing the converter and allow them to patch their solution much easier.

To solve this, I created one method for each field required, which defined how to extract the data and how to validate it. The generic usecase was simply to ensure that the field was not empty and return the extracted data. However, in the `Coverall` file, I had to construct the `FirstName` by concatenating the `FirstName` field with the `MiddleName` field. This solution allows for extrending the converter to deal with various data formats from the various users. 

### ABCConverter and CoverallConverter

These two implementation classes were very simple to write once I nailed the implementation of the previous converter class. All that was required was to pass in the valid fieldname to the extractor/validator methods and write and bespoke methods if the data wasn't exactly in the format required.
