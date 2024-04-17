from dash import Dash
import self_stats.dash_callbacks as dash_callbacks  # If callbacks are separated
from dash_layout import create_layout  # If layout is separated

app = Dash(__name__)
path = '/home/bio/Python_projects/self_stats/data/filtered_watch_history_data.csv'
app.layout = create_layout()
dash_callbacks.register_callbacks(app, path)  # If callbacks are separated

if __name__ == '__main__':
    app.run_server(debug=True)
