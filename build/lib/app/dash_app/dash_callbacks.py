from functools import partial
from io import StringIO
from pathlib import Path
from typing import Union

import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure
from dash import Dash
from dash.dependencies import Input, Output, State

from app.dash_app.tz_offset import get_utc_offset, adjust_time_by_utc_offset

def load_data(n: int, path: Union[str, Path]) -> str:
    """
    Loads and preprocesses data at regular intervals, specified by `n_intervals`.
    This function reads data from a CSV file specified by `path`, preprocesses it,
    and returns a JSON string containing the preprocessed data.

    Args:
        n (int): The number of intervals that have elapsed (unused directly in function).
        path (str | Path): The file path for the CSV file to be processed.

    Returns:
        str: A JSON string of the DataFrame containing preprocessed data.
    """
    df = pd.read_csv(path)
    # Assume some preprocessing is done here
    return df.to_json(date_format='iso', orient='split')

def register_callbacks(app: Dash, path: Union[str, Path]) -> None:
    """
    Registers the callbacks necessary for the Dash application's interactivity.

    Args:
        app (Dash): The Dash application instance to which callbacks will be attached.
        path (str | Path): The file path for the CSV file to be processed.
    """

    # Here we use functools.partial to prefill the `path` parameter for `load_data`
    load_data_with_path = partial(load_data, path=path)

    @app.callback(
        Output('stored-data', 'data'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_data(n: int) -> str:
        """
        Wrapper function to call `load_data_with_path` within the Dash callback context.

        Args:
            n (int): The number of intervals that have elapsed (unused directly in function).

        Returns:
            str: A JSON string of the DataFrame containing preprocessed data.
        """
        return load_data_with_path(n)
    
    @app.callback(
        Output('weekday-chart', 'figure'),
        [Input('stored-data', 'data'),
         Input('time-series-chart', 'relayoutData')]
    )
    def update_weekday_graph(json_data: str, relayoutData: dict) -> Figure:
        """
        Updates the weekday frequency graph based on the stored data and the current zoom level
        of the time-series chart.

        Args:
            json_data (str): The JSON string of the DataFrame containing the preprocessed data.
            relayoutData (dict): The current layout state of the time-series chart, including zoom and range.

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

        fig = px.bar(weekday_counts, x=weekday_counts.index, y=weekday_counts, title="Frequency of Entries by Day of the Week", template='plotly')

        # fig = px.bar(weekday_counts, x=weekday_counts.index, y=weekday_counts, title="Frequency of Entries by Day of the Week")
        # fig.update_traces(marker_color='green')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white"
        )

        return fig

    @app.callback(
        Output('hour-chart', 'figure'),
        [Input('stored-data', 'data'),
         Input('time-series-chart', 'relayoutData')]
    )
    def update_hour_graph(json_data: str, relayoutData: dict) -> Figure:
        """
        Updates the hourly frequency graph based on the stored data and the current zoom level
        of the time-series chart.

        Args:
            json_data (str): The JSON string of the DataFrame containing the preprocessed data.
            relayoutData (dict): The current layout state of the time-series chart, including zoom and range.

        Returns:
            px.Figure: A Plotly Express figure object for the hourly frequency graph.
        """
        df = pd.read_json(StringIO(json_data), orient='split')
        df['Date'] = pd.to_datetime(df['Date'])
        df['Date_tz'] = df['Date'].apply(adjust_time_by_utc_offset)
        df['Hour'] = df['Date_tz'].dt.hour

        if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
            x_start, x_end = pd.to_datetime(relayoutData['xaxis.range[0]']), pd.to_datetime(relayoutData['xaxis.range[1]'])
            df = df[(df['Date'] >= x_start) & (df['Date'] <= x_end)]

        hour_counts = df.groupby('Hour').size()

        fig = px.bar(hour_counts, x=hour_counts.index, y=hour_counts, title="Frequency of Entries by Time of Day", template='plotly_dark')
        # fig.update_traces(marker_color='darkblue')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            xaxis=dict(tickmode='array', tickvals=list(range(24)), title='Hour of the Day'),
            yaxis_title="Number of Entries"
        )

        return fig

    @app.callback(
        Output('time-series-chart', 'figure'),
        [Input('stored-data', 'data'),
         Input('time-series-chart', 'relayoutData')]
    )
    def update_time_series_chart(json_data: str, relayoutData: dict) -> Figure:
        """
        Updates the time-series chart based on the stored data and any user interaction
        that modifies the chart's layout (e.g., zooming and panning).

        Args:
            json_data (str): The JSON string of the DataFrame containing the preprocessed data.
            relayoutData (dict): The current layout state of the time-series chart, including zoom and range.

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
            num_bins = max(int(len(df) / 100), 1)  # Adjust bins based on the data density

        fig = px.histogram(df, x='Date', nbins=num_bins, title="Frequency of Entries Over Time", template='plotly_dark')
        # fig.update_traces(marker_color='#008080')
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

def main():
    path = Path('data/output/extracted_watch_history.csv')
    app = Dash(__name__)
    register_callbacks(app, path)
    app.run_server(debug=True)

if __name__ == '__main__':
    main()