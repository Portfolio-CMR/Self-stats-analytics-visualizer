from typing import List, Any
from datetime import date
import ruptures as rpt

def trim_date(data: List[List[Any]], mapping: List[str]) -> List[List[Any]]:
    """
    Processes a list of lists, extracting relevant datetime features,
    and filters the data based on a changepoint analysis.

    Args:
        data (List[List[Any]]): Input data where each inner list represents a row with elements corresponding to ['search', 'Date', 'lat', 'long'].
        mapping (List[str]): List of column names.

    Returns:
        List[List[Any]]: A list of lists with filtered data.
    """
    date_index = mapping.index('Date')
    
    # Create a dictionary to count occurrences per day
    daily_counts = {}
    for row in data:
        date_key = row[date_index].date()  # Assuming datetime objects, extracting just the date part
        if date_key in daily_counts:
            daily_counts[date_key] += 1
        else:
            daily_counts[date_key] = 1

    # Prepare the data for changepoint detection
    dates_sorted = sorted(daily_counts.keys())
    counts = [daily_counts[date] for date in dates_sorted]
    counts_array = [[count] for count in counts]

    # Perform changepoint detection
    algo = rpt.Binseg(model='l2').fit(counts_array)
    result = algo.predict(n_bkps=1)

    # Determine the changepoint date
    if result:
        changepoint_date = dates_sorted[result[0] - 1]
    else:
        changepoint_date = dates_sorted[0]

    # Filter the data based on the changepoint
    filtered_data = [row for row in data if row[date_index].date() >= changepoint_date]

    return filtered_data
