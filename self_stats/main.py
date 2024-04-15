from extract import parse_html, extract_data
from input_output import read_file, write_to_csv

def main():
    """
    Main function to extract data from HTML and save it to a CSV file.
    """
    file_path = "data/.01_activity.html"
    csv_file_path = 'data/.01_extracted_data.csv'
    
    html_content = read_file(file_path)
    soup = parse_html(html_content)
    data = extract_data(soup)
    write_to_csv(data, csv_file_path)
    
    print("Data extraction complete. Results saved to 'extracted_data.csv'.")

if __name__ == "__main__":
    main()