import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
from prophet import Prophet

# Set Streamlit theme
st.set_page_config(page_title="Stock Analysis App", page_icon="📈", layout="wide")

# Title and user input
st.title("Stock Analysis App")
ticker = st.text_input("Enter the Ticker", "TCS.NS")

# Data period and interval
selected_period = st.selectbox("Select Data Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"])
interval_options = {"1d": ["1m", "2m", "5m", "15m", "30m", "1h"], "5d": ["1m", "2m", "5m", "15m", "30m", "1h", "1d"],"1mo": ["2m", "5m", "15m", "30m", "1h", "1d", "1wk"],
    "3mo": ["1h", "1d", "1wk", "1mo"],
    "6mo": ["1h", "1d", "1wk", "1mo"],
    "1y": ["1h", "1d", "1wk", "1mo"],
    "2y": ["1h", "1d", "1wk", "1mo"],
    "5y": ["1d", "1wk", "1mo"],
    "10y": ["1d", "1wk", "1mo"],
    "ytd": ["1d", "1wk", "1mo"],
    "max": ["1d", "1wk", "1mo"]}
selected_interval = st.selectbox("Select Time Interval", interval_options.get(selected_period, []))
days = st.slider("Select number of Interval for SMA and RSI", min_value=1, max_value=365, step=1, value=30, format="%d")
st.write(f"Selected number of Interval for SMA and RSI: {days}")

# Fetch stock data
try:
    data = yf.Ticker(ticker)
    df = data.history(period=selected_period, interval=selected_interval)
    df.reset_index(inplace=True)
    date_column_name = 'Datetime' if selected_interval in ["1m", "2m", "5m", "15m", "30m", "1h"] else 'Date'
    df['Date'] = df[date_column_name]
    df.set_index(pd.DatetimeIndex(df['Date']), inplace=True)
    column_to_drop = ["Date", "Dividends", "Stock Splits"]
    df = df.drop(columns=column_to_drop)
except Exception as e:
    st.error(f"Error fetching data")
    st.stop()

# Calculating SMA and RSI
df["SMA"] = ta.sma(df["Close"], length=days)
df["RSI"] = ta.rsi(df["Close"], length=days)

# Plotting candle chart
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.6, 0.2, 0.2])

# Add candlestick chart to the main subplot (row 1)
fig.add_trace(go.Candlestick(x=df.index,
                             open=df['Open'],
                             high=df['High'],
                             low=df['Low'],
                             close=df['Close'],
                             name='Candlestick'), row=1, col=1)

# Add volume to the second subplot (row 2)
fig.add_trace(go.Bar(x=df.index,
                     y=df['Volume'],
                     marker=dict(color='blue'),
                     name='Volume'), row=2, col=1)

# Add SMA to the secondary y-axis
fig.add_trace(go.Scatter(x=df.index,
                         y=df['SMA'],
                         mode='lines',
                         line=dict(color='blue'),
                         name='SMA'), row=1, col=1)

# Add RSI to the secondary subplot (row 2)
fig.add_trace(go.Scatter(x=df.index,
                         y=df['RSI'],
                         mode='lines',
                         line=dict(color='green'),
                         name='RSI'), row=3, col=1)

# Set layout
fig.update_layout(title='Stock Analysis with Candlestick and RSI',
                  xaxis_title='Date',
                  yaxis_title='Price',
                  xaxis_rangeslider_visible=False)

# Show the plot
st.plotly_chart(fig)

try:
        # MACD parameters input
        st.subheader("MACD Analysis")
        fast_period = st.slider("Select Fast Period for MACD", min_value=1, max_value=50, value=12)
        slow_period = st.slider("Select Slow Period for MACD", min_value=1, max_value=50, value=26)
        signal_period = st.slider("Select Signal Period for MACD", min_value=1, max_value=50, value=9)

        # Calculating MACD
        macd = ta.macd(df["Close"], fast=fast_period, slow=slow_period, signal=signal_period)
        macd.rename(columns={"MACD_{}_{}_{}".format(fast_period, slow_period, signal_period): "MACD",
                        "MACDh_{}_{}_{}".format(fast_period, slow_period, signal_period): "HISTOGRAM",
                        "MACDs_{}_{}_{}".format(fast_period, slow_period, signal_period): "SIGNAL"}, inplace=True)

        # Plotting MACD chart
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True)
        macd_plot = go.Scatter(x=macd.index, y=macd["MACD"], name="MACD", mode="lines", marker=dict(color='blue'))
        macd_signal = go.Scatter(x=macd.index, y=macd["SIGNAL"], name="Signal", mode="lines", marker=dict(color='black'))
        colors = ['rgb(0, 128, 0)' if v >= 0 else 'rgb(255, 0, 0)' for v in macd["HISTOGRAM"]]
        macd_hist = go.Bar(x=macd.index, y=macd["HISTOGRAM"], name="Histogram", marker=dict(color=colors))

        fig2.add_trace(go.Candlestick(x=df.index,
                                open=df['Open'],
                                high=df['High'],
                                low=df['Low'],
                                close=df['Close'],
                                name='Candlestick'), row=1, col=1)
        fig2.add_trace(macd_plot, row=2, col=1)
        fig2.add_trace(macd_signal, row=2, col=1)
        fig2.add_trace(macd_hist, row=2, col=1)
        fig2.update_layout(title='Stock Analysis with Candlestick and MACD',
                        xaxis_title='Date',
                        yaxis_title='Price',
                        xaxis_rangeslider_visible=False)

        # Show the MACD chart
        st.plotly_chart(fig2)
except Exception as e:
    st.error("Error. Please try again with different input, such as changing the Time Interval or Data Period.")
    st.stop()
    
# Display historical data
st.subheader(f"Showing historical data for {ticker} for the selected period: {selected_period}")
st.write(df[["Open", "High", "Low", "Close", "RSI", "SMA"]])

# Fetch long historical data for prediction
def fetch_long_historical_data(ticker, years=5):
    data = yf.Ticker(ticker)
    end_date = pd.to_datetime("today")
    start_date = end_date - pd.DateOffset(years=years)
    df_long = data.history(start=start_date, end=end_date)
    return df_long

df_long = fetch_long_historical_data(ticker, years=5)

# Predict stock prices using Prophet on df_long
df_long['ds'] = df_long.index
df_long['y'] = df_long['Close']
df_long['ds'] = df_long['ds'].dt.tz_localize(None)
prophet_df = df_long[['ds', 'y']].reset_index(drop=True)
model = Prophet(daily_seasonality=False)
model.fit(prophet_df)
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)

# Plot the forecast using Plotly
st.subheader("Stock Price Prediction:")
fig = go.Figure()

# Plot the historical data
fig.add_trace(go.Scatter(x=df_long['ds'], y=df_long['y'], mode='lines', name='Historical Data'))

# Plot the forecasted data
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', line=dict(color='green'), name='Forecast'))

# Fill the area between the upper and lower bounds of the forecast
fig.add_trace(go.Scatter(
    x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
    y=pd.concat([forecast['yhat_upper'], forecast['yhat_lower'][::-1]]),
    fill='toself',
    fillcolor='rgba(0,100,80,0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    name='Forecast Range'
))

# Customize layout
fig.update_layout(
    title='Stock Price Prediction',
    xaxis_title='Date',
    yaxis_title='Price',
    xaxis_rangeslider_visible=False
)

# Show the plot
st.plotly_chart(fig)
