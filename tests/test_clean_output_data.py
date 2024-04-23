import unittest
import regex as re
from datetime import datetime
from self_stats.munger.search_cleaner import remove_invisible_characters, remove_timezone, parse_date, process_row, clean_and_convert_data

class TestYourModule(unittest.TestCase):
    def setUp(self):
        # This is the regex pattern compiled once for all tests.
        self.pattern = re.compile(r'\p{C}+|\p{Z}+|[\u200B-\u200F\u2028-\u202F]+')

    def test_remove_invisible_characters(self):
        test_str = "Hello\u200BWorld"
        expected = "HelloWorld"
        result = remove_invisible_characters(test_str, self.pattern)
        self.assertEqual(result, expected)

    def test_remove_timezone(self):
        test_date = "Mar12,2021,05:34:00PM PST"
        expected = "Mar12,2021,05:34:00PM"
        result = remove_timezone(test_date)
        self.assertEqual(result, expected)

    def test_parse_date_with_removed_timezone(self):
        test_date = "Mar12,2021,05:34:00PM"
        expected = datetime(2021, 3, 12, 17, 34)
        result = parse_date(test_date)
        self.assertEqual(result, expected)

    # Additional test methods for process_row, clean_and_convert_data, etc.

if __name__ == "__main__":
    unittest.main()
