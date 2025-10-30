"""
SuperTrend Indicator

A trend-following indicator that provides dynamic support and resistance levels.
"""

import pandas as pd
import numpy as np
from typing import Tuple


def calculate_supertrend(
    df: pd.DataFrame,
    period: int = 10,
    multiplier: float = 3.0,
    atr_column: str = 'atr'
) -> pd.DataFrame:
    """
    Calculate SuperTrend indicator.
    
    The SuperTrend indicator is calculated using ATR (Average True Range) and provides
    dynamic support/resistance levels. When price is above the SuperTrend line, the
    trend is considered bullish (green). When below, it's bearish (red).
    
    Args:
        df: DataFrame with OHLC data
        period: ATR period (default: 10)
        multiplier: ATR multiplier (default: 3.0)
        atr_column: Name of ATR column if already calculated
    
    Returns:
        DataFrame with added columns:
        - supertrend: SuperTrend line value
        - supertrend_direction: 1 for bullish, -1 for bearish
        - supertrend_upperband: Upper band
        - supertrend_lowerband: Lower band
    """
    df = df.copy()
    
    # Calculate ATR if not present
    if atr_column not in df.columns:
        df = calculate_atr(df, period)
        atr_column = 'atr'
    
    # Calculate basic bands
    hl2 = (df['high'] + df['low']) / 2
    df['supertrend_upperband'] = hl2 + (multiplier * df[atr_column])
    df['supertrend_lowerband'] = hl2 - (multiplier * df[atr_column])
    
    # Initialize SuperTrend columns
    df['supertrend'] = 0.0
    df['supertrend_direction'] = 1
    
    # Calculate SuperTrend
    for i in range(1, len(df)):
        curr_idx = df.index[i]
        prev_idx = df.index[i-1]
        
        # Adjust upper band
        if df.loc[prev_idx, 'close'] <= df.loc[prev_idx, 'supertrend_upperband']:
            df.loc[curr_idx, 'supertrend_upperband'] = min(
                df.loc[curr_idx, 'supertrend_upperband'],
                df.loc[prev_idx, 'supertrend_upperband']
            )
        
        # Adjust lower band
        if df.loc[prev_idx, 'close'] >= df.loc[prev_idx, 'supertrend_lowerband']:
            df.loc[curr_idx, 'supertrend_lowerband'] = max(
                df.loc[curr_idx, 'supertrend_lowerband'],
                df.loc[prev_idx, 'supertrend_lowerband']
            )
        
        # Determine direction
        if df.loc[curr_idx, 'close'] > df.loc[prev_idx, 'supertrend_upperband']:
            df.loc[curr_idx, 'supertrend_direction'] = 1
        elif df.loc[curr_idx, 'close'] < df.loc[prev_idx, 'supertrend_lowerband']:
            df.loc[curr_idx, 'supertrend_direction'] = -1
        else:
            df.loc[curr_idx, 'supertrend_direction'] = df.loc[prev_idx, 'supertrend_direction']
        
        # Set SuperTrend value based on direction
        if df.loc[curr_idx, 'supertrend_direction'] == 1:
            df.loc[curr_idx, 'supertrend'] = df.loc[curr_idx, 'supertrend_lowerband']
        else:
            df.loc[curr_idx, 'supertrend'] = df.loc[curr_idx, 'supertrend_upperband']
    
    return df


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate Average True Range (ATR).
    
    Args:
        df: DataFrame with OHLC data
        period: ATR period
    
    Returns:
        DataFrame with 'atr' column added
    """
    df = df.copy()
    
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    
    df['atr'] = true_range.rolling(period).mean()
    
    return df


def get_supertrend_signal(df: pd.DataFrame, lookback: int = 1) -> str:
    """
    Get current SuperTrend signal.
    
    Args:
        df: DataFrame with SuperTrend calculated
        lookback: Number of periods to look back for confirmation
    
    Returns:
        'BUY', 'SELL', or 'HOLD'
    """
    if 'supertrend_direction' not in df.columns or len(df) < lookback + 1:
        return 'HOLD'
    
    recent_directions = df['supertrend_direction'].tail(lookback + 1)
    
    # Check for bullish crossover (direction changed from -1 to 1)
    if recent_directions.iloc[-2] <= 0 and recent_directions.iloc[-1] > 0:
        return 'BUY'
    
    # Check for bearish crossover (direction changed from 1 to -1)
    if recent_directions.iloc[-2] >= 0 and recent_directions.iloc[-1] < 0:
        return 'SELL'
    
    return 'HOLD'


def is_supertrend_bullish(df: pd.DataFrame, confirmation_bars: int = 1) -> bool:
    """
    Check if SuperTrend is in bullish mode.
    
    Args:
        df: DataFrame with SuperTrend calculated
        confirmation_bars: Number of consecutive bullish bars required
    
    Returns:
        True if bullish, False otherwise
    """
    if 'supertrend_direction' not in df.columns or len(df) < confirmation_bars:
        return False
    
    recent_directions = df['supertrend_direction'].tail(confirmation_bars)
    return all(recent_directions > 0)


def is_supertrend_bearish(df: pd.DataFrame, confirmation_bars: int = 1) -> bool:
    """
    Check if SuperTrend is in bearish mode.
    
    Args:
        df: DataFrame with SuperTrend calculated
        confirmation_bars: Number of consecutive bearish bars required
    
    Returns:
        True if bearish, False otherwise
    """
    if 'supertrend_direction' not in df.columns or len(df) < confirmation_bars:
        return False
    
    recent_directions = df['supertrend_direction'].tail(confirmation_bars)
    return all(recent_directions < 0)


def calculate_supertrend_strength(df: pd.DataFrame) -> float:
    """
    Calculate SuperTrend strength (distance from price).
    
    Args:
        df: DataFrame with SuperTrend calculated
    
    Returns:
        Strength as percentage (positive for bullish, negative for bearish)
    """
    if 'supertrend' not in df.columns or len(df) == 0:
        return 0.0
    
    latest = df.iloc[-1]
    
    if latest['supertrend'] == 0:
        return 0.0
    
    strength = (latest['close'] - latest['supertrend']) / latest['supertrend'] * 100
    
    return strength


def get_supertrend_stop_loss(df: pd.DataFrame, direction: str = 'long') -> float:
    """
    Get stop loss level based on SuperTrend.
    
    Args:
        df: DataFrame with SuperTrend calculated
        direction: 'long' or 'short'
    
    Returns:
        Stop loss price
    """
    if 'supertrend' not in df.columns or len(df) == 0:
        return 0.0
    
    latest = df.iloc[-1]
    
    if direction == 'long':
        # For long positions, use SuperTrend line as stop loss
        return latest['supertrend']
    else:
        # For short positions, use SuperTrend line as stop loss
        return latest['supertrend']


def calculate_multiple_supertrends(
    df: pd.DataFrame,
    configs: list = None
) -> pd.DataFrame:
    """
    Calculate multiple SuperTrend indicators with different parameters.
    
    Useful for confluence analysis.
    
    Args:
        df: DataFrame with OHLC data
        configs: List of (period, multiplier) tuples
                 Default: [(7, 2), (10, 3), (14, 4)]
    
    Returns:
        DataFrame with multiple SuperTrend columns
    """
    if configs is None:
        configs = [(7, 2), (10, 3), (14, 4)]
    
    df = df.copy()
    
    for period, multiplier in configs:
        suffix = f"_{period}_{multiplier}"
        
        # Calculate this SuperTrend
        temp_df = calculate_supertrend(df, period, multiplier)
        
        # Add columns with suffix
        df[f'supertrend{suffix}'] = temp_df['supertrend']
        df[f'supertrend_direction{suffix}'] = temp_df['supertrend_direction']
    
    return df


def get_supertrend_confluence(df: pd.DataFrame) -> Tuple[int, int]:
    """
    Get SuperTrend confluence (how many are bullish/bearish).
    
    Requires multiple SuperTrend indicators calculated.
    
    Args:
        df: DataFrame with multiple SuperTrend indicators
    
    Returns:
        Tuple of (bullish_count, bearish_count)
    """
    if len(df) == 0:
        return 0, 0
    
    latest = df.iloc[-1]
    
    # Find all supertrend_direction columns
    direction_cols = [col for col in df.columns if 'supertrend_direction' in col]
    
    if not direction_cols:
        return 0, 0
    
    bullish_count = sum(1 for col in direction_cols if latest[col] > 0)
    bearish_count = sum(1 for col in direction_cols if latest[col] < 0)
    
    return bullish_count, bearish_count
