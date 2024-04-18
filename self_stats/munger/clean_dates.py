import numpy as np
import regex as re
from datetime import datetime
from typing import List, Any, Tuple, Pattern, Dict

def convert_to_arrays(data: List[Dict[str, Any]], mappings: List[str]) -> Tuple[np.ndarray, ...]:
    """
    Converts specified fields from a list of dictionaries into separate numpy arrays.
    
    Args:
        data (List[Dict[str, Any]]): Data to be converted, where each dictionary contains varying data.
        mappings (List[str]): A list of keys to extract data for each corresponding numpy array.
    
    Returns:
        Tuple[np.ndarray, ...]: A tuple of numpy arrays, each corresponding to the specified keys in the same order.
    """
    # Initialize a list of lists to hold the data for each key
    extracted_data = [[] for _ in mappings]

    # Extract data for each specified key
    for item in data:
        for idx, key in enumerate(mappings):
            extracted_data[idx].append(item.get(key, np.nan))  # np.nan as a default for missing values

    # Convert lists to numpy arrays
    arrays = tuple(np.array(column, dtype=float if any(isinstance(x, (float, int)) for x in column) else object)
                   for column in extracted_data)

    return arrays

def parse_dates(date_array: np.ndarray) -> Tuple[np.ndarray, list]:
    """
    Parse datetime from strings in a numpy array after timezone information has been removed and adjust to desired format.
    
    Args:
    - date_array (np.ndarray): Array of datetime strings without timezone information.
    
    Returns:
    - Tuple[np.ndarray, list]: Tuple of numpy array with datetime objects formatted to year, month, day, hour, and minute,
                               and list of indices with invalid dates.
    """
    parsed_dates = [None] * len(date_array)  # Pre-allocate list for parsed dates
    bad_indices = []  # List to store indices of unparseable dates

    for i, date_str in enumerate(date_array):
        try:
            # Parse the date string, replacing 'Z' with '+00:00' to handle UTC format properly
            full_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # Create a new datetime object without seconds and timezone information
            new_date = datetime(year=full_date.year, month=full_date.month, day=full_date.day,
                                hour=full_date.hour, minute=full_date.minute)
            parsed_dates[i] = new_date  # Store the adjusted datetime object
        except ValueError:
            bad_indices.append(i)  # Record the index of any unparseable date string

    parsed_dates_array = np.array(parsed_dates, dtype=object)  # Convert list to numpy array
    return parsed_dates_array, bad_indices

def remove_indices_from_tuple(data: Tuple[np.ndarray, ...], indices: List[int]) -> Tuple[np.ndarray, ...]:
    """
    Removes specified indices from each numpy array in a tuple.
    
    Args:
    - data (Tuple[np.ndarray, ...]): Tuple of numpy arrays, where each array represents a column of data.
    - indices (List[int]): List of indices to be removed from each array.
    
    Returns:
    - Tuple[np.ndarray, ...]: A new tuple of numpy arrays with specified indices removed.
    """
    if not indices:
        return data

    # Convert the list of indices to a numpy array for efficient deletion
    indices_to_remove = np.array(indices)
    # Apply numpy deletion to each array in the tuple and return the result as a new tuple
    return tuple(np.delete(arr, indices_to_remove) for arr in data)

def main(arr_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], mappings: List[str]) -> np.ndarray:
    """
    Main function to process data arrays for cleaning and type conversion.
    
    Args:
    search_texts, dates, latitudes, longitudes (np.ndarray): Arrays of data.

    Returns:
    Tuple of arrays after processing.
    """

    if mappings[0] == 'Text Title':
        date, bad_indices = parse_dates(arr_data[1])  # Parse dates and get indices of failures
        arr_data = arr_data[:1] + (date,) + arr_data[2:]  # Replace the parsed date array back into the tuple
        clean_arr = remove_indices_from_tuple(arr_data, bad_indices)
    elif mappings[0] == 'Video URL':
        date, bad_indices = parse_dates(arr_data[3])
        arr_data = arr_data[:3] + (date,) + arr_data[4:]  # Replace the parsed date array back into the tuple
        clean_arr = remove_indices_from_tuple(arr_data, bad_indices)


    return clean_arr
