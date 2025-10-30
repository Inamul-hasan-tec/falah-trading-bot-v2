# 🚀 Phase 2 & 3 Implementation Guide

Complete guide to implement broker integration, data management, and live trading.

---

## 📋 Phase 2: Core Integration (Weeks 1-4)

### Step 1: Broker Interface (Zerodha Kite Connect)

Create: `src/core/broker.py`

```python
"""
Zerodha Kite Connect Broker Interface
Handles authentication, orders, and data fetching
"""

from kiteconnect import KiteConnect, KiteTicker
import logging
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ZerodhaBroker:
    """Interface to Zerodha Kite Connect API"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.kite = KiteConnect(api_key=api_key)
        self.access_token = None
        self.tokens_file = "data/kite_tokens.json"
        
        # Load saved token
        self._load_token()
    
    def _load_token(self):
        """Load saved access token"""
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'r') as f:
                data = json.load(f)
                self.access_token = data.get('access_token')
                
                if self.access_token:
                    self.kite.set_access_token(self.access_token)
                    logger.info("Loaded saved access token")
    
    def _save_token(self):
        """Save access token"""
        os.makedirs(os.path.dirname(self.tokens_file), exist_ok=True)
        with open(self.tokens_file, 'w') as f:
            json.dump({'access_token': self.access_token}, f)
    
    def authenticate(self, request_token: str = None):
        """
        Authenticate with Zerodha.
        
        First time: Provide request_token from login URL
        Subsequent: Uses saved access_token
        """
        if self.access_token:
            try:
                # Test if token is valid
                self.kite.profile()
                logger.info("Using existing access token")
                return True
            except:
                logger.warning("Saved token invalid, need new authentication")
        
        if request_token:
            try:
                data = self.kite.generate_session(
                    request_token, 
                    api_secret=self.api_secret
                )
                self.access_token = data["access_token"]
                self.kite.set_access_token(self.access_token)
                self._save_token()
                logger.info("Authentication successful")
                return True
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                return False
        else:
            # Generate login URL
            login_url = self.kite.login_url()
            print(f"\n🔐 Please login at: {login_url}\n")
            print("After login, copy the request_token from URL and run:")
            print("broker.authenticate(request_token='YOUR_TOKEN')\n")
            return False
    
    def get_historical_data(
        self, 
        symbol: str, 
        interval: str, 
        from_date: datetime, 
        to_date: datetime
    ) -> List[Dict]:
        """
        Fetch historical OHLCV data.
        
        Args:
            symbol: Trading symbol (e.g., 'RELIANCE')
            interval: 'day', 'hour', '15minute', '5minute'
            from_date: Start date
            to_date: End date
        
        Returns:
            List of candles with OHLCV data
        """
        try:
            # Get instrument token
            instrument_token = self._get_instrument_token(symbol)
            
            if not instrument_token:
                logger.error(f"Instrument token not found for {symbol}")
                return []
            
            # Fetch data
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            logger.info(f"Fetched {len(data)} candles for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return []
    
    def _get_instrument_token(self, symbol: str) -> Optional[int]:
        """Get instrument token for symbol"""
        try:
            instruments = self.kite.instruments("NSE")
            for inst in instruments:
                if inst['tradingsymbol'] == symbol:
                    return inst['instrument_token']
            return None
        except Exception as e:
            logger.error(f"Error getting instrument token: {e}")
            return None
    
    def place_buy_order(
        self, 
        symbol: str, 
        quantity: int, 
        price: float = None,
        order_type: str = "MARKET",
        product: str = "CNC"
    ) -> Optional[str]:
        """
        Place buy order.
        
        Args:
            symbol: Trading symbol
            quantity: Number of shares
            price: Limit price (for LIMIT orders)
            order_type: MARKET or LIMIT
            product: CNC (delivery) or MIS (intraday)
        
        Returns:
            Order ID if successful
        """
        try:
            order_params = {
                "tradingsymbol": symbol,
                "exchange": "NSE",
                "transaction_type": "BUY",
                "quantity": quantity,
                "order_type": order_type,
                "product": product,
                "variety": "regular"
            }
            
            if order_type == "LIMIT" and price:
                order_params["price"] = price
            
            order_id = self.kite.place_order(**order_params)
            logger.info(f"BUY order placed: {symbol} x {quantity}, Order ID: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error placing BUY order: {e}")
            return None
    
    def place_sell_order(
        self, 
        symbol: str, 
        quantity: int, 
        price: float = None,
        order_type: str = "MARKET",
        product: str = "CNC"
    ) -> Optional[str]:
        """Place sell order"""
        try:
            order_params = {
                "tradingsymbol": symbol,
                "exchange": "NSE",
                "transaction_type": "SELL",
                "quantity": quantity,
                "order_type": order_type,
                "product": product,
                "variety": "regular"
            }
            
            if order_type == "LIMIT" and price:
                order_params["price"] = price
            
            order_id = self.kite.place_order(**order_params)
            logger.info(f"SELL order placed: {symbol} x {quantity}, Order ID: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error placing SELL order: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price"""
        try:
            quote = self.kite.quote(f"NSE:{symbol}")
            return quote[f"NSE:{symbol}"]["last_price"]
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        try:
            positions = self.kite.positions()
            return positions.get('net', [])
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_orders(self) -> List[Dict]:
        """Get all orders"""
        try:
            return self.kite.orders()
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
```

