import numpy as np
import re
from urllib.parse import urlparse
import tldextract
from typing import Any, List, Tuple
import spacy
from datetime import datetime

################# Search Queries #################

def extract_search_queries(data: np.ndarray, dates: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract search queries from a numpy array of strings.
    
    Args:
        data (np.ndarray): The array containing the entries.
    
    Returns:
        np.ndarray: An array of search queries.
    """
    mask_one = np.char.startswith(data, "Searched for ")
    mask_two = np.char.startswith(data, "\"Searched for ")

    combined_mask = mask_one | mask_two
    filtered_data = data[combined_mask]
    filtered_dates = dates[combined_mask]

    first_filter = np.char.replace(filtered_data, "Searched for ", "", count=1)
    queries = np.char.replace(first_filter, "\"Searched for ", "", count=1)
    return (queries, filtered_dates)

def extract_video_titles(data: np.ndarray, dates: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract video titles from a numpy array of strings.
    
    Args:
        data (np.ndarray): The array containing the entries.
    
    Returns:
        np.ndarray: An array of search queries.
    """
    mask_one = np.char.startswith(data, "Watched ")
    mask_two = np.char.startswith(data, "\"Watched")
    combined_mask = mask_one | mask_two
    filtered_data = data[combined_mask]
    filtered_dates = dates[combined_mask]
    first_filter = np.char.replace(filtered_data, "Watched ", "", count=1)
    queries = np.char.replace(first_filter, "\"Watched ", "", count=1)
    return (queries, filtered_dates)

def process_texts(texts: np.ndarray, dates: np.ndarray, nlp: Any) -> Tuple[List[List[str]], np.ndarray]:
    """
    Process an array of texts using spaCy to tokenize and clean the text by removing stopwords, punctuation,
    and any tokens that are not meaningful (e.g., single characters, two-letter tokens).
    Assumes that the spaCy model is loaded and available as 'nlp'.
    
    Args:
        texts (np.ndarray): An array of texts to process.
        dates (np.ndarray): An array of dates corresponding to each text.
    
    Returns:
        Tuple[List[List[str]], np.ndarray]: A tuple of a list of lists of tokens for each text and the corresponding dates.
    
    Note:
        This function requires the spaCy library and a model to be loaded with 'nlp'.
        It disables parser and named entity recognition for efficiency during tokenization.
    """
    meaningful_tokens_list = []
    meaningful_dates_list = []
    str_texts = [str(text) for text in texts]  # Ensure all inputs are strings
    for doc, date in zip(nlp.pipe(str_texts, disable=["parser", "ner"]), dates):
        doc_tokens = [token.text.lower() for token in doc if not token.is_stop 
                      and not token.is_punct 
                      and len(token.text.strip()) > 2]  # Exclude single and two-letter tokens
        if doc_tokens:  # Only append if there are tokens
            meaningful_tokens_list.append(doc_tokens)
            meaningful_dates_list.append(date)

    return meaningful_tokens_list, meaningful_dates_list

def propagate_dates(dates: List[datetime], texts: List[List[str]]) -> np.ndarray:
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

def extract_visited_sites(data: np.ndarray, dates: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
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
    start_mask_two = np.char.startswith(data, "\"Visited ")
    end_mask_two = ~np.char.endswith(data, "...\"")
    combined_mask = (start_mask & end_mask) | (start_mask_two & end_mask_two)

    # Apply the combined mask
    filtered_data = data[combined_mask]
    filtered_dates = dates[combined_mask]

    # Remove the "Visited " prefix
    first_filter = np.char.replace(filtered_data, "Visited ", "", count=1)
    sites = np.char.replace(first_filter, "\"Visited ", "", count=1)
    return sites, filtered_dates

def extract_homepage_from_url(url):
    """
    Extracts the homepage name from a given URL, using urlparse and tldextract for accurate domain extraction.
    
    Args:
        url (str): The URL from which to extract the homepage name.

    Returns:
        str: The homepage name including the top-level domain, but without the scheme or 'www.' prefix.
    """
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

    if len(result) < 3:
        return None
    
    if result.count(' ') > 4:
        return None

    return result

def compile_homepage_names(texts: np.ndarray, dates: np.ndarray) -> np.ndarray:
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
    for text, date in zip(texts, dates):
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

    search = True if mappings[1] == 'Query_Text' else False
    text_array = arr_data[1].astype(str)
    date_array = arr_data[0]

    if search:
        visited_sites, paired_dates_with_sites = extract_visited_sites(text_array, date_array)
        trimed_sites, paired_dates_with_sites_trimmed = compile_homepage_names(visited_sites, paired_dates_with_sites)

        search_queries, paired_dates_with_text = extract_search_queries(text_array, date_array)
        tokens_list, paired_dates_with_text_tokens = process_texts(search_queries, paired_dates_with_text, nlp)

        tokens_list_split, pair_dates_with_text_split = propagate_dates(paired_dates_with_text_tokens, tokens_list)
        
        return (paired_dates_with_sites_trimmed, trimed_sites), (pair_dates_with_text_split, tokens_list_split)
    else:
        visited_sites = None
        paired_dates_with_sites = None

        search_queries, paired_dates_with_text = extract_video_titles(text_array, date_array)
        tokens_list, paired_dates_with_text_tokens = process_texts(search_queries, paired_dates_with_text, nlp)

        tokens_list_split, pair_dates_with_text_split = propagate_dates(paired_dates_with_text_tokens, tokens_list)
        
        return (paired_dates_with_sites, visited_sites), (pair_dates_with_text_split, tokens_list_split)
