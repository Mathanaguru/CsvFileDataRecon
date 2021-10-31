 # -*- coding: utf-8 -*-
"""
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

"""
#*****************************************************************************
#  Import the modules required for the program
#*****************************************************************************
# To check for file availability and get basefile name
import os

# To exit the program
import sys

# To use the logging
import logging

# To get the current date and time
from datetime import datetime
now = datetime.now() # Get the current timestamp

# To get the file name without extension
from pathlib import Path

# To print the summary Stats file header record
import csv

# To import csv files and compare them
import pandas as pd

#*****************************************************************************
#  Setup logging
#*****************************************************************************
# Default logging level is set as info
logging.basicConfig(filename='python.log', level=logging.INFO,
                    format='%(asctime)s:python program file name-%(filename)\
                        s:%(funcName)s:%(name)s:%(levelno)s:%(levelname)\
                        s:%(lineno)d:%(thread)d:%(threadName)\
                        s:%(process)d:%(processName)\
                        s:%(module)s:%(message)s')

# Program start log
logging.info('Program execution starts')

#*****************************************************************************
#  Initialize Flags/Variables
#*****************************************************************************
# Flags - Exit program
exit_program_flag = 0

#*****************************************************************************
#  Define class(s)
#*****************************************************************************
class InputDirectoryValidations:
    '''Validate the user input directories'''
    def __init__(self,dir_path, dir_type):
        ''' Initialize directory path and directory type (source/target)'''
        self.dir_path = dir_path
        self.dir_type = dir_type

    def dir_check_exists(self):
        '''Check if the directory exists'''
        if os.path.isdir(self.dir_path):
            exit_program_flag = 0
            logging.info(f"{self.dir_type} directory exists validation has \
passed: A directory with user provided {self.dir_type} directory name exists")
        else:
            exit_program_flag = 1
            logging.critical(f"Error, a directory with user provided \
{self.dir_type} directory name does not exists")
        return exit_program_flag

    def dir_check_empty(self):
        '''Check if the directory is empty'''
        if os.listdir(self.dir_path):
            exit_program_flag = 0
            logging.info(f"{self.dir_type} directory empty validation has \
passed:A directory with user provided {self.dir_type} directory is not empty")
        else:
            exit_program_flag = 1
            logging.critical(f"Error, a directory with user provided \
{self.dir_type} directory name is empty")
        return exit_program_flag

    def dir_check_csv(self):
        '''Check if the directory has at lease one .csv file'''
        # The program has to exit, if directory does not have any .csv files
        exit_program_flag = 1
        for object in os.listdir(self.dir_path):
            if object.lower().endswith('.csv'):
                 exit_program_flag = 0
                 break
        if exit_program_flag == 0:
            logging.info(f"{self.dir_type} directory has at least \
one .csv file validation has passed")
        else:
            logging.critical(f"Error, {self.dir_type} directory \
does not even have a .csv file")
        return exit_program_flag

class CompareDirectoriesValidation:
    '''Compare the source and target directory - validations,
source and target file by its name, and check for .csv'''

    def __init__(self, source_dir, target_dir, output_dir):
        '''Initialize source directory, target directory, output directory'''
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.output_dir = output_dir

    def dirs_are_same(self):
        '''Check if the source and target directory is the same'''
        if self.source_dir != self.target_dir:
            exit_program_flag = 0
            logging.info("Source and target directory is not the same \
validation has passed: Source and target files are different")
        else:
            exit_program_flag = 1
            msg = 'Error, source and target directory should not be the same'
            logging.critical(msg)
        return exit_program_flag

class ObjectList:
    '''Get the list of objects in a directory'''
    def __init__(self,dir_path, dir_type):
        ''' Initialize directory path and directory type (source/target)'''
        self.dir_path = dir_path
        self.dir_type = dir_type
    
    def object_list(self):
        '''Get the list of objects in a directory'''
        objects = os.listdir(self.dir_path)
        logging.info(f"{self.dir_type} directory object list is {objects}")
        return objects

