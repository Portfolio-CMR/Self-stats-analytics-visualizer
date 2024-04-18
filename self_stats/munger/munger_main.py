from pathlib import Path
from typing import List
from self_stats.munger.input_output import save_to_csv
from self_stats.munger.changepoint_analysis import trim_date
from self_stats.munger.parse_and_process import main as parse_and_process 

def main(directory: str, data_source: str, mappings: List[str]) -> None:

    cleaned_data = parse_and_process.main(directory, data_source, mappings)

    out_dir = Path(f'{directory}/output')
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {out_dir}\n")
    save_to_csv(cleaned_data, f'{out_dir}/extracted_{data_source}_data.csv', mappings)
    print(f"Search data extraction complete. Results saved to '{directory}/extracted_{data_source}_data.csv'.\n")
    
    dash_ready_data = trim_date(cleaned_data, mappings)
    save_to_csv(dash_ready_data, f'{out_dir}/dash_ready_{data_source}_data.csv', mappings)
    print(f"Data processing complete. Results saved to '{directory}/dash_ready_{data_source}_data.csv'.\n")

    