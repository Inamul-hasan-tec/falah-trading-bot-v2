"""
Real-Time Backtesting with Zerodha Data
Fetches 12 months of real market data and backtests strategies
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from kiteconnect import KiteConnect
from src.strategies.supertrend_strategy import SuperTrendStrategy
from src.strategies.enhanced_supertrend import EnhancedSuperTrendStrategy

load_dotenv()

print("\n" + "="*70)
print("REAL-TIME BACKTESTING - 12 MONTHS")
print("="*70)

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

# Configuration
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

# Test stocks
symbols = ['TATAMOTORS', 'INDUSINDBK', 'ACC', 'APOLLOTYRE', 'LAURUSLABS','NITINSPIN']

print("\n📊 Fetching 12 months of data for 6 stocks...")
print(f"Period: {(datetime.now() - timedelta(days=365)).date()} to {datetime.now().date()}")
print("\nThis may take a minute...\n")

# Results storage
all_results = []

for symbol in symbols:
    try:
        print(f"📈 Processing {symbol}...")
        
        # Get instrument token
        instruments = kite.instruments("NSE")
        token = None
        for inst in instruments:
            if inst['tradingsymbol'] == symbol:
                token = inst['instrument_token']
                break
        
        if not token:
            print(f"   ❌ {symbol} not found")
            continue
        
        # Fetch 12 months of daily data
        to_date = datetime.now()
        from_date = to_date - timedelta(days=365)
        
        historical_data = kite.historical_data(
            instrument_token=token,
            from_date=from_date,
            to_date=to_date,
            interval="day"
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        print(f"   ✅ Got {len(df)} days of data")
        
        # Run strategy
        strategy = SuperTrendStrategy(config)
        signals = strategy.generate_signals(df, df)
        
        # Simulate trades
        trades = []
        capital = 100000
        position = None
        
        for signal in signals:
            if signal.signal_type == 'BUY' and position is None:
                # Open position
                position = {
                    'entry_price': signal.price,
                    'stop_loss': signal.stop_loss,
                    'target': signal.target,
                    'shares': int((capital * 0.01) / (signal.price - signal.stop_loss))
                }
                
            elif signal.signal_type == 'SELL' and position is not None:
                # Close position
                exit_price = signal.price
                pnl = (exit_price - position['entry_price']) * position['shares']
                pnl_pct = ((exit_price - position['entry_price']) / position['entry_price']) * 100
                
                trades.append({
                    'entry': position['entry_price'],
                    'exit': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'win': pnl > 0
                })
                
                capital += pnl
                position = None
        
        # Calculate metrics
        if trades:
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t['win'])
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades) * 100
            
            total_profit = sum(t['pnl'] for t in trades if t['win'])
            total_loss = abs(sum(t['pnl'] for t in trades if not t['win']))
            profit_factor = total_profit / total_loss if total_loss > 0 else 0
            
            avg_win = total_profit / winning_trades if winning_trades > 0 else 0
            avg_loss = total_loss / losing_trades if losing_trades > 0 else 0
            
            total_return = ((capital - 100000) / 100000) * 100
            
            # Calculate max drawdown
            equity_curve = [100000]
            for trade in trades:
                equity_curve.append(equity_curve[-1] + trade['pnl'])
            
            peak = equity_curve[0]
            max_dd = 0
            for value in equity_curve:
                if value > peak:
                    peak = value
                dd = ((peak - value) / peak) * 100
                if dd > max_dd:
                    max_dd = dd
            
            result = {
                'symbol': symbol,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'total_return': total_return,
                'max_drawdown': max_dd,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'final_capital': capital
            }
            
            all_results.append(result)
            
            print(f"   📊 Trades: {total_trades} | Win Rate: {win_rate:.1f}% | Return: {total_return:.1f}%")
        else:
            print(f"   ⚠️  No trades generated")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        continue

print("\n" + "="*70)
print("BACKTEST RESULTS - 12 MONTHS")
print("="*70)

if all_results:
    # Individual stock results
    print("\n📊 RESULTS BY STOCK:")
    print("-" * 70)
    
    for result in all_results:
        print(f"\n🔹 {result['symbol']}")
        print(f"   Total Trades: {result['total_trades']}")
        print(f"   Win Rate: {result['win_rate']:.1f}% ({result['winning_trades']}W / {result['losing_trades']}L)")
        print(f"   Profit Factor: {result['profit_factor']:.2f}")
        print(f"   Total Return: {result['total_return']:.1f}%")
        print(f"   Max Drawdown: {result['max_drawdown']:.1f}%")
        print(f"   Avg Win: ₹{result['avg_win']:,.0f} | Avg Loss: ₹{result['avg_loss']:,.0f}")
        print(f"   Final Capital: ₹{result['final_capital']:,.0f}")
    
    # Overall statistics
    print("\n" + "="*70)
    print("📈 OVERALL STATISTICS")
    print("="*70)
    
    total_trades = sum(r['total_trades'] for r in all_results)
    total_wins = sum(r['winning_trades'] for r in all_results)
    overall_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    avg_return = sum(r['total_return'] for r in all_results) / len(all_results)
    avg_drawdown = sum(r['max_drawdown'] for r in all_results) / len(all_results)
    avg_profit_factor = sum(r['profit_factor'] for r in all_results) / len(all_results)
    
    print(f"\n📊 Total Trades Across All Stocks: {total_trades}")
    print(f"✅ Overall Win Rate: {overall_win_rate:.1f}%")
    print(f"💰 Average Return per Stock: {avg_return:.1f}%")
    print(f"📉 Average Max Drawdown: {avg_drawdown:.1f}%")
    print(f"📈 Average Profit Factor: {avg_profit_factor:.2f}")
    
    # Performance rating
    print("\n" + "="*70)
    print("🎯 PERFORMANCE RATING")
    print("="*70)
    
    if overall_win_rate >= 60:
        rating = "EXCELLENT ⭐⭐⭐⭐⭐"
    elif overall_win_rate >= 55:
        rating = "VERY GOOD ⭐⭐⭐⭐"
    elif overall_win_rate >= 50:
        rating = "GOOD ⭐⭐⭐"
    else:
        rating = "NEEDS IMPROVEMENT ⭐⭐"
    
    print(f"\n{rating}")
    print(f"\nWin Rate: {overall_win_rate:.1f}%")
    print(f"Average Return: {avg_return:.1f}%")
    print(f"Risk (Max DD): {avg_drawdown:.1f}%")
    
    # Recommendations
    print("\n" + "="*70)
    print("💡 RECOMMENDATIONS")
    print("="*70)
    
    if overall_win_rate >= 55 and avg_return > 50:
        print("\n✅ Strategy is performing well!")
        print("   • Win rate above 55%")
        print("   • Positive returns across stocks")
        print("   • Ready for paper trading")
        print("   • Consider starting with ₹50,000 - ₹1,00,000")
    elif overall_win_rate >= 50:
        print("\n⚠️  Strategy is profitable but can be improved")
        print("   • Win rate is acceptable")
        print("   • Consider parameter optimization")
        print("   • Test with enhanced strategy")
        print("   • Start with smaller capital (₹25,000)")
    else:
        print("\n❌ Strategy needs optimization")
        print("   • Win rate below 50%")
        print("   • Adjust parameters before live trading")
        print("   • Test different timeframes")
        print("   • Consider adding more filters")
    
    # Next steps
    print("\n" + "="*70)
    print("🚀 NEXT STEPS")
    print("="*70)
    print("\n1. Review individual stock performance")
    print("2. Test enhanced strategy: python3 backtest_enhanced.py")
    print("3. Start paper trading: python3 main.py --mode paper")
    print("4. Monitor for 2-4 weeks")
    print("5. Go live with small capital")
    
else:
    print("\n❌ No results generated")
    print("Possible reasons:")
    print("1. Market was closed during data period")
    print("2. Insufficient data")
    print("3. No trading signals generated")

print("\n" + "="*70)
print("✅ BACKTEST COMPLETE!")
print("="*70)
print()
