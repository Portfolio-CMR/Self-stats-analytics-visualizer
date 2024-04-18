import numpy as np
import regex as re
from typing import List, Any, Tuple, Pattern
from self_stats.munger.clean_data_shared import safe_convert_to_float, remove_invisible_characters, parse_date, clean_all_columns

def type_data(clean_dates , clean_latitudes, clean_longitudes, timezone_pattern: Pattern):
    """
    Process the data from numpy arrays by cleaning and converting each element.
    
    Args:
    search_texts, dates, latitudes, longitudes (np.ndarray): Arrays of data.
    compiled_pattern (Pattern): A compiled regex pattern to remove invisible characters.
    data_source (str): String indicating the type of data to process.

    Returns:
    Tuple of arrays after processing.
    """
    typed_dates = np.vectorize(parse_date)(clean_dates, timezone_pattern)
    typed_latitudes = np.vectorize(safe_convert_to_float)(clean_latitudes)
    typed_longitudes = np.vectorize(safe_convert_to_float)(clean_longitudes)

    return typed_dates, typed_latitudes, typed_longitudes


def main(search_texts: np.ndarray, dates: np.ndarray, latitudes: np.ndarray, longitudes: np.ndarray) -> np.ndarray:
    """
    Main function to process data arrays for cleaning and type conversion.
    
    Args:
    search_texts, dates, latitudes, longitudes (np.ndarray): Arrays of data.

    Returns:
    Tuple of arrays after processing.
    """
    # Compile the regex pattern once and remove hidden characters
    hidden_char_pattern = re.compile(r'\p{C}+|\p{Z}+|[\u200B-\u200F\u2028-\u202F]+')
    clean_search_texts, clean_dates, clean_latitudes, clean_longitudes = clean_all_columns(search_texts, dates, latitudes, longitudes, hidden_char_pattern)
    
    # Compile the regex pattern once and then clean/apply data types
    timezone_pattern = re.compile(r'(?<=AM|PM)\s*([A-Z]{2,4})$')
    typed_dates, typed_latitude, typed_longitude = type_data(clean_dates, clean_latitudes, clean_longitudes, timezone_pattern)
    processed_data = np.array([clean_search_texts, typed_dates, typed_latitude, typed_longitude]).T

    return processed_data
