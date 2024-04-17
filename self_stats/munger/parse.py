from bs4 import BeautifulSoup
from typing import List

def parse_html(html_content: str) -> BeautifulSoup:
    """
    Parses the provided HTML content using BeautifulSoup and returns the parsed soup object.
    
    Args:
    - html_content (str): String containing HTML content.
    
    Returns:
    - BeautifulSoup object of the parsed HTML.
    """
    return BeautifulSoup(html_content, 'lxml')

def extract_div(soup: BeautifulSoup) -> List[BeautifulSoup]:
    """
    Extracts the div elements containing class identifiers from a BeautifulSoup object.
    
    Args:
    - soup (BeautifulSoup): Parsed HTML document.
    
    Returns:
    - list of div elements
    """
    return soup.find_all('div', class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
