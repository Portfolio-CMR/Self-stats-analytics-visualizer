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

def write_to_csv(data, csv_file_path):
    """
    Writes extracted data to a CSV file.
    
    Args:
    - data (list of lists): Data to write.
    - csv_file_path (str): Path to the output CSV file.
    """
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Search Text', 'Date of Search', 'Latitude', 'Longitude'])
        writer.writerows(data)
