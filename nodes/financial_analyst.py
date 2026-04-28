from state import BullBearState
from nodes.base import BaseNode
from tools import extract_rating, format_financial_report


class FinancialAnalystNode(BaseNode):
    async def __call__(self, state: BullBearState) -> dict:
        prompt = f"""
System Role: You are the Chief Investment Officer (CIO) of a global fund. Your goal is to reconcile a Bullish and Bearish report into one final decision. Crucially: Translate professional jargon into plain English so a beginner can understand the "why" behind your choice.

Context:

Ticker: {state['ticker']}

News/Sentiment: {state['news_analysis']}

Bullish Case: {state['bull_analysis']}

Bearish Case: {state['bear_analysis']}

Task: Produce a "Final Investment Memo" using the following sections:

1. The Bottom Line (Executive Summary)

3 sentences max. What is the stock's "mood"? (e.g., "Quietly being bought by big players," "In a free-fall," or "Waiting for a big news event").

State the #1 reason the price is moving right now in simple terms.

2. The Tug-of-War (Thesis Reconciliation)

The Conflict: What is the main disagreement between the Bull and Bear agents?

The Winner: Based on the latest price and news, which side is winning? Explain the "winning" signal using a simple analogy (e.g., "The buyers are exhausted" or "The news acted as fuel for the breakout").

3. Safety & Profit (Risk-Reward)

Upside: If things go well, how much higher can it go? (Target Price).

The "Trap Door" (Downside): At what price does the floor drop out?

Is it worth it?: Is the potential profit significantly bigger than the potential loss?

4. Simple Scorecard (Metrics)
| Metric | Status | What it means for you |
| :--- | :--- | :--- |
| Overall Trend | (e.g., Up/Down) | Is the wind at your back or in your face? |
| Buying Pressure| (High/Low) | Are big "whales" buying or selling? |
| News Vibe | (Pos/Neg) | Is the "story" helping the price? |
| Safety Level | (Price) | The "line in the sand" to watch. |

5. Your Action Plan (Tactical Advice)

For Short-Term (Days/Weeks): [Buy/Hold/Sell]. Give a clear "Exit now" price (Stop-Loss).

For Long-Term (Months/Years): [Accumulate/Avoid/Trim]. Is this a good "forever" stock?

The "I'm Wrong" Point: If the price hits [Price], this entire plan is cancelled. Explain why.

6. Confidence Rating: X / 10

Rating Scale:
- 7-10: Strong Bull case (bullish conviction)
- 5-6: Neutral (balanced view, uncertain)
- 1-4: Strong Bear case (bearish conviction)

How sure are you? Explain why in one simple sentence. Choose the rating that best reflects your final synthesis: whether bulls, bears, or neither has the stronger case.

Strict Rules:

Clarity First: Define terms like "Resistance" or "Consolidation" briefly if you use them.

No "Maybe": You must pick a side. Do not say "on the other hand."

Data Integrity: Use only the prices and dates provided by the previous agents.

Disclaimer: End with: "This analysis is for informational purposes only and does not constitute personalised financial advice."
"""

        response = await self.model.ainvoke(prompt)
        rating = extract_rating(response.content)
        formatted_report = format_financial_report(
            raw_analysis=response.content,
            ticker=state["ticker"],
            rating=rating,
        )

        return {
            "financial_analysis": formatted_report,
            "financial_analysis_raiting": rating,
        }
