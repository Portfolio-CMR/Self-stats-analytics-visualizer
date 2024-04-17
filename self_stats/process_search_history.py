import re
import self_stats.remove_unicode_characters as remove_unicode_characters
from typing import List, Tuple
from bs4 import BeautifulSoup, Tag  # Assuming BeautifulSoup is used
from parse import parse_html, extract_div
from input_output import read_file, save_to_csv


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

def main(directory: str) -> None:
    html_content = read_file(f'{directory}/MyActivity.html')
    soup = parse_html(html_content)
    entries = extract_div(soup)
    data = extract_search_data(entries, soup)
    cleaned_data = remove_unicode_characters.main(data)
    save_to_csv(cleaned_data, f'{directory}/extracted_search_history_data.csv', ['Search Text', 'Date', 'Latitude', 'Longitude'])
    
    print(f"Search data extraction complete. Results saved to '{directory}/extracted_search_history_data.csv'.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
