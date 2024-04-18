from typing import List, Any
from bs4 import Tag, ResultSet  # Assuming BeautifulSoup is used
from pathlib import Path
import numpy as np
from self_stats.munger.parse import parse_html, extract_div
from self_stats.munger.input_output import read_file
import self_stats.munger.watch_history_cleaner as watch_history_cleaner
from self_stats.munger.clean_data_shared import convert_to_arrays

def extract_video_data(entries: ResultSet) -> List[List[str]]:
    """
    Extracts video URL, video title, channel title, and date from all entries.
    
    Args:
    - entries (ResultSet): A BeautifulSoup ResultSet containing multiple entries.
    
    Returns:
    - list of lists containing extracted data.
    """
    data: List[List[str]] = []
    for entry in entries:
        video_data: List[str] = extract_video_field(entry)
        if video_data:
            data.append(video_data)
    return data

def extract_video_field(entry: Tag) -> List[str]:
    """
    Extracts the video data from an entry.
    
    Args:
    - entry (Tag): A BeautifulSoup Tag object representing the entry.
    
    Returns:
    - list: Extracted video data as a list.
    """
    links = entry.find_all('a', href=True)
    video_url = links[0]['href'] if len(links) > 0 and 'watch' in links[0]['href'] else "No URL found"
    video_title = links[0].text.strip() if len(links) > 0 else "No video title found"
    channel_title = links[1].text.strip() if len(links) > 1 else "No channel title found"
    date_text = extract_date(entry)
    return [video_url, video_title, channel_title, date_text]

def extract_date(entry: Tag) -> str:
    """
    Extracts the date from an entry using safe navigation for next siblings.
    
    Args:
    - entry (Tag): A BeautifulSoup Tag object representing the entry.
    
    Returns:
    - str: Extracted date text.
    """
    last_br = entry.find_all('br')[-1]
    if last_br and last_br.next_sibling:
        return last_br.next_sibling.strip() if isinstance(last_br.next_sibling, str) else "No date found"
    return "No date found"

def main(directory: str) -> None:
    html_content = read_file(f'{directory}/watch-history.html')
    soup = parse_html(html_content)
    entries = extract_div(soup)
    data = extract_video_data(entries)
    video_urls, video_titles, channel_titles, dates = convert_to_arrays(data)
    cleaned_data = watch_history_cleaner.main(video_urls, video_titles, channel_titles, dates)
    return cleaned_data

