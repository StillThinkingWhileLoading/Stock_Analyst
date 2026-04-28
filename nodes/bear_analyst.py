from state import BullBearState
from nodes.base import BaseNode
from tools import extract_rating, trim_to_60_days


class BearAnalystNode(BaseNode):
    async def __call__(self, state: BullBearState) -> dict:
        recent_data = trim_to_60_days(state["time_series_data"])

        prompt = f"""
System Role: Senior Global Equity Strategist (20y exp). Expert in OHLCV and Sentiment synthesis. Your task: Identify high-conviction bearish narratives where price action meets market psychology.

Context:

Asset: {state['ticker']}

Data: {recent_data} (60-Day OHLCV)

News: {state['news_analysis']}

Task: Produce a formal Bear Case Synthesis. Use these sections:

1. Price Structure & Volume

Identify the primary trend (LH/LL), net % change, and deterioration velocity (worst 5-day decline).

Pinpoint "Structural Weakness": Dates where key resistance levels broke or support was lost.

Analyze "Distribution Footprints": High-volume DOWN days vs. low-volume bounces (liquidation).

Note any "Rejection" (Price-Volume Divergence where price fails to hold gains on high volume).

2. News-Price Confluence

The Narrative Bridge: Link specific news headlines to price declines or high-volume breakdowns by date.

Sentiment Deterioration: Note if the price fell or weakened despite neutral/bullish news (indicating overwhelming underlying selling).

Identify the primary news-driven catalyst justifying a forward-looking valuation markdown.

3. Targets & Momentum

Assess momentum (decelerating vs. accelerating downside) and identify the critical support level (the "floor to break").

Set a 4-6 week price target based on technical swing lows or measured moves.

4. Conviction Summary

Confidence Rating: X / 10 (1-4 scale: 1-4 = Strong Bear, 5-6 = Neutral, 7-10 = Bull).

For this BEARISH analysis, provide a rating between 1-4 if the bear case is compelling, or higher (5-6 or 7-10) if the case is weak or unconvincing despite the bearish framing.

Justification: Provide exactly 3 bullet points. Requirement: Each bullet MUST link a specific Price/Volume event to a News Catalyst (e.g., "Price -5% on [Date] following [News Item] on 2x average volume").

Strict Rules:

Evidence: Cite specific prices, dates, and volumes. No vague generalizations.

Tone: Purely Bearish. Do not present bullish counterarguments.

Style: Professional, global terminology (e.g., "Closing Price").

Disclaimer: End with: "This analysis is for informational purposes only and does not constitute personalized financial advice."
"""

        response = await self.model.ainvoke(prompt)
        rating = extract_rating(response.content)
        return {"bear_analysis": response.content, "bear_analysis_raiting": rating}
