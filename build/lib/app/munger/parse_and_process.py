import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from app.munger.clean_dates import convert_to_arrays, main as cleaner_main
from app.munger.input_output import read_json_file

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
        title = entry.get('title', '')
        time = entry.get('time', None)

        location_infos = entry.get('locationInfos', [])
        if location_infos:
            location_url = location_infos[0].get('url', None)
            lat, long = extract_coordinates(location_url) if location_url else (None, None)
        else:
            lat, long = None, None

        extracted_data.append({
            'Text Title': title,
            'Date': time,
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
        title = entry.get('title', '')
        time = entry.get('time', None)
        titleUrl = entry.get('titleUrl', None)
        channel_info = entry.get('subtitles', [])
        if channel_info:
            channel_name = channel_info[0].get('name', None)

        extracted_data.append({
            'Video URL': titleUrl,
            'Video Title': title,
            'Channel Title': channel_name,
            'Date': time
        })

    return extracted_data

def main(directory: str, data_source: str | Path, mappings: List[str]) -> None:

    json_data = read_json_file(data_source)
    if data_source == f'{directory}/MyActivity.json':
        extracted_data = extract_search_information(json_data)
    if data_source == f'{directory}/watch-history.json':
        extracted_data = extract_watch_information(json_data)

    arr_data = convert_to_arrays(extracted_data, mappings)
    cleaned_data = cleaner_main(arr_data, mappings)
    return cleaned_data