### Step 2: Data Manager

Create: `src/core/data_manager.py`

```python
"""
Data Manager
Handles fetching, caching, and serving market data
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

logger = logging.getLogger(__name__)


class DataManager:
    """Manages market data fetching and caching"""
    
    def __init__(self, broker, config: Dict):
        self.broker = broker
        self.config = config
        self.cache_dir = "data/historical"
        self.cache_enabled = config.get('data', {}).get('cache_enabled', True)
        
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_historical_data(
        self, 
        symbol: str, 
        interval: str,
        days: int = None
    ) -> Optional[pd.DataFrame]:
        """
        Get historical data for symbol.
        
        Args:
            symbol: Trading symbol
            interval: 'day', 'hour', '15minute'
            days: Number of days to fetch (default from config)
        
        Returns:
            DataFrame with OHLCV data
        """
        if days is None:
            days = self.config.get('data', {}).get('historical_days', 365)
        
        # Check cache first
        if self.cache_enabled:
            cached_data = self._load_from_cache(symbol, interval)
            if cached_data is not None:
                logger.info(f"Loaded {symbol} {interval} from cache")
                return cached_data
        
        # Fetch from broker
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        data = self.broker.get_historical_data(
            symbol, 
            interval, 
            from_date, 
            to_date
        )
        
        if not data:
            logger.warning(f"No data received for {symbol}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Save to cache
        if self.cache_enabled:
            self._save_to_cache(symbol, interval, df)
        
        return df
    
    def _load_from_cache(self, symbol: str, interval: str) -> Optional[pd.DataFrame]:
        """Load data from cache"""
        cache_file = f"{self.cache_dir}/{symbol}_{interval}.csv"
        
        if not os.path.exists(cache_file):
            return None
        
        # Check if cache is recent (within 1 day)
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_time > timedelta(days=1):
            return None  # Cache too old
        
        try:
            df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            return df
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return None
    
    def _save_to_cache(self, symbol: str, interval: str, df: pd.DataFrame):
        """Save data to cache"""
        cache_file = f"{self.cache_dir}/{symbol}_{interval}.csv"
        try:
            df.to_csv(cache_file)
            logger.info(f"Saved {symbol} {interval} to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
```

### Step 3: Portfolio Manager

Create: `src/core/portfolio.py`

