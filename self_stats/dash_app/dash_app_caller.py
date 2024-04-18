from dash import Dash
import self_stats.dash_app.dash_callbacks as dash_callbacks  # Assuming callbacks are separated
from self_stats.dash_app.dash_layout import create_layout  # Assuming layout is separated
from pathlib import Path

def main(path: str | Path) -> None:
    """
    Main function that visualizes processed data using Dash.
    """
    app = Dash(__name__)
    app.layout = create_layout()
    dash_callbacks.register_callbacks(app, path)  # Registering callbacks with the app
    app.run_server(debug=True)  # Running the server within the main function

if __name__ == '__main__':
    main(Path('/path/to/your/data'))  # Pass the correct path as an argument