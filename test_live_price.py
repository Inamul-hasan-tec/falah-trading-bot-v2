"""
Test Live Price Fetching
Demonstrates fetching real-time prices from Zerodha
"""

import os
import json
from dotenv import load_dotenv
from kiteconnect import KiteConnect

load_dotenv()

print("\n" + "="*60)
print("TEST: LIVE PRICE FETCHING")
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

# Test stocks
symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK']

print("\n📊 Fetching live prices...\n")

try:
    # Get quotes
    quotes = kite.quote([f"NSE:{symbol}" for symbol in symbols])
    
    print("="*60)
    for symbol in symbols:
        key = f"NSE:{symbol}"
        if key in quotes:
            quote = quotes[key]
            ltp = quote['last_price']
            change = quote['net_change']
            change_pct = (change / (ltp - change)) * 100
            volume = quote['volume']
            
            change_symbol = "+" if change >= 0 else ""
            emoji = "📈" if change >= 0 else "📉"
            
            print(f"\n{emoji} {symbol}")
            print(f"   Price: ₹{ltp:,.2f}")
            print(f"   Change: {change_symbol}₹{change:.2f} ({change_symbol}{change_pct:.2f}%)")
            print(f"   Volume: {volume:,}")
            print(f"   High: ₹{quote['ohlc']['high']:,.2f}")
            print(f"   Low: ₹{quote['ohlc']['low']:,.2f}")
    
    print("\n" + "="*60)
    print("✅ Live price fetching successful!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error fetching prices: {e}")
    print("\nPossible reasons:")
    print("1. Market is closed")
    print("2. Token expired (run connect_broker.py again)")
    print("3. Internet connection issue")
