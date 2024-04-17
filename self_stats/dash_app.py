import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

# Assume the CSV file is named 'data.csv' and is in the same directory as this script.
CSV_FILE_PATH = '/home/bio/Python_projects/self_stats/data/extracted_search_history_data.csv'

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Entries Frequency Over Time"),
    dcc.Graph(id='time-series-chart'),
    dcc.Interval(
            id='interval-component',
            interval=1*60000,  # in milliseconds
            n_intervals=0
        )
])

@app.callback(
    Output('time-series-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    # Read the data from CSV
    df = pd.read_csv(CSV_FILE_PATH)

    # Ensure 'Date' is in datetime format and coerce invalid dates to NaT
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Remove rows where Date is NaT
    df = df.dropna(subset=['Date'])

    # Create a histogram of entries over time
    fig = px.histogram(df, x='Date', nbins=50, title="Frequency of Entries Over Time")

    # Update layout
    fig.update_layout(bargap=0.2)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
