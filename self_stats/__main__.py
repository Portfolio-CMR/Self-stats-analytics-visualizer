from self_stats.munger.selector import get_file_presence_flags
from self_stats.munger.munger_main import main as munger_main

def main() -> None:
    """
    Main function that orchestr
    ates the processing of watch history and search history based on file presence.
    """
    directory: str = input("Enter the directory path where your input data is held: ")
    print(f"\Initializing from directory: {directory}...\n")

    file_flags: dict = get_file_presence_flags(directory)

    if file_flags['my_activity_present']:
        print("Processing search history...\n")
        munger_main(directory, f'{directory}/MyActivity.json', [
            'Text Title',
            'Date',
            'Latitude',
            'Longitude'
        ])

    if file_flags['watch_history_present']:
        print("Processing watch history...\n")
        munger_main(directory, f'{directory}/watch-history.json', [
            'Video URL',
            'Video Title',
            'Channel Title',
            'Date'
        ])
    
    #TODO Implement dash visualization sub-module here

if __name__ == "__main__":
    main()
