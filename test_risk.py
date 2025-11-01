"""
Test 5: Risk Management
Tests position sizing and risk calculation
"""

print("\n" + "="*60)
print("TEST 5: RISK MANAGEMENT")
print("="*60)

# Test position sizing and risk calculation
capital = 100000  # ₹1 lakh
risk_per_trade = 0.01  # 1%

print(f"\n💰 Capital: ₹{capital:,}")
print(f"📊 Risk Per Trade: {risk_per_trade*100}%")
print(f"💵 Max Risk Amount: ₹{capital * risk_per_trade:,}")

scenarios = [
    {'name': 'Low Volatility (TCS)', 'price': 3800, 'atr': 30, 'multiplier': 2.5},
    {'name': 'Medium Volatility (RELIANCE)', 'price': 2450, 'atr': 50, 'multiplier': 2.5},
    {'name': 'High Volatility (Small Cap)', 'price': 500, 'atr': 25, 'multiplier': 2.5}
]

print("\n" + "="*60)
print("POSITION SIZING EXAMPLES")
print("="*60)

for scenario in scenarios:
    risk_amount = capital * risk_per_trade
    stop_distance = scenario['atr'] * scenario['multiplier']
    position_size = int(risk_amount / stop_distance)
    position_value = position_size * scenario['price']
    capital_used_pct = (position_value/capital)*100
    
    print(f"\n📈 {scenario['name']}:")
    print(f"   Price: ₹{scenario['price']}")
    print(f"   ATR (Volatility): ₹{scenario['atr']}")
    print(f"   Stop Distance: ₹{stop_distance:.2f}")
    print(f"   Position Size: {position_size} shares")
    print(f"   Position Value: ₹{position_value:,}")
    print(f"   Risk Amount: ₹{risk_amount:,} (1% of capital)")
    print(f"   Capital Used: {capital_used_pct:.1f}%")
    
    if capital_used_pct > 20:
        print(f"   ⚠️  Warning: Using >20% capital in single position")
    else:
        print(f"   ✅ Good: Within risk limits")

print("\n" + "="*60)
print("KEY INSIGHTS:")
print("="*60)
print("• Higher volatility → Smaller position size")
print("• Lower volatility → Larger position size")
print("• Risk amount stays constant (₹1,000 per trade)")
print("• This ensures consistent risk across all trades")

print("\n✅ Test 5 Complete!")
print("="*60)
