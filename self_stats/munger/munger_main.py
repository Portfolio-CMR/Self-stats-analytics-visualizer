from pathlib import Path
from typing import List
import pandas as pd
from datetime import datetime
import numpy as np

from self_stats.munger.input_output import save_to_csv
from self_stats.munger.process_dates import trim_date
from self_stats.munger.parse_and_process import main as parse_and_process
from self_stats.munger.add_date_columns import main as add_date_columns
from self_stats.munger.impute_time_data import main as imputer
from self_stats.munger.content_analysis import main as content_analysis
from self_stats.munger.aggregate_data import main as aggregate_by_day

def main(directory: str, input_file_name: str, mappings: List[str]) -> None:

    if mappings[1] == 'Query_Text':
        data_source = 'search'
    elif mappings[1] == 'Video_Title':
        data_source = 'watch'

    print("\n********************************************************************")
    print(f"*****************  Processing {data_source} history...  ********************")
    print("********************************************************************\n")

    extracted_data = parse_and_process(directory, input_file_name, mappings)

    out_dir = Path(f'{directory}/output')
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {out_dir}\n")
    save_to_csv(extracted_data, f'{directory}/output/{data_source.upper()}_raw.csv', mappings)
    print(f"Search data extraction complete.\nResults saved to '{directory}/output/{data_source.upper()}_raw.csv'.\n")
    
    # Optional injection of fake data for testing purposes
    fake_data = pd.read_csv(f'{directory}/output_orig/{data_source.upper()}_fake.csv')
    fake_data['Date'] = pd.to_datetime(fake_data['Date']).apply(lambda x: x.to_pydatetime())
    date_objects = [date.to_pydatetime() for date in fake_data['Date']]
    date_array = np.array(date_objects, dtype=object)
    non_date_data = [fake_data[column].to_numpy() for column in mappings[1:]]
    extracted_data = (date_array, *non_date_data)

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

    print(f"\n**************  Completed {data_source} history processing!  *********************\n")

    save_to_csv(imputed_data, f'{directory}/output/{data_source.upper()}_processed.csv', mappings)
    print(f"Processed data table results saved to '{directory}/output/{data_source.upper()}_processed.csv.csv'.\n")

    save_to_csv(metadata, f'{directory}/output/{data_source.upper()}_metadata.csv', ['Activity_Window_Start_Date', 'Activity_Window_Start_Index', 'Activity_Window_End_Index', 'Activity_Window_Duration', 'Actions_per_Activity_Window', 'Approximate_Actions_per_Minute'])
    print(f"Metadata saved to '{directory}/output/{data_source.upper()}_metadata.csv'.\n")
    
    if data_source == 'search':
        save_to_csv(visited_sites, f'{directory}/output/{data_source.upper()}_visited_sites.csv', ['Date', 'Visited_Sites'])
        print(f"Visited sites saved to '{directory}/output/{data_source.upper()}_visited_sites.csv'.\n")

    save_to_csv(tokens_per_date, f'{directory}/output/{data_source.upper()}_keywords.csv', ['Date', 'Keywords'])
    print(f'Tokens per date saved to {directory}/output/{data_source.upper()}_keywords.csv.\n')

    aggregated_data = aggregate_by_day(imputed_data, mappings)
    save_to_csv(aggregated_data, f'{directory}/output/{data_source.upper()}_aggregated.csv', ['Date', *mappings[1:]])
    print(f'Aggregated data saved to {directory}/output/{data_source.upper()}_aggregated.csv.\n')
