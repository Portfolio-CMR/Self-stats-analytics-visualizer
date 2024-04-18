import re
from typing import List, Tuple
import numpy as np
import json
from self_stats.munger.input_output import read_json_file
from self_stats.munger.parse_and_process import extract_search_information, extract_coordinates, extract_watch_information
from self_stats.munger.clean_dates import convert_to_arrays, main as cleaner_main

def main(directory: str, mappings: List[str]) -> None:'
'
    json_data = read_json_file(f'{directory}/watch_history.json')
    extracted_data = extract_watch_information(json_data)

    arr_data = convert_to_arrays(extracted_data, mappings)
    cleaned_data = cleaner_main(arr_data, mappings)
    return cleaned_data
