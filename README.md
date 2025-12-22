# Overview
This repository contains all the quantitative side projects that I am currently working and exploring on.

## #1. Order Book
Simple in-memory order book supporting LIMIT and MARKET orders, FIFO fills within price levels, and order cancellation.

### Features
- Limit and market orders
- Buy/Sell sides
- Price-level aggregation with FIFO
- Partial fills and cancellations
- Maintains price-time priority

### Quick usage
Run demo:
```bash
python3 app/orderbook/main.py
```

📅 Last Updated: 23 December 2025

## #2 Dollar-Cost-Averaging ETF Backtester
A simple dollar-cost-averaging (DCA) backtester for ETFs listed on NYSE Arca. The script in `app/dca_etf/dca_etf.py` downloads historical prices (via `yfinance`), simulates monthly DCA from `START_DATE` to `END_DATE`, ranks tickers by return, and saves the top 10 results.

![img.png](img.png)

📅 Last Updated: 21 September 2025
