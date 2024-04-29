from self_stats.munger.input_output import get_file_presence_flags
from self_stats.munger.munger_main import main as munger_main

def main() -> None:
    """
    Main function that orchestrates the processing of watch history and search history based on file presence.
    """
    skip_preprocess = False # This line will be used if the user just wants data viz functionality
    directory = 'personal_data' # This line skips user input for quicker testing

    # if the user has already processed the data, they can skip the preprocessing step
    # this option will be make available through the command line arguments at a later point
    if not skip_preprocess:
        # directory: str = input("Enter the directory path where your input data is held: ")
        print(f"\nInitializing from directory: {directory}...\n")

        file_flags: dict = get_file_presence_flags(directory)

        if file_flags['my_activity_present']:
            munger_main(directory, f'{directory}/MyActivity.json', [
                'Date',                
                'Text Title', 
                'Latitude',
                'Longitude'
            ])

        if file_flags['watch_history_present']:
            munger_main(directory, f'{directory}/watch-history.json', [
                'Date',                
                'Video Title',
                'Channel Title',
                'Video URL'
            ])

if __name__ == "__main__":

    main()
