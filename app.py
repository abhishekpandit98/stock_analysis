import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import pandas_ta as ta
import mplfinance as mf
import streamlit as st
import matplotlib.pyplot as plt

st.title("Stock Analysis")
ticker = st.text_input("Enter the Ticker", "TCS.NS")
period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
selected_period = st.selectbox("Select Data Period", period_options)

interval_options = ["1m", "2m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
selected_interval = st.selectbox("Select Data Interval", interval_options)


days = st.slider("select number of Interval for SMA and RSI", min_value=1, max_value=365, step=1, value=30, format="%d")
# Use the selected number of days in your analysis
st.write(f"Selected number of Interval for SMA and RSI: {days}")

# Fetch stock data
data = yf.Ticker(ticker)
df = data.history(period=selected_period,interval=selected_interval)
df.reset_index(inplace=True)
df.set_index(pd.DatetimeIndex(df["Datetime"]), inplace=True)

column_to_drop =["Datetime","Dividends","Stock Splits"]
df = df.drop(columns=column_to_drop )
df["SMA"] = ta.sma(df["Close"], length=days)
df["RSI"] = ta.rsi(df["Close"], length=days)

st.write(f"Showing historical data for {ticker} for the selected period: {selected_period}")
st.write(df)

# Plotting candlestick chart using mplfinance
fig_candle, ax = mf.plot(df, type="candle", volume=True, returnfig=True)
# Display the mplfinance chart using st_mpl_chart
st.pyplot(fig_candle.figure)

# Plotting SMA and Close
fig_sma_close = plt.figure()
plt.plot(df["SMA"].dropna(), label='SMA', color='blue')
plt.plot(df["Close"].dropna(), color='red', label='Close Price')
plt.xlabel('Date')
plt.xticks(rotation=45)
plt.ylabel('SMA and Close')
plt.title('SMA and Close Chart')
plt.legend()

# Display the Matplotlib chart using st.pyplot
st.pyplot(fig_sma_close)

# Plotting RSI
fig_rsi = plt.figure()
plt.plot(df["RSI"].dropna(), color='red', label='RSI')
plt.xlabel('Date')
plt.ylabel('RSI')
plt.xticks(rotation=45)
plt.title('RSI Chart')
plt.legend()

# Display the Matplotlib chart using st.pyplot
st.pyplot(fig_rsi)


