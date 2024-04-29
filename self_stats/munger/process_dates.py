import numpy as np
import regex as re
from datetime import datetime, timezone
from typing import List, Any, Tuple, Pattern, Dict

from collections import Counter
from datetime import datetime
from typing import List, Optional, Tuple

import numpy as np
import ruptures as rpt
from numpy import ndarray
import tzlocal  # Import tzlocal for detecting local timezone
from zoneinfo import ZoneInfo  

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

def get_local_naive_datetime_from_utc(utc_datetime):
    """
    Converts a given UTC datetime to the local timezone and then makes it naive.

    Args:
        utc_datetime (datetime.datetime): A datetime object in UTC.

    Returns:
        datetime.datetime: A naive datetime object converted to the local timezone.
    """
    # Get the local timezone using tzlocal
    local_timezone = tzlocal.get_localzone()
    # Ensure the UTC datetime is timezone-aware
    if utc_datetime.tzinfo is None or utc_datetime.tzinfo.utcoffset(utc_datetime) is None:
        utc_datetime = utc_datetime.replace(tzinfo=datetime.timezone.utc)
    # Convert the datetime to the local timezone
    local_datetime = utc_datetime.astimezone(local_timezone)
    # Make the datetime object naive by removing timezone information
    naive_local_datetime = local_datetime.replace(tzinfo=None, microsecond=0)

    return naive_local_datetime

def parse_iso_datetime(date_str):
    """
    Parse an ISO 8601 datetime string to a datetime object with timezone awareness.
    
    Args:
        date_str (str): ISO 8601 formatted datetime string (e.g., '2024-04-20T05:55:07.811Z').
    
    Returns:
        datetime: A timezone-aware datetime object.
    """
    # Remove the 'Z' and replace it with '+00:00' to indicate UTC offset
    if date_str.endswith('Z'):
        date_str = date_str[:-1] + '+00:00'
    
    # Parse the datetime string to a datetime object
    date_object = datetime.fromisoformat(date_str)
    
    # Set the timezone to UTC if it's not already set
    if date_object.tzinfo is None:
        date_object = date_object.replace(tzinfo=timezone.utc)
    
    return date_object

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
        if not date_str:
            bad_indices.append(i)
        try:
            full_date = parse_iso_datetime(date_str)
            local_date = get_local_naive_datetime_from_utc(full_date)

            parsed_dates[i] = local_date  # Store the adjusted datetime object
        except (ValueError, TypeError):
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

####### Changepoint analysis #######

def calculate_daily_counts(dates: ndarray) -> Tuple[ndarray, ndarray]:
    """
    Count occurrences of each unique date in the provided array.

    Args:
        dates (ndarray): Array of dates.

    Returns:
        Tuple[ndarray, ndarray]: Arrays of sorted dates and their corresponding counts.
    """
    daily_counts = Counter(dates)
    dates_sorted = sorted(daily_counts.keys())
    counts_array = np.array([daily_counts[date] for date in dates_sorted]).reshape(-1, 1)
    return np.array(dates_sorted), counts_array

def detect_changepoint(dates_sorted: ndarray, counts_array: ndarray, threshold: float = 0.05) -> Optional[datetime]:
    """
    Perform changepoint detection on the array of counts and assess the significance of the change.

    Args:
        dates_sorted (ndarray): Array of sorted dates.
        counts_array (ndarray): Array where each entry represents the count of occurrences for a specific date.
        threshold (float): Significance level for determining the changepoint.

    Returns:
        Optional[datetime]: The determined changepoint date, or None if no significant changepoint is detected.
    """
    algo = rpt.Binseg(model='l2').fit(counts_array)
    result = algo.predict(n_bkps=1)
    if result:
        changepoint_index = result[0] - 1
        # Calculate the relative change in magnitude at the changepoint
        if changepoint_index > 0:
            pre_change = np.mean(counts_array[:changepoint_index])
            post_change = np.mean(counts_array[changepoint_index:])
            relative_change = abs(post_change - pre_change) / pre_change
            if relative_change > threshold:
                return dates_sorted[changepoint_index]
    return None

def trim_date(data: Tuple[ndarray, ndarray, ndarray, ndarray], mapping: List[str], threshold: float = 20) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
    """
    Filters data based on a changepoint analysis of datetime features. If no significant changepoint is found,
    returns the original dataset.

    Args:
        data (Tuple[ndarray, ndarray, ndarray, ndarray]): Input data tuple, each ndarray representing a column.
        mapping (List[str]): List indicating what each column represents.
        threshold (float): Threshold to determine the significance of the changepoint.

    Returns:
        Tuple[ndarray, ndarray, ndarray, ndarray]: Filtered or original data tuple.
    """
    date_index = mapping.index('Date')
    dates = data[date_index].astype('datetime64[D]')
    dates_sorted, counts_array = calculate_daily_counts(dates)
    changepoint_date = detect_changepoint(dates_sorted, counts_array, threshold)
    if changepoint_date:
        filtered_indices = np.array([date >= changepoint_date for date in dates])
        return tuple(arr[filtered_indices] for arr in data)
    else:
        return data

####### Main function for cleaning dates #######

def clean_dates_main(arr_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], mappings: List[str]) -> np.ndarray:
    """
    Main function to process data arrays for cleaning and type conversion.
    
    Args:
    search_texts, dates, latitudes, longitudes (np.ndarray): Arrays of data.

    Returns:
    Tuple of arrays after processing.
    """

    dates, bad_indices = parse_dates(arr_data[0])
    arr_data = (dates,) + arr_data[1:]
    clean_arr = remove_indices_from_tuple(arr_data, bad_indices)


    return clean_arr
