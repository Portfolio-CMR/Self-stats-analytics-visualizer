# dash_app_caller.py
from dash import Dash
import self_stats.dash_app.dash_callbacks as dash_callbacks 
from self_stats.dash_app.dash_layout import create_layout

app = Dash(__name__)
server = app.server

def setup_app(path: str):
    """
    Configures the Dash app with layout and callbacks, ready to be run externally.
    """
    app.layout = create_layout()
    dash_callbacks.register_callbacks(app, path)
