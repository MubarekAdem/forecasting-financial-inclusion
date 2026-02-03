"""
Unit tests for forecasting_utils module
"""

import pytest
import pandas as pd
import numpy as np
import sys
sys.path.append('../src')

from src.forecasting_utils import (
    prepare_time_series,
    generate_scenarios,
    calculate_confidence_intervals,
    validate_forecast,
    create_event_indicators
)
from datetime import datetime


def test_prepare_time_series():
    """Test time series preparation"""
    df = pd.DataFrame({
        'observation_date': pd.date_range('2020-01-01', periods=5, freq='A'),
        'indicator_code': ['ACC_OWNERSHIP'] * 5,
        'value_numeric': [40, 42, 44, 46, 48]
    })
    
    ts = prepare_time_series(df, 'ACC_OWNERSHIP')
    
    assert len(ts) == 5
    assert 'value' in ts.columns
    assert isinstance(ts.index, pd.DatetimeIndex)


def test_generate_scenarios():
    """Test scenario generation"""
    base_forecast = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=3, freq='A'),
        'forecast': [55.0, 58.0, 60.0],
        'lower_ci': [50.0, 53.0, 55.0],
        'upper_ci': [60.0, 63.0, 65.0]
    })
    
    scenario_adjustments = {
        'accelerated': 1.10,
        'stagnation': 0.90
    }
    
    scenarios = generate_scenarios(base_forecast, scenario_adjustments)
    
    assert 'base' in scenarios
    assert 'accelerated' in scenarios
    assert 'stagnation' in scenarios
    assert len(scenarios) == 3


def test_calculate_confidence_intervals():
    """Test confidence interval calculation"""
    forecasts = [
        np.array([50, 55, 60]),
        np.array([52, 57, 62]),
        np.array([48, 53, 58])
    ]
    
    lower, upper = calculate_confidence_intervals(forecasts, confidence_level=0.95)
    
    assert len(lower) == 3
    assert len(upper) == 3
    assert all(lower < upper)


def test_validate_forecast():
    """Test forecast validation metrics"""
    actual = pd.Series([50, 55, 60])
    predicted = pd.Series([51, 54, 61])
    
    metrics = validate_forecast(actual, predicted)
    
    assert 'MAE' in metrics
    assert 'RMSE' in metrics
    assert 'MAPE' in metrics
    assert metrics['MAE'] > 0
    assert metrics['RMSE'] > 0
    assert metrics['MAPE'] > 0


def test_create_event_indicators():
    """Test event indicator creation"""
    dates = pd.date_range('2020-01-01', periods=12, freq='M')
    event_dates = {
        'telebirr': datetime(2021, 5, 1),
        'mpesa': datetime(2023, 1, 1)
    }
    
    indicators = create_event_indicators(dates, event_dates, lag_months=6)
    
    assert len(indicators) == 12
    assert 'event_telebirr' in indicators.columns
    assert 'event_mpesa' in indicators.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
