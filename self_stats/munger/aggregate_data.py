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
    Count the number of entries per day in the DataFrame.
    
    Parameters:
    - df (pd.DataFrame): DataFrame indexed by datetime.
    
    Returns:
    - pd.Series: Series with counts of entries per day.
    """
    return df.resample('D').size()


def calculate_category_ratios(df: pd.DataFrame) -> pd.Series:
    """
    Calculate the ratio of 'Short-Form' to 'Long-Form' occurrences per day.
    
    Parameters:
    - df (pd.DataFrame): DataFrame indexed by datetime with a categorical column.
    
    Returns:
    - pd.Series: Series with the ratio of 'Short-form' to 'Long-form' per day.
    """
    short_form_counts = df[df['Category'] == 'Short-form'].resample('D').count()
    long_form_counts = df[df['Category'] == 'Long-form'].resample('D').count()
    undetermined_counts = df[df['Category'] == 'Undetermined'].resample('D').count()
    ratio_per_day = (short_form_counts / long_form_counts).fillna(0)['Category']

    return ratio_per_day

def prepare_output(date_series: pd.Series, counts: np.ndarray) -> Tuple[np.ndarray, ...]:
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
    return (date_strings, counts)

# Define all the previously created functions here or ensure they are imported if defined elsewhere

def main(arr_data: Tuple[np.ndarray, ...], mappings: List[str]) -> Tuple[np.ndarray, ...]:

    datetime_array = arr_data[0]
    try:
        video_type_index = mappings.index('Short_Form_Video')
        video_type = arr_data[video_type_index]
    except ValueError:
        video_type = None

    if video_type is not None:
        df = pd.DataFrame({'Datetime': pd.to_datetime(datetime_array), 'Category': video_type})
        df.set_index('Datetime', inplace=True)
        # Count entries per day
        counts_per_day = count_entries_per_day(df)
        # Calculate the ratio of 'Short-Form' to 'Long-Form'
        ratios_per_day = calculate_category_ratios(df)
        # Prepare the final output
        just_date_counts = prepare_output(counts_per_day, counts_per_day.values)
        output = (just_date_counts[0], just_date_counts[1], ratios_per_day.values)
        
        return output
    else:
        df = pd.DataFrame({'Datetime': pd.to_datetime(datetime_array)})
        df.set_index('Datetime', inplace=True)
        # Count entries per day
        counts_per_day = count_entries_per_day(df)
        # Prepare the final output
        output = prepare_output(counts_per_day, counts_per_day.values)

        return output

