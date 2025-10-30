"""
Trading Engine

Main trading engine that orchestrates strategy execution, order management,
and risk management.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from ..strategies.base import BaseStrategy, Signal, SignalType
from ..strategies.supertrend_strategy import SuperTrendStrategy
from ..strategies.macd_rsi_strategy import MacdRsiStrategy


logger = logging.getLogger(__name__)


class TradingEngine:
    """
    Main trading engine that coordinates all trading activities.
    
    Responsibilities:
    - Load and manage trading strategies
    - Execute strategy signals
    - Manage positions and orders
    - Apply risk management rules
    - Track performance
    """
    
    def __init__(self, config: Dict, broker, data_manager, risk_manager, portfolio_manager):
        """
        Initialize trading engine.
        
        Args:
            config: Configuration dictionary
            broker: Broker interface for order execution
            data_manager: Data manager for market data
            risk_manager: Risk manager for risk controls
            portfolio_manager: Portfolio manager for position tracking
        """
        self.config = config
        self.broker = broker
        self.data_manager = data_manager
        self.risk_manager = risk_manager
        self.portfolio = portfolio_manager
        
        # Load strategies
        self.strategies: List[BaseStrategy] = []
        self._load_strategies()
        
        # State
        self.running = False
        self.last_execution_time = None
        
        logger.info(f"Trading Engine initialized with {len(self.strategies)} strategies")
    
    def _load_strategies(self):
        """Load and initialize trading strategies from config"""
        
        strategy_config = self.config.get('strategies', {})
        active_strategies = strategy_config.get('active', [])
        
        strategy_map = {
            'supertrend': SuperTrendStrategy,
            'macd_rsi': MacdRsiStrategy,
        }
        
        for strategy_name in active_strategies:
            if strategy_name in strategy_map:
                strategy_class = strategy_map[strategy_name]
                strategy_params = strategy_config.get(f'{strategy_name}_strategy', {})
                
                # Add global config
                strategy_params['risk_per_trade'] = self.config['trading']['risk_per_trade']
                strategy_params['max_position_size'] = self.config['trading']['max_position_size']
                
                strategy = strategy_class(strategy_params)
                
                if strategy.enabled:
                    self.strategies.append(strategy)
                    logger.info(f"Loaded strategy: {strategy.name}")
                else:
                    logger.info(f"Strategy {strategy.name} is disabled")
            else:
                logger.warning(f"Unknown strategy: {strategy_name}")
    
    def execute_cycle(self, symbols: List[str]) -> Dict:
        """
        Execute one trading cycle.
        
        Args:
            symbols: List of symbols to analyze
        
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Starting trading cycle for {len(symbols)} symbols")
        
        results = {
            'timestamp': datetime.now(),
            'symbols_analyzed': len(symbols),
            'signals_generated': 0,
            'orders_placed': 0,
            'orders_failed': 0,
            'positions_exited': 0,
            'errors': []
        }
        
        # Check if trading is allowed
        if not self.risk_manager.can_trade():
            logger.warning("Trading blocked by risk manager")
            results['errors'].append("Trading blocked by risk manager")
            return results
        
        # Process each symbol
        for symbol in symbols:
            try:
                # Check existing position
                position = self.portfolio.get_position(symbol)
                
                if position:
                    # Check exit conditions for existing position
                    self._check_exit_conditions(symbol, position, results)
                else:
                    # Look for entry signals
                    self._check_entry_signals(symbol, results)
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                results['errors'].append(f"{symbol}: {str(e)}")
        
        self.last_execution_time = datetime.now()
        logger.info(f"Trading cycle completed: {results['signals_generated']} signals, "
                   f"{results['orders_placed']} orders placed")
        
        return results
    
    def _check_entry_signals(self, symbol: str, results: Dict):
        """Check for entry signals from all strategies"""
        
        # Get market data for all timeframes
        data = self._get_symbol_data(symbol)
        
        if not data or not data.get('15min') or data['15min'].empty:
            return
        
        # Generate signals from all strategies
        all_signals = []
        for strategy in self.strategies:
            try:
                signals = strategy.generate_signals(data)
                all_signals.extend(signals)
            except Exception as e:
                logger.error(f"Error generating signals from {strategy.name} for {symbol}: {e}")
        
        # Process signals
        for signal in all_signals:
            if signal.signal_type == SignalType.BUY:
                results['signals_generated'] += 1
                
                # Validate signal
                if not self._validate_signal(signal, data):
                    continue
                
                # Execute signal
                success = self._execute_buy_signal(signal, data)
                if success:
                    results['orders_placed'] += 1
                else:
                    results['orders_failed'] += 1
    
    def _check_exit_conditions(self, symbol: str, position: Dict, results: Dict):
        """Check if existing position should be exited"""
        
        # Get current market data
        data = self._get_symbol_data(symbol)
        
        if not data or not data.get('15min') or data['15min'].empty:
            return
        
        current_data = data['15min'].iloc[-1]
        
        # Check exit conditions from strategy
        strategy_name = position.get('strategy')
        strategy = self._get_strategy_by_name(strategy_name)
        
        if strategy:
            should_exit, reason = strategy.should_exit(position, current_data)
            
            if should_exit:
                logger.info(f"Exit signal for {symbol}: {reason}")
                success = self._execute_sell_signal(symbol, position, reason)
                if success:
                    results['positions_exited'] += 1
    
    def _get_symbol_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Get multi-timeframe data for a symbol"""
        
        try:
            data = {}
            
            # Get daily data
            daily_df = self.data_manager.get_historical_data(symbol, 'day')
            if daily_df is not None and not daily_df.empty:
                data['daily'] = self._add_indicators(daily_df)
            
            # Get hourly data
            hourly_df = self.data_manager.get_historical_data(symbol, 'hour')
            if hourly_df is not None and not hourly_df.empty:
                data['hourly'] = self._add_indicators(hourly_df)
            
            # Get 15-minute data
            fifteen_df = self.data_manager.get_historical_data(symbol, '15minute')
            if fifteen_df is not None and not fifteen_df.empty:
                data['15min'] = self._add_indicators(fifteen_df)
                data['primary'] = data['15min']  # Alias
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return {}
    
    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to DataFrame"""
        
        try:
            # Import indicator calculation functions
            from ..indicators.supertrend import calculate_supertrend
            import pandas_ta as ta
            
            df = df.copy()
            
            # Calculate SuperTrend
            df = calculate_supertrend(df, period=10, multiplier=3.0)
            
            # Calculate MACD
            macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
            df['macd_line'] = macd['MACD_12_26_9']
            df['macd_signal'] = macd['MACDs_12_26_9']
            
            # Calculate RSI
            df['rsi_14'] = ta.rsi(df['close'], length=14)
            
            # Calculate Bollinger Bands
            bbands = ta.bbands(df['close'], length=20, std=2)
            df['bb_lower'] = bbands['BBL_20_2.0']
            df['bb_upper'] = bbands['BBU_20_2.0']
            df['bb_middle'] = bbands['BBM_20_2.0']
            
            # Calculate ATR (if not already done by SuperTrend)
            if 'atr' not in df.columns:
                df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
            
            # Calculate EMAs
            df['ema10'] = ta.ema(df['close'], length=10)
            df['ema21'] = ta.ema(df['close'], length=21)
            df['ema200'] = ta.ema(df['close'], length=200)
            
            # Calculate Chandelier Exit
            ch_length = 22
            atr_mult = 2.0
            highest_high = df['high'].rolling(ch_length).max()
            df['chandelier_exit'] = highest_high - atr_mult * df['atr']
            
            df.dropna(inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df
    
    def _validate_signal(self, signal: Signal, data: Dict[str, pd.DataFrame]) -> bool:
        """Validate if signal should be executed"""
        
        # Check risk manager
        if not self.risk_manager.can_open_position():
            logger.info(f"Signal blocked: Max positions reached")
            return False
        
        # Check if enough capital
        available_capital = self.portfolio.get_available_capital()
        estimated_cost = signal.price * (signal.position_size or 1)
        
        if estimated_cost > available_capital:
            logger.info(f"Signal blocked: Insufficient capital")
            return False
        
        # Check signal confidence
        if signal.confidence < 0.5:
            logger.info(f"Signal blocked: Low confidence ({signal.confidence:.2f})")
            return False
        
        return True
    
    def _execute_buy_signal(self, signal: Signal, data: Dict[str, pd.DataFrame]) -> bool:
        """Execute buy signal"""
        
        try:
            symbol = signal.symbol
            price = signal.price
            
            # Get ATR for position sizing
            latest_data = data['15min'].iloc[-1]
            atr = latest_data.get('atr', price * 0.02)
            
            # Calculate position size
            available_capital = self.portfolio.get_available_capital()
            strategy = self._get_strategy_by_name(signal.reason.split()[0])
            
            if strategy:
                qty = strategy.calculate_position_size(symbol, price, atr, available_capital)
            else:
                # Fallback position sizing
                risk_amount = available_capital * 0.01
                stop_distance = atr * 2.5
                qty = int(risk_amount / stop_distance) if stop_distance > 0 else 0
            
            if qty <= 0:
                logger.warning(f"Invalid quantity calculated for {symbol}")
                return False
            
            # Place order
            order_id = self.broker.place_buy_order(
                symbol=symbol,
                quantity=qty,
                price=price,
                order_type=self.config['execution']['order_type']
            )
            
            if order_id:
                # Record position
                self.portfolio.add_position({
                    'symbol': symbol,
                    'qty': qty,
                    'entry_price': price,
                    'entry_time': datetime.now(),
                    'strategy': signal.reason.split()[0],
                    'stop_loss_price': signal.stop_loss,
                    'take_profit_price': signal.take_profit,
                    'order_id': order_id
                })
                
                logger.info(f"BUY order placed: {symbol} x {qty} @ {price:.2f}")
                return True
            else:
                logger.error(f"Failed to place BUY order for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing buy signal for {signal.symbol}: {e}")
            return False
    
    def _execute_sell_signal(self, symbol: str, position: Dict, reason: str) -> bool:
        """Execute sell signal"""
        
        try:
            qty = position['qty']
            current_price = self.broker.get_current_price(symbol)
            
            if not current_price:
                logger.error(f"Could not get current price for {symbol}")
                return False
            
            # Place sell order
            order_id = self.broker.place_sell_order(
                symbol=symbol,
                quantity=qty,
                price=current_price,
                order_type=self.config['execution']['order_type']
            )
            
            if order_id:
                # Update position
                self.portfolio.close_position(symbol, current_price, reason)
                
                logger.info(f"SELL order placed: {symbol} x {qty} @ {current_price:.2f} - {reason}")
                return True
            else:
                logger.error(f"Failed to place SELL order for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing sell signal for {symbol}: {e}")
            return False
    
    def _get_strategy_by_name(self, name: str) -> Optional[BaseStrategy]:
        """Get strategy instance by name"""
        for strategy in self.strategies:
            if strategy.name.lower() == name.lower():
                return strategy
        return None
    
    def start(self):
        """Start the trading engine"""
        self.running = True
        logger.info("Trading Engine started")
    
    def stop(self):
        """Stop the trading engine"""
        self.running = False
        logger.info("Trading Engine stopped")
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'running': self.running,
            'strategies': [s.name for s in self.strategies],
            'last_execution': self.last_execution_time,
            'positions': self.portfolio.get_position_count(),
            'available_capital': self.portfolio.get_available_capital()
        }
