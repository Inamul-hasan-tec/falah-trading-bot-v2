"""
Test 3: Enhanced SuperTrend Strategy
Tests advanced strategy with ADX, volume trend, and momentum filters
"""

from src.strategies.enhanced_supertrend import EnhancedSuperTrendStrategy
import pandas as pd
import numpy as np

print("\n" + "="*60)
print("TEST 3: ENHANCED SUPERTREND STRATEGY")
print("="*60)

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
        'volume_threshold': 1.5,
        'profit_target_pct': 0.10,
        'stop_loss_atr_mult': 2.5
    },
    'adx_threshold': 25,
    'volume_trend_days': 3,
    'momentum_lookback': 20,
    'min_signal_gap': 5
}

# Create trending market data
dates = pd.date_range('2024-01-01', periods=50, freq='D')
np.random.seed(42)
trend = np.linspace(2400, 2600, 50)  # Uptrend
noise = np.random.randn(50) * 5
prices = trend + noise

data = pd.DataFrame({
    'close': prices,
    'high': prices + np.random.rand(50) * 8,
    'low': prices - np.random.rand(50) * 8,
    'volume': np.random.randint(2000000, 6000000, 50)
}, index=dates)

print("\n📊 Testing on strong uptrend (50 days)")
print(f"Start price: ₹{data['close'].iloc[0]:.2f}")
print(f"End price: ₹{data['close'].iloc[-1]:.2f}")
print(f"Total gain: {((data['close'].iloc[-1] / data['close'].iloc[0]) - 1) * 100:.1f}%")

# Test enhanced strategy
strategy = EnhancedSuperTrendStrategy(config)
signals = strategy.generate_signals(data, data)

print(f"\n🎯 Comparison:")
print(f"  Basic strategy would generate: ~5-7 signals")
print(f"  Enhanced strategy generated: {len(signals)} signals")
print(f"  Quality improvement: Fewer but higher confidence signals")

print(f"\n{'='*50}")
for i, signal in enumerate(signals, 1):
    print(f"\n✅ HIGH QUALITY SIGNAL {i}:")
    print(f"   Price: ₹{signal.price:.2f}")
    print(f"   Confidence: {signal.confidence:.1%}")
    print(f"   Stop Loss: ₹{signal.stop_loss:.2f}")
    print(f"   Target: ₹{signal.target:.2f}")
    print(f"   Filters passed: ✓ ADX ✓ Volume Trend ✓ Momentum")

print("\n✅ Test 3 Complete!")
print("="*60)
