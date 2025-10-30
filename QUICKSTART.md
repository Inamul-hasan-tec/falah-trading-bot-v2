# Quick Start Guide

Get up and running with Falah Trading Bot V2 in minutes!

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd /Users/inamulhasan/Desktop/Is\ doct/AI-TradingBot/falah-trading-bot-v2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Credentials

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Add your Zerodha API credentials:
```
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
```

### Step 3: Test the Setup

```bash
# Run in paper trading mode (simulation)
python main.py --mode paper
```

## 📊 Understanding the System

### Project Structure

```
falah-trading-bot-v2/
├── src/
│   ├── strategies/          # Trading strategies
│   │   ├── supertrend_strategy.py    # NEW! SuperTrend strategy
│   │   └── macd_rsi_strategy.py      # Improved MACD+RSI
│   ├── indicators/          # Technical indicators
│   │   └── supertrend.py             # SuperTrend indicator
│   ├── core/                # Core engine
│   └── utils/               # Utilities
├── config/
│   └── config.yaml          # Main configuration
├── docs/                    # Documentation
└── main.py                  # Entry point
```

### Key Improvements Over V1

1. **Clean Architecture**: Modular, organized code structure
2. **SuperTrend Strategy**: New trend-following strategy
3. **Better Documentation**: Comprehensive guides and examples
4. **Improved Risk Management**: Enhanced drawdown protection
5. **Easier Configuration**: YAML-based config system
6. **Testing Support**: Unit and integration tests

## 🎯 Running Different Modes

### Paper Trading (Recommended for Testing)

```bash
python main.py --mode paper
```

This simulates trading without risking real money.

### Live Trading (Real Money!)

```bash
python main.py --mode live
```

⚠️ **WARNING**: This executes real trades with real money!

### Backtesting

```bash
python main.py --mode backtest --start 2023-01-01 --end 2024-01-01
```

Test strategies on historical data.

### API Server

```bash
python main.py --mode api
```

Access dashboard at `http://localhost:8000`

## 🔧 Configuration

### Basic Configuration

Edit `config/config.yaml`:

```yaml
trading:
  initial_capital: 100000      # Starting capital
  max_positions: 5             # Max concurrent positions
  risk_per_trade: 0.01         # 1% risk per trade

strategies:
  active:
    - "supertrend"             # Use SuperTrend strategy
    - "macd_rsi"               # Use MACD+RSI strategy
```

### Strategy-Specific Configuration

#### SuperTrend Strategy

```yaml
supertrend_strategy:
  enabled: true
  period: 10                   # SuperTrend period
  multiplier: 3.0              # SuperTrend multiplier
  profit_target_pct: 0.10      # 10% profit target
  stop_loss_atr_mult: 2.5      # Stop loss = 2.5 × ATR
```

#### MACD + RSI Strategy

```yaml
macd_rsi_strategy:
  enabled: true
  rsi_min: 40                  # Minimum RSI for entry
  rsi_max: 70                  # Maximum RSI for entry
  profit_target_pct: 0.08      # 8% profit target
```

## 📈 Using Specific Strategies

### Run with SuperTrend Only

```bash
python main.py --strategy supertrend
```

### Run with Multiple Strategies

```bash
python main.py --strategies supertrend,macd_rsi
```

### Run with Custom Config

```bash
python main.py --config my_config.yaml
```

## 🎓 Understanding SuperTrend Strategy

### What is SuperTrend?

SuperTrend is a trend-following indicator that:
- Shows clear BUY (green) and SELL (red) signals
- Adapts to market volatility using ATR
- Provides dynamic support/resistance levels

### When to Use SuperTrend

✅ **Best for:**
- Trending markets
- Swing trading (multi-day positions)
- Volatile stocks
- Clear directional moves

❌ **Avoid in:**
- Sideways/choppy markets
- Very low volatility
- News-driven stocks

### SuperTrend Entry Example

```
Symbol: RELIANCE
Price: ₹2,450
SuperTrend: ₹2,420 (Green - Bullish)
Signal: BUY

Entry Price: ₹2,450
Stop Loss: ₹2,375 (2.5 × ATR below entry)
Target: ₹2,695 (10% profit)
Position Size: 100 shares (based on 1% risk)
```

### SuperTrend Exit Example

```
Exit when:
1. SuperTrend turns Red (bearish)
2. Price closes below SuperTrend line
3. Stop loss hit
4. Profit target reached
```

## 📊 Monitoring Your Trades

