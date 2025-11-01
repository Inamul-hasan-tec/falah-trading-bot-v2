"""
Test 2: SuperTrend Strategy
Tests the complete trading strategy with entry/exit rules
"""

import pandas as pd
import numpy as np
from src.strategies.supertrend_strategy import SuperTrendStrategy

print("\n" + "="*60)
print("TEST 2: SUPERTREND STRATEGY")
print("="*60)

# Sample configuration
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

# Create sample price data (simulating RELIANCE stock)
dates = pd.date_range('2024-01-01', periods=30, freq='D')
np.random.seed(42)
prices = 2450 + np.cumsum(np.random.randn(30) * 10)

data = pd.DataFrame({
    'close': prices,
    'high': prices + np.random.rand(30) * 10,
    'low': prices - np.random.rand(30) * 10,
    'volume': np.random.randint(1000000, 5000000, 30)
}, index=dates)

print("\n📊 Testing on 30 days of price data")
print(f"Price range: ₹{data['close'].min():.2f} - ₹{data['close'].max():.2f}")

# Initialize strategy
strategy = SuperTrendStrategy(config)

# Generate signals
signals = strategy.generate_signals(data, data)

print(f"\n🎯 Total signals generated: {len(signals)}")

for i, signal in enumerate(signals, 1):
    print(f"\n{'='*50}")
    print(f"Signal {i}:")
    print(f"  Type: {signal.signal_type}")
    print(f"  Symbol: {signal.symbol}")
    print(f"  Price: ₹{signal.price:.2f}")
    print(f"  Confidence: {signal.confidence:.1%}")
    print(f"  Stop Loss: ₹{signal.stop_loss:.2f}")
    print(f"  Target: ₹{signal.target:.2f}")
    print(f"  Risk/Reward: {(signal.target - signal.price)/(signal.price - signal.stop_loss):.2f}")
    print(f"  Reason: {signal.reason}")

print("\n✅ Test 2 Complete!")
print("="*60)
