import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup

# Assuming the script's functions are in a module named 'video_script'
from self_stats.process_watch_history import extract_video_data, extract_video_field, extract_date
d
class TestVideoScript(unittest.TestCase):
    def setUp(self):
        self.html_content = "<html><body><div><a href='http://youtube.com/watch?v=example'>Video Title</a><a href='http://youtube.com/channel'>Channel Title</a></div></body></html>"
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        self.entry = self.soup.find('div')

    @patch('video_script.extract_video_field', return_value=['http://youtube.com/watch?v=example', 'Video Title', 'Channel Title', '2024-04-16'])
    def test_extract_video_data(self, mock_extract_video_field):
        entries = [self.entry, self.entry]  # Duplicate entry to test multiple entries
        result = extract_video_data(entries)
        expected = [['http://youtube.com/watch?v=example', 'Video Title', 'Channel Title', '2024-04-16'],
                    ['http://youtube.com/watch?v=example', 'Video Title', 'Channel Title', '2024-04-16']]
        self.assertEqual(result, expected)

    def test_extract_video_field(self):
        result = extract_video_field(self.entry)
        self.assertEqual(result, ['http://youtube.com/watch?v=example', 'Video Title', 'Channel Title', 'No date found'])

    def test_extract_date(self):
        br_tag = self.soup.new_tag('br')
        self.entry.append(br_tag)
        next_sibling = self.soup.new_string("2024-04-16")
        br_tag.insert_after(next_sibling)
        result = extract_date(self.entry)
        self.assertEqual(result, "2024-04-16")

if __name__ == '__main__':
    unittest.main()
