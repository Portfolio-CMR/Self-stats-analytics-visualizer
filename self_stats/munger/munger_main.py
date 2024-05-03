from pathlib import Path
from typing import List
import pandas as pd
from datetime import datetime
import numpy as np
from itertools import chain

from self_stats.munger.input_output import create_output_directories, save_to_csv, write_arrays_to_excel, write_arrays_to_single_excel
from self_stats.munger.process_dates import trim_date
from self_stats.munger.parse_and_process import main as parse_and_process
from self_stats.munger.add_date_columns import main as add_date_columns
from self_stats.munger.impute_time_data import main as imputer
from self_stats.munger.content_analysis import main as content_analysis
from self_stats.munger.aggregate_data import main as aggregate_by_day
from self_stats.munger.aggregate_data import remove_unique_entries
from self_stats.munger.aggregate_data import aggregate_activity_by_day

def main(directory: Path, input_file_name: Path, mappings: List[str]) -> None:

    if mappings[1] == 'Query_Text':
        data_source = 'search'
    elif mappings[1] == 'Video_Title':
        data_source = 'watch'

    print("\n********************************************************************")
    print(f"*****************  Processing {data_source} history...  ********************")
    print("********************************************************************\n")

    # Define paths for saving output files
    outer_path = directory / 'output'
    path = outer_path / 'full_data'
    agg_dir = outer_path / 'aggregated_data'
    raw_save_path = path / f'{data_source.upper()}_raw.csv'
    processed_save_path = path / f'{data_source.upper()}_processed.csv'
    metadata_save_path = path / f'{data_source.upper()}_metadata.csv'
    visited_sites_save_path = path / f'{data_source.upper()}_visited_sites.csv'
    keywords_save_path = path / f'{data_source.upper()}_keywords.csv'
    agg_save_path = outer_path / 'aggregated_data' / f'{data_source.upper()}.xlsx'
    single_agg_save_path = outer_path / 'aggregated_data' / f'{data_source.upper()}_collated.xlsx'

    directory_list = [outer_path, path, agg_dir]
    create_output_directories(directory_list)

    print("Extracting data from input file...\n")

    extracted_data = parse_and_process(directory, input_file_name, mappings)

    save_to_csv(extracted_data, raw_save_path, mappings)
    print(f"Search data extraction complete.\nResults saved to {raw_save_path}'.\n")
    
    ############################################################
    # Optional injection of fake data for testing purposes
    ############################################################
    # fake_data = pd.read_csv(f'{directory}/output/full_data/{data_source.upper()}_fake.csv')
    # fake_data['Date'] = pd.to_datetime(fake_data['Date']).apply(lambda x: x.to_pydatetime())
    # date_objects = [date.to_pydatetime() for date in fake_data['Date']]
    # date_array = np.array(date_objects, dtype=object)
    # non_date_data = [fake_data[column].to_numpy() for column in mappings[1:]]
    # extracted_data = (date_array, *non_date_data)

    # outer_path = directory / 'output_fake'
    # path = outer_path / 'full_data'
    # agg_dir = outer_path / 'aggregated_data'
    # raw_save_path = path / f'{data_source.upper()}_raw.csv'
    # processed_save_path = path / f'{data_source.upper()}_processed.csv'
    # metadata_save_path = path / f'{data_source.upper()}_metadata.csv'
    # visited_sites_save_path = path / f'{data_source.upper()}_visited_sites.csv'
    # keywords_save_path = path / f'{data_source.upper()}_keywords.csv'
    # agg_save_path = outer_path / 'aggregated_data' / f'{data_source.upper()}.xlsx'
    # single_agg_save_path = outer_path / 'aggregated_data' / f'{data_source.upper()}_collated.xlsx'
    
    # directory_list = [outer_path, path, agg_dir]
    # create_output_directories(directory_list)    
    ############################################################

    print("Cleaning data...")
    
    arr_data_trimmed = trim_date(extracted_data, mappings)
    mappings.extend(['Day_of_the_Week', 'Hour_of_the_Day', 'Date_Only'])
    arr_data_dated = add_date_columns(arr_data_trimmed)

    if data_source == 'search':
        mappings.extend(['Search_Duration'])
    if data_source == 'watch':
        mappings.extend(['Video_Duration', 'Short_Form_Video'])
    imputed_data, metadata = imputer(arr_data_dated, mappings)

    print("Data cleaning complete.\n")
    
    print("Executing keyword analysis. This may take a moment...")

    visited_sites, tokens_per_date = content_analysis(imputed_data, mappings)

    print("Keyword analysis complete.\n")

    save_to_csv(imputed_data, processed_save_path, mappings)
    print(f"Processed data table results saved to {processed_save_path}.")

    save_to_csv(metadata, metadata_save_path, ['Activity_Window_Start_Date', 'Activity_Window_Start_Index', 'Activity_Window_End_Index', 'Activity_Window_Duration', 'Actions_per_Activity_Window', 'Approximate_Actions_per_Minute'])
    print(f"Metadata saved to {metadata_save_path}.")
    
    if data_source == 'search':
        save_to_csv(visited_sites, visited_sites_save_path, ['Date', 'Visited_Sites'])
        print(f"Visited sites saved to {visited_sites_save_path}.")

    save_to_csv(tokens_per_date, keywords_save_path, ['Date', 'Keywords'])
    print(f'Tokens per date saved to {keywords_save_path}.\n')

    ############################################################

    print(f'\nAggregating {data_source} data by day...\n')

    aggregate_keywords = remove_unique_entries(tokens_per_date)

    if data_source == 'search':
        aggregated_sites = remove_unique_entries(visited_sites)

    mappings = ['Activity_Window_Start_Date', 'Activity_Window_Start_Index', 'Activity_Window_End_Index', 'Activity_Window_Duration', 'Actions_per_Activity_Window', 'Approximate_Actions_per_Minute']
    aggregate_activity = aggregate_activity_by_day(metadata, mappings)
    mappings = ['Date', 'Record_Count', 'Day_of_the_Week', 'Most_Active_Hour_of_the_Day']
    if data_source == 'watch':
        mappings.extend(['Short_Form_Ratio'])

    aggregated_data = aggregate_by_day(imputed_data, mappings)
    mappings = ['Date', 'Record_Count', 'Day_of_the_Week', 'Most_Active_Hour_of_the_Day']
    if data_source == 'watch':
        mappings.extend(['Short_Form_Ratio'])
    
    def flatten(xss):
        return [x for xs in xss for x in xs]

    array_lists = [aggregated_data, aggregate_activity, aggregate_keywords]
    if data_source == 'search':
        array_lists.append(aggregated_sites)
        sheet_names = ['Time_Series', 'Activity', 'Keywords', 'Sites']
        column_name_lists = [
            ['Date', 'Record_Count', 'Day_of_the_Week', 'Most_Active_Hour_of_the_Day'],
            ['Date_Activity', 'Activity_Window_Duration', 'Actions_per_Activity_Window', 'Actions_per_Minute'],
            ['Date_Keywords', 'Keywords'], 
            ['Date_Sites', 'Visited_Sites']]
        
        combined_tuple = tuple(chain(aggregated_data, aggregate_activity, aggregate_keywords, aggregated_sites))
        single_file_column_name_lists = flatten(column_name_lists)
        single_file_column_types = ['date', 'float', 'str', 'float', 'date', 'float', 'float', 'float', 'date_time', 'str', 'date_time', 'str']

    if data_source == 'watch':
        date_channel_array = (imputed_data[0], imputed_data[2])
        short_form_array = (imputed_data[0], imputed_data[8]) 
        aggregated_channels = remove_unique_entries(date_channel_array)
        array_lists.append(aggregated_channels)
        sheet_names = ['Time_Series', 'Activity_Windows', 'Keywords', 'Channels']
        column_name_lists = [
            ['Date', 'Record_Count', 'Day_of_the_Week', 'Most_Active_Hour_of_the_Day', 'Short_Form_Ratio'],
            ['Date_Activity', 'Activity_Window_Duration', 'Actions_per_Activity_Window', 'Actions_per_Minute'],
            ['Date_Keywords', 'Keywords'], 
            ['Date_Channel', 'Channel_Title']]

        combined_tuple = tuple(chain(aggregated_data, aggregate_activity, aggregate_keywords, aggregated_channels, short_form_array))
        single_file_column_name_lists = flatten(column_name_lists)
        single_file_column_name_lists.extend(['Date_Short_Form', 'Short_Form_Labels'])
        single_file_column_types = ['date', 'float', 'str', 'float', 'float', 'Date', 'float', 'float', 'float', 'date_time', 'str', 'date_time', 'str', 'date_time', 'str']
    
    write_arrays_to_single_excel(combined_tuple, single_file_column_name_lists, single_file_column_types, single_agg_save_path)
    write_arrays_to_excel(array_lists, column_name_lists, sheet_names, agg_save_path)
    print(f'Aggregated data saved to {agg_save_path}\n')

    print(f"\n***********  Completed {data_source} history processing!  ******************\n")