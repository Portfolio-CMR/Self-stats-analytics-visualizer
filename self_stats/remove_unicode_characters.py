import regex as re
from typing import List

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

def clean_data(data: List[List[str]], compiled_pattern: re.Pattern) -> List[List[str]]:
    """
    Apply the remove_invisible_characters function to every string in a nested list (list of lists).
    
    Args:
    data (List[List[str]]): A list of lists where each inner list contains string data.
    compiled_pattern (re.Pattern): A precompiled regex pattern to match invisible characters.

    Returns:
    List[List[str]]: The list of lists with all invisible characters removed from its strings.
    """
    cleaned_data = [[remove_invisible_characters(item, compiled_pattern) for item in row] for row in data]
    return cleaned_data

def main(data):
    # Compile the regex pattern once
    compiled_pattern = re.compile(r'\p{C}+|\p{Z}+|[\u200B-\u200F\u2028-\u202F]+')

    # Clean the data
    cleaned_data = clean_data(data, compiled_pattern)

    return cleaned_data

# Example usage
if __name__ == "__main__":
    main()
