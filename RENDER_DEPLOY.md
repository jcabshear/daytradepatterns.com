# 🚀 Deploy to Render.com - Complete Guide

## Why Render?

- ✅ **Free tier available** (enough to start)
- ✅ **Easy GitHub integration** (auto-deploy on push)
- ✅ **Environment variables** (secure API key storage)
- ✅ **Automatic HTTPS** (secure by default)
- ✅ **Custom domains** (professional URLs)

## Step-by-Step Deployment

### 1. Prepare Your Repository

**Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit - Marketstack Pattern Scanner"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nasdaq-pattern-scanner.git
git push -u origin main
```

### 2. Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repos

### 3. Create New Web Service

1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub repo
4. Fill in details:

```
Name: nasdaq-pattern-scanner
Environment: Python 3
Region: Oregon (US West) - or closest to you
Branch: main
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### 4. Configure Environment Variables

**Click "Advanced" → "Add Environment Variable"**

Add the following:

```
Key: MARKETSTACK_API_KEY
Value: [paste your Marketstack API key]
```

**Optional variables:**
```
Key: PORT
Value: 8000

Key: PYTHON_VERSION
Value: 3.9.0
```

### 5. Choose Your Plan

**Free Tier:**
- ✅ Good for testing
- ✅ 750 hours/month
- ⚠️ Spins down after 15 min inactivity
- ⚠️ Slower cold starts

**Starter ($7/month):**
- ✅ Always on (no spin down)
- ✅ Faster performance
- ✅ Custom domains
- ✅ Better for production

### 6. Deploy!

1. Click "Create Web Service"
2. Wait 2-3 minutes for deployment
3. Your app will be live at: `https://your-app-name.onrender.com`

## 🔒 Security Best Practices

### Never Commit API Keys!

**Create .gitignore:**
```bash
cat > .gitignore << EOF
.env
__pycache__/
*.pyc
.DS_Store
EOF
```

**Use environment variables:**
```python
# Good ✅
api_key = os.getenv('MARKETSTACK_API_KEY')

# Bad ❌
api_key = "1234567890abcdef"  # Never do this!
```

## 🔍 Troubleshooting Render Deployment

### Check Deployment Logs

In Render dashboard:
1. Click your service
2. Go to "Logs" tab
3. Look for errors

**Common issues:**

**"Module not found"**
```
Solution: Check requirements.txt is in root directory
Verify all dependencies are listed
```

**"Port already in use"**
```
Solution: Let Render assign the PORT
Don't hardcode port 8000
```

**"API key not set"**
```
Solution: Go to Environment tab
Verify MARKETSTACK_API_KEY is set
Click "Manual Deploy" to restart
```

### Successful Deployment Logs

You should see:
```
✅ Marketstack client initialized
📊 NASDAQ-100 loaded: 100 stocks
💰 API Efficiency: 100 stocks = 1 API call!
🌐 Starting server on http://0.0.0.0:8000
```

## 🌐 Custom Domain Setup

### 1. Buy a Domain
- Namecheap.com
- Google Domains
- Cloudflare

### 2. Add Custom Domain in Render

1. Go to your service → Settings
2. Click "Add Custom Domain"
3. Enter your domain: `scanner.yourdomain.com`
4. Render shows DNS records to add

### 3. Configure DNS

**Add CNAME record:**
```
Type: CNAME
Name: scanner (or @)
Value: your-app-name.onrender.com
TTL: 3600
```

Wait 5-60 minutes for DNS propagation.

### 4. Enable HTTPS

Render automatically provisions SSL certificate!
Your site will be accessible at: `https://scanner.yourdomain.com`

## 📈 Performance Optimization

### Enable Persistent Disk (Paid Plans)

For better caching across deployments:

1. Settings → Disk
2. Add disk: `/data`
3. Update code to use `/data` for cache

### Health Checks

Add health check endpoint:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

In Render:
- Settings → Health Check Path: `/health`

### Auto-Deploy on Push

Already enabled by default!

Push to GitHub:
```bash
git add .
git commit -m "Update patterns"
git push
```

Render auto-deploys in 2-3 minutes ✨

## 💰 Cost Optimization

### Free Tier Strategy

**Pros:**
- $0/month
- Great for testing
- 750 hours included

**Cons:**
- Spins down after 15 min
- Cold start delay (10-20 seconds)
- Not ideal for frequent use

**Best for:**
- Personal projects
- Occasional scanning
- Demo purposes

### Starter Plan Strategy ($7/month)

**Pros:**
- Always on (no spin down)
- Instant responses
- Better for daily use

**Best for:**
- Regular scanning
- Multiple users
- Production use

**Total monthly cost:**
```
Render Starter: $7/month
Marketstack Basic: $9.99/month
Total: $16.99/month
```

Still cheaper than most paid scanners! 📊

## 🔄 Update Your App

### Deploy New Code

```bash
# Make changes locally
git add .
git commit -m "Add new pattern"
git push origin main

# Render auto-deploys!
```

### Manual Deploy

In Render dashboard:
- Click "Manual Deploy" → "Deploy latest commit"

### Environment Variable Updates

1. Settings → Environment
2. Edit or add variables
3. Service restarts automatically

## 🐛 Debug Common Issues

### App won't start

**Check logs for:**
```
ImportError: No module named 'X'
→ Add missing package to requirements.txt

OSError: Port already in use
→ Remove hardcoded port, let Render assign

RuntimeError: MARKETSTACK_API_KEY not set
→ Add environment variable
```

### API not working

**Test locally first:**
```bash
export MARKETSTACK_API_KEY="your_key"
python main.py
# Visit http://localhost:8000
```

If works locally but not on Render:
1. Check environment variable is set
2. Check API key is valid
3. Check Marketstack account status

### Slow performance

**On free tier:**
- Expected on cold starts
- Upgrade to Starter plan

**On paid tier:**
- Check Render region (use closest)
- Monitor resource usage
- Consider caching optimization

## 📊 Monitoring

### Render Dashboard

**Monitor:**
- Deployment status
- Live logs
- CPU/Memory usage
- Request count

### Custom Monitoring

Add endpoint:
```python
@app.get("/api/stats")
async def get_stats():
    return {
        "uptime": get_uptime(),
        "total_scans": scan_counter,
        "cache_hits": cache_hits,
        "api_calls": api_calls
    }
```

### Alerts

Render can notify you:
- Deployment failures
- Service crashes
- High resource usage

Settings → Notifications

## 🎯 Production Checklist

Before going live:

- [ ] .gitignore includes .env
- [ ] API key set in Render environment
- [ ] Health check endpoint added
- [ ] Error handling implemented
- [ ] Logs properly configured
- [ ] HTTPS enabled (automatic)
- [ ] Custom domain configured (optional)
- [ ] Tested all patterns work
- [ ] Monitored API usage
- [ ] Set up alerts

## 🌟 You're Live!

Your pattern scanner is now:
- ✅ Deployed to the cloud
- ✅ Accessible 24/7
- ✅ Secured with HTTPS
- ✅ Auto-deploying on changes
- ✅ Monitoring API usage

Share your link: `https://your-app-name.onrender.com` 🎉

---

**Questions?** Check Render docs: https://render.com/docs
