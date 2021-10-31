# CsvFileDataRecon
Created on 30-Jan-2021
Last updated on 06-Feb-2021
@author: Mathanaguru
Purpose: Utility to compare .csv files into two folders
Change history
31-Jan-2021:
    1. Replaced merge with concat for performance
    2. Added timer
    3. Gracefully ends for the file if the measure name is not value
    4. Renamed the match and mismatch file name to reduce its length
06-Feb-2021:
    1. Modified the process time format
    2. Column name, order and datatype validation added
    3. Output directory exists validation added
10-Mar-2021:
    1. Final user input to allow the user to see the results when run as .exe
    2. Minor changes to the variable names
    3. Gracefully skip to next filecompare if issues with current one
    4. Some of the core program has been moved to a Class Function


Limitations:
    1. Restricted to .csv file format
    2. Source file and target file should be the same, but the files should in different directories
    3. .csv files should be kept as direct children in the user provided directory path
    4. Files should be in flat structure: measure should be in just 1 column
    5. Measure file/column name should be 'Value' as it is hardcoded in the code
    6. Without the measure value, each record should be unique

Key Points:
    1. '\' is used as line wrapper
