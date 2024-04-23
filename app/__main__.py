from app.munger.selector import get_file_presence_flags
from app.munger.munger_main import main as munger_main
from app.dash_app.dash_app_caller import main as dash_main

def main() -> None:
    """
    Main function that orchestr
    ates the processing of watch history and search history based on file presence.
    """
    skip_preprocess = False # This line will be used if the user just wants data viz functionality
    directory = 'personal_data' # This line skips user input for quicker testing

    if not skip_preprocess:
        # directory: str = input("Enter the directory path where your input data is held: ")
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

    viz_flag = 'watch'

    if viz_flag == 'watch':
        print("Visualizing watch history...\n")
        dash_main('data/output/dash_ready_watch_data.csv')

if __name__ == "__main__":
    main()