class SummaryFileOutput:
    '''Export the comparison results to a summary file'''
    
    def __init__(self,dir_path, fullfilename, obj_list, sno):
        '''Initiate output directory,summary full file name, \
unique object list, and S.No '''
        self.dir_path = dir_path
        self.fullfilename = fullfilename
        self.obj_list = obj_list
        self.sno = sno

    def print_summary_file_header(self):
        '''Print the header in the summary file '''
        # Header record
        header=['S.No',
                'Source Object Name',
                'Target Object Name',
                'Source Object Directory & Path',
                'Target Object Directory & Path',
                'Source Object Exists - Flag',
                'Target Object Exists - Flag',
                'Source & Target Object is csv - Flag',
                'Reconciliation Performed - Flag',
                'Date & Time',
                'No. of records in Source File',
                'No. of records in Target File',
                'No. of Match records',
                'No. of Mismatch records',
                'Dataset Match - Flag',
                'Location of Match records',
                'Location of Mismatch records',
                'Remarks',
        ]

        # Print the header record
        if len(self.obj_list)>0:
            with open(self.fullfilename,"w", newline='') as f:
                writer = csv.writer(f, delimiter=',')
                # Write to Summary Stats file in default, overwrite mode
                writer.writerow(header) # write the header
        return header
    
    def sort_summary_file_by_sno(self):
        ''' Read the file, then sort data by S.No series/column value'''
        # Load the file to a datadrame
        df = pd.read_csv(self.fullfilename)
        logging.debug(f"Summary Stats file,{self.fullfilename},\
output without formating is:\n{df}")
        # Sort the data by S.No column value
        df.sort_values(by=[self.sno]).to_csv(self.fullfilename, index=False)
        return df
    

