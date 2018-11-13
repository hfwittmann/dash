import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
import os
from dotenv import load_dotenv
load_dotenv()

#cimport cufflinks as cf
# cf.set_config_file(offline=True, world_readable=True, theme='ggplot', colorscale='original')
import quandl

app = dash.Dash('stock-ticker')
server = app.server

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Start : Global configuration
# Get Table
url = "https://en.wikipedia.org/wiki/DAX"
tables = pd.read_html(url)
constituents = tables[2]
constituents = constituents.drop(columns=[0]).rename(columns=constituents.iloc[0])[1:]
constituents['Quandl Ticker symbol'] = 'FSE/' + constituents['Ticker symbol'] + '_X'
options = [{'label': stockinfo['Company'], 'value': stockinfo['Quandl Ticker symbol'] } for i, stockinfo in constituents.iterrows()]


# Get Data
#### to load the    
quandl.ApiConfig.api_key = os.getenv('quandl_api_key')
# End : Global configuration


app.layout = html.Div(children = [

    html.H1(children='''
    Performance and Returns Data of Dax Stocks
    '''),

    dcc.Dropdown(
        id = 'stockticker',
        options = options,
        value = 'FSE/BAS_X'
    ),

    html.Div(id='intermediate-value', style={'display': 'none'}),

    dcc.Graph(id='performance'),
    dcc.Graph(id='returns'),
    dcc.Graph(id='histogram')
])


@app.callback(
    dash.dependencies.Output('intermediate-value', 'children'),
    [dash.dependencies.Input('stockticker', 'value')]
)
def get_data(stockticker):
    mydata = quandl.get(stockticker)

    # only use recent years
    performance_data = mydata.loc['2007':].filter(items=['Open', 'Close'])
    return performance_data.to_json()
 
@app.callback(
     dash.dependencies.Output('performance', 'figure'),
     [dash.dependencies.Input('intermediate-value', 'children'),
     dash.dependencies.Input('stockticker', 'value')]
 )
def update_performance_graph(performance_data_json, stockticker):

    # label = constituents[constituents['Quandl Ticker symbol'] == stock_ticker_name]['Company']
    # plot plots 
    performance_data = pd.read_json(performance_data_json)

    trace_open = go.Scatter(
        x = performance_data.index,
        y = performance_data['Open'],
        mode = 'lines',
        marker = {'colorscale': 'Viridis'},
        name = 'Open'
    )

    trace_close = go.Scatter(
        x = performance_data.index,
        y = performance_data['Close'],
        mode = 'lines',
        marker = {'colorscale': 'Viridis'},
        name = 'Close'
    )

    data = [trace_open, trace_close]

    layout = {
              'title' : 'Performance:' + stockticker,
              'yaxis':{'type': 'log'}
              }

    fig_performance = dict(data = data, layout = layout)

    return fig_performance

@app.callback(
    dash.dependencies.Output('returns', 'figure'),
    [dash.dependencies.Input('intermediate-value', 'children'),
    dash.dependencies.Input('stockticker', 'value')]
)
def update_returns_graph(performance_data_json, stockticker):

    performance_data = pd.read_json(performance_data_json)
    returns = performance_data.diff(axis=0)/performance_data

    trace_open = go.Scatter(
        x = returns.index,
        y = returns['Open'],
        mode = 'lines',
        marker = {'colorscale': 'Viridis'},
        name = 'Open'
    )

    trace_close = go.Scatter(
        x = returns.index,
        y = returns['Close'],
        mode = 'lines',
        marker = {'colorscale': 'Viridis'},
        name = 'Close'
    )

    data = [trace_open, trace_close]

    layout = { 'title': 'Returns:' + stockticker
              # 'yaxis':{'type': 'lin'}
              }

    fig_returns = dict(data = data, layout = layout)

    return fig_returns


@app.callback(
    dash.dependencies.Output('histogram', 'figure'),
    [dash.dependencies.Input('intermediate-value', 'children'),
     dash.dependencies.Input('stockticker', 'value')]
)
def update_histogram_graph(performance_data_json, stockticker):
    performance_data = pd.read_json(performance_data_json)
    returns = performance_data.diff(axis=0)/performance_data

    trace_open = go.Histogram(
        x = returns['Open'],
        marker = {'colorscale': 'Viridis'},
        name ='Open'
    )

    trace_close = go.Histogram(
        x = returns['Open'],
        marker = {'colorscale': 'Viridis'},
        name = 'Close'
    )

    data = [trace_open, trace_close]

    layout = { 'title' : 'Histogram:' + stockticker
            # 'yaxis':{'type': 'lin'}
            }


    fig_histogram = dict(data = data, layout = layout)

    return fig_histogram


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)

