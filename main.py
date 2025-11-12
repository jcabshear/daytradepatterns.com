from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from functools import lru_cache
import time

from pattern_detector import PatternDetector

app = FastAPI(title="NASDAQ Pattern Scanner")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize pattern detector
detector = PatternDetector()

# Simple cache for bulk data (expires after 5 minutes)
_data_cache = {}
_cache_timestamp = {}
CACHE_DURATION = 300  # 5 minutes

# Configuration: Choose which NASDAQ list to scan
# Options: 
#   "NASDAQ-100" (100 stocks) - Recommended for free tier, fast scans
#   "NASDAQ-COMPOSITE" (500-3000 stocks) - Full market scan, slower
# 
# ⚡ Performance Notes:
# - NASDAQ-100: ~5-10 seconds per scan
# - 500 stocks: ~20-30 seconds per scan  
# - 3000 stocks: ~2-3 minutes per scan (may timeout on free tier)
#
# 💡 Tip: Start with NASDAQ-100, upgrade Render plan for full composite
SCAN_MODE = "NASDAQ-100"  # Change to "NASDAQ-COMPOSITE" for full NASDAQ

# NASDAQ 100 tickers - Full list dynamically fetched
def get_nasdaq_100_tickers():
    """Fetch NASDAQ-100 tickers from Wikipedia"""
    try:
        import pandas as pd
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        tables = pd.read_html(url)
        # The first table contains the ticker list
        df = tables[4]  # NASDAQ-100 components table
        tickers = df['Ticker'].tolist()
        print(f"Fetched {len(tickers)} NASDAQ-100 tickers")
        return tickers
    except Exception as e:
        print(f"Error fetching NASDAQ-100 list: {e}")
        # Fallback to full hardcoded NASDAQ-100 list
        return [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'COST',
            'NFLX', 'ASML', 'AMD', 'PEP', 'ADBE', 'CSCO', 'CMCSA', 'TMUS', 'INTC', 'TXN',
            'QCOM', 'INTU', 'AMAT', 'HON', 'AMGN', 'BKNG', 'ADP', 'SBUX', 'GILD', 'ISRG',
            'REGN', 'VRTX', 'ADI', 'MU', 'LRCX', 'PANW', 'KLAC', 'MDLZ', 'SNPS', 'CDNS',
            'MELI', 'PYPL', 'MAR', 'CSX', 'ORLY', 'CRWD', 'ABNB', 'FTNT', 'MNST', 'DASH',
            'WDAY', 'NXPI', 'TEAM', 'PCAR', 'ADSK', 'PAYX', 'ROST', 'MRVL', 'ODFL', 'CPRT',
            'AEP', 'CTAS', 'CHTR', 'DXCM', 'FAST', 'KDP', 'VRSK', 'TTD', 'BIIB', 'EA',
            'IDXX', 'KHC', 'CTSH', 'GEHC', 'LULU', 'ANSS', 'FANG', 'EXC', 'ZS', 'DDOG',
            'ON', 'CSGP', 'BKR', 'XEL', 'ILMN', 'WBD', 'GFS', 'CDW', 'MDB', 'MRNA',
            'ZM', 'ALGN', 'DLTR', 'WBA', 'ENPH', 'SGEN', 'LCID', 'RIVN', 'ZI', 'HOOD'
        ]

def get_all_nasdaq_tickers(limit=None):
    """
    Fetch ALL NASDAQ Composite tickers (3000+ stocks)
    
    Args:
        limit: Maximum number of tickers to return (None = all stocks)
               Recommended: 500 for free tier, 1000+ for paid plans
    """
    try:
        import pandas as pd
        # Use NASDAQ's official FTP feed
        ftp_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
        df = pd.read_csv(ftp_url, sep="|")
        
        # Filter out test symbols and get valid tickers
        df = df[df['Test Issue'] == 'N']
        df = df[df['Financial Status'] == 'N']  # Normal financial status
        tickers = df['Symbol'].str.strip().tolist()
        
        # Remove the last row (file trailer) and clean up
        tickers = [t for t in tickers if t and len(t) <= 5 and t != 'Symbol']
        
        # Apply limit if specified
        if limit:
            tickers = tickers[:limit]
        
        print(f"Fetched {len(tickers)} NASDAQ Composite tickers")
        return tickers
    except Exception as e:
        print(f"Error fetching full NASDAQ list: {e}")
        # Fallback to NASDAQ-100
        return get_nasdaq_100_tickers()

# Initialize ticker list on startup based on scan mode
if SCAN_MODE == "NASDAQ-COMPOSITE":
    # Limit to 500 stocks for performance (remove limit=500 for all ~3000 stocks)
    NASDAQ_TICKERS = get_all_nasdaq_tickers(limit=500)
    print(f"⚡ Scanning mode: FULL NASDAQ COMPOSITE ({len(NASDAQ_TICKERS)} stocks)")
else:
    NASDAQ_TICKERS = get_nasdaq_100_tickers()
    print(f"⚡ Scanning mode: NASDAQ-100 ({len(NASDAQ_TICKERS)} stocks)")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/api/patterns")
