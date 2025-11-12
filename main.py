from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
import os
import asyncio

from pattern_detector import PatternDetector
from marketstack_client import MarketstackClient

app = FastAPI(title="NASDAQ Pattern Scanner - Powered by Marketstack")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize pattern detector
detector = PatternDetector()

# Initialize Marketstack client
MARKETSTACK_API_KEY = os.getenv('MARKETSTACK_API_KEY')
if not MARKETSTACK_API_KEY:
    raise RuntimeError("⚠️  MARKETSTACK_API_KEY environment variable not set!")

marketstack = MarketstackClient(MARKETSTACK_API_KEY)
print("✅ Marketstack client initialized")

# NASDAQ-100 tickers (optimized for batch API calls)
# 100 stocks = 1 API call with Marketstack!
NASDAQ_TICKERS = [
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

print(f"📊 NASDAQ-100 loaded: {len(NASDAQ_TICKERS)} stocks")
print(f"💰 API Efficiency: {len(NASDAQ_TICKERS)} stocks = 1 API call!")

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

@app.get("/api/usage")
async def get_api_usage():
    """Get API usage statistics"""
    stats = marketstack.get_usage_stats()
    return {
        "api_calls_made": stats['total_api_calls'],
        "cache_entries": stats['cache_entries'],
        "cache_hit_rate": f"{stats['cache_hit_rate']:.1f}%",
        "estimated_monthly_usage": stats['total_api_calls'] * 30  # Rough estimate
    }

@app.get("/api/scan-stream")
async def scan_pattern_stream(
    pattern: str = Query(..., description="Pattern to scan for"),
    timeframe: str = Query("1d", description="Timeframe: 1d, 1h, 30m, 15m, 5m, 1m"),
    period: str = Query("1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y")
):
    """Stream scan progress in real-time using Server-Sent Events"""
    
    async def event_generator():
        results = []
        
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Initializing Marketstack API...', 'progress': 0})}\n\n"
            await asyncio.sleep(0.1)
            
            # Fetch ALL data in ONE API call (this is the magic!)
            yield f"data: {json.dumps({'type': 'status', 'message': 'Fetching data for 100 stocks in 1 API call...', 'progress': 10})}\n\n"
            await asyncio.sleep(0.1)
            
            # Single batch API call for all tickers
            data_dict = marketstack.get_historical_data(
                symbols=NASDAQ_TICKERS,
                timeframe=timeframe,
                period=period
            )
            
            yield f"data: {json.dumps({'type': 'status', 'message': f'Data loaded! Scanning {len(data_dict)} stocks...', 'progress': 30})}\n\n"
            await asyncio.sleep(0.1)
            
            # Process each ticker
            total_tickers = len(data_dict)
            processed_count = 0
            
            for idx, ticker in enumerate(data_dict.keys()):
                try:
                    df = data_dict[ticker]
                    
                    if df.empty or len(df) < 20:
                        continue
                    
                    processed_count += 1
                    progress = 30 + int((idx / total_tickers) * 60)
                    
                    # Send progress
                    yield f"data: {json.dumps({'type': 'scanning', 'ticker': ticker, 'progress': progress, 'current': idx + 1, 'total': total_tickers})}\n\n"
                    await asyncio.sleep(0.03)  # Small delay for smooth UI
                    
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
                        current_price = float(df['Close'].iloc[-1])
                        previous_price = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
                        price_change = ((current_price - previous_price) / previous_price) * 100 if previous_price != 0 else 0
                        
                        result = {
                            "ticker": ticker,
                            "confidence": round(confidence * 100, 2),
                            "current_price": round(current_price, 2),
                            "price_change": round(price_change, 2),
                            "volume": int(df['Volume'].iloc[-1])
                        }
                        results.append(result)
                        
                        # Send match found event
                        yield f"data: {json.dumps({'type': 'match', 'result': result})}\n\n"
                        await asyncio.sleep(0.03)
                
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'ticker': ticker, 'error': str(e)})}\n\n"
                    continue
            
            # Sort results by confidence
            results.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Get API usage stats
            usage_stats = marketstack.get_usage_stats()
            
            # Send completion with API usage info
            yield f"data: {json.dumps({{'type': 'complete', 'results': results, 'total_scanned': total_tickers, 'total_matches': len(results), 'progress': 100, 'api_calls_used': usage_stats['total_api_calls']}})}\n\n"
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Scan error: {error_msg}")
            yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/scan")
