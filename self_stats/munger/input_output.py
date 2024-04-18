import csv
from typing import List, Tuple
import numpy as np

def read_file(file_path: str) -> str:
    """
    Reads an HTML file from the given path.
    
    Args:
    - file_path (str): Path to the file.
    
    Returns:
    - str: Content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_to_csv(data: Tuple[np.ndarray, ...], filepath: str, mappings: List[str]) -> None:
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

