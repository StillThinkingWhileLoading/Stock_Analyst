import asyncio
import webbrowser
from datetime import datetime, timedelta

from graph import bull_bear_analyst_graph
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache: ticker -> (result_dict, cached_at)
_cache: dict[str, tuple[dict, datetime]] = {}
_CACHE_TTL = timedelta(days=1)


class TickerRequest(BaseModel):
    ticker: str


async def _open_browser():
    await asyncio.sleep(1)
    webbrowser.open("http://localhost:8000")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(_open_browser())


@app.get("/")
def serve_ui():
    return FileResponse("bull_bear_ui.html")


@app.post("/analyze")
async def analyze(request: TickerRequest):
    ticker = request.ticker.upper()
    now = datetime.utcnow()

    try:
        # Return cached result if it is less than 1 day old
        if ticker in _cache:
            cached_result, cached_at = _cache[ticker]
            if now - cached_at < _CACHE_TTL:
                return JSONResponse({**_build_response(cached_result), "cached": True})

        result = await bull_bear_analyst_graph.ainvoke({"ticker": ticker})
        _cache[ticker] = (result, now)

        return JSONResponse({**_build_response(result), "cached": False})

    except ValueError as e:
        return JSONResponse(
            {
                "error": True,
                "message": f"Invalid ticker or data error: {str(e)}",
                "ticker": ticker,
            },
            status_code=400,
        )
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            return JSONResponse(
                {
                    "error": True,
                    "message": f"API rate limit exceeded. Please try again in a few minutes.",
                    "ticker": ticker,
                },
                status_code=429,
            )
        return JSONResponse(
            {
                "error": True,
                "message": f"Error analyzing {ticker}: {error_msg[:200]}",
                "ticker": ticker,
            },
            status_code=500,
        )


def _build_response(result: dict) -> dict:
    return {
        "bull_analysis":              result["bull_analysis"],
        "bull_analysis_raiting":      result["bull_analysis_raiting"],
        "bear_analysis":              result["bear_analysis"],
        "bear_analysis_raiting":      result["bear_analysis_raiting"],
        "financial_analysis":         result["financial_analysis"],
        "financial_analysis_raiting": result["financial_analysis_raiting"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
