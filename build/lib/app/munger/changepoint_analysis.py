from collections import Counter
from datetime import datetime
from typing import List, Optional, Tuple

import numpy as np
import ruptures as rpt
from numpy import ndarray

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
