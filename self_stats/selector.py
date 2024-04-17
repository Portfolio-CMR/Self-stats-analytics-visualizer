from pathlib import Path

def ensure_directory_exists(directory):
    """Ensure that the specified directory exists.
    
    Args:
        directory (str): The path to the directory to check.

    Raises:
        ValueError: If the directory does not exist.
    """
    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Directory {directory} does not exist. Please ensure it is created and accessible.")

def get_file_presence_flags(directory):
    """Check for the presence of specific files in a given directory and return their presence as flags.
    
    Args:
        directory (str): The directory in which to check for files.

    Returns:
        dict: A dictionary with boolean flags for each file type detected.
    """
    ensure_directory_exists(directory)
    path = Path(directory)
    return {
        'watch_history_present': (path / 'watch-history.html').exists(),
        'my_activity_present': (path / 'MyActivity.html').exists()
    }

