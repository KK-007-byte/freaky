import yfinance as yf
import seaborn as sns
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import MACD
import plotly.express as px
import plotly.figure_factory as ff

# --- Sidebar Inputs ---
st.title("📊 Stock Return Analytics Dashboard")

st.sidebar.header("Select Parameters")
tickers = st.sidebar.multiselect(
    "Choose Stocks",
    ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
    default=['AAPL', 'MSFT']
)
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))

# --- Data Loader ---
@st.cache_data
def load_data(tickers, start, end):
    df = yf.download(tickers, start=start, end=end, group_by='ticker')
    return df

data = load_data(tickers, start_date, end_date)

# --- Return Calculations ---
@st.cache_data
def get_returns(data, tickers):
    price_data = pd.concat([data[ticker]['Close'] for ticker in tickers], axis=1)
    price_data.columns = tickers
    returns = price_data.pct_change().dropna()
    return returns

returns = get_returns(data, tickers)

# --- Correlation Heatmap ---
if len(tickers) > 1:
    st.subheader("📈 Correlation Heatmap of Daily Returns")
    corr = returns.corr().round(2)
    heatmap = ff.create_annotated_heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        annotation_text=corr.values,
        colorscale='Viridis',
        showscale=True
    )
    st.plotly_chart(heatmap)

# --- Histogram of Returns ---
st.subheader("📉 Histogram of Daily Return Distributions")
returns_long = returns.reset_index().melt(id_vars='Date', var_name='Stock', value_name='Daily Return')

hist_fig = px.histogram(
    returns_long,
    x='Daily Return',
    facet_col='Stock',
    color='Stock',
    nbins=100,
    title='Daily Return Distributions by Stock',
    marginal='box',
    histnorm='probability'
)
st.plotly_chart(hist_fig)

# --- Indicator Calculation ---
def add_indicators(df):
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['RSI'] = RSIIndicator(close=df['Close'], window=14).rsi()
    macd = MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Diff'] = macd.macd_diff()
    return df

# --- Show indicators for one selected stock ---
if tickers:
    st.subheader("📊 Technical Indicators for Selected Stock")
    selected_stock = st.selectbox("Select one stock", tickers)
    stock_data = yf.download(selected_stock, start=start_date, end=end_date)
    stock_data = add_indicators(stock_data)

    fig = px.line(stock_data, x=stock_data.index, y=['Close', 'MA_20', 'MA_50'], title=f"{selected_stock} Price with Moving Averages")
    st.plotly_chart(fig)

    fig_rsi = px.line(stock_data, x=stock_data.index, y='RSI', title=f"{selected_stock} RSI (14)")
    st.plotly_chart(fig_rsi)

    fig_macd = px.line(stock_data, x=stock_data.index, y=['MACD', 'MACD_Signal', 'MACD_Diff'], title=f"{selected_stock} MACD")
    st.plotly_chart(fig_macd)

st.caption("📌 Built with Streamlit, yFinance, TA, and Plotly")





