# BullBear — LangGraph State Diagram

## Agent Workflow

```mermaid
flowchart TD
    START(["▶ START\nInput: ticker symbol"]):::start

    FSD["🔢 fetch_stock_data\n─────────────────────\nyfinance.history(period=6mo)\nReturns: OHLCV dict\n~1-3s"]:::datanode

    NA["📰 news_analyst\n─────────────────────\nyfinance.Ticker.news\n→ Grok sentiment synthesis\nTop 15 headlines\n~5-10s"]:::llmnode

    BA["🐂 bull_analyst\n─────────────────────\n60-day OHLCV + news_analysis\n→ Grok bullish thesis\nPrice targets · Accumulation\nRating: 7-10 / 10\n~15-20s"]:::bullnode

    BRA["🐻 bear_analyst\n─────────────────────\n60-day OHLCV + news_analysis\n→ Grok bearish thesis\nDownside targets · Distribution\nRating: 1-4 / 10\n~15-20s"]:::bearnode

    FA["⚖️ financial_analyst\n─────────────────────\nbull_analysis + bear_analysis\n→ Grok CIO reconciliation\nFinal memo · Action plan\nConviction rating: 1-10 / 10\n~10-15s"]:::synthnode

    END_(["⏹ END\nOutput: 6 fields\nbull · bear · financial\nanalyses + ratings"]):::start

    START -->|"parallel fork"| FSD
    START -->|"parallel fork"| NA

    FSD -->|"time_series_data"| BA
    FSD -->|"time_series_data"| BRA
    NA  -->|"news_analysis"| BA
    NA  -->|"news_analysis"| BRA

    BA  -->|"bull_analysis\nbull_analysis_raiting"| FA
    BRA -->|"bear_analysis\nbear_analysis_raiting"| FA

    FA  -->|"financial_analysis\nfinancial_analysis_raiting"| END_

    classDef start     fill:#0d1117,stroke:#00ff88,color:#00ff88,font-weight:bold,rx:8
    classDef datanode  fill:#0d1b2a,stroke:#4fc3f7,color:#cfe2f3,rx:4
    classDef llmnode   fill:#1a1200,stroke:#ffa726,color:#ffe0b2,rx:4
    classDef bullnode  fill:#001a0d,stroke:#00e676,color:#b9f6ca,rx:4
    classDef bearnode  fill:#1a0000,stroke:#ff5252,color:#ffcdd2,rx:4
    classDef synthnode fill:#120020,stroke:#ce93d8,color:#e1bee7,font-weight:bold,rx:4
```

## State Schema

```mermaid
classDiagram
    class BullBearState {
        +str ticker
        +str market_region
        +dict time_series_data
        +str news_analysis
        +str bull_analysis
        +str bull_analysis_raiting
        +str bear_analysis
        +str bear_analysis_raiting
        +str financial_analysis
        +str financial_analysis_raiting
    }

    class fetch_stock_data {
        +yfinance.history(6mo)
        +returns time_series_data
    }

    class news_analyst {
        +yfinance.news top 15
        +Grok synthesis
        +returns news_analysis
    }

    class bull_analyst {
        +60-day OHLCV trim
        +Bullish thesis prompt
        +extract_rating()
        +returns bull_analysis, rating
    }

    class bear_analyst {
        +60-day OHLCV trim
        +Bearish thesis prompt
        +extract_rating()
        +returns bear_analysis, rating
    }

    class financial_analyst {
        +CIO reconciliation prompt
        +format_financial_report()
        +extract_rating()
        +returns financial_analysis, rating
    }

    BullBearState --> fetch_stock_data : reads ticker
    BullBearState --> news_analyst : reads ticker
    fetch_stock_data --> BullBearState : writes time_series_data
    news_analyst --> BullBearState : writes news_analysis
    bull_analyst --> BullBearState : writes bull_analysis + rating
    bear_analyst --> BullBearState : writes bear_analysis + rating
    financial_analyst --> BullBearState : writes financial_analysis + rating
```

## Parallelisation Map

```
Wall-clock timeline (approximate):

t=0s   ──────────────────────────────────────────────────────────────
        │ fetch_stock_data     ├───────┤  (~3s)
        │ news_analyst         ├──────────────────┤  (~10s)
                                                   │
t=10s  ──────────────────────────────────────────────────────────────
                                        │ bull_analyst  ├──────────────────┤
                                        │ bear_analyst  ├──────────────────┤
                                                                           │
t=30s  ──────────────────────────────────────────────────────────────
                                                         │ financial_analyst ├────────┤
                                                                                       │
t=45s  ──────────────────────────────────────────────────────────────  ✅ DONE
```

> **Critical path**: `news_analyst` (slowest parallel branch) → `bull/bear_analyst` (parallel) → `financial_analyst`
>
> **Speedup from parallelisation**: ~50% faster vs. sequential execution
