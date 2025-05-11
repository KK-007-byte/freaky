


import yfinance as yf
import seaborn as sns
import ta
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
import streamlit as st
tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
data = yf.download(tickers, start='2018-01-01', end='2024-12-31')
data.to_csv('stock_data.csv')


# In[19]:


returns = data.pct_change().dropna()



sns.heatmap(returns.corr(), annot=True, cmap='coolwarm')



# In[23]:


def add_moving_averages(df, windows=[20, 50, 100]):
    for window in windows:
        df[f'MA_{window}'] = df['Close'].rolling(window=window).mean()
    return df



def add_rsi(df, window=14):
    rsi = RSIIndicator(close=df['Close'], window=window)
    df['RSI'] = rsi.rsi()
    return df




def add_macd(df):
    macd = MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Diff'] = macd.macd_diff()
    return df


# In[26]:


def compute_indicators(ticker):
    df = yf.download(ticker, start='2020-01-01', end='2024-12-31')
    df = df[['Close']]
    df = add_moving_averages(df)
    df = add_rsi(df)
    df = add_macd(df)
    return df.dropna()


# In[27]:


def compute_indicators(ticker):
    df = yf.download(ticker, start='2020-01-01', end='2024-12-31')
    df = df[['Close']]
    df = add_moving_averages(df)
    df = add_rsi(df)
    df = add_macd(df)
    return df.dropna()




corr = returns.corr().round(2)

fig = ff.create_annotated_heatmap(
    z=corr.values,
    x=corr.columns.tolist(),
    y=corr.index.tolist(),
    annotation_text=corr.values,
    colorscale='Viridis',
    showscale=True
)

fig.update_layout(title='Correlation Heatmap of Daily Returns')
fig.show()

returns_long = returns.reset_index().melt(var_name='Stock', value_name='Daily Return')

fig = px.histogram(
    returns_long,
    x='Daily Return',
    facet_col='Stock',
    color='Stock',
    nbins=100,
    title='Daily Return Distributions (by Stock)',
    marginal='box',
    histnorm='probability'
)
fig.update_layout(showlegend=False)
fig.show()


# In[34]:



# In[35]:




# In[36]:




st.title("📊 Stock Return Analysis")

# Sidebar
st.sidebar.header("Select Parameters")
tickers = st.sidebar.multiselect("Choose Stocks", ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'], default=['AAPL', 'MSFT'])
start_date = st.sidebar.date_input("Start Date", pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input("End Date", pd.to_datetime('2024-12-31'))

# Load data
@st.cache_data
def load_data(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)
    return data

data = load_data(tickers, start_date, end_date)
returns = data.pct_change().dropna()

# 📌 Correlation Heatmap
if len(tickers) > 1:
    st.subheader("Correlation Heatmap of Daily Returns")
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

# 📌 Histogram of Daily Returns
st.subheader("Histogram of Daily Return Distributions")


hist_fig = px.histogram(
    returns,
    x=('Close','AAPL'),
    facet_col=('Volume', 'AAPL'),
    color=('Volume', 'AAPL'),
    nbins=100,
    title='Daily Return Distributions',
    histnorm='probability'
)

st.plotly_chart(hist_fig)

st.caption("Built with Streamlit & Plotly")


# In[ ]:




