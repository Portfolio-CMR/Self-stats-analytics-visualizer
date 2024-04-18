import re
from typing import List, Tuple
import numpy as np
import json
from pathlib import Path
from self_stats.munger.input_output import read_json_file
from self_stats.munger.parse_and_process import extract_search_information, extract_coordinates
from self_stats.munger.clean_dates import convert_to_arrays, main as cleaner_main

def main(directory: str, source: str | Path, mappings: List[str], ) -> None:

    arr_data = json_parser.main(directory, mappings, source)

    json_data = read_json_file(f'{directory}/MyActivity.json')
    extracted_data = extract_search_information(json_data)

    arr_data = convert_to_arrays(extracted_data, mappings)
    cleaned_data = cleaner_main(arr_data, mappings)
    return cleaned_data
