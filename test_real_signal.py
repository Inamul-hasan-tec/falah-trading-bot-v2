"""
Test Real Signal Generation
Demonstrates generating trading signals from real market data
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from kiteconnect import KiteConnect
from src.indicators.supertrend import calculate_supertrend, get_supertrend_signal
from src.strategies.supertrend_strategy import SuperTrendStrategy

load_dotenv()

print("\n" + "="*60)
print("TEST: REAL SIGNAL GENERATION")
print("="*60)

# Load saved token
TOKENS_FILE = 'data/kite_tokens.json'

if not os.path.exists(TOKENS_FILE):
    print("\n❌ Not connected to Zerodha!")
    print("Run: python3 connect_broker.py")
    exit(1)

with open(TOKENS_FILE, 'r') as f:
    data = json.load(f)
    access_token = data.get('access_token')

# Initialize Kite
API_KEY = os.getenv('KITE_API_KEY')
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(access_token)

# Strategy configuration
config = {
    'indicators': {
        'supertrend_period': 10,
        'supertrend_multiplier': 3.0,
        'atr_period': 14
    },
    'supertrend_strategy': {
        'enabled': True,
        'period': 10,
        'multiplier': 3.0,
        'volume_confirmation': True,
        'volume_threshold': 1.2,
        'profit_target_pct': 0.10,
        'stop_loss_atr_mult': 2.5
    }
}

# Test on RELIANCE
symbol = 'RELIANCE'

print(f"\n🔍 Analyzing {symbol} with real market data...")

try:
    # Get instrument token
    instruments = kite.instruments("NSE")
    token = None
    for inst in instruments:
        if inst['tradingsymbol'] == symbol:
            token = inst['instrument_token']
            break
    
    if not token:
        print(f"❌ {symbol} not found")
        exit(1)
    
    # Fetch historical data (last 30 days for indicators)
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)
    
    print(f"📊 Fetching data...")
    
    data = kite.historical_data(
        instrument_token=token,
        from_date=from_date,
        to_date=to_date,
        interval="day"
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    print(f"✅ Got {len(df)} days of data")
    
    # Calculate SuperTrend
    df = calculate_supertrend(df, period=10, multiplier=3.0)
    
    # Get latest values
    latest = df.iloc[-1]
    current_price = latest['close']
    supertrend_value = latest['supertrend']
    direction = latest['supertrend_direction']
    
    print("\n" + "="*60)
    print("CURRENT MARKET STATUS")
    print("="*60)
    print(f"Stock: {symbol}")
    print(f"Current Price: ₹{current_price:,.2f}")
    print(f"SuperTrend: ₹{supertrend_value:,.2f}")
    print(f"Direction: {'BULLISH ✅' if direction > 0 else 'BEARISH ❌'}")
    print(f"Distance from ST: {((current_price - supertrend_value) / supertrend_value * 100):.2f}%")
    
    # Generate signal using strategy
    strategy = SuperTrendStrategy(config)
    signals = strategy.generate_signals(df, df)
    
    print("\n" + "="*60)
    print("SIGNAL ANALYSIS")
    print("="*60)
    
    if signals:
        signal = signals[-1]  # Latest signal
        print(f"\n🎯 SIGNAL GENERATED!")
        print(f"   Type: {signal.signal_type}")
        print(f"   Price: ₹{signal.price:.2f}")
        print(f"   Confidence: {signal.confidence:.1%}")
        print(f"   Stop Loss: ₹{signal.stop_loss:.2f} ({((signal.price - signal.stop_loss) / signal.price * 100):.1f}% risk)")
        print(f"   Target: ₹{signal.target:.2f} ({((signal.target - signal.price) / signal.price * 100):.1f}% gain)")
        print(f"   Risk/Reward: {(signal.target - signal.price)/(signal.price - signal.stop_loss):.2f}")
        print(f"   Reason: {signal.reason}")
        
        # Position sizing
        capital = 100000
        risk_amount = capital * 0.01
        stop_distance = signal.price - signal.stop_loss
        position_size = int(risk_amount / stop_distance)
        
        print(f"\n💰 POSITION SIZING (₹{capital:,} capital):")
        print(f"   Risk Amount: ₹{risk_amount:,} (1%)")
        print(f"   Position Size: {position_size} shares")
        print(f"   Position Value: ₹{position_size * signal.price:,.2f}")
        print(f"   Max Loss: ₹{risk_amount:,}")
        print(f"   Potential Gain: ₹{position_size * (signal.target - signal.price):,.2f}")
        
    else:
        print("\n⏸️  NO SIGNAL")
        print("   Waiting for better entry opportunity")
        print(f"   Current trend: {'Bullish' if direction > 0 else 'Bearish'}")
        print("   Recommendation: Monitor for trend change")
    
    print("\n✅ Real signal generation successful!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
