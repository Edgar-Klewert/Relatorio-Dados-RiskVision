import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.analyzer import RiskAnalyzer
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY")

app = FastAPI(title="RiskVision Analyzer API")
analyzer = RiskAnalyzer(API_KEY)


class RiskRequest(BaseModel):
    ticker: str
    benchmark: str | None = "SPY"
    days: int = 90
    confidence: float = 0.95


@app.post("/risk")
async def calcular_risco(req: RiskRequest):
    try:
        result = await analyzer.analyze(
            ticker=req.ticker,
            benchmark=req.benchmark,
            days=req.days,
            confidence=req.confidence,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
