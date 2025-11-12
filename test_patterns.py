#!/usr/bin/env python3
"""
Quick test script to debug pattern detection
Run this to see what's happening with the data
"""

import yfinance as yf
import pandas as pd
from pattern_detector import PatternDetector

detector = PatternDetector()

# Test with a few popular stocks
test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']

print("=" * 60)
print("PATTERN DETECTION TEST")
print("=" * 60)

for ticker in test_tickers:
    print(f"\n📊 Testing {ticker}...")
    
    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo", interval="1d")
        
        if df.empty:
            print(f"  ❌ No data available")
            continue
        
        print(f"  ✓ Fetched {len(df)} data points")
        print(f"  ✓ Latest price: ${df['Close'].iloc[-1]:.2f}")
        
        # Test all patterns
        patterns = {
            'Bull Flag': detector.detect_bull_flag(df),
            'Bear Flag': detector.detect_bear_flag(df),
            'Head & Shoulders': detector.detect_head_shoulders(df),
            'Double Top': detector.detect_double_top(df),
            'Double Bottom': detector.detect_double_bottom(df),
            'Gap Up': detector.detect_gap_up(df),
            'Gap Down': detector.detect_gap_down(df),
            'Volume Spike': detector.detect_volume_spike(df),
            'MA Crossover (Bull)': detector.detect_ma_crossover(df, bullish=True),
            'MA Crossover (Bear)': detector.detect_ma_crossover(df, bullish=False),
        }
        
        # Show results
        found_any = False
        for pattern_name, (found, confidence) in patterns.items():
            if found:
                print(f"  🎯 {pattern_name}: {confidence:.0%} confidence")
                found_any = True
        
        if not found_any:
            print(f"  ℹ️  No patterns detected (all below 30% threshold)")
            # Show top confidence scores anyway
            sorted_patterns = sorted(patterns.items(), key=lambda x: x[1][1], reverse=True)
            top_3 = sorted_patterns[:3]
            print(f"  Top scores:")
            for name, (_, conf) in top_3:
                print(f"    - {name}: {conf:.0%}")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print("Test complete!")
print("\nIf you're seeing 0% confidence everywhere, the patterns")
print("may need adjustment or market conditions don't match.")
print("=" * 60)
