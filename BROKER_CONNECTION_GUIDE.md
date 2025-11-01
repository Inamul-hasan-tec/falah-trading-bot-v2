# 🔌 Zerodha Broker Connection Guide

**Step-by-step guide to connect the trading bot to Zerodha**

---

## 📋 Prerequisites

✅ Zerodha account  
✅ API Key: `ijzeuwuylr3g0kug`  
✅ API Secret: `yy1wd2wn8r0wx4mus00vxllgss03nuqx`  
✅ Bot installed on VPS  

---

## 🚀 Connection Process (Do This Together)

### Step 1: Generate Login URL

On VPS, run:

```bash
cd /root/trading-bots/falah-trading-bot-v2
source venv/bin/activate
python3 connect_broker.py
```

This will show a URL like:
```
https://kite.zerodha.com/connect/login?api_key=ijzeuwuylr3g0kug&v=3
```

---

### Step 2: Login to Zerodha

1. **Copy the URL** and open in browser
2. **Login** with Zerodha credentials
3. **Enter PIN** for 2FA
4. **Authorize** the app

---

### Step 3: Get Request Token

After authorization, browser will redirect to:
```
http://127.0.0.1/?request_token=XXXXXX&action=login&status=success
```

**Copy the `request_token` value** (the XXXXXX part)

---

### Step 4: Complete Authentication

Back on VPS, paste the request token when prompted:

```
Enter request token: [paste token here]
```

The bot will:
- Generate access token
- Save it for future use
- Test the connection
- Show account balance

---

### Step 5: Verify Connection

You should see:
```
✅ Authentication successful!
📊 Account Balance: ₹XXXXX
📈 Current Positions: X
✅ Connection verified!
```

---

## 🧪 Test Real Data Fetching

### Test 1: Get Live Price

```bash
python3 test_live_price.py
```

Expected output:
```
Stock: RELIANCE
Current Price: ₹2,450.50
Change: +1.2%
Volume: 1,234,567
```

---

### Test 2: Fetch Historical Data

```bash
python3 test_historical_data.py
```

Expected output:
```
Fetching RELIANCE data for last 30 days...
✅ Downloaded 30 candles
Date range: 2024-10-01 to 2024-10-31
```

---

### Test 3: Generate Real Signal

```bash
python3 test_real_signal.py
```

Expected output:
```
Analyzing RELIANCE with SuperTrend...
Current Price: ₹2,450
SuperTrend: ₹2,420 (GREEN)
Signal: BUY ✅
Confidence: 75%
Stop Loss: ₹2,375
Target: ₹2,695
```

---

## 🎯 What Happens Next

### Paper Trading Mode

The bot will:
1. ✅ Fetch live prices every minute
2. ✅ Calculate indicators in real-time
3. ✅ Generate buy/sell signals
4. ✅ Simulate trades (NO REAL MONEY)
5. ✅ Track virtual P&L
6. ✅ Send Telegram notifications

### Start Paper Trading

```bash
python3 main.py --mode paper
```

You'll see:
```
╔═══════════════════════════════════════════════════════════╗
║         FALAH TRADING BOT V2 - PAPER TRADING            ║
║  ℹ️  Simulation mode - No real trades will be executed   ║
╚═══════════════════════════════════════════════════════════╝

[09:15:00] 📊 Market opened
[09:15:01] 📈 Fetching data for 5 stocks...
[09:15:05] ✅ Data fetched
[09:15:06] 🔍 Analyzing RELIANCE...
[09:15:07] 🎯 BUY signal generated: RELIANCE @ ₹2,450
[09:15:08] 📝 Simulated BUY: 100 shares @ ₹2,450
[09:15:08] 💰 Virtual position opened
```

---

## 🔒 Security Notes

1. **Access token is saved locally** in `data/kite_tokens.json`
2. **Token expires daily** - need to re-authenticate each day
3. **API credentials are in .env** - never share this file
4. **Paper mode is safe** - no real trades executed

---

## ⚠️ Important Reminders

### Before Going Live

- [ ] Run paper trading for **minimum 2 weeks**
- [ ] Verify win rate matches expectations (55-60%)
- [ ] Check max drawdown stays under 15%
- [ ] Understand every trade the bot makes
- [ ] Start with small capital (₹50K)

### Daily Monitoring

- [ ] Check Telegram notifications
- [ ] Review open positions
- [ ] Verify stop losses are in place
- [ ] Check daily P&L
- [ ] Review logs for errors

---

## 🆘 Troubleshooting

### Issue: "Invalid API Key"
**Solution:** Check .env file has correct credentials

### Issue: "Request token expired"
**Solution:** Generate new login URL and re-authenticate

### Issue: "Connection timeout"
**Solution:** Check internet connection, try again

### Issue: "Insufficient funds"
**Solution:** In paper mode, this shouldn't happen. Check config.

---

## 📞 Next Steps After Connection

1. ✅ Connection successful
2. ✅ Test live data fetching
3. ✅ Generate first real signal
4. ✅ Start paper trading
5. ⏳ Monitor for 2 weeks
6. ⏳ Go live with small capital

---

**Ready to connect? Let's do this!** 🚀