class CompareFiles:
    '''Compare the file, including source and target file check validations'''

    def __init__(self, source_file, target_file,
                 output_dir, summary_stats_fullfilename, sno):
        '''Initialize source file, target file, and measure name'''
        self.source_file = source_file
        self.target_file = target_file
        self.output_dir = output_dir
        self.summary_stats_fullfilename = summary_stats_fullfilename
        self.sno = sno

    def csv_file_recon(self):
        '''Compare two .csv files and export the reconciliation results'''

        # Set the initial flag as files are comparable
        files_comparable = 1

        #*********************************************************************
        #  File attributes
        #*********************************************************************
        output_filename_creation_begin_time = datetime.now()

        ## Export file name is the combination of source and target file
        # Get file name without extension
        # To construct the compare output file name
        source_file_name_wo_ext = Path(self.source_file).stem
        msg = 'Source file name without extension is'
        logging.debug(f"{msg} {source_file_name_wo_ext}")
        msg = 'Target file name without extension is'
        target_file_name_wo_ext = Path(self.target_file).stem
        logging.debug(f"{msg} {target_file_name_wo_ext}")

        # Data match export file name and directory
        match_data_file_name = source_file_name_wo_ext+ ' - match records.csv'
        logging.debug(f"Match data file name is {match_data_file_name}")
        match_data_full_file_name = os.path.join(self.output_dir,
                                                 match_data_file_name)
        msg = 'Match data file name with directory path is'
        logging.info(f"{msg} {match_data_full_file_name}")
        # Data mismatch export file name and directory
        mismatch_data_file_name = (source_file_name_wo_ext
                                   +
                                   ' - mismatch records.csv')
        logging.debug(f"Mismatch data file name is {mismatch_data_file_name}")
        mismatch_data_full_file_name = os.path.join(self.output_dir,
                                                    mismatch_data_file_name)
        msg = 'Mismatch data file name with directory path is'
        logging.info(f"{msg} {mismatch_data_full_file_name}")

        output_filename_creation_end_time = datetime.now()
        output_filename_creation_process_time = (
            output_filename_creation_end_time
            -
            output_filename_creation_begin_time)
        logging.info(f"Output file names created in \
{output_filename_creation_process_time.total_seconds()} seconds")

        #*****************************************************************
        #  Load the source and target file in a DataFrame and Compare
        #*****************************************************************

        # Read csv time ounter begins
        read_csv_begin_time = datetime.now()

        #Read the source and target .csv files
        source_df = pd.read_csv(self.source_file)
        logging.debug(f"Source file data read in dataframe:\n{source_df}")
        target_df = pd.read_csv(self.target_file)
        logging.debug(f"Target file data read in dataframe:\n{target_df}")

        # Read file processing time
        read_csv_end_time = datetime.now()
        read_csv_process_time = read_csv_end_time - read_csv_begin_time
        msg = 'Source and Target csv files read in'
        logging.info(f"{msg} {read_csv_process_time}")

        # Record time counter begins
        no_of_records_count_begin_time = datetime.now()

        # Get the length of source and target file
        no_source_records = len(source_df)
        logging.info(f'Number of records in source file:{no_source_records}')
        no_target_records = len(target_df)
        logging.info(f'Number of records in target file:{no_target_records}')

        # Record count file processing time
        no_of_records_count_end_time = datetime.now()
        no_of_records_count_process_time = (no_of_records_count_end_time
                                            -
                                            no_of_records_count_begin_time)
        logging.info(f"Number of records in source file and target file \
processed in {no_of_records_count_process_time.total_seconds()} seconds")

        # Set index time counter begins
        set_index_begin_time = datetime.now()

        # Source - Get all the index columns,
        # except for the Value/Values as concat_col
        # If a column with the name value does not exist,
        # then skip file recon and export summary stats with remarks
        source_measure_name_value_found_flag = 0
        source_col_names = source_df.columns
        source_concat_key = []
        for source_col_name in source_col_names:
            val = ['value','values']
            if source_col_name.lower() not in val:
                source_concat_key.append(source_col_name)
            else:
                source_measure_name_value_found_flag = 1
                source_measure_name = source_col_name

        # Target - Get all the index columns,
        # except for the Value/Values as concat_col
        target_measure_name_value_found_flag = 0
        target_col_names = target_df.columns
        target_concat_key = []
        for target_col_name in target_col_names:
            val = ['value','values']
            if target_col_name.lower() not in val:
                target_concat_key.append(target_col_name)
            else:
                target_measure_name_value_found_flag = 1
                target_measure_name = target_col_name

        # Set the intial value of remarks as None
        remarks = None
        # Check, if the column names match and are in same order
        # For the specific use case, column order should match too
        col_match_flag = 1 if (source_col_names == target_col_names).all() else 0
        if 0 in [col_match_flag]:
            files_comparable = 0
            remarks = 'Error, source and target file name column or their \
order does not match'

        # Check if source and target measure name is value(s)
        elif 0 in [source_measure_name_value_found_flag,
                 target_measure_name_value_found_flag]:
            files_comparable = 0
            remarks = "Error, both source & target measure name \
should be 'Value(s)'"

        else:
            source_measure_dtype = source_df[source_measure_name].dtypes
            target_measure_dtype = target_df[target_measure_name].dtypes
            if source_measure_dtype != target_measure_dtype:
                files_comparable = 0
                remarks = "Error, source & target measure data type \
does not match"

        if files_comparable == 0:
            logging.info(remarks)
            print(remarks)
            summary_stats_set_n_export_begin_time = datetime.now()
            #*****************************************************************
            #  Export the summary stats - for partial comparison done
            #*****************************************************************
            summary_stats_data = {'S.No': [self.sno],
                                  'Source Object Name': [source_file_name_wo_ext],
                                  'Target Object Name': [target_file_name_wo_ext],
                                  'Source Object Directory & Path': [self.source_file],
                                  'Target Object Directory & Path': [self.target_file],
                                  'Source Object Exists - Flag': 1,
                                  'Target Object Exists - Flag':1,
                                  'Source & Target Object is csv - Flag': 1,
                                  'Reconciliation Performed - Flag': 0,
                                  'Date & Time': [datetime.now()],
                                  'No. of records in Source File': [no_source_records],
                                  'No. of records in Target File': [no_target_records],
                                  'No. of Match records': None,
                                  'No. of Mismatch records': None,
                                  'Dataset Match - Flag': None,
                                  'Location of Match records': None,
                                  'Location of Mismatch records': None,
                                  'Remarks': remarks
                                  }

        else:
            msg = 'Original Source file measure name is'
            logging.info(f"{msg} {source_measure_name}")
            msg = 'Original Target file measure name is'
            logging.info(f"{msg} {target_measure_name}")
            msg = 'Source and Target files are comparable'
            print(msg)

            # Source - Set the concat_col as the multi-index
            source_df = source_df.set_index(list(source_concat_key))
            msg = 'Source dataframe with concat key set as index:'
            logging.debug(f"{msg}\n{source_df}")

            # Target - Set the concat_col as the multi-index
            target_df = target_df.set_index(list(target_concat_key))
            msg = 'Target dataframe with concat key set as index:'
            logging.debug(f"{msg}\n{target_df}")

            # Set index processing time
            set_index_end_time = datetime.now()
            set_index_process_time = set_index_end_time - set_index_begin_time
            logging.info(f"Multi-index set for both source and target \
dataframe in {set_index_process_time.total_seconds()} seconds")

            # Check if source = target
            overall_match_begin_time = datetime.now()
            overall_match = source_df.equals(target_df)
            overall_match = 1 if overall_match==True else 0

            if overall_match:
                logging.info('Overall reconciliation result: Number of \
records and Each data in the source file match with the target file')
            else:
                logging.info('Overall reconciliation result: Atleast some \
source and target file data does not match')

            overall_match_end_time = datetime.now()
            overall_match_process_time = (overall_match_end_time
                                          -
                                          overall_match_begin_time)
            logging.info(f"Overall match result is processed in \
{overall_match_process_time.total_seconds()} seconds")
            print(f"Overall match result is {overall_match} - processed in \
{overall_match_process_time.total_seconds()} seconds")

            # Rename column time counter begins
            rename_column_begin_time = datetime.now()

            # Rename the value column as Source_Value and Target_Value
            source_df = source_df.rename(
                columns={source_measure_name:"Source_Value"})
            target_df = target_df.rename(
                columns={target_measure_name:"Target_Value"})

            # Rename column processing time
            rename_column_end_time = datetime.now()
            rename_column_process_time = (rename_column_end_time
                                          -
                                          rename_column_begin_time)
            logging.info(f"Measure columns renamed in \
{rename_column_process_time.total_seconds()} seconds")

            # Concat time counter begins
            concat_begin_time = datetime.now()

            # Combine the source and target file data with outer join
            #combined_df = pd.merge(source_df,target_df, left_index=True,
            #right_index=True, how='outer')
            combined_df = pd.concat([source_df,target_df], axis=1)
            msg='Source and target comnbined dataframe:'
            logging.debug(f"{msg}\n{combined_df}")
            concat_records = len(combined_df)
            msg = 'Number of records in the merged file is'
            logging.info(f"{msg} {concat_records}")

            # Concat processing time
            concat_end_time = datetime.now()
            concat_process_time  = concat_end_time - concat_begin_time
            logging.info(f"Source and Target Concatenated in \
{concat_process_time.total_seconds()} seconds")

            # Match column creation time counter begins
            match_col_create_begin_time = datetime.now()

            # Create a new column, Match
            # If either/both source and target measure value is None,
            # then Match is set as False by default
            combined_df['Match'] = (combined_df.loc[:,'Source_Value']
                                    ==
                                    combined_df.loc[:,'Target_Value'])
            logging.debug(f"Combined dataframe prior to null records \
exception:\n{combined_df}")

            # Match column creation processing time
            match_col_create_end_time = datetime.now()
            match_col_create_process_time = (match_col_create_end_time
                                             -
                                             match_col_create_begin_time)
            logging.info(f"Match column creation processed in \
{match_col_create_process_time.total_seconds()} seconds")

            # Match column update time counter begins
            match_col_update_begin_time = datetime.now()

            # If both the source and target measure value is None,
            # then update the Match flag as True
            combined_df.loc[(combined_df['Source_Value'].isnull() == True) & (combined_df['Target_Value'].isnull() == True), 'Match'] = True
            logging.debug(f"Combined dataframe post to null records exception:\n{combined_df}")

            # Match column update processing time
            match_col_update_end_time = datetime.now()
            match_col_update_process_time = (match_col_update_end_time
                                             -
                                             match_col_update_begin_time)
            logging.info(f"Match column update for null data processed in \
{match_col_update_process_time.total_seconds()} seconds")

            #*****************************************************************************
            #  Export the match and mismatch data to respective files
            #*****************************************************************************
            # Export the data, only when match/mismatch data is available
            logging.info("Match/Misatch file is created, \
only when the corresponding dataset exist")
            # Comparison #records time counter
            no_of_compare_records_count_begin_time = datetime.now()

            match_records = len(combined_df[combined_df['Match']==True])
            mismatch_records = len(combined_df[combined_df['Match']==False])

            # Comparison #records processing time
            no_of_compare_records_count_end_time = datetime.now()
            no_of_compare_records_count_process_time = (
                no_of_compare_records_count_end_time
                -
                no_of_compare_records_count_begin_time)
            logging.info(f"Count of mismatch and match records is processed \
in {no_of_compare_records_count_process_time.total_seconds()} seconds")
            print(f"Count of mismatch records is {mismatch_records} and \
match records is {match_records}, processed in \
{no_of_compare_records_count_process_time.total_seconds()} seconds")

            # Match data export time counter begins
            match_data_export_begin_time = datetime.now()

            if match_records> 0:
                # Export match records
                combined_df[combined_df['Match']==True].to_csv(match_data_full_file_name)
                logging.info(f"{match_records} records has been exported \
to '{match_data_full_file_name}'")
            else:
                logging.info('Source and target file has no match records')

            # Match data export processing time
            match_data_export_end_time = datetime.now()
            match_data_export_process_time = (match_data_export_end_time
                                              -
                                              match_data_export_begin_time)
            logging.info(f"Match data filtered and .csv file exported in \
{match_data_export_process_time.total_seconds()} seconds")
            print(f"Match data filtered and .csv file exported in \
{match_data_export_process_time.total_seconds()} seconds")

            # Mismatch data & its export time counter begins
            mismatch_data_export_begin_time = datetime.now()

            if mismatch_records > 0:
                # Export mismatch records
                combined_df[combined_df['Match']==False].to_csv(mismatch_data_full_file_name)
                logging.info(f"{mismatch_records} records has been exported \
to '{mismatch_data_full_file_name}'")
            else:
                logging.info('Source and target file has no mismatch records')
            # Mismtach data & its export processing time
            mismatch_data_export_end_time = datetime.now()
            mismatch_data_export_process_time = (mismatch_data_export_end_time
                                                 -
                                                 mismatch_data_export_begin_time)
            logging.info(f"Mismatch data filtered and .csv file exported in \
{mismatch_data_export_process_time.total_seconds()} seconds")
            print(f"Mismatch data filtered and .csv file exported in \
{mismatch_data_export_process_time.total_seconds()} seconds")

            # Total checks time counter begins
            totals_check_recon_begin_time = datetime.now()

            # Totals Check reconciliation
            if concat_records == match_records + mismatch_records:
                logging.info(f"Sum check has passed: Merge file data records \
{concat_records} in memory = Match records({match_records}) + \
Mismatch records({mismatch_records})")
            else:
                logging.info(f"Sum check has failed: Merge file data records \
{concat_records} in memory != Match records({match_records}) + \
Mismatch records({mismatch_records})")

            # Total checks processing time
            totals_check_recon_end_time = datetime.now()
            totals_check_recon_process_time = (totals_check_recon_end_time
                                               -
                                               totals_check_recon_begin_time)
            logging.info(f"Total sum check processed in \
{totals_check_recon_process_time.total_seconds()} seconds")

            #*****************************************************************************
            #  Export the summary stats - for full comparison done
            #*****************************************************************************
            summary_stats_set_n_export_begin_time = datetime.now()
            summary_stats_data = {'S.No': [self.sno],
                                  'Source Object Name': [source_file_name_wo_ext],
                                  'Target Object Name': [target_file_name_wo_ext],
                                  'Source Object Directory & Path': [self.source_file],
                                  'Target Object Directory & Path': [self.target_file],
                                  'Source Object Exists - Flag': 1,
                                  'Target Object Exists - Flag':1,
                                  'Source & Target Object is csv - Flag': 1,
                                  'Reconciliation Performed - Flag': 1,
                                  'Date & Time': [datetime.now()],
                                  'No. of records in Source File': [no_source_records],
                                  'No. of records in Target File': [no_target_records],
                                  'No. of Match records': [match_records],
                                  'No. of Mismatch records': [mismatch_records],
                                  'Dataset Match - Flag': [overall_match],
                                  'Location of Match records': [match_data_full_file_name],
                                  'Location of Mismatch records': [mismatch_data_full_file_name],
                                  'Remarks': ''
                                  }
        summary_stats_df = pd.DataFrame(data=summary_stats_data)
        logging.debug(f"Summary Stats dataframe data is:\n{summary_stats_df}")
        summary_stats_df.to_csv(summary_stats_fullfilename,index=False,
                                mode='a', header=None)
        logging.info(F"Comparison summary stats of {source_file_name_wo_ext} \
and {target_file_name_wo_ext} is exported successfully")

        # Summary Stats output processing time
        summary_stats_set_n_export_end_time = datetime.now()
        summary_stats_set_n_export_process_time = (
            summary_stats_set_n_export_end_time
            -
            summary_stats_set_n_export_begin_time)
        logging.info(f"Summary Stats created and expored in \
{summary_stats_set_n_export_process_time.total_seconds()} seconds")

        return summary_stats_df

