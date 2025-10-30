"""
Falah Trading Bot V2 - Main Entry Point

This is the main entry point for the trading bot.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config/config.yaml') -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables
        config['kite_api_key'] = os.getenv('KITE_API_KEY', '')
        config['kite_api_secret'] = os.getenv('KITE_API_SECRET', '')
        config['telegram_bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN', '')
        config['telegram_chat_id'] = os.getenv('TELEGRAM_CHAT_ID', '')
        
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        sys.exit(1)


def run_live_trading(config: dict):
    """Run live trading mode"""
    logger.info("=" * 60)
    logger.info("FALAH TRADING BOT V2 - LIVE TRADING MODE")
    logger.info("=" * 60)
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           FALAH TRADING BOT V2 - LIVE MODE              ║
    ║                                                           ║
    ║  ⚠️  WARNING: This will execute real trades!             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Exiting...")
        return
    
    # TODO: Implement live trading
    # This would initialize the trading engine and run the main loop
    logger.info("Live trading mode not yet implemented")
    logger.info("Please use paper trading mode for testing")


def run_paper_trading(config: dict):
    """Run paper trading mode (simulation)"""
    logger.info("=" * 60)
    logger.info("FALAH TRADING BOT V2 - PAPER TRADING MODE")
    logger.info("=" * 60)
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         FALAH TRADING BOT V2 - PAPER TRADING            ║
    ║                                                           ║
    ║  ℹ️  Simulation mode - No real trades will be executed   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # TODO: Implement paper trading
    logger.info("Paper trading mode not yet implemented")


def run_backtest(config: dict, start_date: str, end_date: str):
    """Run backtest mode"""
    logger.info("=" * 60)
    logger.info("FALAH TRADING BOT V2 - BACKTEST MODE")
    logger.info("=" * 60)
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           FALAH TRADING BOT V2 - BACKTEST               ║
    ║                                                           ║
    ║  Period: {start_date} to {end_date}                      
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # TODO: Implement backtesting
    logger.info("Backtest mode not yet implemented")
    logger.info("Use scripts/backtest.py for backtesting")


def run_api_server(config: dict):
    """Run API server"""
    logger.info("=" * 60)
    logger.info("FALAH TRADING BOT V2 - API SERVER")
    logger.info("=" * 60)
    
    try:
        import uvicorn
        from src.api.app import app
        
        host = config['api']['host']
        port = config['api']['port']
        
        logger.info(f"Starting API server on {host}:{port}")
        print(f"\n🚀 API Server starting on http://{host}:{port}")
        print(f"📚 API Documentation: http://{host}:{port}/docs\n")
        
        uvicorn.run(app, host=host, port=port)
        
    except ImportError:
        logger.error("FastAPI or uvicorn not installed. Run: pip install fastapi uvicorn")
    except Exception as e:
        logger.error(f"Error starting API server: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Falah Trading Bot V2 - Algorithmic Trading System'
    )
    
    parser.add_argument(
        '--mode',
        choices=['live', 'paper', 'backtest', 'api'],
        default='paper',
        help='Trading mode (default: paper)'
    )
    
    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--strategy',
        help='Strategy to use (overrides config)'
    )
    
    parser.add_argument(
        '--strategies',
        help='Comma-separated list of strategies'
    )
    
    parser.add_argument(
        '--start',
        help='Start date for backtest (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end',
        help='End date for backtest (YYYY-MM-DD)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override strategies if specified
    if args.strategy:
        config['strategies']['active'] = [args.strategy]
    elif args.strategies:
        config['strategies']['active'] = args.strategies.split(',')
    
    # Run appropriate mode
    if args.mode == 'live':
        run_live_trading(config)
    elif args.mode == 'paper':
        run_paper_trading(config)
    elif args.mode == 'backtest':
        if not args.start or not args.end:
            logger.error("Backtest mode requires --start and --end dates")
            sys.exit(1)
        run_backtest(config, args.start, args.end)
    elif args.mode == 'api':
        run_api_server(config)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
