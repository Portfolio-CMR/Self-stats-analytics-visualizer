import regex as re
from datetime import datetime
from typing import List, Any, Tuple, Pattern

def remove_invisible_characters(text: str, compiled_pattern: re.Pattern) -> str:
    """
    Remove invisible and non-printable Unicode characters from a given text string using a precompiled regex pattern.
    
    Args:
    text (str): A string from which to remove invisible characters.
    compiled_pattern (re.Pattern): A precompiled regex pattern to match invisible characters.

    Returns:
    str: The cleaned text string without invisible characters.
    """
    return compiled_pattern.sub('', text).strip()

def remove_timezone(date_str: str) -> str:
    """
    Extract the timezone abbreviation from a date string and return the string without it.
    
    Args:
    date_str (str): The input date string that includes a timezone abbreviation.

    Returns:
    str: The date string with timezone abbreviation removed.
    """
    pattern = re.compile(r'(?<=AM|PM)([A-Z]{2,4})$')
    date_str_no_tz = pattern.sub('', date_str).strip()  # Remove the timezone string from the date_str for parsing
    return date_str_no_tz

def parse_date(date_str: str) -> datetime:
    """
    Parse the datetime from a string assuming it's formatted correctly without timezone information.

    Args:
    date_str (str): The datetime string in a specific format.

    Returns:
    datetime: The naive datetime object parsed from the string.
    """
    date_str_no_tz = remove_timezone(date_str)
    return datetime.strptime(date_str_no_tz, '%b%d,%Y,%I:%M:%S%p')

def process_row(row: List[str], compiled_pattern: Pattern) -> List[Any]:
    """
    Process a single row by cleaning and converting each element to the specified type.
    
    Args:
    row (List[str]): A list of elements (text, date string, and numerical strings).
    compiled_pattern (Pattern): A compiled regex pattern to remove invisible characters.

    Returns:
    List[Any]: The processed row with elements converted to their specific types.
    """
    cleaned_elements = [remove_invisible_characters(item, compiled_pattern) for item in row]
    return [
        cleaned_elements[0],  # Keep string as is
        parse_date(cleaned_elements[1]),  # Convert second element to datetime
        float(cleaned_elements[2]),  # Convert third element to float
        float(cleaned_elements[3])  # Convert fourth element to float
    ]

def clean_and_convert_data(data: List[List[str]], compiled_pattern: Pattern) -> List[List[Any]]:
    """
    Clean the data from invisible characters and convert each element to the specified type.
    
    Args:
    data (List[List[str]]): A list of lists where each inner list has exactly four elements: text, date string, and two numerical strings.
    compiled_pattern (Pattern): A precompiled regex pattern to match invisible characters.

    Returns:
    List[List[Any]]: The list of lists with each element cleaned and converted to its specific type.
    """
    return [process_row(row, compiled_pattern) for row in data]

def main(data: List[List[str]]) -> List[List[Any]]:
    """
    Main function to process data for cleaning and type conversion.
    
    Args:
    data (List[List[str]]): The input data as a list of lists.

    Returns:
    List[List[Any]]: The processed data with elements converted to their specified types.
    """
    # Compile the regex pattern once
    compiled_pattern = re.compile(r'\p{C}+|\p{Z}+|[\u200B-\u200F\u2028-\u202F]+')

    # Clean the data and convert types
    processed_data = clean_and_convert_data(data, compiled_pattern)

    return processed_data

# Example usage
if __name__ == "__main__":
    main()