#*****************************************************************************
#  User inputs for source and target directory
#*****************************************************************************

text = 'Enter the source directoy path of .csv files for comparison:\n'
source_dir = input(text)

text = 'Enter the target directory path of .csv files for comparison:\n'
target_dir = input(text)

#*****************************************************************************
#  User inputs for Output file path and Summary file path
#*****************************************************************************
text = 'Enter the Output directory path:\n'
output_dir = input(text)

# Program start time
begin_time = datetime.now()
logging.info(f"\nProgram execution starts @ {begin_time}")
print(f"\nProgram execution starts @ {begin_time}")

# Log the user inputs
msg = 'User provided source directory path of .csv files for comparison is'
logging.info(f"{msg} '{source_dir}'")

msg = 'User provided target directoy path of .csv files for comparison is'
logging.info(f"{msg} '{target_dir}'")

logging.info(f"User provided output directory path is '{output_dir}'")

#*****************************************************************************
#  Validations - User input; If fails, exit the program
#*****************************************************************************
# Check for directory existence and directory difference
dir_validations_fail1 = [
                        InputDirectoryValidations(
                            dir_path = source_dir,
                            dir_type='Source').dir_check_exists(),
                        InputDirectoryValidations(
                            dir_path = target_dir,
                            dir_type='Target').dir_check_exists(),
                        InputDirectoryValidations(
                            dir_path = output_dir,
                            dir_type='Output').dir_check_exists(),
                        CompareDirectoriesValidation(
                            source_dir = source_dir,
                            target_dir = target_dir,
                            output_dir = output_dir).dirs_are_same(),
                        ]

