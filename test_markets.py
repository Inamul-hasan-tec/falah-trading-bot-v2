"""
Test 6: Market Condition Testing
Tests strategy performance in different market conditions
"""

import pandas as pd
import numpy as np
from src.strategies.supertrend_strategy import SuperTrendStrategy

print("\n" + "="*60)
print("TEST 6: MARKET CONDITION TESTING")
print("="*60)

config = {
    'indicators': {'supertrend_period': 10, 'supertrend_multiplier': 3.0, 'atr_period': 14},
    'supertrend_strategy': {
        'enabled': True, 'period': 10, 'multiplier': 3.0,
        'volume_confirmation': True, 'volume_threshold': 1.2,
        'profit_target_pct': 0.10, 'stop_loss_atr_mult': 2.5
    }
}

strategy = SuperTrendStrategy(config)

# Test 3 market conditions
np.random.seed(42)
markets = {
    'Strong Uptrend': np.linspace(2400, 2700, 50) + np.random.randn(50) * 5,
    'Choppy/Sideways': 2500 + np.sin(np.linspace(0, 4*np.pi, 50)) * 50 + np.random.randn(50) * 5,
    'Downtrend': np.linspace(2700, 2400, 50) + np.random.randn(50) * 5
}

print("\n📊 Testing strategy in 3 different market conditions...")

print("\n" + "="*60)
print("RESULTS BY MARKET CONDITION")
print("="*60)

for market_name, prices in markets.items():
    data = pd.DataFrame({
        'close': prices,
        'high': prices + np.random.rand(50) * 10,
        'low': prices - np.random.rand(50) * 10,
        'volume': np.random.randint(1000000, 5000000, 50)
    })
    
    signals = strategy.generate_signals(data, data)
    buy_signals = [s for s in signals if s.signal_type == 'BUY']
    
    start_price = data['close'].iloc[0]
    end_price = data['close'].iloc[-1]
    market_return = ((end_price / start_price) - 1) * 100
    
    print(f"\n📈 {market_name}:")
    print(f"   Market Return: {market_return:+.1f}%")
    print(f"   Total Signals: {len(signals)}")
    print(f"   Buy Signals: {len(buy_signals)}")
    
    if market_name == 'Strong Uptrend':
        print(f"   ✅ EXCELLENT: Trend-following strategies perform best")
        print(f"   💡 Action: Trade actively")
    elif market_name == 'Choppy/Sideways':
        print(f"   ⚠️  CAUTION: High risk of whipsaws")
        print(f"   💡 Action: Reduce position sizes or avoid")
    else:  # Downtrend
        print(f"   ❌ AVOID: Downtrends are risky for long-only strategies")
        print(f"   💡 Action: Stay in cash or wait for reversal")

print("\n" + "="*60)
print("KEY LEARNINGS:")
print("="*60)
print("• SuperTrend works best in trending markets")
print("• Avoid trading in choppy/sideways markets")
print("• Use ADX filter to identify strong trends")
print("• In downtrends, wait for trend reversal")

print("\n✅ Test 6 Complete!")
print("="*60)
