from datetime import datetime
from .finnhub_client import FinnhubClient
from app.utils.metrics import compute_risk_metrics

class RiskAnalyzer:
    """Classe principal de análise de risco."""

    def __init__(self, api_key: str):
        self.client = FinnhubClient(api_key)

    async def analyze(self, ticker: str, benchmark: str = "SPY", days: int = 90, confidence: float = 0.95):
        stock_df = await self.client.get_candles(ticker, days)
        try:
            benchmark_df = await self.client.get_candles(benchmark, days)
        except Exception:
            benchmark_df = None

        metrics = compute_risk_metrics(
            stock_df["close"], benchmark_df["close"] if benchmark_df is not None else None, confidence
        )

        return {
            "ticker": ticker.upper(),
            "last_price": float(stock_df["close"].iloc[-1]),
            "last_date": str(stock_df.index[-1].date()),
            "confidence": confidence,
            "window_days": days,
            "metrics": metrics,
            "updated_at": datetime.utcnow().isoformat()
        }
