import re
from typing import List, Tuple
import numpy as np
from bs4 import BeautifulSoup, Tag  # Assuming BeautifulSoup is used
from self_stats.munger.parse import parse_html, extract_div
from self_stats.munger.input_output import read_file
import self_stats.munger.search_history_cleaner as search_history_cleaner
from self_stats.munger.clean_data_shared import convert_to_arrays

def extract_search_data(entries: List[Tag], soup: BeautifulSoup) -> List[List[str]]:
    """
    Extracts search text, date, and coordinates from a BeautifulSoup object.
    
    Args:
    - entries (List[Tag]): A list of BeautifulSoup Tag objects representing multiple entries.
    - soup (BeautifulSoup): Parsed HTML document.
    
    Returns:
    - list of lists containing extracted data.
    """
    data: List[List[str]] = []
    for entry in entries:
        search_text: str = extract_search_text(entry)
        date_text: str = extract_date(entry)
        latitude, longitude = extract_coordinates(soup)
        data.append([search_text, date_text, latitude, longitude])
    return data

def extract_search_text(entry: Tag) -> str:
    """
    Extracts the search text from an entry.
    
    Args:
    - entry (Tag): A BeautifulSoup Tag object representing the entry.
    
    Returns:
    - str: Extracted search text.
    """
    search_anchor = entry.find('a', href=True)
    return search_anchor.text.strip() if search_anchor else "No search text found"

def extract_date(entry: Tag) -> str:
    """
    Extracts the date from an entry using safe navigation for next siblings.
    
    Args:
    - entry (Tag): A BeautifulSoup Tag object representing the entry.
    
    Returns:
    - str: Extracted date text.
    """
    date_br = entry.find('br')
    if date_br and date_br.next_sibling:
        return date_br.next_sibling.strip() if isinstance(date_br.next_sibling, str) else "No date found"
    return "No date found"

def extract_coordinates(soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Extracts geographic coordinates from the BeautifulSoup object.
    
    Args:
    - soup (BeautifulSoup): Parsed HTML document.
    
    Returns:
    - tuple: Latitude and longitude as strings.
    """
    location_anchor = soup.find('a', href=re.compile("maps"), text=re.compile("this general area"))
    if location_anchor:
        location_url = location_anchor['href']
        coordinates = re.search(r'center=([0-9.-]+),([0-9.-]+)', location_url)
        if coordinates:
            return coordinates.group(1), coordinates.group(2)
    return "No coordinates", "No coordinates"

def main(directory: str, mappings: List[str]) -> None:
    html_content = read_file(f'{directory}/MyActivity.html')
    soup = parse_html(html_content)
    entries = extract_div(soup)
    data = extract_search_data(entries, soup)
    arr_data = convert_to_arrays(data)
    cleaned_data = search_history_cleaner.main(arr_data, mappings)
    return cleaned_data
