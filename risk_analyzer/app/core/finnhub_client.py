import httpx
import pandas as pd
from datetime import datetime, timedelta

class FinnhubClient:
    """Cliente assíncrono para buscar dados de ações no Finnhub."""

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_candles(self, symbol: str, days: int = 90) -> pd.DataFrame:
        to_dt = datetime.utcnow()
        from_dt = to_dt - timedelta(days=days * 1.5)
        params = {
            "symbol": symbol,
            "resolution": "D",
            "from": int(from_dt.timestamp()),
            "to": int(to_dt.timestamp()),
            "token": self.api_key,
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.BASE_URL}/stock/candle", params=params, timeout=20)
            data = r.json()

        if data.get("s") != "ok":
            raise ValueError(f"Nenhum dado disponível para {symbol}")

        df = pd.DataFrame({"close": data["c"]}, index=pd.to_datetime(data["t"], unit="s"))
        return df.tail(days)