```python
"""
Portfolio Manager
Tracks positions, P&L, and capital allocation
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Manages trading portfolio and positions"""
    
    def __init__(self, initial_capital: float, config: Dict):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.config = config
        self.positions = {}  # symbol -> position dict
        self.closed_positions = []
        self.state_file = "data/portfolio_state.json"
        
        self._load_state()
    
    def add_position(self, position: Dict):
        """Add new position"""
        symbol = position['symbol']
        self.positions[symbol] = {
            **position,
            'entry_time': datetime.now().isoformat(),
            'partial_exit_1': False,
            'partial_exit_2': False
        }
        self._save_state()
        logger.info(f"Added position: {symbol}")
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position for symbol"""
        return self.positions.get(symbol)
    
    def close_position(self, symbol: str, exit_price: float, reason: str):
        """Close position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        position['exit_price'] = exit_price
        position['exit_time'] = datetime.now().isoformat()
        position['exit_reason'] = reason
        
        # Calculate P&L
        pnl = (exit_price - position['entry_price']) * position['qty']
        pnl_pct = (exit_price - position['entry_price']) / position['entry_price']
        
        position['pnl'] = pnl
        position['pnl_pct'] = pnl_pct
        
        # Update capital
        self.current_capital += pnl
        
        # Move to closed positions
        self.closed_positions.append(position)
        del self.positions[symbol]
        
        self._save_state()
        logger.info(f"Closed position: {symbol}, P&L: ₹{pnl:.2f} ({pnl_pct*100:.2f}%)")
    
    def get_available_capital(self) -> float:
        """Get available capital for new trades"""
        # Capital used in open positions
        used_capital = sum(
            pos['entry_price'] * pos['qty'] 
            for pos in self.positions.values()
        )
        
        return self.current_capital - used_capital
    
    def get_position_count(self) -> int:
        """Get number of open positions"""
        return len(self.positions)
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.closed_positions:
            return {}
        
        wins = [p for p in self.closed_positions if p['pnl'] > 0]
        losses = [p for p in self.closed_positions if p['pnl'] <= 0]
        
        total_pnl = sum(p['pnl'] for p in self.closed_positions)
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital
        
        return {
            'total_trades': len(self.closed_positions),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(self.closed_positions) if self.closed_positions else 0,
            'total_pnl': total_pnl,
            'total_return_pct': total_return * 100,
            'avg_win': sum(p['pnl'] for p in wins) / len(wins) if wins else 0,
            'avg_loss': sum(p['pnl'] for p in losses) / len(losses) if losses else 0,
            'current_capital': self.current_capital
        }
    
    def _save_state(self):
        """Save portfolio state"""
        state = {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'positions': self.positions,
            'closed_positions': self.closed_positions
        }
        
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _load_state(self):
        """Load portfolio state"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.current_capital = state.get('current_capital', self.initial_capital)
                    self.positions = state.get('positions', {})
                    self.closed_positions = state.get('closed_positions', [])
                    logger.info("Loaded portfolio state")
            except Exception as e:
                logger.error(f"Error loading state: {e}")
```

---

## 📋 Phase 3: Live Trading (Weeks 5-8)

### Step 1: Update main.py for Live Trading

```python
def run_live_trading(config: dict):
    """Run live trading mode"""
    from src.core.broker import ZerodhaBroker
    from src.core.data_manager import DataManager
    from src.core.portfolio import PortfolioManager
    from src.core.engine import TradingEngine
    
    # Initialize components
    broker = ZerodhaBroker(
        api_key=config['kite_api_key'],
        api_secret=config['kite_api_secret']
    )
    
    # Authenticate
    if not broker.authenticate():
        logger.error("Authentication required")
        return
    
    # Initialize managers
    data_manager = DataManager(broker, config)
    portfolio = PortfolioManager(
        initial_capital=config['trading']['initial_capital'],
        config=config
    )
    
    # Initialize engine
    engine = TradingEngine(
        config=config,
        broker=broker,
        data_manager=data_manager,
        portfolio_manager=portfolio
    )
    
    # Trading symbols
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK']
    
    # Start trading
    engine.start()
    
    try:
        while True:
            # Execute trading cycle
            results = engine.execute_cycle(symbols)
            
            # Log results
            logger.info(f"Cycle complete: {results}")
            
            # Wait for next cycle (e.g., 5 minutes)
            time.sleep(300)
            
    except KeyboardInterrupt:
        logger.info("Stopping trading...")
        engine.stop()
```

---

## ✅ Implementation Checklist

### Phase 2: Core Integration
```
□ Create broker.py
□ Test Zerodha authentication
□ Test historical data fetching
□ Create data_manager.py
□ Test data caching
□ Create portfolio.py
□ Test position tracking
□ Update engine.py to use real components
```

### Phase 3: Live Trading
```
□ Test with paper trading first
□ Verify order placement works
□ Test position tracking
□ Test P&L calculation
□ Run for 1 week in paper mode
□ Start with small capital (₹50K)
□ Monitor daily
□ Scale gradually
```

---

## 🚀 Quick Start Commands

```bash
# Install dependencies
pip install kiteconnect pandas numpy

# Run authentication
python -c "from src.core.broker import ZerodhaBroker; b = ZerodhaBroker('YOUR_KEY', 'YOUR_SECRET'); b.authenticate()"

# Run live trading
python main.py --mode live

# Check portfolio
python -c "from src.core.portfolio import PortfolioManager; p = PortfolioManager(100000, {}); print(p.get_performance_metrics())"
```

---

**Next Steps:** Follow the checklist above to implement Phase 2 & 3!
