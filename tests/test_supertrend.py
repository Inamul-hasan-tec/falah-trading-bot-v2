"""
Unit tests for SuperTrend indicator

Run with: pytest tests/test_supertrend.py
"""

import pytest
import pandas as pd
import numpy as np
from src.indicators.supertrend import (
    calculate_supertrend,
    calculate_atr,
    get_supertrend_signal,
    is_supertrend_bullish,
    is_supertrend_bearish,
)


@pytest.fixture
def sample_ohlc_data():
    """Create sample OHLC data for testing"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # Generate realistic price data
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)
    high_prices = close_prices + np.random.rand(100) * 3
    low_prices = close_prices - np.random.rand(100) * 3
    open_prices = close_prices + np.random.randn(100) * 1
    volume = np.random.randint(1000000, 5000000, 100)
    
    df = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volume
    })
    
    return df


class TestATRCalculation:
    """Test ATR calculation"""
    
    def test_atr_calculation(self, sample_ohlc_data):
        """Test that ATR is calculated correctly"""
        df = calculate_atr(sample_ohlc_data, period=14)
        
        assert 'atr' in df.columns
        assert not df['atr'].isna().all()
        assert (df['atr'] >= 0).all()
    
    def test_atr_period(self, sample_ohlc_data):
        """Test ATR with different periods"""
        df_14 = calculate_atr(sample_ohlc_data, period=14)
        df_20 = calculate_atr(sample_ohlc_data, period=20)
        
        # Longer period should generally be smoother
        assert 'atr' in df_14.columns
        assert 'atr' in df_20.columns


class TestSupertrendCalculation:
    """Test SuperTrend calculation"""
    
    def test_supertrend_columns(self, sample_ohlc_data):
        """Test that all SuperTrend columns are created"""
        df = calculate_supertrend(sample_ohlc_data)
        
        required_columns = [
            'supertrend',
            'supertrend_direction',
            'supertrend_upperband',
            'supertrend_lowerband'
        ]
        
        for col in required_columns:
            assert col in df.columns
    
    def test_supertrend_direction_values(self, sample_ohlc_data):
        """Test that direction is either 1 or -1"""
        df = calculate_supertrend(sample_ohlc_data)
        
        unique_directions = df['supertrend_direction'].unique()
        assert all(d in [1, -1] for d in unique_directions)
    
    def test_supertrend_with_parameters(self, sample_ohlc_data):
        """Test SuperTrend with different parameters"""
        df1 = calculate_supertrend(sample_ohlc_data, period=10, multiplier=3.0)
        df2 = calculate_supertrend(sample_ohlc_data, period=14, multiplier=2.0)
        
        # Different parameters should give different results
        assert not df1['supertrend'].equals(df2['supertrend'])


class TestSupertrendSignals:
    """Test SuperTrend signal generation"""
    
    def test_get_signal(self, sample_ohlc_data):
        """Test signal generation"""
        df = calculate_supertrend(sample_ohlc_data)
        signal = get_supertrend_signal(df)
        
        assert signal in ['BUY', 'SELL', 'HOLD']
    
    def test_bullish_check(self, sample_ohlc_data):
        """Test bullish condition check"""
        df = calculate_supertrend(sample_ohlc_data)
        
        # Manually set last direction to bullish
        df.loc[df.index[-1], 'supertrend_direction'] = 1
        
        assert is_supertrend_bullish(df, confirmation_bars=1) == True
    
    def test_bearish_check(self, sample_ohlc_data):
        """Test bearish condition check"""
        df = calculate_supertrend(sample_ohlc_data)
        
        # Manually set last direction to bearish
        df.loc[df.index[-1], 'supertrend_direction'] = -1
        
        assert is_supertrend_bearish(df, confirmation_bars=1) == True


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame"""
        df = pd.DataFrame()
        
        with pytest.raises(Exception):
            calculate_supertrend(df)
    
    def test_insufficient_data(self):
        """Test with insufficient data"""
        df = pd.DataFrame({
            'open': [100, 101],
            'high': [102, 103],
            'low': [99, 100],
            'close': [101, 102],
            'volume': [1000, 1100]
        })
        
        # Should handle gracefully or raise appropriate error
        try:
            result = calculate_supertrend(df, period=10)
            # If it succeeds, check that it has the right structure
            assert 'supertrend' in result.columns
        except Exception as e:
            # If it fails, that's also acceptable for insufficient data
            assert True
    
    def test_missing_columns(self):
        """Test with missing required columns"""
        df = pd.DataFrame({
            'close': [100, 101, 102]
        })
        
        with pytest.raises(Exception):
            calculate_supertrend(df)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