### View Logs

```bash
# Real-time logs
tail -f data/logs/trading.log

# Error logs
tail -f data/logs/errors.log
```

### Check Positions

```bash
# View current positions
cat data/positions.json

# View trade history
cat data/trade_log.csv
```

### API Dashboard

Start API server and visit:
- Dashboard: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Portfolio: `http://localhost:8000/api/portfolio`

## 🛡️ Risk Management

### Default Risk Settings

```yaml
risk_management:
  max_daily_loss_pct: 0.05     # Stop trading if 5% daily loss
  max_drawdown_pct: 0.10       # Alert at 10% drawdown
  cooling_mode_threshold: 0.08  # Reduce risk at 8% drawdown
```

### Position Sizing

Position size is automatically calculated based on:
1. **Risk per trade** (default: 1% of capital)
2. **ATR** (volatility measure)
3. **Stop loss distance**

Formula:
```
Position Size = (Capital × Risk%) / (ATR × Stop Loss Multiplier)
```

Example:
```
Capital: ₹100,000
Risk: 1% = ₹1,000
ATR: ₹30
Stop Loss Mult: 2.5
Stop Distance: ₹75

Position Size = ₹1,000 / ₹75 = 13 shares
```

## 🔍 Troubleshooting

### Issue: "Authentication failed"

**Solution**: Check your API credentials in `.env` file

```bash
# Verify credentials
cat .env | grep KITE_API
```

### Issue: "No data found for symbol"

**Solution**: Fetch historical data first

```bash
python scripts/fetch_data.py --symbols RELIANCE,TCS,INFY
```

### Issue: "Strategy not found"

**Solution**: Check strategy name in config

```bash
# Valid strategy names:
# - supertrend
# - macd_rsi
```

### Issue: "Insufficient capital"

**Solution**: Adjust position sizing or increase capital

```yaml
trading:
  risk_per_trade: 0.005  # Reduce to 0.5%
```

## 📚 Next Steps

### 1. Read Strategy Documentation

```bash
cat docs/STRATEGIES.md
```

Learn about:
- SuperTrend strategy details
- MACD+RSI strategy details
- Strategy comparison
- When to use each strategy

### 2. Run Backtests

```bash
python scripts/backtest.py --strategy supertrend --start 2023-01-01
```

Validate strategies on historical data.

### 3. Customize Configuration

Edit `config/config.yaml` to:
- Adjust risk parameters
- Enable/disable strategies
- Modify indicator settings
- Set profit targets

### 4. Set Up Notifications

Add Telegram credentials to `.env`:

```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

Get alerts for:
- Trade executions
- Position updates
- Daily P&L summaries
- Risk warnings

## 💡 Pro Tips

### Tip 1: Start Small

Begin with paper trading or small capital to understand the system.

### Tip 2: Use Multiple Strategies

Diversify by running both SuperTrend and MACD+RSI strategies.

### Tip 3: Monitor Daily

Check logs and positions daily, especially in the first week.

### Tip 4: Adjust for Market Conditions

- **Trending markets**: Use SuperTrend
- **Choppy markets**: Reduce position sizes or pause trading
- **High volatility**: Widen stop losses

### Tip 5: Keep Learning

Review closed trades to understand what works and what doesn't.

## 🆘 Getting Help

### Documentation

- **README.md**: Overview and installation
- **STRATEGIES.md**: Detailed strategy documentation
- **API.md**: API reference
- **RISK_MANAGEMENT.md**: Risk management guide

### Logs

Check logs for detailed information:
```bash
tail -f data/logs/trading.log
```

### Configuration

Review your configuration:
```bash
cat config/config.yaml
```

## ⚠️ Important Reminders

1. **Test First**: Always test in paper trading mode before going live
2. **Start Small**: Begin with small capital to validate the system
3. **Monitor Regularly**: Check positions and logs daily
4. **Respect Risk Limits**: Never override risk management rules
5. **Stay Informed**: Keep up with market news and conditions

## 🎉 You're Ready!

You now have a professional trading system with:
- ✅ SuperTrend strategy
- ✅ MACD+RSI strategy
- ✅ Automated risk management
- ✅ Position sizing
- ✅ Real-time monitoring
- ✅ Comprehensive documentation

**Happy Trading! 🚀**

---

**Questions or Issues?**

Check the documentation in the `docs/` folder or review the logs in `data/logs/`.

**Version**: 2.0.0  
**Last Updated**: October 2024
