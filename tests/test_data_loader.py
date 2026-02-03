"""
Unit tests for data_loader module
"""

import pytest
import pandas as pd
import sys
sys.path.append('../src')

from src.data_loader import (
    load_data,
    load_enriched_data,
    filter_by_event_window,
    calculate_pre_post_statistics,
    get_events,
    get_observations
)
from datetime import datetime


def test_filter_by_event_window():
    """Test filtering data by event window"""
    # Create sample data
    dates = pd.date_range('2020-01-01', periods=10, freq='M')
    df = pd.DataFrame({
        'observation_date': dates,
        'value': range(10)
    })
    
    event_date = datetime(2020, 5, 1)
    filtered = filter_by_event_window(df, event_date, window_before_days=60, window_after_days=60)
    
    assert len(filtered) > 0
    assert len(filtered) < len(df)


def test_calculate_pre_post_statistics():
    """Test pre/post event statistics calculation"""
    # Create sample data
    dates = pd.date_range('2020-01-01', periods=10, freq='M')
    df = pd.DataFrame({
        'observation_date': dates,
        'indicator_code': ['ACC_OWNERSHIP'] * 10,
        'value_numeric': range(10, 20)
    })
    
    event_date = datetime(2020, 6, 1)
    stats = calculate_pre_post_statistics(df, event_date, 'ACC_OWNERSHIP')
    
    assert 'pre_event_count' in stats
    assert 'post_event_count' in stats
    assert stats['pre_event_count'] > 0
    assert stats['post_event_count'] > 0


def test_get_events():
    """Test event extraction"""
    df = pd.DataFrame({
        'record_type': ['event', 'observation', 'event'],
        'observation_date': pd.date_range('2020-01-01', periods=3, freq='Y'),
        'indicator': ['Event 1', 'Obs 1', 'Event 2']
    })
    
    events = get_events(df)
    
    assert len(events) == 2
    assert all(events['record_type'] == 'event')


def test_get_observations():
    """Test observation extraction"""
    df = pd.DataFrame({
        'record_type': ['event', 'observation', 'observation'],
        'indicator_code': ['EVT_1', 'ACC_OWNERSHIP', 'MOBILE_MONEY'],
        'value_numeric': [None, 45.0, 30.0]
    })
    
    observations = get_observations(df)
    
    assert len(observations) == 2
    assert all(observations['record_type'] == 'observation')
    assert all(observations['value_numeric'].notna())


def test_get_observations_filtered():
    """Test filtered observation extraction"""
    df = pd.DataFrame({
        'record_type': ['observation'] * 3,
        'indicator_code': ['ACC_OWNERSHIP', 'MOBILE_MONEY', 'ACC_OWNERSHIP'],
        'value_numeric': [45.0, 30.0, 50.0]
    })
    
    observations = get_observations(df, indicator_codes=['ACC_OWNERSHIP'])
    
    assert len(observations) == 2
    assert all(observations['indicator_code'] == 'ACC_OWNERSHIP')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
