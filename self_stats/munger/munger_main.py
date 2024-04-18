from pathlib import Path
from self_stats.munger.input_output import save_to_csv
from self_stats.munger.search_history_main import main as search_main
from self_stats.munger.watch_history_main import main as watch_main
from self_stats.munger.dash_ready_data import trim_date

def main(directory: str, data_source: str, mappings: list) -> None:
    process_flag = 0
    if data_source == 'search_history':
        cleaned_data = search_main(directory)
        process_flag = 1
    elif data_source == 'watch_history':
        cleaned_data = watch_main(directory)
        process_flag = 1

    if process_flag:
        out_dir = Path(f'{directory}/output')
        if not out_dir.exists():
            out_dir.mkdir(parents=True, exist_ok=True)
            print(f"Directory created: {out_dir}\n")
        save_to_csv(cleaned_data, f'{out_dir}/extracted_{data_source}_data.csv', mappings)
        print(f"Search data extraction complete. Results saved to '{directory}/extracted_{data_source}_data.csv'.\n")
        dash_ready_data = trim_date(cleaned_data, mappings)
        save_to_csv(dash_ready_data, f'{out_dir}/dash_ready_{data_source}_data.csv', mappings)
        print(f"Data processing complete. Results saved to '{directory}/dash_ready_{data_source}_data.csv'.\n")
    else:
        error_message = "No data processed. Please check that input data is in the specified directory."
        raise OSError(error_message)