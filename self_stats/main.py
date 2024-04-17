from selector import get_file_presence_flags
import process_watch_history
import process_search_history

def main():
    directory = input("Enter the directory path where your input data is held: ")
    file_flags = get_file_presence_flags(directory)
    if file_flags['watch_history_present']:
        process_watch_history.main(directory)
    if file_flags['my_activity_present']:
        process_search_history.main(directory)

if __name__ == "__main__":
    main()