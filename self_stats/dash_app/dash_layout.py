from dash import html, dcc

def create_layout():
    """
    Creates the layout for the Dash application.

    Returns:
        A Dash html component representing the app layout.
    """
    layout = html.Div([
        html.H1("Entries Frequency Over Time", style={'textAlign': 'center', 'color': 'white'}),
        dcc.Graph(id='time-series-chart', config={'staticPlot': False}),
        dcc.Graph(id='weekday-chart', config={'staticPlot': False}),
        dcc.Graph(id='hour-chart', config={'staticPlot': False}),
        dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),
        dcc.Store(id='stored-data')
    ], className='row', style={
        'textAlign': 'center', 'width': '100%', 'maxHeight': '100vh', 'overflowY': 'auto'
    })
    return layout
