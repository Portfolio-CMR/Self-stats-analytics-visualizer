from bs4 import BeautifulSoup
import re

def parse_html(html_content):
    """
    Parses the provided HTML content using BeautifulSoup and returns the parsed soup object.
    
    Args:
    - html_content (str): String containing HTML content.
    
    Returns:
    - BeautifulSoup object of the parsed HTML.
    """
    return BeautifulSoup(html_content, 'lxml')

def extract_data(soup):
    """
    Extracts search text, date, and coordinates from a BeautifulSoup object.
    
    Args:
    - soup (BeautifulSoup): Parsed HTML document.
    
    Returns:
    - list of lists containing extracted data.
    """
    entries = soup.find_all('div', class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
    data = []
    for entry in entries:
        search_text = extract_search_text(entry)
        date_text = extract_date(entry)
        latitude, longitude = extract_coordinates(soup)
        data.append([search_text, date_text, latitude, longitude])
    return data

def extract_search_text(entry):
    """
    Extracts the search text from an entry.
    
    Args:
    - entry (Tag): A BeautifulSoup Tag object representing the entry.
    
    Returns:
    - str: Extracted search text.
    """
    search_anchor = entry.find('a', href=True)
    return search_anchor.text.strip() if search_anchor else "No search text found"

def extract_date(entry):
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

def extract_coordinates(soup):
    """
    Extracts geographic coordinates from the BeautifulSoup object.
    
    Args:
    - soup (BeautifulSoup): Parsed HTML document.
    
    Returns:
    - tuple: Latitude and longitude as strings.
    """
    location_anchor = soup.find('a', href=re.compile("maps"), text="this general area")
    if location_anchor:
        location_url = location_anchor['href']
        coordinates = re.search(r'center=([0-9.-]+),([0-9.-]+)', location_url)
        if coordinates:
            return coordinates.group(1), coordinates.group(2)
    return "No coordinates", "No coordinates"
