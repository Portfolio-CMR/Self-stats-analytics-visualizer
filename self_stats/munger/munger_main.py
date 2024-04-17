from pathlib import Path
from self_stats.munger.parse import parse_html, extract_div
from self_stats.munger.input_output import read_file, save_to_csv
from self_stats.munger.search_history import extract_search_data
import self_stats.munger.clean_parsed_data as clean_parsed_data


def main(directory: str, data_source: str, mappings: list) -> None:
    html_content = read_file(f'{directory}/MyActivity.html')
    soup = parse_html(html_content)
    entries = extract_div(soup)
    data = extract_search_data(entries, soup)
    cleaned_data = clean_parsed_data.main(data, data_source)

    out_dir = Path(f'{directory}/output')
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {out_dir}\n")
    save_to_csv(cleaned_data, f'{out_dir}/extracted_search_history_data.csv', mappings)
    print(f"Search data extraction complete. Results saved to '{directory}/extracted_search_history_data.csv'.\n")

    

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
