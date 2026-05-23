# 🚀 Jules System - Deployment Guide for iPhone Access

## Quick Deployment to Railway.app (FREE - 2-3 weeks+)

Railway.app gives you **$5 free credits per month** which is more than enough to run Jules for 2-3+ weeks continuously.

### Step 1: Sign Up to Railway
1. Go to: **https://railway.app**
2. Click "Start Project"
3. Sign in with **GitHub** (select your `alanbot88-cmyk` account)
4. Authorize Railway to access your repositories

### Step 2: Create New Project
1. Click **"Create New Project"**
2. Select **"Deploy from GitHub"**
3. Find and select **`alanbot88-cmyk/Jules`** repository
4. Click **"Deploy Now"**

Railway will automatically detect the `Dockerfile` and start building! ✅

### Step 3: Add Environment Variables
1. After deployment starts, go to **"Variables"** tab
2. Add your API keys (optional for preview):
   ```
   GEMINI_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   DEEPSEEK_API_KEY=your_key_here
   ```
3. If you don't have keys, the system will run in demo mode

### Step 4: Get Your Public URL
1. Go to **"Settings"** tab
2. Under "Deployment", you'll see a public domain like:
   ```
   https://jules-production-xxxx.up.railway.app
   ```
3. **Copy this URL** 📋

### Step 5: Access from iPhone
1. Open **Safari** on your iPhone
2. Paste the URL:
   ```
   https://jules-production-xxxx.up.railway.app
   ```
3. You can now see your live dashboard! 🎉

---

## Alternative: Render.com (Also Free)

If Railway has issues:

1. Go to: **https://render.com**
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your `Jules` repository
5. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Port**: `8000`
6. Deploy and get your free `*.onrender.com` URL

---

## Deployment Status Check

After clicking "Deploy", you'll see:

```
✅ Build in progress...
📦 Docker image building
🚀 Starting container
🌐 Service online
```

Once it shows **"Live"** (green), your app is ready! ✨

---

## What You Can Do on iPhone

✅ Submit tasks to the system
✅ View real-time agent status
✅ See live event stream
✅ Monitor system metrics
✅ Track task execution
✅ WebSocket live updates

---

## Monitoring Your Deployment

**Check logs:**
1. In Railway dashboard, click your project
2. Go to **"Logs"** to see system output
3. See real-time agent activity

**Monitor metrics:**
- CPU usage
- Memory usage
- Network bandwidth

---

## Keep It Running 24/7

Railway keeps your app running continuously:
- ✅ Automatic restarts on crash
- ✅ Free tier is always on
- ✅ $5 credit = ~2-3 weeks of runtime
- ✅ When credits run out, either add payment or redeploy

---

## Troubleshooting

**URL not loading?**
```
1. Wait 2-3 minutes after deployment
2. Check Railway logs for errors
3. Refresh page on iPhone
```

**WebSocket connection fails?**
```
1. Ensure wss:// protocol works (Railway handles this)
2. Check browser console on desktop
3. Try refreshing page
```

**Agents not showing?**
```
1. Check environment variables are set
2. View Railway logs
3. Restart deployment
```

---

## Costs Breakdown

**Railway Free Tier:**
- $5/month credit
- Jules uses ~0.7 GB RAM
- Estimated runtime: **20+ days per month**

**Your Timeline:**
- ✅ Week 1-2: Full functionality (plenty of credits)
- ✅ Week 3: Still running strong
- ⚠️ After credits: Upgrade ($5/month) or redeploy

---

## 📱 Your iPhone Link Format

Once deployed, your link will be:

```
https://jules-production-[random-id].up.railway.app
```

**Bookmark this in Safari for easy access!** 🔖

---

## Next Steps

1. **Go to Railway.app →** Sign up with GitHub
2. **Deploy your Jules repo** → Takes 2-3 minutes
3. **Get the URL** → Copy from Railway dashboard
4. **Open on iPhone** → Paste into Safari
5. **Done!** → You can now see your system live 🎉

---

Need help? All files are already in your repo:
- ✅ `Dockerfile` - Container setup
- ✅ `requirements.txt` - Dependencies
- ✅ `Procfile` - Process definition
- ✅ `main.py` - Application entry

**Everything is ready to deploy!** 🚀
