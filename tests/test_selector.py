import unittest
from unittest.mock import patch, MagicMock
from self_stats.munger.selector import ensure_directory_exists, get_file_presence_flags

class TestSelector(unittest.TestCase):
    def test_ensure_directory_exists(self):
        with patch('selector.Path') as mock_path:
            mock_path.return_value.is_dir.return_value = True
            # Test that no exception is raised for existing directory
            try:
                ensure_directory_exists('/path/to/existing/directory')
            except ValueError:
                self.fail("ensure_directory_exists() raised ValueError unexpectedly!")

            # Test that it raises an exception for non-existing directory
            mock_path.return_value.is_dir.return_value = False
            with self.assertRaises(ValueError):
                ensure_directory_exists('/path/to/nonexistent/directory')

    def test_get_file_presence_flags(self):
        with patch('selector.Path') as mock_path:
            # Setup mock to simulate existing directory and file presence
            mock_instance = mock_path.return_value
            mock_instance.is_dir.return_value = True
            mock_instance.__truediv__.return_value.exists.side_effect = [True, False]  # First file exists, second does not

            result = get_file_presence_flags('/path/to/directory')
            expected_result = {
                'watch_history_present': True,
                'my_activity_present': False
            }
            self.assertEqual(result, expected_result)

            # Test with directory check raising an exception
            mock_instance.is_dir.return_value = False
            with self.assertRaises(ValueError):
                get_file_presence_flags('/path/to/nonexistent/directory')

if __name__ == '__main__':
    unittest.main()
