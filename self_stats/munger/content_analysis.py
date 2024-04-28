import numpy as np
import re
from urllib.parse import urlparse
import tldextract
from typing import Any, List, Tuple
import spacy

################# Search Queries #################

def extract_search_queries(data: np.ndarray, dates: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract search queries from a numpy array of strings.
    
    Args:
        data (np.ndarray): The array containing the entries.
    
    Returns:
        np.ndarray: An array of search queries.
    """
    mask = np.char.startswith(data, "Searched for ")
    filtered_data = data[mask]
    filtered_dates = dates[mask]
    queries = np.char.replace(filtered_data, "Searched for ", "", count=1)
    return (queries, filtered_dates)

def process_texts(texts: np.ndarray, dates: np.ndarray, nlp: Any) -> np.ndarray:
    """
    Process an array of texts using spaCy to tokenize and clean the text by removing stopwords, punctuation,
    and any empty strings. Assumes that the spaCy model is loaded and available as 'nlp'.
    
    Args:
        texts (np.ndarray): An array of texts to process.
    
    Returns:
        List[List[str]]: A list of lists of tokens for each text.
    
    Note:
        This function requires the spaCy library and a model to be loaded with 'nlp'.
        It disables parser and named entity recognition for efficiency during tokenization.
    """
    tokens_list = []
    dates_list = []
    str_texts = [str(text) for text in texts]
    for doc in nlp.pipe(str_texts, disable=["parser", "ner"]):
        doc_tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct and token.text.strip() != '']
        tokens_list.extend([doc_tokens])

    remove_small_tokens = []
    for token, date in zip(tokens_list, dates):
        if len(token) > 1:
            remove_small_tokens.append(token)
            dates_list.append(date)

    return remove_small_tokens, dates_list

def propagate_dates(dates: np.ndarray, texts: List[List[str]]) -> np.ndarray:
    # Initialize empty lists to hold strings and their corresponding dates
    output_strings = []
    output_dates = []

    # Iterate over the list of lists and the list of dates using enumerate
    for i, sublist in enumerate(texts):
        for s in sublist:
            output_strings.append(s)         # Add the string to the strings list
            output_dates.append(dates[i])  # Add the corresponding date to the dates list

    return np.array(output_strings), np.array(output_dates)

################# Visit Sites #################

def extract_visited_sites(data: np.ndarray, dates: np.ndarray) -> tuple:
    """
    Filter and process site entries from arrays of strings and corresponding dates.
    Ignores entries that start with "Visited " and do not end with "...".

    Parameters:
        data (np.ndarray): The array containing text entries.
        dates (np.ndarray): The array containing corresponding date entries.

    Returns:
        tuple: A tuple containing an array of processed site URLs and their corresponding dates.
    """
    # Create a mask for entries starting with "Visited " and not ending with "..."
    start_mask = np.char.startswith(data, "Visited ")
    end_mask = ~np.char.endswith(data, "...")
    combined_mask = start_mask & end_mask

    # Apply the combined mask
    filtered_data = data[combined_mask]
    filtered_dates = dates[combined_mask]

    # Remove the "Visited " prefix
    sites = np.char.replace(filtered_data, "Visited ", "", count=1)
    return (sites, filtered_dates)

def extract_homepage_from_url(url):
    """
    Extracts the homepage name from a given URL, using urlparse and tldextract for accurate domain extraction.
    
    Args:
        url (str): The URL from which to extract the homepage name.

    Returns:
        str: The homepage name including the top-level domain, but without the scheme or 'www.' prefix.
    """
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc

    # Using tldextract to get more accurate domain extraction
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    return domain

def is_url(text):
    """
    Checks if the provided string starts with a common web protocol ('http://' or 'https://').

    Args:
        url (str): The string to check.

    Returns:
        bool: True if the string starts with 'http://' or 'https://', False otherwise.
    """
    return text.startswith(('http://', 'https://'))

def extract_homepage_alt_form(text):
    """
    Extracts the relevant part of a string based on delimiters and specific rules.
    
    Args:
        text (str): The input text from which to extract information.

    Returns:
        str or None: The extracted text following the rules, or None if the rules exclude the text.
    """
    parts = re.split(r' \- | \| ', text)
    result = parts[-1].strip()
    if result.endswith('...') or is_url(result) or len(parts) == 1:
        return None
    return result

def compile_homepage_names(text_date_array: Tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    """
    Extracts homepage names from a list of texts, using multiple methods to extract the most relevant information.
    
    Args:
        texts (List[str]): A list of strings from which to extract homepage names.

    Returns:
        List[str]: A list of extracted homepage names.
        List[datetime.datetime]: A list of corresponding dates for the extracted homepage names.
    """
    homepage_names = []
    paired_dates = []
    for text, date in text_date_array:
        if is_url(text):
            homepage_names.append(extract_homepage_from_url(text))
            paired_dates.append(date)
        else:
            alt_form = extract_homepage_alt_form(text)
            if alt_form:
                homepage_names.append(alt_form)
                paired_dates.append(date)
    return homepage_names, paired_dates

################# Main Function #################

def main(arr_data: Tuple[np.ndarray, ...], mappings: List[str]) -> Tuple[np.ndarray, ...]:
    nlp = spacy.load("en_core_web_sm")

    text_index = 0 if mappings[0] == 'Text Title' else 1
    date_index = 1 if mappings[0] == 'Text Title' else 3
    search = True if mappings[0] == 'Text Title' else False
    text_array = arr_data[text_index].astype(str)
    date_array = arr_data[date_index]

    if search:
        visited_sites, paired_dates_with_sites = extract_visited_sites(text_array, date_array)

        search_queries, paired_dates_with_text = extract_search_queries(text_array, date_array)
        tokens_list, paired_dates_with_text_tokens = process_texts(search_queries, paired_dates_with_text, nlp)

        tokens_list_split, pair_dates_with_text_split = propagate_dates(paired_dates_with_text_tokens, tokens_list)
        
        return (visited_sites, paired_dates_with_sites), (tokens_list_split, pair_dates_with_text_split)
    else:
        visited_sites = None
        paired_dates_with_sites = None

        search_queries, paired_dates_with_text = extract_search_queries(text_array, date_array)
        tokens_list, paired_dates_with_text_tokens = process_texts(search_queries, paired_dates_with_text, nlp)

        tokens_list_split, pair_dates_with_text_split = propagate_dates(paired_dates_with_text_tokens, tokens_list)
        
        return (visited_sites, paired_dates_with_sites), (tokens_list_split, pair_dates_with_text_split)