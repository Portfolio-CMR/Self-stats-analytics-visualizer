import numpy as np
import regex as re
from typing import List, Any, Tuple, Pattern
from self_stats.munger.clean_data_shared import safe_convert_to_float, remove_invisible_characters, parse_date, clean_all_columns

def type_data(clean_dates: np.ndarray,  timezone_pattern: Pattern):
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

    return typed_dates


def main(video_urls: np.ndarray, video_titles: np.ndarray, channel_titles: np.ndarray, dates: np.ndarray) -> np.ndarray:
    """
    Main function to process data arrays for cleaning and type conversion.
    
    Args:
    search_texts, dates, latitudes, longitudes (np.ndarray): Arrays of data.

    Returns:
    Tuple of arrays after processing.
    """
    # Compile the regex pattern once and remove hidden characters
    hidden_char_pattern = re.compile(r'\p{C}+|\p{Z}+|[\u200B-\u200F\u2028-\u202F]+')
    clean_video_urls, clean_video_titles, clean_channel_titles, clean_dates = clean_all_columns(video_urls, video_titles, channel_titles, dates, hidden_char_pattern)
    
    # Compile the regex pattern once and then clean/apply data types
    timezone_pattern = re.compile(r'(?<=AM|PM)\s*([A-Z]{2,4})$')
    typed_dates  = type_data(clean_dates, timezone_pattern)
    processed_data = np.array([clean_video_urls, clean_video_titles, clean_channel_titles, typed_dates]).T

    return processed_data
