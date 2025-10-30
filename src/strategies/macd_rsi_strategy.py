"""
MACD + RSI Trading Strategy

Combined momentum strategy using MACD and RSI indicators.
This is an improved version of the original strategy.
"""

from typing import Dict, List, Tuple
import pandas as pd
from .base import BaseStrategy, Signal, SignalType


class MacdRsiStrategy(BaseStrategy):
    """
    MACD + RSI combined momentum strategy.
    
    Entry Conditions:
    - MACD line > 0 and MACD signal > 0
    - RSI between 40-70 (not overbought/oversold)
    - Price above Bollinger Band lower band
    - Daily trend confirmation (optional)
    
    Exit Conditions:
    - RSI < 70 and price < BB upper band (momentum weakening)
    - SuperTrend turns bearish
    - Stop loss hit
    - Profit target reached
    """
    
    def __init__(self, config: Dict):
        super().__init__("MACD_RSI", config)
        
        # Strategy parameters
        self.rsi_min = config.get('rsi_min', 40)
        self.rsi_max = config.get('rsi_max', 70)
        self.macd_threshold = config.get('macd_threshold', 0)
        self.bb_filter = config.get('bb_filter', True)
        self.daily_trend_filter = config.get('daily_trend_filter', True)
        self.profit_target_pct = config.get('profit_target_pct', 0.08)
        self.stop_loss_atr_mult = config.get('stop_loss_atr_mult', 2.8)
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        Generate MACD+RSI trading signals.
        
        Args:
            data: Dictionary with timeframe DataFrames
        
        Returns:
            List of Signal objects
        """
        signals = []
        
        # Get primary timeframe data
        primary_data = data.get('15min') or data.get('primary')
        if primary_data is None or primary_data.empty:
            return signals
        
        # Get daily data for trend filter
        daily_data = data.get('daily')
        
        # Get latest data
        latest = primary_data.iloc[-1]
        
        # Check entry conditions
        if self._check_entry_conditions(latest, primary_data, daily_data):
            signal = self._create_buy_signal(latest, primary_data)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _check_entry_conditions(
        self,
        latest: pd.Series,
        primary_data: pd.DataFrame,
        daily_data: pd.DataFrame
    ) -> bool:
        """Check if entry conditions are met"""
        
        # Check MACD conditions
        macd_line = latest.get('macd_line', 0)
        macd_signal = latest.get('macd_signal', 0)
        
        if macd_line <= self.macd_threshold or macd_signal <= self.macd_threshold:
            return False
        
        # Check RSI range
        rsi = latest.get('rsi_14', 50)
        if not (self.rsi_min <= rsi <= self.rsi_max):
            return False
        
        # Check Bollinger Band filter
        if self.bb_filter:
            bb_lower = latest.get('bb_lower', 0)
            if latest['close'] < bb_lower:
                return False
        
        # Check daily trend filter
        if self.daily_trend_filter and daily_data is not None:
            if not self.check_daily_trend(daily_data):
                return False
        
        return True
    
    def _create_buy_signal(self, latest: pd.Series, data: pd.DataFrame) -> Signal:
        """Create buy signal"""
        
        # Calculate confidence
        confidence = self._calculate_confidence(latest, data)
        
        # Get ATR for stop loss
        atr = latest.get('atr', latest['close'] * 0.02)
        
        # Calculate stop loss and take profit
        stop_loss = self.get_stop_loss(latest['close'], atr, 'long')
        take_profit = self.get_take_profit(latest['close'], 'long')
        
        # Build indicator dictionary
        indicators = {
            'macd_line': latest.get('macd_line', 0),
            'macd_signal': latest.get('macd_signal', 0),
            'rsi_14': latest.get('rsi_14', 50),
            'bb_lower': latest.get('bb_lower', 0),
            'bb_upper': latest.get('bb_upper', 0),
            'atr': atr,
        }
        
        signal = Signal(
            symbol=latest.get('symbol', 'UNKNOWN'),
            signal_type=SignalType.BUY,
            price=latest['close'],
            timestamp=latest.name if isinstance(latest.name, pd.Timestamp) else pd.Timestamp.now(),
            confidence=confidence,
            indicators=indicators,
            reason="MACD positive, RSI in range, above BB lower",
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        return signal
    
    def _calculate_confidence(self, latest: pd.Series, data: pd.DataFrame) -> float:
        """Calculate signal confidence"""
        
        confidence = 0.5  # Base confidence
        
        # MACD strength
        macd_line = latest.get('macd_line', 0)
        macd_signal = latest.get('macd_signal', 0)
        if macd_line > macd_signal:
            confidence += 0.15
        
        # RSI optimal range (45-55 is ideal)
        rsi = latest.get('rsi_14', 50)
        if 45 <= rsi <= 55:
            confidence += 0.15
        elif 40 <= rsi <= 60:
            confidence += 0.10
        
        # Price position in Bollinger Bands
        bb_lower = latest.get('bb_lower', 0)
        bb_upper = latest.get('bb_upper', 0)
        if bb_upper > bb_lower:
            bb_position = (latest['close'] - bb_lower) / (bb_upper - bb_lower)
            if 0.2 <= bb_position <= 0.5:  # Lower half, room to grow
                confidence += 0.10
        
        # Volume confirmation
        if self.check_volume_confirmation(data):
            confidence += 0.10
        
        return min(confidence, 1.0)
    
    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        atr: float,
        available_capital: float
    ) -> int:
        """Calculate position size based on ATR and risk"""
        
        if atr <= 0 or price <= 0:
            return 0
        
        # Risk per trade
        risk_per_trade = self.config.get('risk_per_trade', 0.01)
        risk_amount = available_capital * risk_per_trade
        
        # Stop loss distance
        stop_loss_distance = atr * self.stop_loss_atr_mult
        
        # Calculate quantity
        if stop_loss_distance > 0:
            qty = int(risk_amount / stop_loss_distance)
        else:
            qty = 0
        
        # Ensure position doesn't exceed max position size
        max_position_size = self.config.get('max_position_size', 0.20)
        max_qty = int((available_capital * max_position_size) / price)
        
        return min(qty, max_qty)
    
    def should_exit(
        self,
        position: Dict,
        current_data: pd.Series
    ) -> Tuple[bool, str]:
        """Determine if position should be exited"""
        
        entry_price = position.get('entry_price', 0)
        current_price = current_data.get('close', 0)
        
        if entry_price <= 0 or current_price <= 0:
            return False, ""
        
        # Check momentum exit conditions
        rsi = current_data.get('rsi_14', 50)
        bb_upper = current_data.get('bb_upper', 0)
        
        # Momentum weakening
        if rsi < 70 and current_price < bb_upper:
            return True, "Momentum weakening (RSI < 70, price < BB upper)"
        
        # SuperTrend bearish
        if 'supertrend_direction' in current_data:
            if current_data['supertrend_direction'] < 0:
                return True, "SuperTrend turned bearish"
        
        # Stop loss
        stop_loss = position.get('stop_loss_price')
        if stop_loss and current_price <= stop_loss:
            return True, f"Stop loss hit at {stop_loss:.2f}"
        
        # Profit target
        take_profit = position.get('take_profit_price')
        if take_profit and current_price >= take_profit:
            return True, f"Profit target reached at {take_profit:.2f}"
        
        # Chandelier Exit
        if 'chandelier_exit' in current_data:
            if current_price < current_data['chandelier_exit']:
                return True, "Chandelier Exit triggered"
        
        return False, ""
