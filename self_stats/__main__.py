from self_stats.munger.selector import get_file_presence_flags
import self_stats.munger.watch_history_main as process_watch
import self_stats.munger.search_history_main as process_search
from self_stats.munger.munger_main import main as munger_main

def main() -> None:
    """
    Main function that orchestrates the processing of watch history and search history based on file presence.
    """
    directory: str = input("Enter the directory path where your input data is held: ")
    print(f"\Initializing from directory: {directory}...\n")
    file_flags: dict = get_file_presence_flags(directory)

    if file_flags['my_activity_present']:
        print("Processing search history...\n")
        munger_main(directory, 'search_history', [
            'Search Text',
            'Date',
            'Latitude',
            'Longitude'
        ])

    if file_flags['watch_history_present']:
        print("Processing watch history...\n")
        munger_main(directory, 'watch_history', [
            'Video URL',
            'Video Title',
            'Channel Title',
            'Date'
        ])
    


if __name__ == "__main__":
    main()
