from dash import Dash
from pathlib import Path

import app.dash_app.dash_callbacks as dash_callbacks 
from app.dash_app.dash_layout import create_layout

def main(path: str | Path) -> None:
    """
    Main function that visualizes processed data using Dash.
    """
    app = Dash(__name__)
    app.layout = create_layout()
    dash_callbacks.register_callbacks(app, path)  # Registering callbacks with the app
    app.run_server(debug=True)  # Running the server within the main function

if __name__ == '__main__':
    main(Path('/home/bio/Python_projects/self_stats/data/output/dash_ready_watch_data.csv'))  # Pass the correct path as an argument