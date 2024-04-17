import pandas as pd
import numpy as np
import ruptures as rpt
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from io import StringIO

CSV_FILE_PATH = '/home/bio/Python_projects/self_stats/data/extracted_watch_history_data.csv'

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Entries Frequency Over Time", style={'textAlign': 'center', 'color': 'white'}),
    dcc.Graph(id='time-series-chart', config={'staticPlot': False}),  # Allow zoom and pan
    dcc.Graph(id='weekday-chart', config={'staticPlot': False}),  # New graph for day of the week frequency
    dcc.Graph(id='hour-chart', config={'staticPlot': False}),  # New graph for time of day frequency
    dcc.Interval(
        id='interval-component',
        interval=1*60000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Store(id='stored-data'),  # To store the initial full dataset
], className='row', style={
    'textAlign': 'center',
    'width': '100%',
    'maxHeight': '100vh',
    'overflowY': 'auto'  # Enable verticasl scroll
})

################################################################################

@app.callback(
    Output('stored-data', 'data'),
    [Input('interval-component', 'n_intervals')]
)
def load_data(n):
    df = pd.read_csv(CSV_FILE_PATH)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # Directly extract the hour from the 'Date' column
    df['Hour'] = df['Date'].dt.hour

    # Now convert 'Date' to just the date part
    df['Date'] = df['Date'].dt.date

    # Bin data by day and count the number of entries per day
    daily_counts = df.groupby('Date').size()

    # Convert the daily counts to a 2D array for ruptures
    data = daily_counts.values.reshape(-1, 1)

    # Use the Binseg algorithm to find the changepoint in the daily counts
    algo = rpt.Binseg(model='l2').fit(data)
    result = algo.predict(n_bkps=1)

    # If a changepoint was found, determine its date
    if result:
        changepoint_index = result[0] - 1
        changepoint_date = daily_counts.index[changepoint_index]
    else:
        # If no changepoint is found, default to the earliest date
        changepoint_date = daily_counts.index.min()

    # Filter the DataFrame to only include data from after the changepoint
    df = df[df['Date'] >= changepoint_date]

    # Return data as JSON, include both 'Date' and 'Time' columns
    return df.to_json(date_format='iso', orient='split')

################################################################################

@app.callback(
    Output('weekday-chart', 'figure'),
    [Input('stored-data', 'data'),
     Input('time-series-chart', 'relayoutData')]
)
def update_weekday_graph(json_data, relayoutData):
    df = pd.read_json(StringIO(json_data), orient='split')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Weekday'] = df['Date'].dt.day_name()

    # Check if there is zoom range info in relayoutData and adjust the DataFrame accordingly
    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        x_start, x_end = pd.to_datetime(relayoutData['xaxis.range[0]']), pd.to_datetime(relayoutData['xaxis.range[1]'])
        df = df[(df['Date'] >= x_start) & (df['Date'] <= x_end)]

    # Count the number of entries per weekday and sort them by the order of the week
    weekday_counts = df.groupby('Weekday').size().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    fig = px.bar(weekday_counts, x=weekday_counts.index, y=weekday_counts, title="Frequency of Entries by Day of the Week")
    fig.update_traces(marker_color='green')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )

    return fig

################################################################################

@app.callback(
    Output('hour-chart', 'figure'),
    [Input('stored-data', 'data'),
     Input('time-series-chart', 'relayoutData')]
)
def update_hour_graph(json_data, relayoutData):
    df = pd.read_json(StringIO(json_data), orient='split')
    # df['Time'] = pd.to_datetime(df['Time'])
    # df['Hour'] = df['Time'].dt.hour  # Extract hour from the Date

    # Check if there is zoom range info in relayoutData and adjust the DataFrame accordingly
    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        x_start, x_end = pd.to_datetime(relayoutData['xaxis.range[0]']), pd.to_datetime(relayoutData['xaxis.range[1]'])
        df = df[(df['Date'] >= x_start) & (df['Date'] <= x_end)]

    # Count the number of entries per hour
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


################################################################################

# Assuming that 'num_bins' is the desired number of bins when fully zoomed out
# You can adjust 'num_bins' based on your dataset and preference
num_bins = 20

@app.callback(
    Output('time-series-chart', 'figure'),
    [Input('stored-data', 'data'),
     Input('time-series-chart', 'relayoutData')]
)
def update_graph(json_data, relayoutData):
    df = pd.read_json(StringIO(json_data), orient='split')

    # Check if there is zoom range info in relayoutData
    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        x_start, x_end = relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']
        # Filter data based on zoom range
        df_zoomed = df[(df['Date'] >= x_start) & (df['Date'] <= x_end)]
        # Update number of bins based on the zoomed range
        bin_size = (pd.to_datetime(x_end) - pd.to_datetime(x_start)) / num_bins
        fig = px.histogram(df_zoomed, x='Date', nbins=num_bins, title="Frequency of Entries Over Time")
        # Update the bins' size
        fig.update_traces(xbins=dict(start=x_start, end=x_end, size=bin_size))
    else:
        # Default view with default number of bins
        fig = px.histogram(df, x='Date', nbins=num_bins, title="Frequency of Entries Over Time")

    # Set the color of the histogram bars to teal
    fig.update_traces(marker_color='#008080')
    
    # Ensure the background is transparent and update layout properties as before
    fig.update_layout(
        bargap=0.2,
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background for the plot
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the area around the plot
        font_color="white",  # Change font color to white for better contrast
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

if __name__ == '__main__':
    app.run_server(debug=True)
