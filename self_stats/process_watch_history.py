from parse import parse_html, extract_div
from input_output import read_file, save_to_csv

def extract_video_data(entries):
    """
    Extracts video URL, video title, channel title, and date from all entries.
    
    Args:
    - entries (ResultSet): A BeautifulSoup ResultSet containing multiple entries.
    
    Returns:
    - list of lists containing extracted data.
    """
    data = []
    for entry in entries:
        video_data = extract_video_field(entry)
        if video_data:
            data.append(video_data)
    return data

def extract_video_field(entry):
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

def extract_date(entry):
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

def main(directory):
    html_content = read_file(f'{directory}/watch-history.html')
    soup = parse_html(html_content)
    entries = extract_div(soup)
    data = extract_video_data(entries)
    save_to_csv(data, f'{directory}/extracted_watch_history_data.csv', ['Video URL', 'Video Title', 'Channel Title', 'Date'])
    
    print(f"Watch data extraction complete. Results saved to '{directory}/extracted_watch_history_data.csv'.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