if 1 in dir_validations_fail1:
    logging.critical("Enter valid inputs! Exiting the program...")
    print('Atleast one of the validations has failed. \
Refer to the log file for error details')
    sys.exit(0)

# 2nd level check as these checks cannot be combined with the 1st one
# Because if the directory does not exist, then the program cannot check if it has any files/directory
# Check for empty directory and at least one .csv file
dir_validations_fail2 = [
                        InputDirectoryValidations(
                            dir_path = source_dir,
                            dir_type='Source').dir_check_empty(),
                        InputDirectoryValidations(
                            dir_path = target_dir
                            ,dir_type='Target').dir_check_empty(),
                        InputDirectoryValidations(
                            dir_path = source_dir,
                            dir_type='Source').dir_check_csv(),
                        InputDirectoryValidations(
                            dir_path = target_dir,
                            dir_type='Target').dir_check_csv(),
                        ]

if 1 in dir_validations_fail2:
    logging.critical("Enter valid inputs! Exiting the program...")
    print('Atleast one of the validations has failed. \
Refer to the log file for error details')
    sys.exit(0)

#*****************************************************************************
#  Set the Summary Stats file name
#*****************************************************************************

# Summary Stats file is combination of directory path and hardcoded file name
# Date string in the format: yyyy-mm-dd hh.mm.ss
dt_string = now.strftime("%Y-%m-%d %H.%M.%S")
summary_stats_filename = 'Summary Stats csv File Compare_'+dt_string+'.csv'
summary_stats_fullfilename = os.path.join(output_dir, summary_stats_filename)

