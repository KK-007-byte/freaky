from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly
import json
from ta.momentum import RSIIndicator
from ta.trend import MACD

app = Flask(__name__)

# Stock list
stock_options = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

def get_plots(tickers, selected_stock, start_date, end_date):
    if not tickers or not start_date or not end_date:
        return [None]*5

    data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')

    # Prepare return data
    price_data = pd.concat([data[t]['Close'] for t in tickers], axis=1)
    price_data.columns = tickers
    returns = price_data.pct_change().dropna()

    # Correlation Heatmap
    corr_fig = px.imshow(returns.corr(), text_auto=True, title="Correlation Heatmap of Returns")
    corr_json = json.dumps(corr_fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Histogram
    returns_long = returns.reset_index().melt(id_vars='Date', var_name='Stock', value_name='Daily Return')
    hist_fig = px.histogram(
        returns_long, x='Daily Return', facet_col='Stock', color='Stock', nbins=100,
        title='Daily Return Distributions', marginal='box', histnorm='probability'
    )
    hist_json = json.dumps(hist_fig, cls=plotly.utils.PlotlyJSONEncoder)

    if not selected_stock:
        return corr_json, hist_json, None, None, None

    stock_data = yf.download(selected_stock, start=start_date, end=end_date)
    stock_data['MA_20'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['MA_50'] = stock_data['Close'].rolling(window=50).mean()
    stock_data['RSI'] = RSIIndicator(close=stock_data['Close'], window=14).rsi()
    macd = MACD(close=stock_data['Close'])
    stock_data['MACD'] = macd.macd()
    stock_data['MACD_Signal'] = macd.macd_signal()
    stock_data['MACD_Diff'] = macd.macd_diff()

    ma_fig = px.line(stock_data, x=stock_data.index, y=['Close', 'MA_20', 'MA_50'], title=f"{selected_stock} - Moving Averages")
    rsi_fig = px.line(stock_data, x=stock_data.index, y='RSI', title=f"{selected_stock} - RSI (14)")
    macd_fig = px.line(stock_data, x=stock_data.index, y=['MACD', 'MACD_Signal', 'MACD_Diff'], title=f"{selected_stock} - MACD")

    return corr_json, hist_json, \
           json.dumps(ma_fig, cls=plotly.utils.PlotlyJSONEncoder), \
           json.dumps(rsi_fig, cls=plotly.utils.PlotlyJSONEncoder), \
           json.dumps(macd_fig, cls=plotly.utils.PlotlyJSONEncoder)


@app.route('/', methods=['GET', 'POST'])
def index():
    graphs = [None] * 5
    selected_stocks = ['AAPL', 'MSFT']
    selected_stock = 'AAPL'
    start_date = '2020-01-01'
    end_date = '2024-12-31'

    if request.method == 'POST':
        selected_stocks = request.form.getlist('stocks')
        selected_stock = request.form.get('indicator_stock')
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        graphs = get_plots(selected_stocks, selected_stock, start_date, end_date)

    return (
        
        stock_options==stock_options,
        selected_stocks==selected_stocks,
        selected_stock==selected_stock,
        start_date==start_date,
        end_date==end_date,
        graph1==graphs[0],
        graph2==graphs[1],
        graph3==graphs[2],
        graph4==graphs[3],
        graph5==graphs[4]
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)

