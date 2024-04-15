from bs4 import BeautifulSoup
import re
import csv

# Path to the file
file_path = "data/activity.html"

# Reading the HTML content from the file
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parsing the HTML with lxml for better performance
soup = BeautifulSoup(html_content, 'lxml')

# Find all relevant divs containing the search information
entries = soup.find_all('div', class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")

# List to store each entry's data
data = []

for entry in entries:
    # Extracting search text
    search_anchor = entry.find('a', href=True)
    search_text = search_anchor.text.strip() if search_anchor else "No search text found"
    
    # Extracting date, with improved error handling
    date_br = entry.find('br')
    if date_br and date_br.next_sibling:
        date_text = date_br.next_sibling.strip() if isinstance(date_br.next_sibling, str) else "No date found"
    else:
        date_text = "No date found"
    
    # Extracting coordinates
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
csv_file_path = 'data/full_extracted_data.csv'
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Search Text', 'Date of Search', 'Latitude', 'Longitude'])  # Writing headers
    writer.writerows(data)

# Output message confirming data extraction
print("Data extraction complete. Results saved to 'extracted_data.csv'.")
