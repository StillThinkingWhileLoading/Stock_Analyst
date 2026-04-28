from typing import TypedDict


class BullBearState(TypedDict):
    ticker: str
    market_region: str
    time_series_data: dict
    news_analysis: str
    bull_analysis: str
    bull_analysis_raiting: str
    bear_analysis: str
    bear_analysis_raiting: str
    financial_analysis: str
    financial_analysis_raiting: str
