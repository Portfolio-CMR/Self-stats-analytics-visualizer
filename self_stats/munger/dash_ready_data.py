from typing import List, Any
from datetime import datetime
import ruptures as rpt
import numpy as np
from collections import Counter

def trim_date(data: np.ndarray, mapping: List[str]) -> np.ndarray:
    """
    Processes a numpy array, extracting relevant datetime features,
    and filters the data based on a changepoint analysis.

    Args:
        data (np.ndarray): Input data where each row represents different data types.
        mapping (List[str]): List of column names indicating what each row represents.

    Returns:
        np.ndarray: A numpy array with filtered data.
    """
    date_index = mapping.index('Date')
    
    # Extract just the date part from each datetime object using NumPy's vectorization
    dates_only = np.vectorize(lambda dt: dt.date())(data[date_index])

    # Use Counter to count occurrences of each date
    daily_counts = Counter(dates_only)

    # Convert daily_counts to sorted arrays
    dates_sorted = sorted(daily_counts.keys())
    counts_array = np.array([daily_counts[date] for date in dates_sorted]).reshape(-1, 1)

    # Perform changepoint detection
    algo = rpt.Binseg(model='l2').fit(counts_array)
    result = algo.predict(n_bkps=1)

    # Determine the changepoint date
    if result:
        changepoint_date = dates_sorted[result[0] - 1]
    else:
        changepoint_date = dates_sorted[0]

    # Filter data columns based on the changepoint
    filtered_indices = np.array([date >= changepoint_date for date in dates_only])
    filtered_data = data[:, filtered_indices]  # Assuming data columns are vertically aligned with dates

    return filtered_data
