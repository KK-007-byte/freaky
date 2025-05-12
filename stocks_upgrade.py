import dash
from dash import dcc, html, Input, Output
import yfinance as yf
import pandas as pd
import plotly.express as px
from ta.momentum import RSIIndicator
from ta.trend import MACD
import dash_bootstrap_components as dbc

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # For deployment

# Define stock options
stock_options = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Layout
app.layout = dbc.Container([
    html.H1("\U0001F4C8 Stock Return Analytics Dashboard", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Choose Stocks:"),
            dcc.Dropdown(
                id='stock-dropdown',
                options=[{'label': stock, 'value': stock} for stock in stock_options],
                value=['AAPL', 'MSFT'],
                multi=True
            ),

            html.Br(),
            html.Label("Select Date Range:"),
            dcc.DatePickerRange(
                id='date-range',
                start_date='2020-01-01',
                end_date='2024-12-31',
                display_format='YYYY-MM-DD'
            ),
        ], width=4),

        dbc.Col([
            html.Label("Select One Stock for Technical Indicators:"),
            dcc.Dropdown(id='indicator-stock', multi=False)
        ], width=4)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='correlation-heatmap')),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='histogram')),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='price-ma')),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='rsi-chart')),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='macd-chart')),
    ])
])

# Callback to update indicator dropdown
@app.callback(
    Output('indicator-stock', 'options'),
    Input('stock-dropdown', 'value')
)
def update_indicator_dropdown(selected_stocks):
    return [{'label': s, 'value': s} for s in selected_stocks] if selected_stocks else []

# Callback to update graphs
@app.callback(
    [Output('correlation-heatmap', 'figure'),
     Output('histogram', 'figure'),
     Output('price-ma', 'figure'),
     Output('rsi-chart', 'figure'),
     Output('macd-chart', 'figure')],
    [Input('stock-dropdown', 'value'),
     Input('indicator-stock', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_graphs(tickers, selected_stock, start_date, end_date):
    if not tickers or not start_date or not end_date:
        return [{}]*5

    data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')

    # Return Calculations
    price_data = pd.concat([data[t]['Close'] for t in tickers], axis=1)
    price_data.columns = tickers
    returns = price_data.pct_change().dropna()

    # Correlation Heatmap
    corr_fig = px.imshow(returns.corr(), text_auto=True, title="Correlation Heatmap of Returns")

    # Histogram
    returns_long = returns.reset_index().melt(id_vars='Date', var_name='Stock', value_name='Daily Return')
    hist_fig = px.histogram(
        returns_long, x='Daily Return', facet_col='Stock', color='Stock', nbins=100,
        title='Daily Return Distributions by Stock', marginal='box', histnorm='probability'
    )

    # If no stock selected for indicators, return empty figures for those
    if not selected_stock:
        return corr_fig, hist_fig, {}, {}, {}

    # Indicators
    stock_data = yf.download(selected_stock, start=start_date, end=end_date)
    stock_data['MA_20'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['MA_50'] = stock_data['Close'].rolling(window=50).mean()
    stock_data['RSI'] = RSIIndicator(close=stock_data['Close'], window=14).rsi()
    macd = MACD(close=stock_data['Close'])
    stock_data['MACD'] = macd.macd()
    stock_data['MACD_Signal'] = macd.macd_signal()
    stock_data['MACD_Diff'] = macd.macd_diff()

    ma_fig = px.line(stock_data, x=stock_data.index, y=['Close', 'MA_20', 'MA_50'], title=f"{selected_stock} Price with Moving Averages")
    rsi_fig = px.line(stock_data, x=stock_data.index, y='RSI', title=f"{selected_stock} RSI (14)")
    macd_fig = px.line(stock_data, x=stock_data.index, y=['MACD', 'MACD_Signal', 'MACD_Diff'], title=f"{selected_stock} MACD")

    return corr_fig, hist_fig, ma_fig, rsi_fig, macd_fig

if __name__ == '__main__':
    app.run_server(debug=True)
