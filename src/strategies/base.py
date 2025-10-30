"""
Base Strategy Class
All trading strategies should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd
from dataclasses import dataclass
from enum import Enum


class SignalType(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    EXIT = "EXIT"


@dataclass
class Signal:
    """Trading signal data structure"""
    symbol: str
    signal_type: SignalType
    price: float
    timestamp: pd.Timestamp
    confidence: float  # 0.0 to 1.0
    indicators: Dict[str, float]
    reason: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: Optional[int] = None


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    Subclasses must implement:
    - generate_signals(): Generate trading signals
    - calculate_position_size(): Calculate position size
    - should_exit(): Determine if position should be exited
    """
    
    def __init__(self, name: str, config: Dict):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
            config: Strategy configuration dictionary
        """
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        
    @abstractmethod
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        Generate trading signals based on market data.
        
        Args:
            data: Dictionary of DataFrames with keys like 'daily', 'hourly', '15min'
                  Each DataFrame should have OHLCV data with technical indicators
        
        Returns:
            List of Signal objects
        """
        pass
    
    @abstractmethod
    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        atr: float,
        available_capital: float
    ) -> int:
        """
        Calculate position size based on risk parameters.
        
        Args:
            symbol: Trading symbol
            price: Current price
            atr: Average True Range
            available_capital: Available capital for trading
        
        Returns:
            Position size (number of shares)
        """
        pass
    
    @abstractmethod
    def should_exit(
        self,
        position: Dict,
        current_data: pd.Series
    ) -> Tuple[bool, str]:
        """
        Determine if an open position should be exited.
        
        Args:
            position: Dictionary with position details (symbol, qty, entry_price, etc.)
            current_data: Current market data as pandas Series with indicators
        
        Returns:
            Tuple of (should_exit: bool, reason: str)
        """
        pass
    
    def validate_signal(self, signal: Signal, data: Dict[str, pd.DataFrame]) -> bool:
        """
        Validate if a signal meets basic criteria.
        Can be overridden by subclasses for custom validation.
        
        Args:
            signal: Signal to validate
            data: Market data
        
        Returns:
            True if signal is valid, False otherwise
        """
        # Basic validation
        if signal.confidence < 0.5:
            return False
        
        if signal.price <= 0:
            return False
        
        return True
    
    def get_stop_loss(self, entry_price: float, atr: float, direction: str = "long") -> float:
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price
            atr: Average True Range
            direction: 'long' or 'short'
        
        Returns:
            Stop loss price
        """
        atr_mult = self.config.get('stop_loss_atr_mult', 2.5)
        
        if direction == "long":
            return entry_price - (atr * atr_mult)
        else:
            return entry_price + (atr * atr_mult)
    
    def get_take_profit(self, entry_price: float, direction: str = "long") -> float:
        """
        Calculate take profit price.
        
        Args:
            entry_price: Entry price
            direction: 'long' or 'short'
        
        Returns:
            Take profit price
        """
        profit_target_pct = self.config.get('profit_target_pct', 0.10)
        
        if direction == "long":
            return entry_price * (1 + profit_target_pct)
        else:
            return entry_price * (1 - profit_target_pct)
    
    def check_daily_trend(self, daily_data: pd.DataFrame) -> bool:
        """
        Check if daily trend is bullish.
        
        Args:
            daily_data: Daily timeframe data with indicators
        
        Returns:
            True if trend is bullish, False otherwise
        """
        if daily_data.empty or len(daily_data) < 200:
            return False
        
        latest = daily_data.iloc[-1]
        
        # Check if price is above EMA200
        if 'ema200' in latest:
            return latest['close'] > latest['ema200']
        
        # Fallback: calculate EMA200
        ema200 = daily_data['close'].ewm(span=200, adjust=False).mean().iloc[-1]
        return latest['close'] > ema200
    
    def check_volume_confirmation(self, data: pd.DataFrame, threshold: float = 1.2) -> bool:
        """
        Check if current volume is above average.
        
        Args:
            data: DataFrame with volume data
            threshold: Volume threshold multiplier (e.g., 1.2 = 20% above average)
        
        Returns:
            True if volume is confirmed, False otherwise
        """
        if 'volume' not in data.columns or len(data) < 20:
            return True  # Skip check if no volume data
        
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        current_volume = data['volume'].iloc[-1]
        
        return current_volume >= (avg_volume * threshold)
    
    def __str__(self) -> str:
        return f"{self.name} Strategy (Enabled: {self.enabled})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
