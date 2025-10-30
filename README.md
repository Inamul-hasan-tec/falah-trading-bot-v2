# Falah Trading Bot V2 🚀

A professional-grade algorithmic trading system for Indian stock markets using Zerodha Kite API. This is a complete refactor of the original system with improved architecture, comprehensive documentation, and enhanced trading strategies including SuperTrend indicator integration.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Trading Strategies](#trading-strategies)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Risk Management](#risk-management)
- [Backtesting](#backtesting)
- [Contributing](#contributing)

## ✨ Features

### Core Capabilities
- **Multi-Timeframe Analysis**: Daily, Hourly, and 15-minute timeframe integration
- **Advanced Indicators**: SuperTrend, MACD, RSI, Bollinger Bands, ATR, Chandelier Exit
- **Multiple Strategies**: Pluggable strategy system with pre-built strategies
- **Risk Management**: Position sizing, drawdown protection, capital allocation
- **Live Trading**: Real-time price streaming and order execution
- **Backtesting Engine**: Historical strategy validation
- **Portfolio Tracking**: Real-time P&L monitoring and position management
- **Notifications**: Telegram alerts for trades and portfolio updates

### New Features in V2
- **SuperTrend Strategy**: Dedicated trend-following strategy using SuperTrend indicator
- **Modular Architecture**: Clean separation of concerns with pluggable components
- **Enhanced Documentation**: Comprehensive guides and API documentation
- **Improved Risk Controls**: Advanced drawdown protection and cooling mode
- **Better Testing**: Unit tests and integration tests
- **Configuration Management**: Environment-based configuration system
- **API Dashboard**: FastAPI-based REST API for monitoring and control

## 🏗️ Architecture

```
falah-trading-bot-v2/
├── src/
│   ├── core/               # Core trading engine
│   │   ├── engine.py       # Main trading engine
│   │   ├── broker.py       # Broker API integration (Zerodha)
│   │   ├── data_manager.py # Historical & live data management
│   │   ├── order_manager.py # Order placement & tracking
│   │   ├── position_manager.py # Position tracking
│   │   └── portfolio.py    # Portfolio management
│   ├── strategies/         # Trading strategies
│   │   ├── base.py         # Base strategy class
│   │   ├── supertrend_strategy.py # SuperTrend-based strategy
│   │   ├── macd_rsi_strategy.py # MACD + RSI strategy
│   │   ├── bollinger_breakout.py # Bollinger Band breakout
│   │   └── multi_timeframe.py # Multi-timeframe strategy
│   ├── indicators/         # Technical indicators
│   │   ├── supertrend.py   # SuperTrend indicator
│   │   ├── momentum.py     # RSI, MACD, Stochastic
│   │   ├── trend.py        # EMA, SMA, ADX
│   │   ├── volatility.py   # ATR, Bollinger Bands
│   │   └── volume.py       # Volume indicators
│   ├── utils/              # Utility modules
│   │   ├── risk_manager.py # Risk management
│   │   ├── capital_manager.py # Capital allocation
│   │   ├── logger.py       # Logging utilities
│   │   ├── notifier.py     # Telegram notifications
│   │   └── helpers.py      # Helper functions
│   └── api/                # REST API
│       ├── app.py          # FastAPI application
│       ├── routes.py       # API routes
│       └── models.py       # API data models
├── config/                 # Configuration files
│   ├── config.yaml         # Main configuration
│   ├── strategies.yaml     # Strategy parameters
│   └── credentials.json    # API credentials (gitignored)
├── data/                   # Data storage
│   ├── historical/         # Historical price data
│   ├── live/              # Live candle data
│   └── logs/              # Application logs
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── backtest/          # Backtesting scripts
├── docs/                   # Documentation
│   ├── STRATEGIES.md      # Strategy documentation
│   ├── API.md             # API documentation
│   ├── RISK_MANAGEMENT.md # Risk management guide
│   └── DEPLOYMENT.md      # Deployment guide
├── scripts/               # Utility scripts
│   ├── fetch_data.py      # Data fetching script
│   ├── backtest.py        # Backtesting script
│   └── setup.py           # Setup script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── main.py               # Application entry point
```

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- Zerodha Kite Connect API credentials
- (Optional) Telegram Bot Token for notifications

### Step 1: Clone and Setup

```bash
cd /Users/inamulhasan/Desktop/Is\ doct/AI-TradingBot/falah-trading-bot-v2
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required credentials:
- `KITE_API_KEY`: Your Zerodha API key
- `KITE_API_SECRET`: Your Zerodha API secret
- `TELEGRAM_BOT_TOKEN`: (Optional) Telegram bot token
- `TELEGRAM_CHAT_ID`: (Optional) Your Telegram chat ID

### Step 3: Initial Data Fetch

```bash
python scripts/fetch_data.py --symbols NIFTY50 --period 2y
```

## ⚙️ Configuration

### Main Configuration (`config/config.yaml`)

```yaml
trading:
  initial_capital: 100000
  max_positions: 5
  risk_per_trade: 0.01  # 1% risk per trade
  max_position_size: 0.20  # 20% of capital per position
  
risk_management:
  max_daily_loss: 0.05  # 5% daily loss limit
  max_drawdown: 0.10  # 10% drawdown threshold
  cooling_mode_threshold: 0.08  # 8% drawdown triggers cooling
  
indicators:
  atr_period: 14
  atr_multiplier: 2.8
  supertrend_period: 10
  supertrend_multiplier: 3.0
  rsi_period: 14
  
execution:
  order_type: "MARKET"  # MARKET or LIMIT
  product_type: "CNC"   # CNC for delivery, MIS for intraday
```

## 📊 Trading Strategies

### 1. SuperTrend Strategy (New!)

**Entry Conditions:**
- SuperTrend indicator turns green (bullish)
- Price closes above SuperTrend line
- Volume confirmation (above 20-period average)
- Daily timeframe trend confirmation (price > EMA200)

**Exit Conditions:**
- SuperTrend indicator turns red (bearish)
- Price closes below SuperTrend line
- Trailing stop loss hit (based on ATR)
- Target profit reached (configurable)

**Parameters:**
```yaml
supertrend_strategy:
  period: 10
  multiplier: 3.0
  volume_confirmation: true
  daily_trend_filter: true
  profit_target: 0.10  # 10%
  stop_loss_atr_mult: 2.5
```

### 2. MACD + RSI Strategy (Existing, Improved)

**Entry Conditions:**
- MACD line > 0 and MACD signal > 0
- RSI between 40-70 (not overbought/oversold)
- Price above Bollinger Band lower band
- Daily trend confirmation

**Exit Conditions:**
- RSI < 70 and price < BB upper band
- SuperTrend turns bearish
- Chandelier Exit stop loss hit

### 3. Multi-Timeframe Strategy

Combines signals from multiple timeframes for higher probability trades.

## 🎯 Usage

### Running the Bot

```bash
# Live trading mode
python main.py --mode live

# Paper trading mode (simulation)
python main.py --mode paper

# Backtest mode
python main.py --mode backtest --start 2023-01-01 --end 2024-01-01
```

### Using Specific Strategies

```bash
# Run with SuperTrend strategy
python main.py --strategy supertrend

# Run with multiple strategies
python main.py --strategies supertrend,macd_rsi,bollinger_breakout
```

### API Server

```bash
# Start API server
python -m src.api.app

# Access dashboard at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## 📡 API Documentation

### REST API Endpoints

#### Portfolio
- `GET /api/portfolio` - Get portfolio summary
- `GET /api/positions` - Get open positions
- `GET /api/positions/history` - Get position history

#### Trading
- `POST /api/trade/buy` - Place buy order
- `POST /api/trade/sell` - Place sell order
- `POST /api/trade/exit/{symbol}` - Exit position

#### Monitoring
- `GET /api/signals` - Get latest trading signals
- `GET /api/logs` - Get application logs
- `GET /api/performance` - Get performance metrics

See [docs/API.md](docs/API.md) for detailed API documentation.

## 🛡️ Risk Management

### Position Sizing
- **ATR-Based**: Position size calculated based on ATR and risk per trade
- **Capital-Based**: Maximum position size as percentage of total capital
- **Dynamic Adjustment**: Reduces position size during drawdowns

### Stop Loss Management
- **Initial Stop**: ATR-based stop loss on entry
- **Trailing Stop**: Chandelier Exit or SuperTrend-based trailing
- **Time-Based**: Exit positions held beyond threshold

### Drawdown Protection
- **Cooling Mode**: Reduces position sizes when drawdown exceeds threshold
- **Circuit Breaker**: Stops trading when daily loss limit hit
- **Recovery Mode**: Gradually increases position sizes as equity recovers

See [docs/RISK_MANAGEMENT.md](docs/RISK_MANAGEMENT.md) for detailed risk management guide.

## 📈 Backtesting

### Running Backtests

```bash
# Backtest single strategy
python scripts/backtest.py --strategy supertrend --start 2023-01-01 --end 2024-01-01

# Backtest multiple strategies
python scripts/backtest.py --strategies supertrend,macd_rsi --start 2023-01-01

# Generate detailed report
python scripts/backtest.py --strategy supertrend --report --output results/
```

### Backtest Metrics
- Total Return
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor
- Average Trade Duration

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=src tests/
```

## 📝 Logging

Logs are stored in `data/logs/` with the following structure:
- `trading.log` - Main trading activity
- `orders.log` - Order execution logs
- `errors.log` - Error logs
- `performance.log` - Performance metrics

## 🔔 Notifications

Configure Telegram notifications for:
- Trade executions
- Position updates
- Daily P&L summaries
- Risk alerts
- System errors

## 🤝 Contributing

This is a personal trading system, but improvements are welcome:
1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Test thoroughly before deployment

## ⚠️ Disclaimer

This trading bot is for educational and personal use only. Trading in financial markets involves substantial risk of loss. Past performance does not guarantee future results. Use at your own risk.

## 📄 License

Private use only. Not for distribution.

## 🙏 Acknowledgments

- Original system developed by a passionate trader
- Refactored for better maintainability and performance
- Built with Python, pandas, pandas-ta, and Zerodha Kite Connect API

---

**Version**: 2.0.0  
**Last Updated**: October 2024  
**Status**: Active Development