async def scan_pattern(
    pattern: str = Query(..., description="Pattern to scan for"),
    timeframe: str = Query("1d", description="Timeframe: 1d, 1h, 30m, 15m, 5m, 1m"),
    period: str = Query("1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y")
):
    """Scan all tickers for a specific pattern (fallback for non-streaming)"""
    results = []
    
    try:
        print("\n" + "="*60)
        print(f"🔍 STARTING MARKETSTACK PATTERN SCAN")
        print(f"Pattern: {pattern}")
        print(f"Timeframe: {timeframe}")
        print(f"Period: {period}")
        print("="*60 + "\n")
        
        # Single batch API call for all tickers
        print(f"📡 Fetching {len(NASDAQ_TICKERS)} stocks in 1 API call...")
        data_dict = marketstack.get_historical_data(
            symbols=NASDAQ_TICKERS,
            timeframe=timeframe,
            period=period
        )
        
        print(f"✅ Data received for {len(data_dict)} stocks\n")
        
        # Process each ticker
        processed_count = 0
        error_count = 0
        
        for ticker in data_dict.keys():
            try:
                df = data_dict[ticker]
                
                if df.empty or len(df) < 20:
                    print(f"⚠️  {ticker}: Insufficient data ({len(df) if not df.empty else 0} bars)")
                    continue
                
                processed_count += 1
                
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
                    print(f"✅ {ticker}: MATCH! Confidence: {confidence*100:.1f}%")
                    current_price = float(df['Close'].iloc[-1])
                    previous_price = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
                    price_change = ((current_price - previous_price) / previous_price) * 100 if previous_price != 0 else 0
                    
                    results.append({
                        "ticker": ticker,
                        "confidence": round(confidence * 100, 2),
                        "current_price": round(current_price, 2),
                        "price_change": round(price_change, 2),
                        "volume": int(df['Volume'].iloc[-1])
                    })
                elif processed_count % 10 == 0:
                    print(f"   {ticker}: No match (confidence: {confidence*100:.1f}%)")
            
            except Exception as e:
                error_count += 1
                print(f"❌ {ticker}: Error - {str(e)}")
                continue
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Get API usage
        usage_stats = marketstack.get_usage_stats()
        
        print("\n" + "="*60)
        print(f"📊 SCAN COMPLETE")
        print(f"Successfully processed: {processed_count}")
        print(f"Patterns found: {len(results)}")
        print(f"API calls used: {usage_stats['total_api_calls']}")
        print(f"Cache hit rate: {usage_stats['cache_hit_rate']:.1f}%")
        
        if len(results) > 0:
            print(f"\n🎯 Top Matches:")
            for i, result in enumerate(results[:5], 1):
                print(f"  {i}. {result['ticker']}: {result['confidence']}% confidence")
        
        print("="*60 + "\n")
        
        return {
            "pattern": pattern,
            "timeframe": timeframe,
            "period": period,
            "matches": results,
            "total_scanned": len(NASDAQ_TICKERS),
            "total_matches": len(results),
            "api_calls_used": usage_stats['total_api_calls']
        }
    
    except Exception as e:
        print(f"❌ Scan error: {e}")
        raise HTTPException(status_code=500, detail=f"Error scanning: {str(e)}")

@app.get("/api/chart/{ticker}")
async def get_chart(
    ticker: str,
    timeframe: str = Query("1d", description="Timeframe"),
    period: str = Query("1mo", description="Period")
):
    """Get interactive chart for a specific ticker"""
    try:
        # Fetch data for single ticker
        data_dict = marketstack.get_historical_data(
            symbols=[ticker],
            timeframe=timeframe,
            period=period
        )
        
        if ticker not in data_dict or data_dict[ticker].empty:
            raise HTTPException(status_code=404, detail="No data found for this ticker")
        
        df = data_dict[ticker]
        
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

@app.post("/api/cache/clear")
async def clear_cache():
    """Clear the Marketstack cache"""
    marketstack.clear_cache()
    return {"message": "Cache cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 NASDAQ Pattern Scanner with Marketstack")
    print("="*60)
    print(f"📊 Scanning {len(NASDAQ_TICKERS)} NASDAQ-100 stocks")
    print(f"💰 API Efficiency: 1 API call per scan (batch request)")
    print(f"🔄 15-minute caching enabled")
    print(f"🌐 Starting server on http://0.0.0.0:8000")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
