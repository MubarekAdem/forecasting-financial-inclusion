"""
Dashboard Utility Functions
"""

import pandas as pd
import streamlit as st
from typing import Tuple, Optional

def load_dashboard_data(data_path: str = '../data/') -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Load all necessary data for the dashboard.
    
    Args:
        data_path: Path to data directory
        
    Returns:
        Tuple of (enriched_df, forecast_df, scenario_df)
    """
    try:
        # Load enriched data
        enriched_file = f"{data_path}ethiopia_fi_unified_data_enriched.csv"
        df = pd.read_csv(enriched_file)
        df['observation_date'] = pd.to_datetime(df['observation_date'], errors='coerce')
        
        # Load forecast data
        try:
            forecast_df = pd.read_csv(f"{data_path}account_ownership_forecast.csv")
        except FileNotFoundError:
            st.warning("Forecast file not found. Using sample data.")
            forecast_df = create_sample_forecast()
        
        # Load scenario data
        try:
            scenario_df = pd.read_csv(f"{data_path}forecast_scenarios.csv")
        except FileNotFoundError:
            st.warning("Scenario file not found. Using sample data.")
            scenario_df = create_sample_scenarios()
        
        return df, forecast_df, scenario_df
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

def create_sample_forecast() -> pd.DataFrame:
    """Create sample forecast data for demonstration"""
    return pd.DataFrame({
        'Year': [2025, 2026, 2027],
        'Forecast (%)': [55.5, 58.2, 60.5],
        'Lower 80% CI': [51.5, 54.2, 56.5],
        'Upper 80% CI': [59.5, 62.2, 64.5],
        'Lower 95% CI': [49.5, 52.2, 54.5],
        'Upper 95% CI': [61.5, 64.2, 66.5]
    })

def create_sample_scenarios() -> pd.DataFrame:
    """Create sample scenario data for demonstration"""
    return pd.DataFrame({
        'Year': [2025, 2026, 2027],
        'Base Case (%)': [55.5, 58.2, 60.5],
        'Accelerated (%)': [61.0, 64.0, 66.5],
        'Stagnation (%)': [51.0, 53.5, 55.7]
    })

def format_metric(value: float, suffix: str = "%", decimals: int = 1) -> str:
    """
    Format a metric value for display.
    
    Args:
        value: Numeric value
        suffix: String to append (e.g., "%", "pp")
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    return f"{value:.{decimals}f}{suffix}"

def calculate_growth_rate(current: float, previous: float) -> float:
    """
    Calculate growth rate between two values.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Growth rate as percentage
    """
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

@st.cache_data
def get_latest_observation(df: pd.DataFrame, indicator_code: str) -> Optional[dict]:
    """
    Get the latest observation for a specific indicator.
    
    Args:
        df: DataFrame with observations
        indicator_code: Indicator code to query
        
    Returns:
        Dictionary with observation details or None
    """
    filtered = df[
        (df['record_type'] == 'observation') &
        (df['indicator_code'] == indicator_code) &
        (df['value_numeric'].notna())
    ]
    
    if len(filtered) == 0:
        return None
    
    latest = filtered.sort_values('observation_date').iloc[-1]
    
    return {
        'value': latest['value_numeric'],
        'date': latest['observation_date'],
        'source': latest.get('source_name', 'Unknown'),
        'confidence': latest.get('confidence', 'Unknown')
    }
