# Module: data_scraping.py

import pandas as pd
from lxml import etree
from dateutil import parser

def read_and_scrape_data(filepath):
    # Read HTML file
    with open(filepath, "r", encoding="UTF-8") as file:
        # Parse the HTML
        tree = etree.parse(file, etree.HTMLParser())

    # Define XPath expressions to extract data
    # Selecting nodes that directly contain the date-time information
    date_nodes = tree.xpath('//div[contains(@class, "content-cell") and contains(@class, "mdl-cell--6-col")]/text()[last()]')
    search_nodes = tree.xpath('//div[contains(@class, "content-cell") and contains(@class, "mdl-cell--6-col")]//a')

    dates = []
    searches = []
    
    for date_text in date_nodes:
        # Strip and parse dates
        try:
            date_parsed = parser.parse(date_text.strip(), fuzzy=True)
            dates.append(date_parsed)
        except ValueError:
            continue
    
    for search_node in search_nodes:
        # Extract search text from <a> tags
        search_text = search_node.text.strip()
        searches.append(search_text)

    return pd.DataFrame({
        'timestamp': dates,
        'search': searches
    })

# Example usage:
# data = read_and_scrape_data("Takeout/My Activity/Search/MyActivity.html")