#*****************************************************************************
#  Load source and target directory objects into a list for processing
#*****************************************************************************
# Get the unique list of objects
source_objects=ObjectList(dir_path=source_dir,dir_type='Source').object_list()
target_objects=ObjectList(dir_path=target_dir,dir_type='Target').object_list()
unique_object_list = set(source_objects+target_objects)
msg = 'Combined source and target directory unique object set is'
logging.info(f"{msg} {unique_object_list}")
msg = 'Total number of unqiue objects identified for processing:'
print(f"{msg} {len(unique_object_list)}")

#*****************************************************************************
#  Print the Summary Stats file header
#*****************************************************************************

# Print the header record to the summary stats file
SummaryFileOutput(
    dir_path = output_dir,
    fullfilename = summary_stats_fullfilename,
    obj_list = unique_object_list,
    # S.No info is a dummmy entry passed to satisfy the syntax
    sno = ''
    ).print_summary_file_header()

#*****************************************************************************
#  Loop through each object, check if recon can be performed
#*****************************************************************************

dir_compare = {}
s_no = 0

for object in unique_object_list:
    s_no +=1
    logging.info(f"Object#{s_no}-{object} recon processing starts \
@ {datetime.now()}")
    print(f"\nObject#{s_no}-{object} recon processing starts \
@ {datetime.now()}")
    object_process_begin_time = datetime.now()
    dir_compare[object] = {}
    dir_compare[object]['S.No'] = s_no
    # If the object 1) ends with .csv and 2) is a file, then it is a .csv file
    dir_compare[object]['Is csv Flag'] = 1 if object.endswith('.csv') & os.path.isfile(os.path.join(source_dir, object)) & os.path.isfile(os.path.join(target_dir, object)) else 0
    logging.info(f".csv file check result is \
{dir_compare[object]['Is csv Flag']}")
    dir_compare[object]['In Source Directory Flag'] = 1 if object in source_objects else 0
    logging.info(f"Source Object exists check result is \
{dir_compare[object]['In Source Directory Flag']}")
    dir_compare[object]['In Target Directory Flag'] = 1 if object in target_objects else 0
    logging.info(f"Target Object exists check result is \
{dir_compare[object]['In Target Directory Flag']}")
    dir_compare[object]['Source Object Name'] = object if object in source_objects else None
    dir_compare[object]['Target Object Name'] = object if object in target_objects else None
    dir_compare[object]['Source Object Directory & Path'] = os.path.join(source_dir, object) if object in source_objects else None
    dir_compare[object]['Target Object Directory & Path'] = os.path.join(target_dir, object) if object in target_objects else None

    # Recon flag is based on 2 checks: both source and target file is aviailable and it is in csv file format
    recon_flag = [dir_compare[object]['Is csv Flag'], dir_compare[object]['In Source Directory Flag'],dir_compare[object]['In Target Directory Flag']]
    logging.info(f"Recon flag for the object, {object}, in validation order: \
csv_check, available in source directory, and available in target directory \
is {recon_flag}")

    #*************************************************************************
    #  If recon can be performed, call the csv_file_recon function
    #*************************************************************************
    # If reconciliation can be done, then call the csv file recon program
    # Else, print the summary stats only
    if 0 not in recon_flag:

        logging.info(f"Reconciliation initiated for the file, {object}")
        try:
            CompareFiles(source_file = dir_compare[object]['Source Object Directory & Path'],
                            target_file = dir_compare[object]['Target Object Directory & Path'],
                            output_dir = output_dir,
                            summary_stats_fullfilename = summary_stats_fullfilename,
                            sno = dir_compare[object]['S.No']
                            ).csv_file_recon()
        except OSError as err:
            print("An unexpected OS error: {0}".format(err))
        except ValueError as err:
            print("An unexpected Value error: {0}".format(err))
        except:
            print('An unexpected error has occured')
    else:
        logging.info(f"Reconciliation is not applicable for the object, \
{object}, because at least one of the validations has failed")
        print(f"Reconciliation is not applicable for the object, \
{object}, because at least one of the validations has failed")
    object_process_end_time = datetime.now()
    object_process_time = object_process_end_time - object_process_begin_time
    logging.info(f"Object#{s_no}-{object} recon processed in \
{object_process_time.total_seconds()} seconds")
    print(f"Object#{s_no}-{object} recon processed in \
{object_process_time.total_seconds()} seconds")
    logging.info(f"Object#{s_no}-{object} recon processing ends \
@ {datetime.now()}")
    print(f"Object#{s_no}-{object} recon processing ends @ \
{datetime.now()}")

