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

