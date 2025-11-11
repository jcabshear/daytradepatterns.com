# NASDAQ Pattern Scanner 📈

A powerful web-based trading pattern detection system that scans NASDAQ stocks for various technical analysis patterns in real-time. Built with Python FastAPI backend and interactive Plotly charts.

## Features

### 🎯 Pattern Detection
- **Bull Flag**: Strong upward move followed by consolidation
- **Bear Flag**: Strong downward move followed by consolidation
- **Head and Shoulders**: Classic reversal pattern with three peaks
- **Double Top**: Two peaks at similar levels indicating resistance
- **Double Bottom**: Two troughs at similar levels indicating support
- **Gap Up**: Significant upward price gap between sessions
- **Gap Down**: Significant downward price gap between sessions
- **Volume Spike**: Unusual trading volume (2x+ average)
- **MA Crossover (Bullish)**: Fast MA crosses above slow MA
- **MA Crossover (Bearish)**: Fast MA crosses below slow MA

### 📊 Multiple Timeframes
- **Intraday**: 1m, 5m, 15m, 1h
- **Daily**: 1d
- **Weekly**: 1wk
- **Monthly**: 1mo

### 📈 Interactive Features
- Real-time pattern scanning across 50+ NASDAQ stocks
- Interactive candlestick charts with volume
- Moving average overlays (SMA 20 & 50)
- Confidence scoring for each pattern match
- Click any stock card to view detailed chart
- Responsive design for all devices

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project**
```bash
cd nasdaq_pattern_scanner
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the server**
```bash
python main.py
```

4. **Open your browser**
Navigate to: `http://localhost:8000`

## Usage Guide

### Scanning for Patterns

1. **Select a Pattern**: Choose from the dropdown (e.g., "Bull Flag")
2. **Choose Timeframe**: Select data granularity (1m to 1mo)
3. **Set Period**: Choose how far back to analyze (1d to 2y)
4. **Click "Scan for Pattern"**: Wait for results

### Understanding Results

**Stock Cards Display:**
- **Ticker Symbol**: Company stock symbol
- **Current Price**: Latest trading price
- **Price Change**: Percentage change (green = up, red = down)
- **Volume**: Trading volume with K/M/B formatting
- **Confidence Bar**: Pattern match confidence (0-100%)

**Confidence Levels:**
- **70-100%**: Strong pattern match
- **50-70%**: Moderate pattern match
- **Below 50%**: Weak match (filtered out by default)

### Viewing Charts

Click any stock card to view an interactive chart showing:
- **Candlestick Pattern**: OHLC data visualization
- **Moving Averages**: 20 & 50 period SMAs
- **Volume**: Bar chart with volume moving average
- **Zoom & Pan**: Interactive chart controls
- **Dark Theme**: Professional trading interface

## API Endpoints

### GET `/api/patterns`
Returns list of available patterns

**Response:**
```json
{
  "patterns": [
    {"id": "bull_flag", "name": "Bull Flag"},
    ...
  ]
}
```

### GET `/api/scan`
Scan stocks for a specific pattern

**Parameters:**
- `pattern` (required): Pattern ID to scan for
- `timeframe` (default: "1d"): Data timeframe
- `period` (default: "1mo"): Historical period

**Response:**
```json
{
  "pattern": "bull_flag",
  "timeframe": "1d",
  "period": "1mo",
  "matches": [
    {
      "ticker": "AAPL",
      "confidence": 85.5,
      "current_price": 185.25,
      "price_change": 2.34,
      "volume": 52341000
    }
  ],
  "total_scanned": 50,
  "total_matches": 5
}
```

### GET `/api/chart/{ticker}`
Get interactive chart data for a ticker

**Parameters:**
- `ticker` (required): Stock ticker symbol
- `timeframe` (default: "1d"): Chart timeframe
- `period` (default: "1mo"): Chart period

**Response:** Plotly JSON chart specification

### GET `/api/stock/{ticker}`
Get detailed stock information

**Response:**
```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "market_cap": 2800000000000,
  "pe_ratio": 28.5,
  "dividend_yield": 0.0052,
  "52_week_high": 199.62,
  "52_week_low": 124.17
}
```

## Technical Details

### Pattern Detection Algorithms

Each pattern uses specific criteria:

