"""
Zerodha Broker Connection Script
Run this to connect the bot to your Zerodha account
"""

import os
import json
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# Load environment variables
load_dotenv()

API_KEY = os.getenv('KITE_API_KEY')
API_SECRET = os.getenv('KITE_API_SECRET')
TOKENS_FILE = 'data/kite_tokens.json'

print("\n" + "="*60)
print("ZERODHA BROKER CONNECTION")
print("="*60)

# Initialize Kite Connect
kite = KiteConnect(api_key=API_KEY)

# Check if we have a saved token
if os.path.exists(TOKENS_FILE):
    print("\n📁 Found saved token, testing...")
    try:
        with open(TOKENS_FILE, 'r') as f:
            data = json.load(f)
            access_token = data.get('access_token')
            
        kite.set_access_token(access_token)
        profile = kite.profile()
        
        print(f"✅ Connected as: {profile['user_name']}")
        print(f"📧 Email: {profile['email']}")
        print(f"📱 User ID: {profile['user_id']}")
        
        # Get account balance
        margins = kite.margins()
        available_cash = margins['equity']['available']['cash']
        print(f"💰 Available Cash: ₹{available_cash:,.2f}")
        
        # Get positions
        positions = kite.positions()
        net_positions = positions.get('net', [])
        print(f"📊 Open Positions: {len(net_positions)}")
        
        print("\n✅ Connection verified! Token is still valid.")
        print("="*60)
        exit(0)
        
    except Exception as e:
        print(f"⚠️  Saved token expired or invalid: {e}")
        print("Need to re-authenticate...\n")

# Generate login URL
login_url = kite.login_url()

print("\n🔐 STEP 1: LOGIN TO ZERODHA")
print("="*60)
print("\nPlease open this URL in your browser:")
print(f"\n{login_url}\n")
print("1. Login with your Zerodha credentials")
print("2. Enter your PIN")
print("3. Authorize the app")
print("4. Copy the 'request_token' from the redirected URL")
print("\nThe URL will look like:")
print("http://127.0.0.1/?request_token=XXXXXX&action=login&status=success")
print("                              ^^^^^^")
print("                         Copy this part")
print("="*60)

# Get request token from user
request_token = input("\n🔑 Enter request token: ").strip()

if not request_token:
    print("❌ No token provided. Exiting.")
    exit(1)

print("\n🔄 Generating access token...")

try:
    # Generate session
    data = kite.generate_session(request_token, api_secret=API_SECRET)
    access_token = data["access_token"]
    
    # Save token
    os.makedirs(os.path.dirname(TOKENS_FILE), exist_ok=True)
    with open(TOKENS_FILE, 'w') as f:
        json.dump({'access_token': access_token}, f)
    
    print("✅ Access token generated and saved!")
    
    # Set access token
    kite.set_access_token(access_token)
    
    # Get profile
    profile = kite.profile()
    
    print("\n" + "="*60)
    print("CONNECTION SUCCESSFUL!")
    print("="*60)
    print(f"\n👤 User: {profile['user_name']}")
    print(f"📧 Email: {profile['email']}")
    print(f"📱 User ID: {profile['user_id']}")
    
    # Get account balance
    margins = kite.margins()
    available_cash = margins['equity']['available']['cash']
    used_margin = margins['equity']['used']['debits']
    
    print(f"\n💰 Available Cash: ₹{available_cash:,.2f}")
    print(f"📊 Used Margin: ₹{used_margin:,.2f}")
    
    # Get positions
    positions = kite.positions()
    net_positions = positions.get('net', [])
    
    print(f"\n📈 Open Positions: {len(net_positions)}")
    
    if net_positions:
        print("\nCurrent Holdings:")
        for pos in net_positions:
            if pos['quantity'] != 0:
                pnl = pos['pnl']
                pnl_symbol = "+" if pnl >= 0 else ""
                print(f"  • {pos['tradingsymbol']}: {pos['quantity']} shares, P&L: {pnl_symbol}₹{pnl:,.2f}")
    
    print("\n✅ Connection verified!")
    print("="*60)
    
    print("\n🎯 NEXT STEPS:")
    print("1. Test live price fetching: python3 test_live_price.py")
    print("2. Test historical data: python3 test_historical_data.py")
    print("3. Generate real signal: python3 test_real_signal.py")
    print("4. Start paper trading: python3 main.py --mode paper")
    
except Exception as e:
    print(f"\n❌ Authentication failed: {e}")
    print("\nPlease check:")
    print("1. Request token is correct")
    print("2. API credentials in .env are correct")
    print("3. Token hasn't expired (valid for only a few minutes)")
    exit(1)
