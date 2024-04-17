import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup

# Assuming the script's functions are in a module named 'script'
from self_stats.process_search_history import extract_search_data, extract_search_text, extract_date, extract_coordinates

class TestScript(unittest.TestCase):
    def setUp(self):
        self.html_content = "<html><body><a href='http://maps.example.com/?center=40.7128,-74.0060' text='this general area'>Location</a></body></html>"
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        self.entry = self.soup.new_tag('div')
        self.entry.append(self.soup.new_tag('a', href="http://example.com"))
        self.entry.a.string = "Example Search"

    @patch('script.extract_search_text', return_value="Example Search")
    @patch('script.extract_date', return_value="2024-04-16")
    @patch('script.extract_coordinates', return_value=("40.7128", "-74.0060"))
    def test_extract_search_data(self, mock_search_text, mock_date, mock_coords):
        entries = [self.entry]
        result = extract_search_data(entries, self.soup)
        self.assertEqual(result, [["Example Search", "2024-04-16", "40.7128", "-74.0060"]])

    def test_extract_search_text(self):
        result = extract_search_text(self.entry)
        self.assertEqual(result, "Example Search")

    def test_extract_date(self):
        br_tag = self.soup.new_tag('br')
        self.entry.append(br_tag)
        next_sibling = self.soup.new_string("2024-04-16")
        br_tag.insert_after(next_sibling)
        result = extract_date(self.entry)
        self.assertEqual(result, "2024-04-16")

    def test_extract_coordinates(self):
        result = extract_coordinates(self.soup)
        self.assertEqual(result, ("40.7128", "-74.0060"))

if __name__ == '__main__':
    unittest.main()
