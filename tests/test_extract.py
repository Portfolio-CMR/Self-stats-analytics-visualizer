import unittest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
import data_extraction

class TestDataExtraction(unittest.TestCase):
    def setUp(self):
        # Example HTML content
        self.html_content = """
        <div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">
            Searched for <a href="https://www.example.com/search">Example Search</a>
            <br/>June 1, 2022, 12:00:00 AM GMT
        </div>
        """
        self.soup = BeautifulSoup(self.html_content, 'lxml')

    def test_parse_html(self):
        """Test parsing of HTML content."""
        result = data_extraction.parse_html(self.html_content)
        self.assertIsInstance(result, BeautifulSoup)

    def test_extract_search_text(self):
        """Test extraction of search text."""
        entry = self.soup.find('div', class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
        result = data_extraction.extract_search_text(entry)
        self.assertEqual(result, "Example Search")

    def test_extract_date(self):
        """Test extraction of the date."""
        entry = self.soup.find('div', class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
        result = data_extraction.extract_date(entry)
        self.assertEqual(result, "June 1, 2022, 12:00:00 AM GMT")

    def test_extract_coordinates(self):
        """Test extraction of coordinates."""
        # Mocking the next sibling for a location URL
        location_anchor = MagicMock()
        location_anchor['href'] = "https://maps.example.com/?center=40.7128,-74.0060"
        data_extraction.soup.find = MagicMock(return_value=location_anchor)
        result = data_extraction.extract_coordinates(self.soup)
        self.assertEqual(result, ("40.7128", "-74.0060"))

    def test_extract_data(self):
        """Test extraction of all data from the soup."""
        result = data_extraction.extract_data(self.soup)
        expected = [["Example Search", "June 1, 2022, 12:00:00 AM GMT", "No coordinates", "No coordinates"]]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