#*****************************************************************************
#  Load dir_compare library into a dataframe and 
#  Create a recon_na dataframe to update summary file with uncomaprable data
#  based on file exists & .csv checks; other checks are done during comparison
#*****************************************************************************
df = pd.DataFrame(dir_compare)
df = df.T
df.index.name = 'Object Name'
logging.debug(f"Source and Target directory comparison result is \n{df}")

# Get the files that can be reconciled
df_recon = df[(df['Is csv Flag'] == 1) & 
              (df['In Source Directory Flag'] == 1) &
              (df['In Target Directory Flag'] == 1)]
logging.debug(f"Source and Target files identified for recon are \n{df_recon}")

# When the source and target file name is not the same or
# when the file is not .csv, reconciliation is not applicable
df_recon_na = df[(df['Is csv Flag'] == 0) | 
                 (df['In Source Directory Flag'] == 0) |
                 (df['In Target Directory Flag'] == 0)]
msg = 'Reconciliation is not applicable for the object set:'
logging.debug(f"\n{msg} {df_recon_na}")

#*****************************************************************************
#  Update the Summary Stats with objects that cannot be compared
#*****************************************************************************
## Set the output file to export the summary stats
## Add additional columns to the dataframe faciliate the summary stats export

# Add the available columns from recon_na dataframe
df_recon_na_summary_stats = df_recon_na.loc[:,['S.No',
                                               'Source Object Name',
                                               'Target Object Name',
                                               'Source Object Directory & Path',
                                               'Target Object Directory & Path'
                                               ]]
