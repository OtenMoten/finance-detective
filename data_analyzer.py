import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple
import multiprocessing


def calculate_roc(price_data: pd.DataFrame, n: int = 12) -> pd.Series:
    """
    Calculate the Price Rate of Change (ROC) for the entire date range.

    Args:
        price_data (pd.DataFrame): DataFrame containing the 'Close' price column.
        n (int): The number of periods to use for ROC calculation. Default is 12.

    Returns:
        pd.Series: A series containing the ROC values for each date in the range.
    """
    return ((price_data['Close'] - price_data['Close'].shift(n)) / price_data['Close'].shift(n)) * 100


def analyze_stock(stock_data_tuple: Tuple[str, Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
    """
    Analyze the financial data for a single stock.

    Args:
        stock_data_tuple (Tuple[str, Dict[str, Any]]): Tuple containing stock symbol and its data.

    Returns:
        Tuple[str, Dict[str, Any]]: Tuple containing stock symbol and analyzed data for the stock.
    """
    stock, stock_data = stock_data_tuple
    price_data = stock_data['price_data']
    news_data = stock_data['news_data']

    # Calculate daily returns
    price_data['Daily Return'] = price_data['Close'].pct_change()

    # Calculate volatility (standard deviation of returns)
    volatility = price_data['Daily Return'].std()

    # Calculate average daily return
    avg_daily_return = price_data['Daily Return'].mean()

    # Calculate Sharpe Ratio (assuming risk-free rate of 0 for simplicity)
    # Use actual number of trading days for more precise annualization
    trading_days = len(price_data)
    sharpe_ratio = (avg_daily_return / volatility) * np.sqrt(trading_days)

    # Calculate MACD (Moving Average Convergence Divergence)
    exp12 = price_data['Close'].ewm(span=12, adjust=False).mean()
    exp26 = price_data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()

    # Calculate Bollinger Bands
    price_data['SMA20'] = price_data['Close'].rolling(window=20).mean()
    price_data['UpperBand'] = price_data['SMA20'] + (price_data['Close'].rolling(window=20).std() * 2)
    price_data['LowerBand'] = price_data['SMA20'] - (price_data['Close'].rolling(window=20).std() * 2)

    # Calculate average Bollinger Bands gap
    price_data['BB_Gap'] = price_data['UpperBand'] - price_data['LowerBand']
    avg_bb_gap = price_data['BB_Gap'].mean()

    # Calculate RSI (Relative Strength Index)
    delta = price_data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    price_data['RSI'] = 100 - (100 / (1 + rs))

    # Calculate Average True Range (ATR)
    high_low = price_data['High'] - price_data['Low']
    high_close = np.abs(price_data['High'] - price_data['Close'].shift())
    low_close = np.abs(price_data['Low'] - price_data['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(window=14).mean().iloc[-1]

    # Calculate ROC for the entire range
    price_data['ROC'] = calculate_roc(price_data)

    # Calculate average ROC and latest ROC
    avg_roc = price_data['ROC'].mean()
    latest_roc = price_data['ROC'].iloc[-1]

    return stock, {
        'latest_price': price_data['Close'].iloc[-1],
        'volatility': volatility,
        'avg_daily_return': avg_daily_return,
        'sharpe_ratio': sharpe_ratio,
        'macd': macd.iloc[-1],
        'macd_signal': signal.iloc[-1],
        'upper_band': price_data['UpperBand'].iloc[-1],
        'lower_band': price_data['LowerBand'].iloc[-1],
        'avg_bb_gap': avg_bb_gap,
        'rsi': price_data['RSI'].iloc[-1],
        'atr': atr,
        'avg_roc': avg_roc,
        'latest_roc': latest_roc,
        'price_data': price_data[['Close', 'Daily Return', 'RSI', 'UpperBand', 'LowerBand', 'ROC']],
        'macd_data': pd.DataFrame({'MACD': macd, 'Signal': signal}),
    }


def analyze_clues(evidence: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Analyze the gathered financial evidence to uncover insights.

    Args:
        evidence (Dict[str, Dict[str, Any]]): Dictionary containing stock data for multiple stocks.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary containing analyzed data for each stock.
    """
    analyzed_data = {}
    with multiprocessing.Pool() as pool:
        results = pool.map(analyze_stock, evidence.items())

    for stock, result in results:
        analyzed_data[stock] = result
        logging.info(f"✅ Analysis complete for {stock}!")

    return analyzed_data
