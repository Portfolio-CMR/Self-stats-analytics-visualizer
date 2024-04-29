from pathlib import Path
from typing import List

from self_stats.munger.input_output import save_to_csv
from self_stats.munger.process_dates import trim_date
from self_stats.munger.parse_and_process import main as parse_and_process
from self_stats.munger.add_date_columns import main as add_date_columns
from self_stats.munger.impute_time_data import main as imputer
from self_stats.munger.content_analysis import main as content_analysis

def main(directory: str, input_file_name: str, mappings: List[str]) -> None:

    if mappings[1] == 'Text Title':
        data_source = 'search'
    elif mappings[1] == 'Video Title':
        data_source = 'watch'

    print("\n********************************************************************")
    print(f"*****************  Processing {data_source} history...  ********************")
    print("********************************************************************\n")

    cleaned_data = parse_and_process(directory, input_file_name, mappings)

    out_dir = Path(f'{directory}/output')
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {out_dir}\n")
    save_to_csv(cleaned_data, f'{directory}/output/{data_source.upper()}_raw.csv', mappings)
    print(f"Search data extraction complete.\nResults saved to '{directory}/output/{data_source.upper()}_raw.csv'.\n")
    
    print("Cleaning data...")
    
    arr_data_trimmed = trim_date(cleaned_data, mappings)
    mappings.extend(['Weekday', 'Hour', 'Date Only'])
    arr_data_dated = add_date_columns(arr_data_trimmed)

    if data_source == 'search':
        mappings.extend(['Search Duration'])
    if data_source == 'watch':
        mappings.extend(['Video Duration', 'Short-Form Video'])
    imputed_data, metadata = imputer(arr_data_dated, mappings)

    print("Data cleaning complete.\n")
    
    print("Executing keyword analysis. This may take a moment...")

    visited_sites, tokens_per_date = content_analysis(imputed_data, mappings)

    print(f"\n**************  Completed {data_source} history processing!  *********************\n")

    save_to_csv(imputed_data, f'{directory}/output/{data_source.upper()}_processed.csv', mappings)
    print(f"Processed data table results saved to '{directory}/output/{data_source.upper()}_processed.csv.csv'.\n")

    save_to_csv(metadata, f'{directory}/output/{data_source.upper()}_metadata.csv', ['Activity Window Start Date/Time', 'Activity Window Start Index', 'Activity Window End Index', 'Duration', 'Count', 'Count Per 10 minutes'])
    print(f"Metadata saved to '{directory}/output/{data_source.upper()}_metadata.csv'.\n")
    
    if data_source == 'search':
        save_to_csv(visited_sites, f'{directory}/output/{data_source.upper()}_visited_sites.csv', ['Date', 'Visted Site'])
        print(f"Visited sites saved to '{directory}/output/{data_source.upper()}_visited_sites.csv'.\n")

    save_to_csv(tokens_per_date, f'{directory}/output/{data_source.upper()}_keywords.csv', ['Date', 'Tokens'])
    print(f'Tokens per date saved to {directory}/output/{data_source.upper()}_keywords.csv.\n')