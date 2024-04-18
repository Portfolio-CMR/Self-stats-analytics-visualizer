# Standard library imports
from io import StringIO
from pathlib import Path
from typing import Union
from functools import partial

# Third-party library imports
from dash import Dash
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure

# Callback registration function
def register_callbacks(app: Dash, path: Union[str, Path]) -> None:
    """ Registers the callbacks necessary for the Dash application's interactivity. """
    load_data_with_path = partial(load_data, path=path)

    @app.callback(Output('stored-data', 'data'), [Input('interval-component', 'n_intervals')])
    def update_data(n: int) -> str:
        """ Periodically updates data based on a specified interval. """
        return load_data_with_path(n)

    @app.callback(Output('weekday-chart', 'figure'), [Input('stored-data', 'data'), Input('time-series-chart', 'relayoutData')])
    def update_weekday_graph(json_data: str, relayoutData: dict) -> Figure:
        """ Updates the weekday frequency graph based on stored data and zoom level of the time-series chart. """
        return generate_weekday_chart(json_data, relayoutData)

    @app.callback(Output('hour-chart', 'figure'), [Input('stored-data', 'data'), Input('time-series-chart', 'relayoutData')])
    def update_hour_graph(json_data: str, relayoutData: dict) -> Figure:
        """ Updates the hourly frequency graph based on stored data and zoom level of the time-series chart. """
        return generate_hour_chart(json_data, relayoutData)

    @app.callback(Output('time-series-chart', 'figure'), [Input('stored-data', 'data'), Input('time-series-chart', 'relayoutData')])
    def update_time_series_chart(json_data: str, relayoutData: dict) -> Figure:
        """ Updates the time-series chart based on stored data and user interactions. """
        return generate_time_series_chart(json_data, relayoutData)

def generate_weekday_chart(json_data: str, relayoutData: dict) -> Figure:
    """
    Generates a bar chart displaying the frequency of entries by weekdays.

    Args:
        json_data (str): JSON string of the DataFrame containing the preprocessed data.
        relayoutData (dict): Current layout state of the time-series chart, including zoom and range.

    Returns:
        px.Figure: A Plotly Express figure object for the weekday frequency graph.
    """
    df = pd.read_json(StringIO(json_data), orient='split')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Weekday'] = df['Date'].dt.day_name()

    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        x_start, x_end = pd.to_datetime(relayoutData['xaxis.range[0]']), pd.to_datetime(relayoutData['xaxis.range[1]'])
        df = df[(df['Date'] >= x_start) & (df['Date'] <= x_end)]

    weekday_counts = df.groupby('Weekday').size().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    fig = px.bar(weekday_counts, x=weekday_counts.index, y=weekday_counts, title="Frequency of Entries by Day of the Week")
    fig.update_traces(marker_color='green')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )

    return fig

def generate_hour_chart(json_data: str, relayoutData: dict) -> Figure:
    """
    Generates a bar chart displaying the frequency of entries by hour of the day.

    Args:
        json_data (str): JSON string of the DataFrame containing the preprocessed data.
        relayoutData (dict): Current layout state of the time-series chart, including zoom and range.

    Returns:
        px.Figure: A Plotly Express figure object for the hourly frequency graph.
    """
    df = pd.read_json(StringIO(json_data), orient='split')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Hour'] = df['Date'].dt.hour

    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        x_start, x_end = pd.to_datetime(relayoutData['xaxis.range[0]']), pd.to_datetime(relayoutData['xaxis.range[1]'])
        df = df[(df['Date'] >= x_start) & (df['Date'] <= x_end)]

    hour_counts = df.groupby('Hour').size()

    fig = px.bar(hour_counts, x=hour_counts.index, y=hour_counts, title="Frequency of Entries by Time of Day")
    fig.update_traces(marker_color='darkblue')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        xaxis=dict(tickmode='array', tickvals=list(range(24)), title='Hour of the Day'),
        yaxis_title="Number of Entries"
    )

    return fig

def generate_time_series_chart(json_data: str, relayoutData: dict) -> Figure:
    """
    Generates a histogram displaying the frequency of entries over time.

    Args:
        json_data (str): JSON string of the DataFrame containing the preprocessed data.
        relayoutData (dict): Current layout state of the time-series chart, including zoom and range.

    Returns:
        px.Figure: A Plotly Express figure object for the time-series frequency graph.
    """
    df = pd.read_json(StringIO(json_data), orient='split')
    df['Date'] = pd.to_datetime(df['Date'])

    # Handle zooming and panning by adjusting the number of bins dynamically
    num_bins = 20  # Default number of bins
    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        x_start, x_end = pd.to_datetime(relayoutData['xaxis.range[0]']), pd.to_datetime(relayoutData['xaxis.range[1]'])
        df = df[(df['Date'] >= x_start) & (df['Date'] <= x_end)]
        # Adjust bins based on the data density
        num_bins = max(int(len(df) / 3), 1)

    fig = px.histogram(df, x='Date', nbins=num_bins, title="Frequency of Entries Over Time")
    fig.update_traces(marker_color='#008080')  # Setting a teal color for histogram bars
    fig.update_layout(
        bargap=0.2,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        xaxis=dict(
            showline=True,
            showgrid=True,
            linecolor='white',
            gridcolor='grey'
        ),
        yaxis=dict(
            showline=True,
            showgrid=True,
            linecolor='white',
            gridcolor='grey'
        )
    )

    return fig

# Data loading function
def load_data(n: int, path: Union[str, Path]) -> str:
    """ Loads and preprocesses data from a specified path. """
    df = pd.read_csv(path)
    # Assume some preprocessing is done here
    return df.to_json(date_format='iso', orient='split')

# Main application logic
def main():
    path = Path('data/output/dash_ready_watch_data.csv')
    app = Dash(__name__)
    register_callbacks(app, path)
    app.run_server(debug=True)

if __name__ == '__main__':
    main()
