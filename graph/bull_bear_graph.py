from langgraph.graph import StateGraph, START, END

from state import BullBearState
from nodes import (
    fetch_stock_data,
    news_analyst,
    bull_analyst,
    bear_analyst,
    financial_analyst,
)

graph = StateGraph(BullBearState)

graph.add_node("fetch_stock_data", fetch_stock_data)
graph.add_node("news_analyst", news_analyst)
graph.add_node("bull_analyst", bull_analyst)
graph.add_node("bear_analyst", bear_analyst)
graph.add_node("financial_analyst", financial_analyst)

graph.add_edge(START, "fetch_stock_data")
graph.add_edge(START, "news_analyst")
graph.add_edge("fetch_stock_data", "bull_analyst")
graph.add_edge("fetch_stock_data", "bear_analyst")
graph.add_edge("news_analyst", "bull_analyst")
graph.add_edge("news_analyst", "bear_analyst")
graph.add_edge("bull_analyst", "financial_analyst")
graph.add_edge("bear_analyst", "financial_analyst")
graph.add_edge("financial_analyst", END)

bull_bear_analyst_graph = graph.compile()
