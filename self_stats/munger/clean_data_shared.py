import numpy as np
import regex as re
from datetime import datetime
from typing import List, Any, Tuple, Pattern

def safe_convert_to_float(value: str) -> float:
    """
    Attempts to convert a given string to a float. If the string cannot be 
    converted to a float, it returns the original string.
    
    Args:
    value (str): The string to be converted to a float.
    
    Returns:
    float or str: The converted float value or the original string if the conversion fails.
    """
    try:
        return float(value)
    except ValueError:
        return value

def remove_invisible_characters(text: str, hidden_char_pattern: Pattern) -> str:
    """
    Remove invisible and non-printable Unicode characters from a given text string using a precompiled regex pattern.
    
    Args:
    text (str): A string from which to remove invisible characters.
    compiled_pattern (Pattern): A precompiled regex pattern to match invisible characters.

    Returns:
    str: The cleaned text string without invisible characters.
    """
    return hidden_char_pattern.sub(' ', text).strip()

def remove_timezone(date_str: str, timezone_pattern: Pattern) -> str:
    """
    Extract the timezone abbreviation from a date string and return the string without it.
    
    Args:
    date_str (str): The input date string that includes a timezone abbreviation.

    Returns:
    str: The date string with timezone abbreviation removed.
    """
    return timezone_pattern.sub('', date_str).strip()

def parse_date(date_str: str, timezone_pattern: Pattern) -> datetime:
    """
    Parse the datetime from a string assuming it's formatted correctly without timezone information.

    Args:
    date_str (str): The datetime string in a specific format.

    Returns:
    datetime: The naive datetime object parsed from the string.
    """
    date_str_no_tz = remove_timezone(date_str, timezone_pattern)
    try:
        return datetime.strptime(date_str_no_tz, '%b %d, %Y, %I:%M:%S %p')
    except ValueError:
        return date_str_no_tz
    
def clean_all_columns(col_1, col_2, col_3, col_4, hidden_char_pattern: Pattern) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Apply the remove_invisible_characters function to all four numpy arrays and return new numpy arrays.
    
    Args:
    col_1, col_2, col_3, col_4 (np.ndarray): Arrays of data containing strings.
    hidden_char_pattern (Pattern): A compiled regex pattern to remove invisible characters.
    
    Returns:
    Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: A tuple of cleaned numpy arrays.
    """
    clean_columns = []
    for column in (col_1, col_2, col_3, col_4):
        cleaned = np.vectorize(remove_invisible_characters)(column, hidden_char_pattern)
        clean_columns.append(cleaned)
    
    return tuple(clean_columns)

def convert_to_arrays(data: List[List[str]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Converts a list of lists into a list of 4 numpy arrays, each representing a column in the data.
    
    Args:
    - data (List[List[str]]): Data to be converted.
    
    Returns:
    - Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: A tuple of numpy arrays.
    """
    arr = np.array(data)
    return arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]