**Bull Flag:**
- Flagpole: >5% upward move in first half
- Flag: -5% to +2% consolidation in second half
- Position: Near top of consolidation range

**Head and Shoulders:**
- Three peaks with middle peak highest
- Shoulders within 10% of each other
- Price breaks below neckline

**Volume Spike:**
- Current volume ≥ 2x the 20-period average
- Confidence scales with volume ratio

**MA Crossover:**
- Uses SMA 20 and SMA 50
- Detects crossover in last period
- Confidence based on separation

### Data Source

Uses `yfinance` library which provides:
- Free access to Yahoo Finance data
- Real-time and historical data
- No API key required
- OHLCV (Open, High, Low, Close, Volume) data

### Stock Universe

Currently scans 50 popular NASDAQ stocks including:
- AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA
- And 43 more major tech and growth companies

**To add more stocks:** Edit the `NASDAQ_TICKERS` list in `main.py`

## Architecture

```
nasdaq_pattern_scanner/
├── main.py                 # FastAPI server & endpoints
├── pattern_detector.py     # Pattern detection algorithms
├── static/
│   └── index.html         # Frontend interface
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Technology Stack
- **Backend**: FastAPI (Python)
- **Data**: yfinance (Yahoo Finance API)
- **Analysis**: pandas, numpy, scipy
- **Visualization**: Plotly
- **Frontend**: HTML5, CSS3, JavaScript

## Configuration

### Adjusting Pattern Sensitivity

Edit `pattern_detector.py` and modify `self.min_confidence`:
```python
def __init__(self):
    self.min_confidence = 0.5  # Lower = more results, Higher = stricter
```

### Adding Custom Patterns

1. Add detection method to `PatternDetector` class:
```python
def detect_my_pattern(self, df: pd.DataFrame) -> tuple[bool, float]:
    # Your logic here
    return pattern_found, confidence
```

2. Add endpoint in `main.py`:
```python
elif pattern == "my_pattern":
    pattern_found, confidence = detector.detect_my_pattern(df)
```

3. Add to patterns list in frontend

### Expanding Stock Universe

Edit `NASDAQ_TICKERS` in `main.py`:
```python
NASDAQ_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL',  # Add your tickers here
    ...
]
```

## Performance Tips

1. **Intraday Scanning**: Use shorter periods (1d-5d) for faster scans
2. **Daily/Weekly**: Can use longer periods (1mo-1y)
3. **Large Stock Lists**: Consider async processing for 100+ stocks
4. **Rate Limiting**: yfinance has rate limits; add delays if needed

## Troubleshooting

### No Data Retrieved
- Check internet connection
- Verify ticker symbols are valid
- Yahoo Finance may have temporary outages

### Slow Scanning
- Reduce number of stocks in `NASDAQ_TICKERS`
- Use shorter periods for intraday timeframes
- Close other applications using bandwidth

### Pattern Not Detected
- Try different timeframes
- Adjust period length
- Lower `min_confidence` threshold
- Pattern may genuinely not be present

## Limitations

1. **Historical Data Only**: Not real-time tick data
2. **Yahoo Finance Dependency**: Subject to their service availability
3. **Pattern Accuracy**: Technical analysis is probabilistic, not predictive
4. **No Trading Advice**: Tool is for educational/research purposes only

## Future Enhancements

Potential additions:
- [ ] Real-time data streaming
- [ ] Email/SMS alerts for pattern matches
- [ ] Portfolio tracking
- [ ] Backtesting capabilities
- [ ] Machine learning pattern recognition
- [ ] Support for more exchanges (NYSE, etc.)
- [ ] Pattern success rate analytics
- [ ] Options chain data
- [ ] News sentiment analysis

## Disclaimer

⚠️ **Important**: This tool is for educational and research purposes only. It does not constitute financial advice. Always do your own research and consult with financial professionals before making investment decisions. Past patterns do not guarantee future results.

## License

MIT License - Feel free to modify and use as needed.

## Support

For issues or questions:
1. Check this README
2. Review the code comments
3. Test with different parameters
4. Ensure dependencies are correctly installed

## Credits

Built with:
- FastAPI - Web framework
- yfinance - Market data
- Plotly - Interactive charts
- pandas/numpy - Data analysis
- scipy - Signal processing

---

**Happy Pattern Hunting! 📊🚀**
