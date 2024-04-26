import csv
import json
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Loads JSON data from a specified file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing JSON data.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def save_to_csv(data: Tuple[np.ndarray, ...], filepath: str | Path, mappings: List[str]) -> None:
    """
    Saves extracted data to a CSV file using writerows for better performance.
    
    Args:
    - data (Tuple[np.ndarray, ...]): Tuple where each element is a NumPy array representing a column of data.
    - filepath (str): Path to save the CSV file.
    - mappings (List[str]): List of column names for the CSV file.
    """

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(mappings)
        
        # Combine the column arrays into a single 2D array
        combined_data = np.column_stack(data)
        
        # Write the rows to the CSV file
        writer.writerows(combined_data)

def ensure_directory_exists(directory: str) -> None:
    """Ensure that the specified directory exists.
    
    Args:
        directory (str): The path to the directory to check.

    Raises:
        ValueError: If the directory does not exist.
    """
    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Directory {directory} does not exist. Please ensure it is created and accessible.")

def get_file_presence_flags(directory: str) -> Dict[str, bool]:
    """Check for the presence of specific files in a given directory and return their presence as flags.
    
    Args:
        directory (str): The directory in which to check for files.

    Returns:
        Dict[str, bool]: A dictionary with boolean flags for each file type detected.
    """
    ensure_directory_exists(directory)
    path = Path(directory)
    return {
        'watch_history_present': (path / 'watch-history.json').exists(),
        'my_activity_present': (path / 'MyActivity.json').exists()
    }
