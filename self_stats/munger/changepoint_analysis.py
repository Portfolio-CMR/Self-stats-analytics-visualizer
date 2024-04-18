import numpy as np
from numpy import ndarray
from datetime import datetime
from typing import Tuple, List
import ruptures as rpt
from collections import Counter

def remove_timezones(date_array: ndarray) -> ndarray:
    """
    Simplify datetime objects to dates only, assuming numpy datetime objects are used.

    Args:
        date_array (ndarray): Array of datetime objects.

    Returns:
        ndarray: Array of dates only.
    """
    return date_array.astype('datetime64[D]')

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

def detect_changepoint(dates_sorted: ndarray, counts_array: ndarray) -> datetime:
    """
    Perform changepoint detection on the array of counts.

    Args:
        dates_sorted (ndarray): Array of sorted dates.
        counts_array (ndarray): Array where each entry represents the count of occurrences for a specific date.

    Returns:
        datetime: The determined changepoint date.
    """
    algo = rpt.Binseg(model='l2').fit(counts_array)
    result = algo.predict(n_bkps=1)
    if result:
        return dates_sorted[result[0] - 1]
    return dates_sorted[0]

def trim_date(data: Tuple[ndarray, ndarray, ndarray, ndarray], mapping: List[str]) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
    """
    Filters data based on a changepoint analysis of datetime features.

    Args:
        data (Tuple[ndarray, ndarray, ndarray, ndarray]): Input data tuple, each ndarray representing a column.
        mapping (List[str]): List indicating what each column represents.

    Returns:
        Tuple[ndarray, ndarray, ndarray, ndarray]: Filtered data tuple.
    """
    date_index = mapping.index('Date')
    dates = remove_timezones(data[date_index])
    dates_sorted, counts_array = calculate_daily_counts(dates)
    changepoint_date = detect_changepoint(dates_sorted, counts_array)
    filtered_indices = np.array([date >= changepoint_date for date in dates])
    return tuple(arr[filtered_indices] for arr in data)
