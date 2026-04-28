from state import BullBearState
from nodes.base import BaseNode
from tools import extract_rating, trim_to_60_days


class BullAnalystNode(BaseNode):
    async def __call__(self, state: BullBearState) -> dict:
        recent_data = trim_to_60_days(state["time_series_data"])

        prompt = f"""
System Role: Senior Global Equity Strategist (20y exp). Expert in OHLCV and Sentiment synthesis. Your task: Identify high-conviction bullish narratives where price action meets market psychology.

Context:

Asset: {state['ticker']}

Data: {recent_data} (60-Day OHLCV)

News: {state['news_analysis']}

Task: Produce a Bull Case Synthesis. Use these sections:

1. Price Structure & Volume

Identify trend (HH/HL), net % change, and "Breakout Velocity" (best 5-day gain).

Pinpoint "Structural Strength": dates of key support defense or consolidation.

Analyze "Institutional Footprints": high-volume UP days and evidence of accumulation (low volume on pullbacks).

Note any Price-Volume Divergence (absorption).

2. News-Price Confluence

The Narrative Bridge: Link specific news headlines to price gaps or breakouts by date.

Sentiment Resilience: Note if the price held or rose despite neutral/bearish news.

Identify the primary catalyst justifying a valuation re-rating.

3. Targets & Momentum

Assess momentum (accelerating/basing) and identify "Final Boss" resistance.

Set a 4-6 week price target based on technical swing highs.

4. Conviction Summary

Confidence Rating: X / 10 (7-10 scale: 7-10 = Strong Bull, 5-6 = Neutral, 1-4 = Bear).

For this BULLISH analysis, provide a rating between 7-10 if the bull case is compelling, or lower (5-6 or 1-4) if the case is weak or unconvincing despite the bullish framing.

Justification: 3 bullets. Requirement: Every bullet MUST link a specific Price/Volume event to a News Catalyst (e.g., "Price +5% on [Date] following [News Item]").

Strict Rules:

Evidence: Cite specific prices, dates, and volumes. No generalizations.

Tone: Purely Bullish. No bearish counterarguments.

Style: Professional, global terminology (e.g., "Closing Price").

Disclaimer: End with: "This analysis is for informational purposes only and does not constitute personalized financial advice."
"""

        response = await self.model.ainvoke(prompt)
        rating = extract_rating(response.content)
        return {"bull_analysis": response.content, "bull_analysis_raiting": rating}
