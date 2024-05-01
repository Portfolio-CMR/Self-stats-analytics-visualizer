import numpy as np
import pandas as pd
from typing import Tuple, List

def create_dataframe(datetime_array: np.ndarray, categorical_array: np.ndarray) -> pd.DataFrame:
    """
    Create a DataFrame from datetime and categorical arrays.
    
    Parameters:
    - datetime_array (np.ndarray): Array of datetime objects.
    - categorical_array (np.ndarray): Array of categorical data.
    
    Returns:
    - pd.DataFrame: DataFrame with a datetime index and a category column.
    """
    df = pd.DataFrame({'Datetime': pd.to_datetime(datetime_array), 'Category': categorical_array})
    df.set_index('Datetime', inplace=True)
    return df

def count_entries_per_day(df: pd.DataFrame) -> pd.Series:
    """
    Count the number of entries per day in the DataFrame, only reporting days with entries.
    
    Parameters:
    - df (pd.DataFrame): DataFrame indexed by datetime.
    
    Returns:
    - pd.Series: Series with counts of entries per day.
    """
    # Resample by day and count entries
    daily_counts = df.resample('D').size()
    # Filter out days with no entries (count == 0)
    filtered_counts = daily_counts[daily_counts > 0]
    day_of_week = filtered_counts.index.day_name()

    # Extract date and hour from the datetime
    df['Date'] = df.index.date
    df['Hour'] = df.index.hour

    # Group by date and hour, count occurrences, and find the hour with the maximum count per day
    most_frequent = df.groupby('Date')['Hour'].agg(lambda x: x.mode()[0] if not x.mode().empty else None).reset_index()
    max_hour = most_frequent.set_index('Date')['Hour']

    return filtered_counts, day_of_week, max_hour 

def calculate_category_ratios(df: pd.DataFrame) -> pd.Series:
    """
    Calculate the ratio of 'Short-Form' to 'Long-Form' occurrences per day from a DataFrame that contains datetime indices and 
    categorical values indicating entry types. The function handles days with no 'Long-Form' entries by setting the ratio to NaN 
    for those days. Additionally, any result that computes to 0 is also set to NaN to exclude days with no 'Short-Form' entries.

    Parameters:
    - df (pd.DataFrame): DataFrame indexed by datetime with a categorical column.
    
    Returns:
    - pd.Series: Series with the ratio of 'Short-Form' to 'Long-Form' per day. Days without 'Long-Form' entries or with a ratio of 0
      result in NaN.
    """
    # Group by day and category, then pivot to create a table of counts per category each day
    daily_counts = df.groupby([pd.Grouper(freq='D'), 'Category']).size().unstack(fill_value=0)
    
    # Calculate the ratio of 'Short-Form' to 'Long-Form'
    ratio_per_day = daily_counts['Short-Form'] / daily_counts['Long-Form']
    
    # Replace any infinities or NaNs resulting from division by 0, and convert any 0 ratios to NaN
    ratio_per_day = ratio_per_day.replace([np.inf, np.nan, 0], np.nan)

    return ratio_per_day

def prepare_output(date_series: pd.Series, counts: np.ndarray, weekday: pd.Series) -> Tuple[np.ndarray, ...]:
    """
    Prepare the output tuple with formatted dates, counts, and category ratios.
    
    Parameters:
    - date_series (pd.Series): Series of datetime objects.
    - counts (np.ndarray): Array of daily entry counts.
    - ratios (np.ndarray): Array of daily category ratios.
    
    Returns:
    - Tuple[np.ndarray, ...]: Tuple containing formatted date strings, counts, and ratios.
    """
    date_strings = date_series.index.strftime('%Y-%m-%d').astype(str)
    return (date_strings, counts, weekday)

def remove_unique_entries(data_tuple):
    """
    Removes entries from both arrays in the tuple where the entry in the second array is unique.
    
    Parameters:
    - data_tuple (tuple): A tuple of two arrays. First array holds datetime information,
                          and the second array holds keywords.
    
    Returns:
    - tuple: A tuple of two arrays with unique entries removed.
    """
    # Unpack the tuple into two arrays
    datetime_array, keyword_array = data_tuple

    datetime_array = np.array(datetime_array)
    keyword_array = np.array(keyword_array)
    
    # Find all unique values and their counts in the keyword array
    unique_keywords, counts = np.unique(keyword_array, return_counts=True)
    
    # Filter out keywords that occur less than  3 times
    non_unique_keywords = unique_keywords[counts > 2]
    
    # Create a mask that is True for indices where the keyword is not unique
    mask = np.isin(keyword_array, non_unique_keywords)
    
    # Filter both arrays using the mask
    filtered_datetime_array = datetime_array[mask]
    filtered_keyword_array = keyword_array[mask]
    
    return (filtered_datetime_array, filtered_keyword_array)

def aggregate_activity_by_day(data: Tuple[np.ndarray, ...], column_names: List[str]) -> Tuple[np.ndarray, ...]:
    """
    Calculates the average values for each numerical column per day from a tuple of arrays.

    Parameters:
    - data (Tuple[np.ndarray, ...]): Tuple of arrays where each array represents a column. 
      The first column is assumed to be datetime.
    - column_names (List[str]): Names of the columns corresponding to the arrays in the data tuple.

    Returns:
    - Tuple[np.ndarray, ...]: A tuple of arrays, each containing the daily averages of the respective columns.
    """
    # Create a DataFrame from the tuple of arrays
    df = pd.DataFrame(data={name: array for name, array in zip(column_names, data)})

    # Ensure the datetime column is treated as datetime type
    df[column_names[0]] = pd.to_datetime(df[column_names[0]])

    # Extract date part from the datetime
    df['Date'] = df[column_names[0]].dt.date
    df = df.drop([column_names[0], column_names[1], column_names[2]], axis=1)


    # Group by the date and calculate mean for each column except the datetime
    grouped = df.groupby('Date').mean()

    # Return the results as a tuple of arrays, one for each column (including the date)
    return (grouped.index.values,) + tuple(grouped[col].values for col in grouped.columns)


def main(arr_data: Tuple[np.ndarray, ...], mappings: List[str]) -> Tuple[np.ndarray, ...]:

    datetime_array = arr_data[0]
    try:
        # video_type_index = mappings.index('Short_Form_Ratio')
        video_type = arr_data[8]
    except IndexError:
        video_type = None

    if video_type is not None:
        df = pd.DataFrame({'Datetime': pd.to_datetime(datetime_array), 'Category': video_type})
        df.set_index('Datetime', inplace=True)
        # Count entries per day
        counts_per_day, weekday, max_hour = count_entries_per_day(df)
        # Calculate the ratio of 'Short-Form' to 'Long-Form'
        ratios_per_day = calculate_category_ratios(df)
        # Prepare the final output
        date_strings = counts_per_day.index.strftime('%Y-%m-%d').astype(str)
        output = (date_strings, counts_per_day.values, weekday.values, max_hour.values, ratios_per_day.values)
        return output
    else:
        df = pd.DataFrame({'Datetime': pd.to_datetime(datetime_array)})
        df.set_index('Datetime', inplace=True)
        # Count entries per day
        counts_per_day, weekday, max_hour = count_entries_per_day(df)
        date_strings = counts_per_day.index.strftime('%Y-%m-%d').astype(str)
        # Prepare the final output
        output = (date_strings, counts_per_day.values, weekday.values, max_hour.values)

        return output

