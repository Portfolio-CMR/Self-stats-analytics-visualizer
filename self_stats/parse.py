from bs4 import BeautifulSoup
import re

# Path to the file
file_path = "data/.01_activity.html"

# Reading the HTML content from the file
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parsing the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Extracting search text
search_anchor = soup.find('a', href=True)
search_text = search_anchor.text.strip() if search_anchor else "No search text found"

# Extracting date using targeted text extraction
date_div = soup.find('div', class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
if date_div:
    # Using regex to find date pattern, including handling non-standard whitespace
    date_text = date_div.find('br').next_sibling.strip() if date_div.find('br') else "No date found"
else:
    date_text = "No date found"

# Extracting coordinates
location_anchor = soup.find('a', href=re.compile("maps"))
if location_anchor:
    location_url = location_anchor['href']
    coordinates = re.search(r'center=([0-9.-]+),([0-9.-]+)', location_url)
    if coordinates:
        latitude = coordinates.group(1)
        longitude = coordinates.group(2)
    else:
        latitude, longitude = "No coordinates", "No coordinates"
else:
    latitude, longitude = "No coordinates", "No coordinates"

print("Search Text:", search_text)
print("Date of Search:", date_text)
print("Location Coordinates: Latitude {}, Longitude {}".format(latitude, longitude))
