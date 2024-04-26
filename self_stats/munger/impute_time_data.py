from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import numpy as np

def compute_difference(previous: datetime, current: datetime) -> Optional[float]:
    """
    Calculate the time difference in minutes between two datetime objects.
    
    Parameters:
        previous (datetime): The earlier datetime object.
        current (datetime): The later datetime object.
    
    Returns:
        Optional[float]: The time difference in minutes if less than or equal to 60 minutes; otherwise, None.
    """
    try:
        difference = current - previous
        difference_in_minutes = abs(round(difference.total_seconds() / 60, 2))
        if difference_in_minutes > 60:
            return None
        return difference_in_minutes
    except TypeError:
        return None

def calculate_differences(datetimes: List[datetime]) -> List[Optional[float]]:
    """
    Calculate the time differences in minutes between consecutive datetime entries in a list.
    
    Parameters:
        datetimes (List[datetime]): A list of datetime objects in chronological order.
    
    Returns:
        List[Optional[float]]: A list of the time differences in minutes between each consecutive datetime.
                                Differences greater than 60 minutes are returned as None.
    """
    time_differences = [None]
    previous_datetime = datetimes[0]

    for current_datetime in datetimes[1:]:
        diff = compute_difference(previous_datetime, current_datetime)
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
    Identify user activity windows based on periods of inactivity of more than 60 minutes.
    
    Returns:
        List[Tuple[int, int]]: List of tuples indicating the start and end indices of each activity window.
    """
    windows = []
    start_index = 0

    for i, diff in enumerate(differences):
        if diff is None and i > 0:
            windows.append((start_index, i))
            start_index = i + 1

    # Ensure to add the last window if the last activity did not end with a timeout
    if start_index < len(differences):
        windows.append((start_index, len(differences)))

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
            grouped_timestamps.append(timestamps[start + 1:end + 1])  # end + 1 because end index is inclusive
        else:
            # If the range is invalid (start + 1 > end), append an empty list or handle accordingly
            continue

    return grouped_timestamps

def average_window_length(timestamps: List[datetime], windows: List[Tuple[int, int]]) -> float:
    """
    Calculate the average length of activity windows.
    
    Parameters:
        timestamps (List[datetime]): List of timestamp data.
        windows (List[Tuple[int, int]]): List of tuples, each tuple containing the start and end index of an activity window.
    
    Returns:
        float: The average length of the activity windows in minutes.
    """
    total_duration = 0
    num_windows = len(windows)
    
    for end, start in windows:
        if end < len(timestamps) and start < len(timestamps):
            start_time = timestamps[start]
            end_time = timestamps[end]
            duration = (end_time - start_time).total_seconds() / 60  # Duration in minutes
            total_duration += duration
    
    if num_windows > 0:
        average_duration = total_duration / num_windows
    else:
        average_duration = 0  # No windows to average
    
    return average_duration

def average_actions_per_minute(timestamps: List[datetime], windows: List[Tuple[int, int]]) -> List[float]:
    """
    Calculate the average number of user actions per minute for each activity window.
    
    Parameters:
        timestamps (List[datetime]): List of timestamp data indicating when actions occurred.
        windows (List[Tuple[int, int]]): List of tuples, each tuple containing the start and end index of an activity window.
    
    Returns:
        List[float]: List of average actions per minute for each activity window.
    """
    averages = []

    for end, start in windows:
        if start < len(timestamps) and end < len(timestamps):
            window_duration_minutes = (timestamps[end] - timestamps[start]).total_seconds() / 60
            num_actions = end - start + 1
            if window_duration_minutes > 0:
                average_actions = num_actions / window_duration_minutes
            else:
                average_actions = 0  # To handle the case where the window duration is zero
            averages.append(average_actions)
        else:
            averages.append(0)  # Append 0 if the indices are out of range

    return averages

def main(arr_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], mappings: List[str]) -> Tuple[np.ndarray, ...]:

    if mappings[0] == 'Text Title':
        timestamps = arr_data[1]
        video = False
    elif mappings[0] == 'Video URL':
        timestamps = arr_data[3]
        video = True
    else:
        raise ValueError("Invalid mapping value")

    differences = calculate_differences(timestamps)
    paired_differences = pair_differences_with_videos(timestamps, differences)
    
    windows = identify_activity_windows(differences)
    grouped_timestamps = group_timestamps_by_windows(timestamps, windows)
    avg_window = average_window_length(timestamps, windows)
    avg_actions = average_actions_per_minute(timestamps, windows)


    if video:
        # Create flags and append to imputed_arr
        short_flags = flag_short_videos([pair[1] for pair in paired_differences]) 
        imputed_arr = arr_data + (np.array(differences), np.array(short_flags))
    else:
        # Always add differences array to imputed_arr
        imputed_arr = arr_data + (np.array(differences),)

    return imputed_arr