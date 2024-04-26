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
        Optional[float]: The time difference in minutes if less than or equal to 30 minutes; otherwise, None.
    """
    try:
        difference = current - previous
        difference_in_minutes = abs(round(difference.total_seconds() / 60, 1))
        if difference_in_minutes > 30:
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
                                Differences greater than 30 minutes are returned as None.
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
    return [duration is not None and duration < 1 for duration in video_durations]

def main(arr_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], mappings: List[str]) -> Tuple[np.ndarray, ...]:

    if mappings[0] == 'Text Title':
        timestamps = arr_data[1]
        video = False
    elif mappings[0] == 'Video URL':
        timestamps = arr_data[2]
        video = True
    else:
        raise ValueError("Invalid mapping value")

    differences = calculate_differences(timestamps)
    paired_differences = pair_differences_with_videos(timestamps, differences)
    
    # Always add differences array to imputed_arr
    imputed_arr = arr_data + (np.array(differences),)
    
    if video:
        # Create flags and append to imputed_arr
        short_flags = flag_short_videos([pair[1] for pair in paired_differences]) 
        imputed_arr = imputed_arr + (np.array(short_flags),)

    return imputed_arr