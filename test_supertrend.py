"""
Test 1: SuperTrend Indicator
Tests the core SuperTrend calculation and signal generation
"""

import pandas as pd
import numpy as np
from src.indicators.supertrend import calculate_supertrend, get_supertrend_signal

print("\n" + "="*60)
print("TEST 1: SUPERTREND INDICATOR")
print("="*60)

# Create sample data (simulating stock prices)
data = {
    'high': [2500, 2520, 2540, 2530, 2550, 2560, 2555, 2570, 2580, 2575],
    'low': [2480, 2500, 2520, 2510, 2530, 2540, 2535, 2550, 2560, 2555],
    'close': [2490, 2515, 2535, 2525, 2545, 2555, 2550, 2565, 2575, 2570]
}
df = pd.DataFrame(data)

print("\n📊 Sample Price Data:")
print(df[['close']].to_string())

# Calculate SuperTrend
df = calculate_supertrend(df, period=10, multiplier=3.0)

# Show results
print("\n📈 SuperTrend Results:")
print(df[['close', 'supertrend', 'supertrend_direction']].tail().to_string())

# Get signal
signal = get_supertrend_signal(df)
direction = 'BULLISH ✅' if df['supertrend_direction'].iloc[-1] > 0 else 'BEARISH ❌'

print(f"\n🎯 Current Signal: {signal}")
print(f"📍 Latest Direction: {direction}")

print("\n✅ Test 1 Complete!")
print("="*60)
