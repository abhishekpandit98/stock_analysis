# Stock Analysis App

[Stock Analysis App](https://abhishekpandit98-stock-analysis-app-hnre6x.streamlit.app/)

This web application provides a comprehensive analysis of stock data, allowing users to visualize candlestick charts, moving averages, RSI (Relative Strength Index), MACD (Moving Average Convergence Divergence), and predict future stock prices using the Prophet forecasting model.

## Getting Started
To access the app, click [here](https://abhishekpandit98-stock-analysis-app-hnre6x.streamlit.app/).

## Code Overview
The code for this project is written in Python using the Streamlit framework for the web interface. Additionally, it utilizes various libraries for data analysis and visualization, including yfinance, pandas, numpy, plotly, pandas_ta, and Prophet.

### Requirements
Make sure to install the required Python libraries by running:

```bash
pip install -r requirements.txt
```
### Running the App
To run the app locally, execute the following command in your terminal:
```bash
streamlit run app.py
```

### User Guide
1. Enter the stock ticker symbol in the designated input field.
2. Select the desired data period and time interval.
3. Adjust the number of intervals for SMA (Simple Moving Average) and RSI (Relative Strength Index).
4. Explore the candlestick chart, volume, SMA, and RSI plots for the selected stock.
5. Analyze MACD (Moving Average Convergence Divergence) with customizable parameters.
6. View historical data, including Open, High, Low, Close, RSI, and SMA.
7. Access stock price predictions using the Prophet forecasting model for an extended historical period.
### Disclaimer
This application is for educational and informational purposes only. It does not constitute financial advice, and users should conduct thorough research or consult with financial professionals before making investment decisions.
