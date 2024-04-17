import self_stats.munger.clean_parsed_data as clean_parsed_data
from typing import List, Any
from bs4 import Tag, ResultSet  # Assuming BeautifulSoup is used
from pathlib import Path
from self_stats.munger.parse import parse_html, extract_div
from self_stats.munger.input_output import read_file, save_to_csv
from self_stats.munger.trim_and_clean_dates import clean_date

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
    cleaned_data = clean_parsed_data.main(data, 'watch_history')

    out_dir = Path(f'{directory}/output')
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {out_dir}\n")
    col_names = ['Video URL', 'Video Title', 'Channel Title', 'Date']
    save_to_csv(cleaned_data, f'{out_dir}/extracted_watch_history_data.csv', col_names)
    print(f"Search data extraction complete. Results saved to '{directory}/extracted_watch_history_data.csv'.\n")



if __name__ == "__main__":
    import sys
    main(sys.argv[1])
