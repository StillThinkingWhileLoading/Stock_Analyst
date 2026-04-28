import yfinance as yf
from state import BullBearState


class FetchStockDataNode:
    async def __call__(self, state: BullBearState) -> dict:
        ticker = state["ticker"]

        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")

            if hist.empty:
                raise ValueError(f"No trading data found for ticker '{ticker}'. Please verify the ticker symbol is correct.")

            time_series = {}
            for date, row in hist.iterrows():
                date_str = date.strftime("%Y-%m-%d")
                time_series[date_str] = {
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                }

            if not time_series:
                raise ValueError(f"Could not process trading data for {ticker}")

            return {"time_series_data": time_series}

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error fetching stock data for {ticker}: {str(e)}")
