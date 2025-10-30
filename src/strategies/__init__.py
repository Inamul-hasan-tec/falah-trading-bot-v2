"""Trading Strategies Module"""

from .base import BaseStrategy, Signal, SignalType
from .supertrend_strategy import SuperTrendStrategy
from .macd_rsi_strategy import MacdRsiStrategy

__all__ = [
    'BaseStrategy',
    'Signal',
    'SignalType',
    'SuperTrendStrategy',
    'MacdRsiStrategy',
]
