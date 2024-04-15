# Module: data_scraping.py

import pandas as pd
from lxml import etree
from dateutil import parser
import re

def read_and_scrape_data(filepath):
    # Read HTML file
    with open(filepath, "r", encoding="UTF-8") as file:
        # Parse the HTML
        tree = etree.parse(file, etree.HTMLParser())

    # Define XPath to extract each search block containing "Searched for"
    search_blocks = tree.xpath('//div[contains(.//text(), "Searched for")]')

    data = []

    for block in search_blocks:
        # Extract the search term
        search_text = block.xpath('.//a[contains(@href, "google.com/search?q=")]/text()')
        if search_text:
            search_text = search_text[0].strip()
        else:
            continue  # If no search term found, skip this block

        # Extract date and time, assuming it follows the search link
        date_text = block.xpath('string(.)')
        # Using regex to find date and time information
        date_matches = re.search(r'\b[A-Z][a-z]{2} \d{1,2}, \d{4}, \d{1,2}:\d{2}:\d{2}\s[AP]M\b', date_text)
        if date_matches:
            date_parsed = parser.parse(date_matches.group(0), fuzzy=True)
        else:
            continue  # If no date found, skip this block

        # Navigate to the parent of the search block and find the location div
        location_block = block.getparent().xpath('.//div[contains(@class, "mdl-typography--caption")]//a[contains(@href, "maps")]/@href')
        if location_block:
            coords_match = re.search(r'center=([-.\d]+),([-.\d]+)', location_block[0])
            if coords_match:
                coords = coords_match.groups()  # (latitude, longitude)
            else:
                coords = (None, None)  # No coordinates found
        else:
            continue  # If no location URL found, skip this block

        data.append({
            'timestamp': date_parsed,
            'search': search_text,
            'latitude': coords[0],
            'longitude': coords[1]
        })

    return pd.DataFrame(data)

# Example usage:
# data = read_and_scrape_data("Takeout/My Activity/Search/MyActivity.html")
