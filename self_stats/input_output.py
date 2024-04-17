import csv

def read_file(file_path):
    """
    Reads an HTML file from the given path.
    
    Args:
    - file_path (str): Path to the file.
    
    Returns:
    - str: Content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_to_csv(data, filepath, mappings):
    """
    Saves extracted data to a CSV file using writerows for better performance.
    
    Args:
    - data (list of lists): List containing lists of extracted data.
    - filepath (str): Path to save the CSV file.
    - mappings (list): List of column names for the CSV file.
    """
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(mappings)
        writer.writerows(data)
        