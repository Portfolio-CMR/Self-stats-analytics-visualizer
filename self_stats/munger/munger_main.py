from pathlib import Path
from typing import List

from self_stats.munger.input_output import save_to_csv
from self_stats.munger.process_dates import trim_date
from self_stats.munger.parse_and_process import main as parse_and_process
from self_stats.munger.add_date_columns import main as add_date_columns
from self_stats.munger.impute_time_data import main as imputer
from self_stats.munger.content_analysis import main as content_analysis


def main(directory: str, input_file_name: str, mappings: List[str]) -> None:

    if mappings[0] == 'Text Title':
        data_source = 'search'
    elif mappings[0] == 'Video URL':
        data_source = 'watch'

    print("\n\n********************************************************************\n\n")
    print(f"\n\n*****************  Processing {data_source} history...  ********************\n\n")
    print("\n\n********************************************************************\n\n")

    cleaned_data = parse_and_process(directory, input_file_name, mappings)

    out_dir = Path(f'{directory}/output')
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {out_dir}\n")
    save_to_csv(cleaned_data, f'{directory}/output/raw_extracted_{data_source}_history.csv', mappings)
    print(f"Search data extraction complete. Results saved to '{directory}/output/raw_extracted_{data_source}_data.csv'.\n")
    
    print("Cleaning data...\n")
    
    arr_data_trimmed = trim_date(cleaned_data, mappings)
    mappings.extend(['Weekday', 'Hour', 'Date Only'])
    arr_data_dated = add_date_columns(arr_data_trimmed, mappings)

    if data_source == 'search':
        mappings.extend(['Search Duration'])
    if data_source == 'watch':
        mappings.extend(['Video Duration', 'Short-Form Video'])
    imputed_data, metadata = imputer(arr_data_dated, mappings)

    print("Data cleaning complete.\n")
    
    print("Executing keyword analysis. This may take a moment...\n")

    if data_source == 'search':
        mappings.extend(['Search Terms', 'Domains Visited'])
    if data_source == 'watch':
        mappings.extend(['Title Terms'])
    visited_sites, tokens_per_date = content_analysis(imputed_data, mappings)

    print(f"\n**************  Completed {data_source} history processing!  *********************\n")

    save_to_csv(imputed_data, f'{directory}/output/imputed_{data_source}_data.csv', mappings)
    print(f"Processed data table results saved to '{directory}/output/imputed_{data_source}_data.csv'.\n")

    save_to_csv(metadata, f'{directory}/output/metadata_{data_source}_data.csv', ['Activity Window Start Index', 'Activity Window End Index', 'Activity Window Start Date/Time', 'Duration', 'Count', 'Count Per 10 minutes'])
    print(f"Metadata saved to '{directory}/output/metadata_{data_source}_data.csv'.\n")
    
    if data_source == 'search':
        save_to_csv(visited_sites, f'{directory}/output/visited_sites_{data_source}_data.csv', ['Visited Sites', 'Date'])
        print(f"Visited sites saved to '{directory}/output/visited_sites_{data_source}_data.csv'.\n")

    save_to_csv(tokens_per_date, f'{directory}/output/tokens_per_date_{data_source}_data.csv', ['Tokens', 'Date'])
    print(f'Tokens per date saved to {directory}/output/tokens_per_date_{data_source}_data.csv.\n')