async def get_available_patterns():
    """Get list of available patterns"""
    return {
        "patterns": [
            {"id": "bull_flag", "name": "Bull Flag"},
            {"id": "bear_flag", "name": "Bear Flag"},
            {"id": "head_shoulders", "name": "Head and Shoulders"},
            {"id": "double_top", "name": "Double Top"},
            {"id": "double_bottom", "name": "Double Bottom"},
            {"id": "gap_up", "name": "Gap Up"},
            {"id": "gap_down", "name": "Gap Down"},
            {"id": "volume_spike", "name": "Volume Spike"},
            {"id": "ma_crossover_bullish", "name": "MA Crossover (Bullish)"},
            {"id": "ma_crossover_bearish", "name": "MA Crossover (Bearish)"}
        ]
    }

@app.get("/api/tickers")
async def get_tickers():
    """Get list of available tickers"""
    return {"tickers": NASDAQ_TICKERS}

@app.get("/api/scan")
async def scan_pattern(
    pattern: str = Query(..., description="Pattern to scan for"),
    timeframe: str = Query("1d", description="Timeframe: 1m, 5m, 15m, 1h, 1d, 1wk, 1mo"),
    period: str = Query("1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y")
):
    """Scan all tickers for a specific pattern"""
    results = []
    
    try:
        # Check cache
        cache_key = f"{timeframe}_{period}"
        current_time = time.time()
        
        if (cache_key in _data_cache and 
            cache_key in _cache_timestamp and 
            current_time - _cache_timestamp[cache_key] < CACHE_DURATION):
            print(f"Using cached data for {cache_key}")
            bulk_data = _data_cache[cache_key]
        else:
            # BULK DOWNLOAD - Download all tickers at once
            print(f"Downloading bulk data for {len(NASDAQ_TICKERS)} tickers...")
            tickers_str = " ".join(NASDAQ_TICKERS)
            
            bulk_data = yf.download(
                tickers=tickers_str,
                period=period,
                interval=timeframe,
                group_by='ticker',
                threads=True,
                progress=False
            )
            
            # Cache the data
            _data_cache[cache_key] = bulk_data
            _cache_timestamp[cache_key] = current_time
            print(f"Bulk download complete. Data cached.")
        
        # Process each ticker's data
        for ticker in NASDAQ_TICKERS:
            try:
                # Extract data for this ticker
                if len(NASDAQ_TICKERS) == 1:
                    df = bulk_data
                else:
                    df = bulk_data[ticker]
                
                # Skip if not enough data
                if df.empty or len(df) < 20:
                    continue
                
                # Detect pattern
                pattern_found = False
                confidence = 0
                
                if pattern == "bull_flag":
                    pattern_found, confidence = detector.detect_bull_flag(df)
                elif pattern == "bear_flag":
                    pattern_found, confidence = detector.detect_bear_flag(df)
                elif pattern == "head_shoulders":
                    pattern_found, confidence = detector.detect_head_shoulders(df)
                elif pattern == "double_top":
                    pattern_found, confidence = detector.detect_double_top(df)
                elif pattern == "double_bottom":
                    pattern_found, confidence = detector.detect_double_bottom(df)
                elif pattern == "gap_up":
                    pattern_found, confidence = detector.detect_gap_up(df)
                elif pattern == "gap_down":
                    pattern_found, confidence = detector.detect_gap_down(df)
                elif pattern == "volume_spike":
                    pattern_found, confidence = detector.detect_volume_spike(df)
                elif pattern == "ma_crossover_bullish":
                    pattern_found, confidence = detector.detect_ma_crossover(df, bullish=True)
                elif pattern == "ma_crossover_bearish":
                    pattern_found, confidence = detector.detect_ma_crossover(df, bullish=False)
                
                if pattern_found:
                    current_price = df['Close'].iloc[-1]
                    price_change = ((current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                    
                    results.append({
                        "ticker": ticker,
                        "confidence": round(confidence, 2),
                        "current_price": round(current_price, 2),
                        "price_change": round(price_change, 2),
                        "volume": int(df['Volume'].iloc[-1])
                    })
            
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
                continue
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"Scan complete. Found {len(results)} matches.")
        
        return {
            "pattern": pattern,
            "timeframe": timeframe,
            "period": period,
            "matches": results,
            "total_scanned": len(NASDAQ_TICKERS),
            "total_matches": len(results)
        }
    
    except Exception as e:
        print(f"Bulk download error: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading data: {str(e)}")

@app.get("/api/chart/{ticker}")
async def get_chart(
    ticker: str,
    timeframe: str = Query("1d", description="Timeframe"),
    period: str = Query("1mo", description="Period")
):
    """Get interactive chart for a specific ticker"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=timeframe)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Calculate technical indicators
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        # Create candlestick chart
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxis=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(f'{ticker} Price', 'Volume')
        )
        
        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Moving averages
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_20'],
                name='SMA 20',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_50'],
                name='SMA 50',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        
        # Volume
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                  for i in range(len(df))]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Volume_MA'],
                name='Volume MA',
                line=dict(color='purple', width=1)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f'{ticker} - {timeframe} Chart',
            yaxis_title='Price ($)',
            xaxis_rangeslider_visible=False,
            height=600,
            template='plotly_dark'
        )
        
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return JSONResponse(content=json.loads(fig.to_json()))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{ticker}")
async def get_stock_info(ticker: str):
    """Get detailed stock information"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "52_week_high": info.get("fiftyTwoWeekHigh", 0),
            "52_week_low": info.get("fiftyTwoWeekLow", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
