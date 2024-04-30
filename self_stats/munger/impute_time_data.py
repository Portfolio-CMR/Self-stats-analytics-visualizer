from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import numpy as np

from datetime import datetime, timedelta

def compute_difference(previous: datetime, current: datetime, interrupt_time: int) -> float:
    """
    Calculate the time difference in minutes between two datetime objects, return None if above interrupt_time.
    """
    difference = current - previous
    difference_in_minutes = abs(round(difference.total_seconds() / 60, 2))
    return difference_in_minutes if difference_in_minutes <= interrupt_time else None

def calculate_differences(datetimes: np.ndarray, interrupt_time: timedelta) -> np.ndarray:
    """
    Calculate exact time differences between consecutive datetime entries using Python datetime,
    maintaining precision and flagging differences greater than a specified interrupt_time.
    Shift differences so the first entry shows the first calculated difference,
    and the last entry is None to indicate it is unknown.

    Parameters:
        datetimes (np.ndarray): Array of datetime.datetime objects, assumed to be sorted.
        interrupt_time (timedelta): Time difference threshold to flag interruptions.

    Returns:
        np.ndarray: Array of time differences as timedelta objects, with None where the difference exceeds interrupt_time,
                    and the last entry as None indicating an unknown difference.
    """
    # Compute differences between consecutive datetimes
    differences = [datetimes[i] - datetimes[i+1] for i in range(len(datetimes) - 1)]

    # Apply interrupt_time threshold and convert to timedelta or None
    differences = [diff if diff <= interrupt_time else None for diff in differences]

    # Append None to the end to mark the last entry as unknown
    differences.append(None)

    return np.array(differences, dtype=object)

def flag_short_videos(differences: np.ndarray) -> np.ndarray:
    """
    Flag videos as "Short-Form" if their duration is less than 2 minutes, and "Long-Form" otherwise, using NumPy timedelta objects.
    Entries that are None will have a label of "Undetermined".

    Parameters:
        differences (np.ndarray): Array of time differences as timedelta objects, where each element can be None or a timedelta.

    Returns:
        np.ndarray: Array of strings where "Short-Form" indicates a video duration less than 2 minutes, and "Long-Form" otherwise.
        Entries corresponding to None inputs will be labeled as "Undetermined".
    """
    two_minutes = np.timedelta64(2, 'm')  # Define two-minute timedelta for comparison

    # Create a mask for None values in the array
    none_mask = np.vectorize(lambda x: x is None)(differences)

    # Handle valid timedelta comparisons separately
    valid_differences = np.where(none_mask, np.timedelta64(0, 'm'), differences)  # Replace None with a neutral value
    comparison_mask = valid_differences < two_minutes  # This comparison is now safe

    # Use np.where to handle None values and assign appropriate labels
    labels = np.where(
        none_mask,
        "Undetermined",
        np.where(comparison_mask, "Short-Form", "Long-Form")
    )

    return labels

def identify_activity_windows(differences: np.ndarray) -> np.ndarray:
    """
    Identify continuous segments of activity enclosed by None, using NumPy methods.
    This version excludes any 'windows' where the start and end indices are the same, ensuring only meaningful windows are returned.

    Parameters:
        differences (np.ndarray): Array where continuous segments are to be identified, with None indicating breaks.

    Returns:
        np.ndarray: An array of [start, end] indices, excluding windows that start and end on the same index.
    """
    # Identify all non-None indices
    non_none_indices = np.where(differences != None)[0]
    
    # Identify breaks in continuous sequences
    breaks = np.where(np.diff(non_none_indices) != 1)[0] + 1
    
    # Determine start and end indices for each window
    starts = non_none_indices[np.insert(breaks, 0, 0)]
    ends = non_none_indices[np.append(breaks - 1, len(non_none_indices) - 1)]
    
    # Filter out windows where the start and end indices are the same
    windows = np.column_stack((starts, ends))
    windows = windows[windows[:, 0] != windows[:, 1]]

    return windows

def group_timestamps_by_windows(timestamps: np.ndarray, windows: np.ndarray) -> list:
    """
    Group timestamps based on the provided windows.
    """
    return [timestamps[start:end+1] for start, end in windows if start + 1 <= end]

def calculate_window_durations(timestamps: np.ndarray, windows: np.ndarray) -> tuple:
    """
    Calculate the total duration for each window in minutes and extract the actual start time for each window.

    Parameters:
        timestamps (np.ndarray): Array of datetime.datetime objects.
        windows (np.ndarray): Array of tuples, each containing the start and end index of a window.

    Returns:
        tuple: A tuple containing two numpy arrays:
               1. Durations of each window in minutes (float).
               2. Actual start datetime for each window (datetime.datetime).
    """
    # Calculate durations
    durations = [round((timestamps[start] - timestamps[end]).total_seconds() / 60, 4) for start, end in windows]

    # Extract start times using the start index for each window
    start_times = np.array([timestamps[end] for _ , end in windows], dtype=object)

    return np.array(durations, dtype=float), start_times

def calculate_average_counts_per_window(durations: np.ndarray, counts: np.ndarray) -> np.ndarray:
    """
    Calculate the average counts per minute for each activity window by dividing the counts by the window duration.
    Replace any result exceeding 10 with NaN.
    """
    valid = durations > 0  # durations must be positive
    averages = np.zeros_like(durations, dtype=float)
    averages[valid] = np.round(counts[valid] / durations[valid], 3)

    # Replace values greater than 20 with NaN
    averages[averages > 10] = np.nan
    return averages

def count_entries_in_windows(windows: np.ndarray) -> np.ndarray:
    """
    Calculate the total number of entries for each activity window using NumPy.

    Parameters:
        timestamps (np.ndarray): Array of datetime objects.
        windows (np.ndarray): Array of tuples, each containing the start and end index of an activity window.
    
    Returns:
        np.ndarray: Array of the total number of entries for each window.
    """
    counts = np.array([end - start + 1 for start, end in windows])
    return counts

def main(arr_data: tuple, mappings: list) -> tuple:
    """
    Main function to process datetime data and perform analyses.
    """
    timestamps = arr_data[0]
    video = mappings[1] == 'Video_Title'

    interrupt_time = timedelta(minutes=20)  # Maximum time difference in minutes to consider as an interruption
    differences = calculate_differences(timestamps, interrupt_time)
    
    windows = identify_activity_windows(differences)
    grouped_timestamps = group_timestamps_by_windows(timestamps, windows)
    window_durations, start_markers = calculate_window_durations(timestamps, windows)
    window_counts = count_entries_in_windows(windows)
    counts_over_duration = calculate_average_counts_per_window(window_durations, window_counts)

    if video:
        short_flags = flag_short_videos(differences)  # flags for short videos
        imputed_arr = (*arr_data, differences, short_flags)
        metadata = (start_markers, windows[:, 1], windows[:, 0], window_durations, window_counts, counts_over_duration)
    else:
        imputed_arr = (*arr_data, differences)
        metadata = (start_markers, windows[:, 1], windows[:, 0], window_durations, window_counts, counts_over_duration)

    return imputed_arr, metadata
