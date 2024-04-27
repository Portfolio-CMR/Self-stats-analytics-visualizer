from typing import List
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from typing import List, Tuple, Counter, Dict, Any
from collections import Counter
import pandas as pd

import spacy

import re

# Preprocessing

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

def clean_text(text: str) -> str:
    """
    Convert text to lowercase and remove punctuation.
    
    Args:
    text (str): The text to clean.
    
    Returns:
    str: The cleaned text.
    """
    text = text.lower()  # Convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    return text

def tokenize_text(text: str) -> List[str]:
    """
    Tokenize the text into words.
    
    Args:
    text (str): The text to tokenize.
    
    Returns:
    List[str]: A list of words (tokens).
    """
    tokens = word_tokenize(text)
    return tokens

def remove_stop_words(tokens: List[str]) -> List[str]:
    """
    Remove common English stop words from a list of tokens.
    
    Args:
    tokens (List[str]): The list of tokens from which to remove stop words.
    
    Returns:
    List[str]: A list of tokens with stop words removed.
    """
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    return filtered_tokens

def stem_tokens(tokens: List[str]) -> List[str]:
    """
    Apply stemming to a list of tokens using the Porter stemming algorithm.
    
    Args:
    tokens (List[str]): The list of tokens to stem.
    
    Returns:
    List[str]: A list of stemmed tokens.
    """
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens

def preprocess_query(query: str) -> List[str]:
    """
    Preprocess a query by cleaning, tokenizing, removing stop words, and stemming.
    
    Args:
    query (str): The search query to preprocess.
    
    Returns:
    List[str]: A list of processed tokens.
    """
    cleaned = clean_text(query)
    tokens = tokenize_text(cleaned)
    tokens_no_stop = remove_stop_words(tokens)
    stemmed_tokens = stem_tokens(tokens_no_stop)
    return stemmed_tokens

# Data exploration
####################################################################################################

def get_word_frequency(tokens: List[str], num_words: int = 20) -> List[Tuple[str, int]]:
    """
    Get the frequency of the top `num_words` most common words in `tokens`.
    
    Args:
    tokens (List[str]): A list of all tokens from the dataset.
    num_words (int): The number of top words to display.
    
    Returns:
    List[Tuple[str, int]]: A list of tuples where each tuple is (word, frequency).
    """
    word_counts = Counter(tokens)
    most_common_words = word_counts.most_common(num_words)
    return most_common_words

def compute_query_trends(data: pd.DataFrame, query: str) -> pd.Series:
    """
    Compute the trend of occurrences for a specific query over time.
    
    Args:
    data (pd.DataFrame): DataFrame with 'date' and 'query' columns.
    query (str): Specific query to analyze.
    
    Returns:
    pd.Series: A time series of the count of occurrences.
    """
    df = data[data['query'].str.contains(query, case=False)]
    trend_data = df.resample('M', on='date').size()  # 'M' for monthly frequency
    return trend_data

def get_category_distribution(data: pd.DataFrame) -> pd.Series:
    """
    Get the distribution of queries across categories.
    
    Args:
    data (pd.DataFrame): DataFrame with a 'category' column.
    
    Returns:
    pd.Series: Counts of queries in each category.
    """
    category_counts = data['category'].value_counts()
    return category_counts

def analyze_search_queries(tokens: List[str], data: pd.DataFrame, query: str, category_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze search queries by performing frequency analysis, trend analysis, and categorical analysis.
    
    Args:
    tokens (List[str]): A list of all tokens from the dataset for frequency analysis.
    data (pd.DataFrame): DataFrame with 'date' and 'query' columns for trend analysis.
    query (str): Specific query to analyze for trend analysis.
    category_data (pd.DataFrame): DataFrame with 'category' column for category distribution analysis.
    
    Returns:
    Dict[str, Any]: A dictionary containing results of the analyses with keys 'frequency', 'trends', and 'categories'.
    """
    # Frequency analysis of words
    word_frequency = get_word_frequency(tokens)
    
    # Trend analysis of a specific query
    query_trends = compute_query_trends(data, query)
    
    # Categorical distribution of queries
    category_distribution = get_category_distribution(category_data)
    
    # Compile all results into a dictionary
    results = {
        'frequency': word_frequency,
        'trends': query_trends,
        'categories': category_distribution
    }
    
    return results

# Load a pre-trained NLP model
nlp = spacy.load("en_core_web_sm")

def extract_topic(query: str) -> str:
    doc = nlp(query)
    # Example: use noun chunks as crude topic identifiers
    topics = [chunk.text for chunk in doc.noun_chunks]
    return ', '.join(topics) if topics else 'General'

if __name__ == "__main__":
    # Example usage
    table = pd.read_csv('personal_data/output/dash_ready_search_data.csv')
    data = [s.replace("Searched for", "", 1) for s in table['Text Title'] if s.startswith("Searched")]
    data = data[:1000]
    
    # Preprocess search queries
    tokens = [preprocess_query(query) for query in data]
    
    category_data = [extract_topic(query) for query in data]


    # Analyze search queries
    query = 'machine learning'
    results = analyze_search_queries(tokens, data, query, category_data)
    
    print("Frequency analysis:")
    for word, freq in results['frequency']:
        print(f"{word}: {freq}")
    
    print("\nTrend analysis:")
    print(results['trends'])
    
    print("\nCategory distribution:")
    print(results['categories'])