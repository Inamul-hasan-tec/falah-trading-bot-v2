"""
Test 4: Parameter Optimization
Tests how different parameters affect signal generation
"""

import pandas as pd
import numpy as np
from src.strategies.supertrend_strategy import SuperTrendStrategy

print("\n" + "="*60)
print("TEST 4: PARAMETER OPTIMIZATION")
print("="*60)

# Create consistent test data
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=100, freq='D')
prices = 2450 + np.cumsum(np.random.randn(100) * 8)
data = pd.DataFrame({
    'close': prices,
    'high': prices + np.random.rand(100) * 10,
    'low': prices - np.random.rand(100) * 10,
    'volume': np.random.randint(1000000, 5000000, 100)
}, index=dates)

print("\n📊 Testing on 100 days of data")
print(f"Price range: ₹{data['close'].min():.2f} - ₹{data['close'].max():.2f}")

# Test different parameters
test_configs = [
    {'period': 7, 'multiplier': 2.5, 'name': 'Aggressive'},
    {'period': 10, 'multiplier': 3.0, 'name': 'Balanced'},
    {'period': 14, 'multiplier': 3.5, 'name': 'Conservative'}
]

print("\n" + "="*60)
print("PARAMETER COMPARISON")
print("="*60)

results = []

for test in test_configs:
    config = {
        'indicators': {
            'supertrend_period': test['period'],
            'supertrend_multiplier': test['multiplier'],
            'atr_period': 14
        },
        'supertrend_strategy': {
            'enabled': True,
            'period': test['period'],
            'multiplier': test['multiplier'],
            'volume_confirmation': True,
            'volume_threshold': 1.2,
            'profit_target_pct': 0.10,
            'stop_loss_atr_mult': 2.5
        }
    }
    
    strategy = SuperTrendStrategy(config)
    signals = strategy.generate_signals(data, data)
    
    avg_conf = sum(s.confidence for s in signals)/len(signals) if signals else 0
    
    results.append({
        'name': test['name'],
        'period': test['period'],
        'mult': test['multiplier'],
        'signals': len(signals),
        'confidence': avg_conf
    })
    
    print(f"\n{test['name']} (Period={test['period']}, Multiplier={test['multiplier']}):")
    print(f"  Signals Generated: {len(signals)}")
    print(f"  Avg Confidence: {avg_conf:.1%}" if signals else "  No signals generated")
    print(f"  Best for: {'Active trading' if len(signals) > 5 else 'Patient trading'}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
print("• Aggressive: More signals, good for active traders")
print("• Balanced: Moderate signals, good for most traders ✅")
print("• Conservative: Fewer signals, good for patient traders")

print("\n✅ Test 4 Complete!")
print("="*60)
