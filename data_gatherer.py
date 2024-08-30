import yfinance as yf
from yfinance.exceptions import YFException
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests


def collect_evidence(stocks: List[str], start_date: str, end_date: str) -> Dict[str, Dict[str, Any]]:
    """
    Gather financial evidence (stock data) from Yahoo Finance.

    Args:
        stocks (List[str]): List of stock symbols to investigate.
        start_date (str): Start date for data collection in 'YYYY-MM-DD' format.
        end_date (str): End date for data collection in 'YYYY-MM-DD' format.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary containing price and news data for each stock.

    Raises:
        Exception: If no data could be retrieved for any of the stocks.
    """
    evidence_locker = {}
    for stock in stocks:
        logging.info(f"🔍 Investigating {stock}...")
        try:
            # Create a Ticker object
            ticker = yf.Ticker(stock)

            # Fetch the data
            data = ticker.history(start=start_date, end=end_date)

            # If data is empty, raise an exception
            if data.empty:
                raise ValueError(f"No data available for {stock}")

            # Fetch news data
            news = ticker.news

            # Filter news data for the past month
            news_end_date = datetime.now()
            news_start_date = news_end_date - timedelta(days=30)
            filtered_news = [
                article for article in news
                if news_start_date.timestamp() <= article['providerPublishTime'] <= news_end_date.timestamp()
            ]

            # Store the data and news
            evidence_locker[stock] = {
                'price_data': data,
                'news_data': filtered_news
            }

            logging.info(f"✅ Evidence for {stock} securely stored!")
        except YFException as e:
            logging.error(f"🚫 YFinance error for {stock}: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"🚫 Network error for {stock}: {e}")
        except ValueError as e:
            logging.error(f"🚫 Data error for {stock}: {e}")
        except Exception as e:
            logging.error(f"🚫 Unexpected error for {stock}: {e}")

    if not evidence_locker:
        raise Exception("No data could be retrieved for any of the stocks.")

    return evidence_locker
