import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse
import regex

from self_stats.munger.process_dates import convert_to_arrays, clean_dates_main
from self_stats.munger.input_output import read_json_file

def clean_string(input_string: str) -> str:
    """
    Cleans a string by removing non-printable characters and other potential unwanted characters or patterns.
    
    Args:
    - input_string (str): The string to be cleaned.
    
    Returns:
    - str: The cleaned string.
    """
    if input_string is None:
        return None

    # Remove all non-printable characters (Unicode category C)
    cleaned_string = regex.sub(r'[\p{C}]', '', input_string)
    
    # Remove leading and trailing whitespace
    cleaned_string = cleaned_string.strip()
    
    # Optionally replace multiple spaces with a single space
    cleaned_string = regex.sub(r'\s+', ' ', cleaned_string)
    
    return cleaned_string

def extract_coordinates(location_url: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extracts latitude and longitude from a location URL.

    Args:
        location_url (str): The URL containing the geolocation coordinates.

    Returns:
        Tuple[Optional[float], Optional[float]]: A tuple containing latitude and longitude,
        or (None, None) if the coordinates cannot be extracted.
    """
    try:
        parsed_url = urlparse(location_url)
        query_params = parse_qs(parsed_url.query)
        center = query_params.get('center', [])

        if center:
            lat, long = center[0].split(',')
            return float(lat), float(long)
    except ValueError as e:
        print(f"Error extracting coordinates: {e}")
    return None, None

def extract_search_information(json_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts title, time, and coordinates from a list of JSON entries.

    Args:
        json_data (List[Dict[str, Any]]): A list of dictionaries representing JSON entries.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with extracted information including title,
        time, and coordinates (latitude and longitude).
    """
    extracted_data = []

    for entry in json_data:
        title = clean_string(entry.get('title', None))
        time = clean_string(entry.get('time', None))

        location_infos = entry.get('locationInfos', [])
        if location_infos:
            location_url = clean_string(location_infos[0].get('url', None))
            lat, long = extract_coordinates(location_url) if location_url else (None, None)
        else:
            lat, long = None, None

        extracted_data.append({
            'Date': time,
            'Query_Text': title,
            'Latitude': lat,
            'Longitude': long
        })

    return extracted_data

def extract_watch_information(json_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts title, time, and coordinates from a list of JSON entries.

    Args:
        json_data (List[Dict[str, Any]]): A list of dictionaries representing JSON entries.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with extracted information including title,
        time, and coordinates (latitude and longitude).
    """
    extracted_data = []

    for entry in json_data:
        title = clean_string(entry.get('title', None))
        time = clean_string(entry.get('time', None))
        titleUrl = clean_string(entry.get('titleUrl', None))
        channel_info = entry.get('subtitles', [])
        if channel_info:
            channel_name = clean_string(channel_info[0].get('name', None))

        extracted_data.append({
            'Date': time,
            'Video_Title': title,
            'Channel_Title': channel_name,
            'Video_URL': titleUrl
        })

    return extracted_data

def main(directory: Path, data_source: str | Path, mappings: List[str]) -> None:

    json_data = read_json_file(data_source)
    if data_source == directory / 'MyActivity.json':
        extracted_data = extract_search_information(json_data)
    if data_source == directory / 'watch-history.json':
        extracted_data = extract_watch_information(json_data)

    arr_data = convert_to_arrays(extracted_data, mappings)
    cleaned_data = clean_dates_main(arr_data, mappings)
    return cleaned_data
