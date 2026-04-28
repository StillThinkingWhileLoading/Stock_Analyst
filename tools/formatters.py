import re
from datetime import datetime
import yfinance as yf


# Company name cache to avoid repeated API calls
_company_cache = {}


def get_company_name(ticker: str) -> str:
    """Fetch company name for ticker using yfinance."""
    if ticker in _company_cache:
        return _company_cache[ticker]

    try:
        stock = yf.Ticker(ticker)
        name = stock.info.get("longName", ticker)
        _company_cache[ticker] = name
        return name
    except Exception:
        return ticker


def format_financial_report(raw_analysis: str, ticker: str, rating: str) -> str:
    """Format financial analysis report with company name and improved styling."""
    today = datetime.today().strftime("%B %d, %Y")
    company_name = get_company_name(ticker)

    # Determine sentiment based on rating
    def get_sentiment(rating_str: str) -> str:
        """Convert rating to sentiment label."""
        try:
            rating_num = int(rating_str.split()[0])
            if rating_num >= 7:
                return "BULLISH"
            elif rating_num <= 4:
                return "BEARISH"
            else:
                return "NEUTRAL"
        except (ValueError, IndexError):
            return "NEUTRAL"

    sentiment = get_sentiment(rating)

    # Header with company info
    header = f"""
{'=' * 80}
                        FINANCIAL ANALYSIS REPORT
                          {company_name} ({ticker.upper()})
{'=' * 80}

  Report Generated: {today}
  Overall Rating:  {rating}
  Investment Outlook: {sentiment}

{'=' * 80}
"""

    # Clean and format the analysis
    cleaned = re.sub(r'\n{3,}', '\n\n', raw_analysis.strip())

    def format_section_header(match):
        title = match.group(0).strip()
        return f"\n{'─' * 80}\n  {title.upper()}\n{'─' * 80}"

    cleaned = re.sub(
        r'^\d+\.\s+[A-Z][A-Z &/]+',
        format_section_header,
        cleaned,
        flags=re.MULTILINE
    )

    # Remove any existing "This analysis is for informational purposes" text
    cleaned = re.sub(
        r'This analysis is for informational purposes.*?financial advice\.',
        '',
        cleaned,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Disclaimer with formatting
    disclaimer = f"""

{'=' * 80}
⚠️  DISCLAIMER - PLEASE READ CAREFULLY ⚠️
{'=' * 80}

This report is NOT personalised financial advice. It is generated for
informational and educational purposes only. Always consult a qualified
financial advisor before making investment decisions.

Investment decisions should be based on your personal financial situation,
risk tolerance, and investment objectives. Past performance does not
guarantee future results. All investments carry risk, including potential
loss of principal.

{'=' * 80}

"""

    footer = f"""
END OF REPORT
Generated on {today} | {company_name} ({ticker.upper()})
{'=' * 80}
"""

    return header + cleaned + disclaimer + footer


def extract_rating(analysis_text: str) -> str:
    """
    Extracts rating from analysis text and returns it in 'X / 10' format.

    Rating Scale:
    - 7-10: Bull (strong bullish conviction)
    - 5-6: Neutral (balanced, uncertain)
    - 1-4: Bear (strong bearish conviction)
    """
    patterns = [
        r'(?i)\*{0,2}(?:Bull|Bear|Confidence)\s*Rating\s*:\*{0,2}\s*(\d{1,2})\s*(?:/|out of)\s*10',
        r'(?i)\*{0,2}Rating\s*:\*{0,2}\s*(\d{1,2})\s*(?:/|out of)\s*10',
        r'(?i)(?:Bull|Bear|Confidence)\s*Rating\s*:\s*(\d{1,2})',
        r'(\d{1,2})\s*(?:/|out of)\s*10',
    ]
    for pattern in patterns:
        match = re.search(pattern, analysis_text)
        if match:
            rating = match.group(1).strip()
            return f"{rating} / 10"
    return "N/A"


def trim_to_60_days(time_series: dict) -> dict:
    """Trim time series data to last 60 days."""
    sorted_dates = sorted(time_series.keys(), reverse=True)[:60]
    return {date: time_series[date] for date in sorted_dates}
