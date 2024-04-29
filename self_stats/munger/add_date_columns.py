import numpy as np
from datetime import datetime
from typing import Tuple, List

def get_weekdays_np(dates: np.ndarray) -> np.ndarray:
    """
    Converts a NumPy array of datetime objects into a NumPy array of strings representing the day of the week.

    Args:
    dates (np.ndarray): A NumPy array of datetime objects.

    Returns:
    np.ndarray: A NumPy array of strings, each representing the day of the week for the corresponding datetime object.
    """
    vectorized_strftime = np.vectorize(lambda date: date.strftime('%A'))
    return vectorized_strftime(dates)

def get_hours(dates: np.ndarray) -> np.ndarray:
    """
    Converts a NumPy array of datetime objects into a NumPy array of integers representing the hour of the day.

    Args:
    dates (np.ndarray): A NumPy array of datetime objects.

    Returns:
    np.ndarray: A NumPy array of integers, each representing the hour of the day for the corresponding datetime object.
    """
    vectorized_hour = np.vectorize(lambda date: date.hour)
    return vectorized_hour(dates)

def get_dates_only(dates: np.ndarray) -> np.ndarray:
    """
    Converts a NumPy array of datetime objects into a NumPy array of date objects representing only the year, month, and day.

    Args:
    dates (np.ndarray): A NumPy array of datetime objects.

    Returns:
    np.ndarray: A NumPy array of date objects, each representing only the year, month, and day of the corresponding datetime object.
    """
    vectorized_date = np.vectorize(lambda date: date.date())
    return vectorized_date(dates)

def main(arr_data: Tuple[np.ndarray,...]) -> Tuple[np.ndarray,...]:
    """
    Processes a tuple containing at least one array of datetime objects and potentially other arrays.
    Applies transformations to extract weekdays, hours, and dates from the datetime array and combines them with other arrays in the tuple.

    Args:
    data_tuple (tuple): A tuple where the first element is assumed to be a NumPy array of datetime objects.

    Returns:
    tuple: A new tuple containing the transformed datetime arrays along with the original other elements of the input tuple.
    """
    dates = arr_data[0]

    # Apply the transformations
    weekdays_array = get_weekdays_np(dates)
    hours_array = get_hours(dates)
    dates_only_array = get_dates_only(dates)

    # Create a new tuple that includes the transformed arrays and the rest of the original tuple elements
    new_data_tuple = arr_data + (weekdays_array, hours_array, dates_only_array)

    return new_data_tuple