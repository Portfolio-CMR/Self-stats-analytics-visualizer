import numpy as np
import regex as re
from typing import List, Any, Tuple, Pattern
from self_stats.munger.clean_data_shared import safe_convert_to_float, remove_invisible_characters, parse_dates, clean_all_columns, remove_indices_from_tuple

def type_data(arr_data: Tuple[np.ndarray, np.ndarray, np.ndarray], timezone_pattern: Pattern, mapping: List[str]):
    """
    Process the data from numpy arrays by cleaning and converting each element.
    
    Args:
    search_texts, dates, latitudes, longitudes (np.ndarray): Arrays of data.
    compiled_pattern (Pattern): A compiled regex pattern to remove invisible characters.
    data_source (str): String indicating the type of data to process.

    Returns:
    Tuple of arrays after processing.
    """

    for i, column_name in enumerate(mapping):
        if column_name == 'Date':
            clean_dates, bad_indices = parse_dates(arr_data[i], timezone_pattern)
        elif column_name == 'Latitude':
            clean_latitudes = safe_convert_to_float(arr_data[i])
        elif column_name == 'Longitude':
            clean_longitudes = safe_convert_to_float(arr_data[i])
        elif column_name == 'Search Text':
            clean_search_texts = arr_data[i]

    typed_arr_data = remove_indices_from_tuple((clean_search_texts, clean_dates, clean_latitudes, clean_longitudes), bad_indices)

    return typed_arr_data

def main(arr_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], mappings: List[str]) -> np.ndarray:
    """
    Main function to process data arrays for cleaning and type conversion.
    
    Args:
    search_texts, dates, latitudes, longitudes (np.ndarray): Arrays of data.

    Returns:
    Tuple of arrays after processing.
    """
    # Compile the regex pattern once and remove hidden characters
    hidden_char_pattern = re.compile(r'\p{C}+|\p{Z}+|[\u200B-\u200F\u2028-\u202F]+')
    clean_arr_data = clean_all_columns(arr_data, hidden_char_pattern)
    
    # Compile the regex pattern once and then clean/apply data types
    timezone_pattern = re.compile(r'(?<=AM|PM)\s*([A-Z]{2,4})$')
    typed_arr_data = type_data(clean_arr_data, timezone_pattern, mappings)
    processed_data = typed_arr_data

    return processed_data
