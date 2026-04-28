import asyncio
import yfinance as yf
from state import BullBearState
from nodes.base import BaseNode


class NewsAnalystNode(BaseNode):
    async def __call__(self, state: BullBearState) -> dict:
        await asyncio.sleep(1)
        news_data = await self._fetch_news(state)

        prompt = f"""You are a Financial Research Assistant. Below is a list of recent news items for {state['ticker']}.

Cross-reference the summaries to identify recurring themes (e.g., M&A rumors, earnings growth).

Highlight any 'New Laws' or regulatory shifts mentioned.

Provide a 'Consensus Sentiment' based on the overall tone of the provided reports.

NEWS DATA: {news_data}"""

        response = await self.model.ainvoke(prompt)
        return {"news_analysis": response.content}

    async def _fetch_news(self, state: BullBearState) -> list:
        ticker = state["ticker"]

        try:
            stock = yf.Ticker(ticker)
            news = stock.news

            if not news:
                return [{"title": "No recent news available", "summary": f"No recent news found for {ticker}", "source": "N/A", "link": "", "published_date": ""}]

            extracted = []
            for item in news[:15]:
                extracted.append({
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "source": item.get("source", ""),
                    "link": item.get("link", ""),
                    "published_date": item.get("published_utc", ""),
                })

            return extracted if extracted else [{"title": "Limited news data", "summary": f"Insufficient news data for {ticker}", "source": "N/A", "link": "", "published_date": ""}]

        except Exception as e:
            return [{"title": "News fetch warning", "summary": f"Limited news availability: {str(e)[:100]}", "source": "N/A", "link": "", "published_date": ""}]
