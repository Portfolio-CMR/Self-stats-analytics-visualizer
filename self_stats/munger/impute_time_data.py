from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import numpy as np

def compute_difference(previous: datetime, current: datetime, interrupt_time: int) -> Optional[float]:
    """
    Calculate the time difference in minutes between two datetime objects.
    
    Parameters:
        previous (datetime): The earlier datetime object.
        current (datetime): The later datetime object.
        interrupt_time (int): The maximum time difference in minutes to consider as an interruption.
    
    Returns:
        Optional[float]: The time difference in minutes if less than or equal to the interrupt_time; otherwise, None.
    """
    try:
        difference = current - previous
        difference_in_minutes = abs(round(difference.total_seconds() / 60, 2))
        if difference_in_minutes > interrupt_time:
            return None
        return difference_in_minutes
    except TypeError:
        return None

def calculate_differences(datetimes: List[datetime], interrupt_time: int) -> List[Optional[float]]:
    """
    Calculate the time differences in minutes between consecutive datetime entries in a list.
    
    Parameters:
        datetimes (List[datetime]): A list of datetime objects in chronological order.
        interrupt_time (int): The maximum time difference in minutes to consider as an interruption.
        
    Returns:
        List[Optional[float]]: A list of the time differences in minutes between each consecutive datetime.
                                Differences greater than the interrupt time are returned as None.
    """
    time_differences = [None]
    previous_datetime = datetimes[0]

    for current_datetime in datetimes[1:]:
        diff = compute_difference(previous_datetime, current_datetime, interrupt_time)
        time_differences.append(diff)
        previous_datetime = current_datetime

    return time_differences

def pair_differences_with_videos(datetimes: List[datetime], differences: List[Optional[float]]) -> List[Tuple[datetime, Optional[float]]]:
    """
    Pair each datetime with the corresponding difference expressed in minutes.
    The first datetime has None as its difference since there's no prior video to compare.
    
    Parameters:
        datetimes (List[datetime]): A list of datetime objects in chronological order.
        differences (List[Optional[float]]): A list of differences in minutes between each consecutive datetime.
    
    Returns:
        List[Tuple[datetime, Optional[float]]]: A list of tuples where each tuple consists of a datetime object and
                                                the corresponding time difference. The first datetime is paired with None.
    """
    paired_list = [(datetimes[0], None)] + [(datetimes[i], differences[i-1]) for i in range(1, len(datetimes))]
    return paired_list

def flag_short_videos(video_durations: List[Optional[float]]) -> List[bool]:
    """
    Flag each video duration to determine if it is a "short" video (less than 1 minute).
    
    Parameters:
        video_durations (List[Optional[float]]): List of video durations in minutes.
    
    Returns:
        List[bool]: A list of boolean flags where True  indicates a short video and False otherwise.
    """
    return [duration is not None and duration < 2 for duration in video_durations]

def identify_activity_windows(differences: List[Optional[float]]) -> List[Tuple[int, int]]:
    """
    Find index ranges in a list that are fully enclosed by None values on both ends.
    
    Parameters:
        data (List[Optional[float]]): A list containing numbers and None types.
    
    Returns:
        List[Tuple[int, int]]: A list of tuples, each representing the start and end index of sequences enclosed by None.
    """
    windows = []
    start = None

    # Check that a window starts only if preceded by None and not already started
    for i in range(1, len(differences)):
        if differences[i] is not None and differences[i-1] is None:
            start = i  # Start of a new range if preceded by None
        elif differences[i] is None and start is not None:
            if i-1 > start:  # Check if the range has more than one element
                windows.append((int(start), int(i - 1)))
            start = None  # End the current range
    
    return windows

def group_timestamps_by_windows(timestamps: List[datetime], windows: List[Tuple[int, int]]) -> List[List[datetime]]:
    """
    Group timestamps based on provided index ranges representing activity windows, excluding the first entry of each window.
    
    Parameters:
        timestamps (List[datetime]): List of timestamp data.
        windows (List[Tuple[int, int]]): List of tuples, where each tuple contains the start and end index of an activity window.
    
    Returns:
        List[List[datetime]]: A list of lists, where each inner list contains the timestamps corresponding to an activity window, excluding the first entry which is still part of an inactivity period.
    """
    grouped_timestamps = []
    for start, end in windows:
        # Increment the start index to exclude the first entry and check if the range is still valid
        if start + 1 <= end:
            grouped_timestamps.append(timestamps[start:end + 1])  # end + 1 because end index is inclusive
        else:
            # If the range is invalid (start + 1 > end), append an empty list or handle accordingly
            continue

    return grouped_timestamps

