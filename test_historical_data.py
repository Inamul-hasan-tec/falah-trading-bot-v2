"""
Test Historical Data Fetching
Demonstrates fetching historical OHLCV data from Zerodha
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from kiteconnect import KiteConnect

load_dotenv()

print("\n" + "="*60)
print("TEST: HISTORICAL DATA FETCHING")
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

# Get instrument token for RELIANCE
print("\n🔍 Finding RELIANCE instrument token...")

try:
    instruments = kite.instruments("NSE")
    reliance_token = None
    
    for inst in instruments:
        if inst['tradingsymbol'] == 'RELIANCE':
            reliance_token = inst['instrument_token']
            break
    
    if not reliance_token:
        print("❌ RELIANCE not found")
        exit(1)
    
    print(f"✅ Found: {reliance_token}")
    
    # Fetch historical data
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)
    
    print(f"\n📊 Fetching data from {from_date.date()} to {to_date.date()}...")
    
    data = kite.historical_data(
        instrument_token=reliance_token,
        from_date=from_date,
        to_date=to_date,
        interval="day"
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    print(f"✅ Downloaded {len(df)} candles")
    
    print("\n" + "="*60)
    print("SAMPLE DATA (Last 5 days)")
    print("="*60)
    print(df[['date', 'open', 'high', 'low', 'close', 'volume']].tail().to_string(index=False))
    
    # Calculate some stats
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    print(f"Period: {len(df)} days")
    print(f"Highest: ₹{df['high'].max():,.2f}")
    print(f"Lowest: ₹{df['low'].min():,.2f}")
    print(f"Average Volume: {df['volume'].mean():,.0f}")
    print(f"Total Return: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
    
    print("\n✅ Historical data fetching successful!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error fetching data: {e}")
    print("\nPossible reasons:")
    print("1. Token expired (run connect_broker.py again)")
    print("2. Internet connection issue")
    print("3. API rate limit exceeded")
