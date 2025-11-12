# Troubleshooting: Zero Patterns Found

If you're getting zero stocks back no matter what settings you use, here's how to debug:

## 🔍 Quick Fixes

### 1. Lower the Confidence Threshold

The pattern detector has a minimum confidence threshold. I've already lowered it from 50% to 30%, but you can adjust it further:

**Edit `pattern_detector.py`:**
```python
def __init__(self):
    self.min_confidence = 0.3  # Lower this to 0.2 or 0.1 to catch more patterns
```

### 2. Use the Debug Endpoint

I've added a debug endpoint to test individual stocks:

**Visit in your browser:**
```
https://daytradepatterns-com.onrender.com/api/debug/AAPL
```

This will show:
- If data is being fetched correctly
- How many data points we have
- Confidence scores for ALL patterns (even if below threshold)

### 3. Run the Test Script Locally

```bash
cd nasdaq_pattern_scanner
python test_patterns.py
```

This will test pattern detection on 5 popular stocks and show you exactly what's happening.

## 🐛 Common Issues

### Issue 1: Market Hours
If running during market hours, some patterns (like gaps) only show up after market close.

**Solution:** Try different times of day or use "1d" data from yesterday.

### Issue 2: Pattern Rarity
Some patterns are genuinely rare. You might not see them every day.

**Patterns by frequency:**
- ✅ **Common**: Volume Spike, MA Crossover
- 🟡 **Moderate**: Bull/Bear Flag, Gap Up/Down
- 🔴 **Rare**: Head & Shoulders, Double Top/Bottom

**Solution:** Try "Volume Spike" or "MA Crossover" first - these should show results.

### Issue 3: Timeframe Mismatch
Some patterns work better on certain timeframes:
- **Intraday (1m, 5m)**: Best for volume spikes, gaps
- **Daily (1d)**: Best for flags, moving averages
- **Weekly (1wk)**: Best for larger patterns (H&S, double tops)

**Solution:** Try 1d timeframe with 1mo period first.

### Issue 4: Period Too Short
If you use "1d" period with "1d" timeframe, you only get 1 data point!

**Solution:** Use at least "1mo" period for daily data.

## ✅ Recommended Test Settings

Try these settings - they should show results:

### Test 1: Volume Spike
- **Pattern**: Volume Spike
- **Timeframe**: 1d
- **Period**: 1mo
- **Why**: Very common, easy to detect

### Test 2: Moving Average Crossover
- **Pattern**: MA Crossover (Bullish)
- **Timeframe**: 1d
- **Period**: 3mo
- **Why**: Happens regularly in markets

### Test 3: Gap Patterns
- **Pattern**: Gap Up
- **Timeframe**: 1d
- **Period**: 1mo
- **Why**: Common after earnings or news

## 📊 Check Render Logs

1. Go to Render dashboard
2. Click on your service
3. Click "Logs"
4. Look for lines like:
   ```
   ✓ AAPL: Pattern found! Confidence: 45%
   Processing Summary:
     - Tickers in dataset: 100
     - Successfully processed: 98
     - Patterns found: 12
   ```

If you see:
- **"Insufficient data"** → Data fetching issue
- **"Error processing"** → Code bug (send me the error)
- **"Patterns found: 0"** → Try lowering confidence threshold

## 🛠️ Manual Pattern Threshold Adjustment

For testing, you can temporarily disable the threshold:

**In `pattern_detector.py`, change ALL `return` statements from:**
```python
return confidence > self.min_confidence, confidence
```

**To:**
```python
return True, confidence  # Always return pattern, regardless of confidence
```

This will show ALL patterns with their confidence scores, helping you understand what's being detected.

## 📞 Still Having Issues?

Share with me:
1. The debug endpoint output: `/api/debug/AAPL`
2. Your scan settings (pattern, timeframe, period)
3. Render logs (especially the "Processing Summary" section)

I'll help you fix it!
