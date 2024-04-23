import datetime
import pytz
from tzlocal import get_localzone

def get_utc_offset():
    # Get the local timezone from the system
    local_tz = get_localzone()
    
    # Get the current time in the local timezone
    local_time = datetime.datetime.now(local_tz)
    
    # Extract and return the UTC offset only
    return local_time.strftime('%z')

def adjust_time_by_utc_offset(input_time):
    # Get the UTC offset as a timedelta
    offset_str = get_utc_offset()
    offset_hours = int(offset_str[:3])  # Extract hour part and convert to integer
    offset_minutes = int(offset_str[0] + offset_str[3:])  # Include sign for minutes
    
    # Create a timedelta based on the offset
    offset_delta = datetime.timedelta(hours=offset_hours, minutes=offset_minutes)
    
    # Adjust input time by the offset
    adjusted_time = input_time + offset_delta
    return adjusted_time
