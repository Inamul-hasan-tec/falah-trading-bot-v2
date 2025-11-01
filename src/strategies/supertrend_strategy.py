"""
SuperTrend Trading Strategy

A trend-following strategy based on the SuperTrend indicator.
Entry when SuperTrend turns green, exit when it turns red.
"""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from .base import BaseStrategy, Signal, SignalType


class SuperTrendStrategy(BaseStrategy):
    """
    SuperTrend-based trading strategy.
    
    Entry Conditions:
    - SuperTrend indicator turns green (bullish)
    - Price closes above SuperTrend line
    - Volume confirmation (optional)
    - Daily trend filter (optional)
    
    Exit Conditions:
    - SuperTrend indicator turns red (bearish)
    - Price closes below SuperTrend line
    - Stop loss hit
    - Profit target reached
    """
    
    def __init__(self, config: Dict):
        super().__init__("SuperTrend", config)
        
        # Strategy parameters
        self.period = config.get('period', 10)
        self.multiplier = config.get('multiplier', 3.0)
        self.volume_confirmation = config.get('volume_confirmation', True)
        self.volume_threshold = config.get('volume_threshold', 1.2)
        self.daily_trend_filter = config.get('daily_trend_filter', True)
        self.profit_target_pct = config.get('profit_target_pct', 0.10)
        self.stop_loss_atr_mult = config.get('stop_loss_atr_mult', 2.5)
        self.trailing_stop_enabled = config.get('trailing_stop_enabled', True)
        self.trailing_stop_activation = config.get('trailing_stop_activation', 0.05)
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        Generate SuperTrend-based trading signals.
        
        Args:
            data: Dictionary with 'daily', 'hourly', '15min' DataFrames
        
        Returns:
            List of Signal objects
        """
        signals = []
        
        # Get primary timeframe data (15min)
        primary_data = data.get('15min')
        if primary_data is None or primary_data.empty:
            primary_data = data.get('primary')

        # Validate primary data
        if primary_data is None or primary_data.empty:
            return signals

        
        # Get daily data for trend filter
        daily_data = data.get('daily')
        
        # Ensure SuperTrend indicator is calculated
        if 'supertrend_direction' not in primary_data.columns:
            primary_data = self._calculate_supertrend(primary_data)
        
        # Get latest data
        latest = primary_data.iloc[-1]
        previous = primary_data.iloc[-2] if len(primary_data) > 1 else None
        
        # Check for bullish signal (SuperTrend turns green)
        if previous is not None:
            supertrend_turned_green = (
                previous['supertrend_direction'] <= 0 and
                latest['supertrend_direction'] > 0
            )
            
            if supertrend_turned_green:
                # Validate entry conditions
                if self._validate_entry(latest, primary_data, daily_data):
                    signal = self._create_buy_signal(latest, primary_data)
                    if signal:
                        signals.append(signal)
        
        return signals
    
    def _validate_entry(
        self,
        latest: pd.Series,
        primary_data: pd.DataFrame,
        daily_data: pd.DataFrame
    ) -> bool:
        """Validate entry conditions"""
        
        # Check price above SuperTrend line
        if 'supertrend' in latest:
            if latest['close'] <= latest['supertrend']:
                return False
        
        # Check volume confirmation
        if self.volume_confirmation:
            if not self.check_volume_confirmation(primary_data, self.volume_threshold):
                return False
        
        # Check daily trend filter
        if self.daily_trend_filter and daily_data is not None and not daily_data.empty:
            if not self.check_daily_trend(daily_data):
                return False
        
        return True
    
    def _create_buy_signal(self, latest: pd.Series, data: pd.DataFrame) -> Signal:
        """Create buy signal"""
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_confidence(latest, data)
        
        # Get ATR for stop loss calculation
        atr = latest.get('atr', latest['close'] * 0.02)  # Fallback to 2% of price
        
        # Calculate stop loss and take profit
        stop_loss = self.get_stop_loss(latest['close'], atr, 'long')
        take_profit = self.get_take_profit(latest['close'], 'long')
        
        # Build indicator dictionary
        indicators = {
            'supertrend': latest.get('supertrend', 0),
            'supertrend_direction': latest.get('supertrend_direction', 0),
            'atr': atr,
            'rsi': latest.get('rsi_14', 50),
            'volume': latest.get('volume', 0),
        }
        
        signal = Signal(
            symbol=latest.get('symbol', 'UNKNOWN'),
            signal_type=SignalType.BUY,
            price=latest['close'],
            timestamp=latest.name if isinstance(latest.name, pd.Timestamp) else pd.Timestamp.now(),
            confidence=confidence,
            indicators=indicators,
            reason="SuperTrend turned bullish",
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        return signal
    
    def _calculate_confidence(self, latest: pd.Series, data: pd.DataFrame) -> float:
        """
        Calculate signal confidence (0.0 to 1.0)
        
        Factors:
        - SuperTrend strength
        - Volume confirmation
        - RSI level
        - Price position relative to SuperTrend
        """
        confidence = 0.5  # Base confidence
        
        # SuperTrend strength (distance from price)
        if 'supertrend' in latest and latest['supertrend'] > 0:
            distance_pct = (latest['close'] - latest['supertrend']) / latest['supertrend']
            if distance_pct > 0.01:  # More than 1% above
                confidence += 0.1
        
        # Volume confirmation
        if self.check_volume_confirmation(data, self.volume_threshold):
            confidence += 0.15
        
        # RSI level (prefer 40-60 range for entries)
        if 'rsi_14' in latest:
            rsi = latest['rsi_14']
            if 40 <= rsi <= 60:
                confidence += 0.15
            elif 30 <= rsi <= 70:
                confidence += 0.10
        
        # Recent trend strength
        if len(data) >= 5:
            recent_closes = data['close'].tail(5)
            if recent_closes.is_monotonic_increasing:
                confidence += 0.10
        
        return min(confidence, 1.0)
    
    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        atr: float,
        available_capital: float
    ) -> int:
        """
        Calculate position size based on ATR and risk parameters.
        
        Args:
            symbol: Trading symbol
            price: Current price
            atr: Average True Range
            available_capital: Available capital
        
        Returns:
            Position size (number of shares)
        """
        if atr <= 0 or price <= 0:
            return 0
        
        # Risk per trade (from config)
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
        """
        Determine if position should be exited.
        
        Exit conditions:
        - SuperTrend turns red
        - Price closes below SuperTrend line
        - Stop loss hit
        - Profit target reached
        
        Args:
            position: Position details
            current_data: Current market data
        
        Returns:
            (should_exit, reason)
        """
        entry_price = position.get('entry_price', 0)
        current_price = current_data.get('close', 0)
        
        if entry_price <= 0 or current_price <= 0:
            return False, ""
        
        # Calculate current P&L percentage
        pnl_pct = (current_price - entry_price) / entry_price
        
        # Check SuperTrend direction
        if 'supertrend_direction' in current_data:
            if current_data['supertrend_direction'] <= 0:
                return True, "SuperTrend turned bearish"
        
        # Check if price below SuperTrend line
        if 'supertrend' in current_data:
            if current_price < current_data['supertrend']:
                return True, "Price below SuperTrend line"
        
        # Check stop loss
        stop_loss = position.get('stop_loss_price')
        if stop_loss and current_price <= stop_loss:
            return True, f"Stop loss hit at {stop_loss:.2f}"
        
        # Check profit target
        take_profit = position.get('take_profit_price')
        if take_profit and current_price >= take_profit:
            return True, f"Profit target reached at {take_profit:.2f}"
        
        # Trailing stop logic
        if self.trailing_stop_enabled and pnl_pct >= self.trailing_stop_activation:
            trailing_stop = self._calculate_trailing_stop(position, current_data)
            if trailing_stop and current_price <= trailing_stop:
                return True, f"Trailing stop hit at {trailing_stop:.2f}"
        
        return False, ""
    
    def _calculate_trailing_stop(self, position: Dict, current_data: pd.Series) -> float:
        """Calculate trailing stop loss price"""
        
        # Use SuperTrend line as trailing stop
        if 'supertrend' in current_data:
            return current_data['supertrend']
        
        # Fallback: ATR-based trailing stop
        entry_price = position.get('entry_price', 0)
        atr = current_data.get('atr', 0)
        
        if atr > 0:
            return entry_price + (atr * self.stop_loss_atr_mult * 0.5)
        
        return position.get('stop_loss_price', 0)
    
    def _calculate_supertrend(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SuperTrend indicator if not present.
        
        Args:
            df: DataFrame with OHLC data
        
        Returns:
            DataFrame with SuperTrend columns added
        """
        df = df.copy()
        
        # Calculate ATR if not present
        if 'atr' not in df.columns:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            df['atr'] = true_range.rolling(self.period).mean()
        
        # Calculate SuperTrend
        hl2 = (df['high'] + df['low']) / 2
        df['upperband'] = hl2 + (self.multiplier * df['atr'])
        df['lowerband'] = hl2 - (self.multiplier * df['atr'])
        
        # Initialize SuperTrend
        df['supertrend'] = 0.0
        df['supertrend_direction'] = 1
        
        for i in range(1, len(df)):
            # Update bands
            if df['close'].iloc[i-1] <= df['upperband'].iloc[i-1]:
                df.loc[df.index[i], 'upperband'] = min(df['upperband'].iloc[i], df['upperband'].iloc[i-1])
            
            if df['close'].iloc[i-1] >= df['lowerband'].iloc[i-1]:
                df.loc[df.index[i], 'lowerband'] = max(df['lowerband'].iloc[i], df['lowerband'].iloc[i-1])
            
            # Determine direction
            if df['close'].iloc[i] > df['upperband'].iloc[i-1]:
                df.loc[df.index[i], 'supertrend_direction'] = 1
            elif df['close'].iloc[i] < df['lowerband'].iloc[i-1]:
                df.loc[df.index[i], 'supertrend_direction'] = -1
            else:
                df.loc[df.index[i], 'supertrend_direction'] = df['supertrend_direction'].iloc[i-1]
            
            # Set SuperTrend value
            if df['supertrend_direction'].iloc[i] == 1:
                df.loc[df.index[i], 'supertrend'] = df['lowerband'].iloc[i]
            else:
                df.loc[df.index[i], 'supertrend'] = df['upperband'].iloc[i]
        
        return df
