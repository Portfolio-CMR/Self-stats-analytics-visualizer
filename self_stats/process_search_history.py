import re
from parse import parse_html, extract_div
from input_output import read_file, save_to_csv

def extract_search_data(entries, soup):
    """
    Extracts search text, date, and coordinates from a BeautifulSoup object.
    
    Args:
    - soup (BeautifulSoup): Parsed HTML document.
    
    Returns:
    - list of lists containing extracted data.
    """
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

def main(directory):
    html_content = read_file(f'{directory}/MyActivity.html')
    soup = parse_html(html_content)
    entries = extract_div(soup)
    data = extract_search_data(entries, soup)
    save_to_csv(data, f'{directory}/extracted_search_history_data.csv', ['Search Text', 'Date', 'Latitude', 'Longitude'])
    
    print(f"Search data extraction complete. Results saved to '{directory}/extracted_search_history_data.csv'.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