# Assign values to applicable columns
df_recon_na_summary_stats['Source Object Exists - Flag'] = df['In Source Directory Flag']
df_recon_na_summary_stats['Target Object Exists - Flag'] = df['In Target Directory Flag']
df_recon_na_summary_stats['Source & Target Object is csv - Flag'] = 0
df_recon_na_summary_stats['Reconciliation Performed - Flag'] = 0
df_recon_na_summary_stats['Date & Time'] = datetime.now()
msg = 'Summary Stats export for objects that cannot be reconciled'
logging.debug(f"{msg} {df_recon_na_summary_stats}")

# Export the summary stats
# Do not export the index and header, and write to Summary Stats file in append mode
df_recon_na_summary_stats.to_csv(summary_stats_fullfilename,index=False,
                                 mode='a', header=None)

#*****************************************************************************
#  Sort the Summary Stats file based on S.No
#*****************************************************************************
SummaryFileOutput(
    dir_path = output_dir,
    fullfilename = summary_stats_fullfilename,
    # obj_list info is a dummmy entry passed to satisfy the syntax
    obj_list = '',
    sno = 'S.No',
    ).print_summary_file_header()

#*****************************************************************************
#  Program run successfully print message
#*****************************************************************************
# Last info message of the program, if it successful
msg = 'File compare Program has completed successfully without any errors'
logging.info(msg)
print(f'\n{msg}')
logging.info(f"Total program run time: \
{(datetime.now() - begin_time).total_seconds()} seconds")
print(f"Total program run time: \
{(datetime.now() - begin_time).total_seconds()} seconds")
# Program End log
logging.info(f"Program execution ends @ {datetime.now()}")
print(f"Program execution ends @ {datetime.now()}")

#*****************************************************************************
#  Final user input to allow the user to see the results when run as .exe
#*****************************************************************************
input('Enter any key to Quit the program\n')
print('\n')
