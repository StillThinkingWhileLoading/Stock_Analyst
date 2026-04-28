from .fetch_stock_data import FetchStockDataNode
from .news_analyst import NewsAnalystNode
from .bull_analyst import BullAnalystNode
from .bear_analyst import BearAnalystNode
from .financial_analyst import FinancialAnalystNode

fetch_stock_data = FetchStockDataNode()
news_analyst = NewsAnalystNode()
bull_analyst = BullAnalystNode()
bear_analyst = BearAnalystNode()
financial_analyst = FinancialAnalystNode()

__all__ = [
    "fetch_stock_data",
    "news_analyst",
    "bull_analyst",
    "bear_analyst",
    "financial_analyst",
]
