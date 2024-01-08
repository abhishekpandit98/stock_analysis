import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
from prophet import Prophet
from prophet.plot import plot_plotly

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

# Additional technical indicators
indicator_options = ["SMA", "RSI", "Bollinger Bands", "Moving Average Envelopes"]
selected_indicators = st.multiselect("Select Technical Indicators", indicator_options)

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

# Customizable technical indicators
if "SMA" in selected_indicators:
    sma_days = st.slider("Select number of Interval for SMA", min_value=1, max_value=365, step=1, value=30, format="%d")
    df["SMA"] = ta.sma(df["Close"], length=sma_days)

if "RSI" in selected_indicators:
    rsi_days = st.slider("Select number of Interval for RSI", min_value=1, max_value=365, step=1, value=14, format="%d")
    df["RSI"] = ta.rsi(df["Close"], length=rsi_days)

if "Bollinger Bands" in selected_indicators:
    bollinger_window = st.slider("Select Bollinger Bands Window", min_value=1, max_value=365, step=1, value=20, format="%d")

    # Compute Bollinger Bands using pandas_ta
    bb_result = ta.bbands(df["Close"], length=bollinger_window)

    # Use the correct column names for Bollinger Bands
    df["Bollinger Upper"] = bb_result["BBU_{}_2.0".format(bollinger_window)]
    df["Bollinger Lower"] = bb_result["BBL_{}_2.0".format(bollinger_window)]
    
if "Moving Average Envelopes" in selected_indicators:
    envelopes_window = st.slider("Select Moving Average Envelopes Window", min_value=1, max_value=365, step=1, value=20, format="%d")

    df["Upper Envelope"] = df["Close"].rolling(window=envelopes_window).mean() + 2 * df["Close"].rolling(window=envelopes_window).std()
    df["Lower Envelope"] = df["Close"].rolling(window=envelopes_window).mean() - 2 * df["Close"].rolling(window=envelopes_window).std()
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

# Plot selected technical indicators
for indicator in selected_indicators:
    if indicator == "SMA":
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], mode='lines', line=dict(color='blue'), name='SMA'), row=1, col=1)
    elif indicator == "RSI":
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', line=dict(color='green'), name='RSI'), row=3, col=1)
    elif indicator == "Bollinger Bands":
        fig.add_trace(go.Scatter(x=df.index, y=df['Bollinger Upper'], mode='lines', line=dict(color='orange'), name='Bollinger Upper'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Bollinger Lower'], mode='lines', line=dict(color='purple'), name='Bollinger Lower'), row=1, col=1)
    elif indicator == "Moving Average Envelopes":
        fig.add_trace(go.Scatter(x=df.index, y=df['Upper Envelope'], mode='lines', line=dict(color='orange'), name='Upper Envelope'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Lower Envelope'], mode='lines', line=dict(color='purple'), name='Lower Envelope'), row=1, col=1)
# Set layout
fig.update_layout(title='Stock Analysis with Candlestick and Technical Indicators',
                  xaxis_title='Date',
                  yaxis_title='Price',
                  xaxis_rangeslider_visible=False)

# Show the plot
st.plotly_chart(fig)

try:
        # MACD parameters input
        st.subheader("MACD Analysis")
        fast_period, slow_period, signal_period = st.slider("Fast Period", 1, 50, 12), st.slider("Slow Period", 1, 50, 26), st.slider("Signal Period", 1, 50, 9)

        # Calculating MACD
        macd = ta.macd(df["Close"], fast=fast_period, slow=slow_period, signal=signal_period)
        macd.rename(columns={"MACD_{}_{}_{}".format(fast_period, slow_period, signal_period): "MACD",
                        "MACDh_{}_{}_{}".format(fast_period, slow_period, signal_period): "HISTOGRAM",
                        "MACDs_{}_{}_{}".format(fast_period, slow_period, signal_period): "SIGNAL"}, inplace=True)

        # Plotting MACD chart
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True)
        macd_plot = go.Scatter(x=macd.index, y=macd["MACD"], name="MACD", mode="lines", marker=dict(color='blue'))
        macd_signal = go.Scatter(x=macd.index, y=macd["SIGNAL"], name="Signal", mode="lines", marker=dict(color='green'))
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
# Display historical data
st.subheader(f"Showing historical data for {ticker} for the selected period: {selected_period}")

# Check if columns exist before trying to access them
display_columns = ["Open", "High", "Low", "Close"]
if "RSI" in selected_indicators:
    display_columns.append("RSI")
if "SMA" in selected_indicators:
    display_columns.append("SMA")
if "Bollinger Bands" in selected_indicators:
    display_columns.extend(["Bollinger Upper", "Bollinger Lower"])
if "Moving Average Envelopes" in selected_indicators:
    display_columns.extend(["Upper Envelope", "Lower Envelope"])

# Display the filtered DataFrame
st.write(df[display_columns])

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

# Display the last 90 days of forecasted data in a table without the index
st.write("### Last 90 Days Forecasted Data")
last_90_days_predicted_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].iloc[-90:].rename(columns={'ds': 'Date', 'yhat': 'Predicted', 'yhat_lower': 'Lower Bound', 'yhat_upper': 'Upper Bound'}).reset_index(drop=True)
st.table(last_90_days_predicted_data)