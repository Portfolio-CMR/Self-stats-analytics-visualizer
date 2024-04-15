from lxml import etree
import re

def extract_data(file_path):
    # Define the variables to store the extracted data
    search_text = None
    search_date = None
    location_coordinates = None

    # Define the context for iterparse with the events you're interested in
    context = etree.iterparse(file_path, events=('end',), tag='div')

    # Iterate over the events and find the relevant data
    for event, elem in context:
        if 'content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1' in elem.get('class', ''):
            # Extract the search text
            a_tag = elem.find('.//a')
            if a_tag is not None and 'google.com/search' in a_tag.get('href', ''):
                search_text = a_tag.text

            # Extract the search date
            if search_text:
                text = elem.text_content()
                date_match = re.search(r'(\w+ \d{1,2}, \d{4}, \d{1,2}:\d{2}:\d{2}\s\w+)', text)
                if date_match:
                    search_date = date_match.group(1)

        elif 'content-cell mdl-cell mdl-cell--12-col mdl-typography--caption' in elem.get('class', ''):
            # Extract the location coordinates
            a_tag = elem.find('.//a')
            if a_tag is not None and 'google.com/maps/@' in a_tag.get('href', ''):
                href = a_tag.get('href')
                coords_match = re.search(r'center=([-\d.]+),([-\d.]+)', href)
                if coords_match:
                    location_coordinates = (coords_match.group(1), coords_match.group(2))

        # Clear the element to free up memory
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    # Return the extracted data
    return search_text, search_date, location_coordinates

# Usage example
file_path = 'data/.01_activity.html'
data = extract_data(file_path)
print(data)