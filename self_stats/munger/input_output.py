import csv
import json
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pathlib import Path
from typing import List
import pandas as pd

def create_output_directories(directories: List[Path]) -> None:
    """
    Creates each specified directory in the provided list and prints a list of all created directories at the end.

    Args:
    directories (List[str]): A list of paths of directories to be created.

    Returns:
    None: This function does not return any value, but prints a single message listing all directories that were created.
    """
    created_directories = []  # List to store paths of directories created
    for directory in directories:
        out_dir = Path(f'{directory}')
        if not out_dir.exists():
            out_dir.mkdir(parents=True, exist_ok=True)
            created_directories.append(out_dir)

    # Print all created directories in one go
    if created_directories:
        print("Directories created:\n")
        for dir in created_directories:
            print(dir)
        print("\n")  # Add a newline for better formatting at the end


def read_json_file(file_path: Path) -> List[Dict[str, Any]]:
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

def ensure_directory_exists(directory: Path) -> None:
    """Ensure that the specified directory exists.
    
    Args:
        directory (str): The path to the directory to check.

    Raises:
        ValueError: If the directory does not exist.
    """
    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Directory {directory} does not exist. Please ensure it is created and accessible.")

def get_file_presence_flags(directory: Path) -> Dict[str, bool]:
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

def write_arrays_to_excel(
    array_lists: List[List[np.ndarray]], 
    column_name_lists: List[List[str]], 
    sheet_names: List[str], 
    filename: Path
) -> None:
    """
    Writes multiple lists of arrays to an Excel file, each on a different sheet with specified column names.
    
    Parameters:
    - array_lists (list of list of np.array): Each list contains arrays that should be written to a sheet.
    - column_name_lists (list of list of str): Names for the columns corresponding to each array in array_lists.
    - sheet_names (list of str): Names for each sheet.
    - filename (str): The filename for the output Excel file.
    """
    # Create a Pandas Excel writer using XlsxWriter as the engine
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        # Iterate over each list of arrays, column names list, and sheet name
        for arrays, col_names, sheet_name in zip(array_lists, column_name_lists, sheet_names):
            # Create a DataFrame for each list of arrays with the corresponding column names
            df = pd.DataFrame({col_name: arr for arr, col_name in zip(arrays, col_names)})
            # Write the DataFrame to a named sheet in the Excel file
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def write_arrays_to_single_excel(
    combined_tuple: Tuple[np.ndarray, ...], 
    column_name_lists: List[str], 
    column_types: List[str],
    filename: Path
) -> None:
    """
    Writes multiple arrays to an Excel file, each on a different sheet with specified column names.
    
    Parameters:
    - combined_tuple (Tuple of np.array): A tuple of arrays.
    - column_name_lists (list of str): Names for the columns corresponding to each array.
    - filename (str): The filename for the output Excel file.
    """
    # Create a Pandas Excel writer using XlsxWriter as the engine
    converted_arrays = []
    for arr in combined_tuple:
        converted_arrays.append(arr.astype(str))
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        max_length = max(len(arr) for arr in combined_tuple)
        data = {f'Column_{i}': np.pad(arr, (0, max_length - len(arr)), mode='constant', constant_values='') for i, arr in enumerate(converted_arrays)}
        df = pd.DataFrame(data)
        df.columns = column_name_lists

        # Convert columns to specified types
        for i, col_type in enumerate(column_types):
            if col_type == 'date':
                df[column_name_lists[i]] = pd.to_datetime(df[column_name_lists[i]], errors='coerce').dt.date
            elif col_type == 'float':
                df[column_name_lists[i]] = pd.to_numeric(df[column_name_lists[i]], errors='coerce')
            # elif col_type == 'date_hour':
            #     df[column_name_lists[i]] = pd.to_datetime(df[column_name_lists[i]], format='%H').dt.time
            elif col_type == 'date_time':
                df[column_name_lists[i]] = pd.to_datetime(df[column_name_lists[i]], errors='coerce')
        
        df.to_excel(writer, sheet_name='_', index=False)