def calculate_window_durations(timestamps: List[datetime], windows: List[Tuple[int, int]]) -> List[float]:
    """
    Calculate the total duration for each activity window in minutes.
    
    Parameters:
        timestamps (List[datetime]): List of timestamp data.
        windows (List[Tuple[int, int]]): List of tuples, each containing the start and end index of an activity window.
    
    Returns:
        List[float]: A list of durations for each window in minutes.
    """
    durations = []
    window_timestamps = []
    for end, start in windows:
        if start < len(timestamps) and end < len(timestamps):
            duration = round((timestamps[end] - timestamps[start]).total_seconds() / 60, 3)  # Duration in minutes
            durations.append(duration)
            window_timestamps.append(timestamps[start])  # Append the start timestamp for each window for future indexing in plots
        else:
            # Handle out-of-range indices
            durations.append(0.0)  # Could be changed to None or another placeholder to indicate an invalid range
            window_timestamps.append(timestamps[start])  # Append the start timestamp for each window for future indexing in plots

    return durations, window_timestamps

def count_entries_in_windows(timestamps: List[datetime], windows: List[Tuple[int, int]]) -> List[int]:
    """
    Calculate the total number of entries for each activity window.
    
    Parameters:
        timestamps (List[datetime]): List of timestamp data.
        windows (List[Tuple[int, int]]): List of tuples, each containing the start and end index of an activity window.
    
    Returns:
        List[int]: A list of the total number of entries for each window.
    """
    counts = []
    for end, start in windows:
        if end <= start and start < len(timestamps) and end < len(timestamps):
            count = start - end + 1  # Include both start and end in the count
            counts.append(count)
        else:
            # Handle out-of-range indices or invalid ranges
            counts.append(0)  # Could be changed to None to indicate an invalid or non-existent window

    return counts

def calculate_average_durations_per_entry(durations: List[float], counts: List[int]) -> List[float]:
    """
    Calculate the average duration per entry for each activity window by dividing the total duration by the total number of entries.
    
    Parameters:
        durations (List[float]): List of total durations for each window in minutes.
        counts (List[int]): List of total entries for each window.
    
    Returns:
        List[float]: A list of average durations per entry for each window, in minutes.
    """
    all_window_counts_per_10_minutes = []
    for duration, count in zip(durations, counts):
        if counts == 2:
            counts_per_10_minutes = None # Quick clicks distort the data so we will ignore them
        if duration > 0:
            counts_per_10_minutes = round(10 * (count / duration), 3)
        else:
            counts_per_10_minutes = None  # Assign 0 or None if count is zero to indicate no entries or undefined
        all_window_counts_per_10_minutes.append(counts_per_10_minutes)

    return all_window_counts_per_10_minutes

def main(arr_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], mappings: List[str]) -> Tuple[np.ndarray, ...]:

    if mappings[0] == 'Text Title':
        timestamps = arr_data[1]
        video = False
    elif mappings[0] == 'Video URL':
        timestamps = arr_data[3]
        video = True
    else:
        raise ValueError("Invalid mapping value")

    interrupt_time = 20 # Maximum time difference in minutes to consider as an interruption

    differences = calculate_differences(timestamps, interrupt_time)
    paired_differences = pair_differences_with_videos(timestamps, differences)
    
    windows = identify_activity_windows(differences)
    grouped_timestamps = group_timestamps_by_windows(timestamps, windows)
    window_durations, window_timestamps = calculate_window_durations(timestamps, windows)
    window_counts = count_entries_in_windows(timestamps, windows)
    counts_over_duration = calculate_average_durations_per_entry(window_durations, window_counts)

    if video:
        # Create flags and append to imputed_arr
        short_flags = flag_short_videos([pair[1] for pair in paired_differences]) 
        imputed_arr = (*arr_data, np.array(differences), np.array(short_flags),)
        metadata = (np.array(windows)[:,1], np.array(windows)[:,0], np.array(window_timestamps), np.array(window_durations), np.array(window_counts), np.array(counts_over_duration))
    else:
        imputed_arr = (*arr_data, np.array(differences))
        metadata = (np.array(windows)[:,1], np.array(windows)[:,0], np.array(window_timestamps), np.array(window_durations), np.array(window_counts), np.array(counts_over_duration))

    return imputed_arr, metadata