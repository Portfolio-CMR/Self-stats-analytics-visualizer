from bs4 import BeautifulSoup
import re
import csv

# Path to the file
file_path = "data/.01_activity.html"

# Reading the HTML content from the file
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parsing the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find all relevant divs containing the search information
entries = soup.find_all('div', class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")

# List to store each entry's data
data = []

for entry in entries:
    # Extracting search text
    search_anchor = entry.find('a', href=True)
    search_text = search_anchor.text.strip() if search_anchor else "No search text found"
    
    # Extracting date
    date_text = entry.find('br').next_sibling.strip() if entry.find('br') else "No date found"
    
    # Extracting coordinates
    # Assuming that the coordinates div is another entry somewhere below the current div
    location_anchor = soup.find('a', href=re.compile("maps"), text="this general area")
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
    
    # Append the collected data for this entry to the list
    data.append([search_text, date_text, latitude, longitude])

# Writing the data to a CSV file
csv_file_path = 'data/extracted_data.csv'
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Search Text', 'Date of Search', 'Latitude', 'Longitude'])  # Writing headers
    writer.writerows(data)

# Output message confirming data extraction
print("Data extraction complete. Results saved to 'extracted_data.csv'.")
