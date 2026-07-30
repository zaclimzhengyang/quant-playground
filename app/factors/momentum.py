import pandas as pd
from typing import Optional


def generate_momentum_scores(price_df: pd.DataFrame, windows: list[int] = [30, 60, 90]) -> Optional[dict[int, float]]:
    """
    Calculate the momentum score for a stock.

    The momentum score is the percentage change in closing price over the last 60 days.

    Financial Description:
    - Momentum: The tendency of assets with recent high returns to continue performing well.
    """
    """
    Generate trading signals based on price and its 50-day moving average.

    Returns:
    - 1 if price > 50-day MA (buy signal)
    - -1 if price <= 50-day MA (sell signal)
    - 0 otherwise

    Financial Description:
    - Moving average crossover is a classic trend-following strategy.
    - Momentum Score = (Price_today / Price_60_days_ago) - 1
    """
    if price_df is None or price_df.empty or "Adj Close" not in price_df.columns:
        return None

    px = price_df["Adj Close"]
    if isinstance(px, pd.DataFrame):
        px = px.iloc[:, 0]
    px = px.dropna()
    if px.empty:
        return None

    scores = {}
    for w in windows:
        idx = max(0, len(px) - w)
        base = px.iloc[idx]
        if base == 0 or pd.isna(base):
            return None
        scores[w] = round(float(px.iloc[-1] / base - 1), 4)

    return scores


def generate_signals(prices: pd.Series) -> list[int]:
    """
    Generate trading signals based on price and its 50-day moving average.

    Returns:
    - 1 if price > 50-day MA (buy signal)
    - -1 if price <= 50-day MA (sell signal)
    - 0 otherwise

    Financial Description:
    - Moving average crossover is a classic trend-following strategy.
    """
    ma50 = prices.rolling(window=50).mean()
    signals = pd.Series(0, index=prices.index)
    signals[prices > ma50] = 1
    signals[(prices <= ma50) & (~ma50.isna())] = -1
    return signals.tolist()
