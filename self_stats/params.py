import os
from pathlib import Path

def detect_files(directory):
    """Detect specific files and set parameters based on the presence of certain files."""
    # Use pathlib to handle paths
    path = Path(directory)
    
    # Initialize a dictionary to hold parameters and flags for file detection
    params = {'watch_history_present': False, 'my_activity_present': False, 'total_files': 0}
    
    # Check if the directory exists
    if not path.is_dir():
        raise ValueError(f"The directory {directory} does not exist.")
    
    # Scan the directory for specific files
    for file in path.iterdir():
        if file.is_file():
            if 'watch-history.html' == file.name:
                params['watch_history_present'] = True
            elif 'MyActivity.html' == file.name:
                params['my_activity_present'] = True
            params['total_files'] += 1
    
    # Set parameters based on detected files
    if params['watch_history_present']:
        params['source'] = 'YouTube Watch History'
    if params['my_activity_present']:
        params['source'] = 'Google Activity'
    
    return params

# Example usage
if __name__ == "__main__":
    directory = "./data"
    parameters = detect_files(directory)
    print(parameters)
