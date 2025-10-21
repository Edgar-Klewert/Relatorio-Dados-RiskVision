import numpy as np
from scipy.stats import norm

def compute_risk_metrics(prices, benchmark=None, confidence=0.95):
    logrets = np.log(prices).diff().dropna()
    mean = logrets.mean()
    std = logrets.std()

    # VaR paramétrico
    z = norm.ppf(1 - confidence)
    var_param = -(mean + z * std)

    # VaR histórico
    hist_var = -np.percentile(logrets, (1 - confidence) * 100)
    hist_cvar = -logrets[logrets < -hist_var].mean()

    vol_annual = std * np.sqrt(252)
    ret_annual = mean * 252
    sharpe = ret_annual / vol_annual if vol_annual > 0 else 0

    return {
        "mean_daily_return": float(mean),
        "std_daily_return": float(std),
        "annualized_return": float(ret_annual),
        "annualized_volatility": float(vol_annual),
        "VaR_parametric": float(var_param),
        "VaR_historical": float(hist_var),
        "CVaR": float(hist_cvar),
        "Sharpe_ratio": float(sharpe),
    }
