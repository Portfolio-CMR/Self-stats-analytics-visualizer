from self_stats.munger.selector import get_file_presence_flags
from self_stats.munger.munger_main import main as munger_main
from self_stats.dash_app.dash_app_caller import main as dash_main
from sys import argv

def main() -> None:
    """
    Main function that orchestrates the processing of watch history and search history based on file presence.
    """
    skip_preprocess = False
    directory = 'data'

    # if the user has already processed the data, they can skip the preprocessing step
    # this option will be make available through the command line arguments at a later point
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
