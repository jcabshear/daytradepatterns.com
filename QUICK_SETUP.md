# 🚀 Quick Setup Guide - Marketstack Edition

## Step 1: Get Your API Key (2 minutes)

1. Go to https://marketstack.com/signup/free
2. Create a free account
3. Verify your email
4. Copy your API key from dashboard

**Pricing:**
- Free: 100 calls/month (very limited)
- Basic: $9.99/mo - 10,000 calls ✅ **RECOMMENDED**
- Pro: $49.99/mo - 100,000 calls

## Step 2: Install Dependencies (1 minute)

```bash
cd nasdaq_pattern_scanner
pip install -r requirements.txt
```

## Step 3: Set API Key (30 seconds)

**Option A: Environment Variable (Quick)**
```bash
export MARKETSTACK_API_KEY="paste_your_key_here"
```

**Option B: .env File (Persistent)**
```bash
cp .env.example .env
nano .env  # or use any text editor
# Add: MARKETSTACK_API_KEY=your_key_here
```

## Step 4: Run the App (10 seconds)

```bash
python main.py
```

Open browser: http://localhost:8000

## Step 5: First Scan (20 seconds)

1. Select "Volume Spike" pattern
2. Keep "1d" timeframe (most efficient)
3. Keep "1mo" period
4. Click "Scan Market"
5. Watch the magic! 🎉

## 🎯 What Just Happened?

✅ Fetched 100 stocks in **1 API call** (not 100!)  
✅ Detected patterns across entire NASDAQ-100  
✅ Cached results for 15 minutes  
✅ Used only **1 API call** from your monthly quota  

## 💰 API Usage Estimate

**With Basic Plan (10,000 calls/month):**
- Each scan = 1 call
- With caching = ~0.5 calls average
- **You can do 300+ scans per month easily!**

That's 10+ scans per day! 🚀

## 🔍 Check Your Usage

```bash
curl http://localhost:8000/api/usage
```

Output:
```json
{
  "api_calls_made": 1,
  "cache_entries": 1,
  "cache_hit_rate": "0%",
  "estimated_monthly_usage": 30
}
```

## 🎨 Try Different Patterns

**Most Common (Easiest to Find):**
- Volume Spike ⚡ (high success rate)
- MA Crossover (Bullish/Bearish) 📈

**Moderate (Sometimes Present):**
- Bull Flag 🚩
- Bear Flag 🚩
- Gap Up/Down 📊

**Rare (Need Right Market Conditions):**
- Head and Shoulders 👤
- Double Top/Bottom 🔝

## 🐛 Troubleshooting

**"No patterns found":**
- Try "Volume Spike" pattern first
- Use 1d timeframe with 1mo period
- Market might not have patterns today (normal!)

**"API key not set":**
```bash
# Check if set:
echo $MARKETSTACK_API_KEY

# If empty, set it:
export MARKETSTACK_API_KEY="your_key"
```

**"Rate limit exceeded":**
- Wait 60 seconds
- App has built-in rate limiting
- Consider upgrading plan

## 📊 Deploy to Render (5 minutes)

1. Push code to GitHub
2. Create Render account
3. New Web Service → Connect repo
4. Add environment variable: `MARKETSTACK_API_KEY=your_key`
5. Deploy!

Done! Your scanner is now live 24/7 🌐

## 🎯 Next Steps

1. ✅ Run first scan
2. ✅ Try different patterns
3. ✅ Check API usage
4. ✅ Explore interactive charts
5. ✅ Deploy to cloud (optional)

## 💡 Pro Tips

**Save API Calls:**
- Run multiple pattern scans within 15 minutes (uses cache)
- Use EOD (1d) data when possible (most stable)
- Clear cache only when you need fresh data

**Best Results:**
- Scan during market hours (9:30 AM - 4 PM ET)
- Try multiple timeframes for same pattern
- Volume Spike works great on 1d timeframe
- MA Crossover needs longer periods (3mo+)

## 🎉 You're Ready!

Start finding patterns efficiently with Marketstack! 📈🚀

---

**Questions?** Check the main README.md for detailed documentation.
