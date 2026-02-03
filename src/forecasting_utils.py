"""
Forecasting Utilities for Financial Inclusion Metrics

This module provides functions for time series forecasting using multiple approaches:
- ARIMA with exogenous variables
- Facebook Prophet with custom regressors
- Ensemble forecasting
- Scenario generation
- Uncertainty quantification
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def prepare_time_series(df: pd.DataFrame, indicator_code: str, 
                        freq: str = 'A') -> pd.DataFrame:
    """
    Prepare time series data for forecasting.
    
    Args:
        df: DataFrame with observations
        indicator_code: Indicator code to prepare
        freq: Frequency for resampling ('A'=Annual, 'Q'=Quarterly, 'M'=Monthly)
        
    Returns:
        Prepared time series DataFrame with date index
    """
    # Filter to indicator
    ts_data = df[df['indicator_code'] == indicator_code].copy()
    ts_data = ts_data[ts_data['value_numeric'].notna()]
    
    # Sort by date
    ts_data = ts_data.sort_values('observation_date')
    
    # Set date as index
    ts_data.set_index('observation_date', inplace=True)
    
    # Select relevant columns
    ts_series = ts_data[['value_numeric']].copy()
    ts_series.columns = ['value']
    
    return ts_series


def fit_arima_model(ts_data: pd.DataFrame, order: Tuple[int, int, int] = (1, 1, 1),
                    exog: Optional[pd.DataFrame] = None) -> dict:
    """
    Fit ARIMA model to time series data.
    
    Args:
        ts_data: Time series DataFrame with 'value' column
        order: ARIMA order (p, d, q)
        exog: Exogenous variables (optional)
        
    Returns:
        Dictionary with model results and diagnostics
    """
    try:
        from statsmodels.tsa.arima.model import ARIMA
        
        model = ARIMA(ts_data['value'], order=order, exog=exog)
        fitted_model = model.fit()
        
        results = {
            'model': fitted_model,
            'aic': fitted_model.aic,
            'bic': fitted_model.bic,
            'params': fitted_model.params,
            'fitted_values': fitted_model.fittedvalues,
            'residuals': fitted_model.resid
        }
        
        return results
    except ImportError:
        print("statsmodels not installed. Please install: pip install statsmodels")
        return {}
    except Exception as e:
        print(f"Error fitting ARIMA: {e}")
        return {}


def fit_prophet_model(ts_data: pd.DataFrame, custom_regressors: Optional[List[str]] = None) -> dict:
    """
    Fit Facebook Prophet model to time series data.
    
    Args:
        ts_data: Time series DataFrame with DatetimeIndex and 'value' column
        custom_regressors: List of column names to use as additional regressors
        
    Returns:
        Dictionary with model and diagnostics
    """
    try:
        from prophet import Prophet
        
        # Prepare data in Prophet format
        prophet_df = ts_data.reset_index()
        prophet_df.columns = ['ds', 'y']
        
        # Initialize model
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False,
            interval_width=0.95
        )
        
        # Add custom regressors if provided
        if custom_regressors:
            for regressor in custom_regressors:
                if regressor in prophet_df.columns:
                    model.add_regressor(regressor)
        
        # Fit model
        model.fit(prophet_df)
        
        results = {
            'model': model,
            'train_data': prophet_df
        }
        
        return results
    except ImportError:
        print("Prophet not installed. Please install: pip install prophet")
        return {}
    except Exception as e:
        print(f"Error fitting Prophet: {e}")
        return {}


def generate_forecast(model_results: dict, periods: int, 
                     freq: str = 'A', exog_future: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Generate forecasts from fitted model.
    
    Args:
        model_results: Dictionary from fit_arima_model or fit_prophet_model
        periods: Number of periods to forecast
        freq: Frequency ('A', 'Q', 'M')
        exog_future: Future exogenous variables for ARIMA
        
    Returns:
        DataFrame with forecasts and confidence intervals
    """
    if 'model' not in model_results:
        print("No model found in results")
        return pd.DataFrame()
    
    model = model_results['model']
    
    # Check if Prophet or ARIMA
    if hasattr(model, 'predict') and hasattr(model, 'make_future_dataframe'):
        # Prophet model
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)
        forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        forecast.columns = ['date', 'forecast', 'lower_ci', 'upper_ci']
        return forecast
    else:
        # ARIMA model
        forecast_result = model.forecast(steps=periods, exog=exog_future)
        
        # Get confidence intervals
        conf_int = model.get_forecast(steps=periods, exog=exog_future).conf_int()
        
        # Create forecast dataframe
        last_date = model.data.dates[-1]
        future_dates = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'forecast': forecast_result,
            'lower_ci': conf_int.iloc[:, 0],
            'upper_ci': conf_int.iloc[:, 1]
        })
        
        return forecast_df


def generate_scenarios(base_forecast: pd.DataFrame, 
                      scenario_adjustments: Dict[str, float]) -> Dict[str, pd.DataFrame]:
    """
    Generate scenario-based forecasts.
    
    Args:
        base_forecast: Base case forecast DataFrame
        scenario_adjustments: Dict mapping scenario names to percentage adjustments
            Example: {'accelerated': 1.15, 'stagnation': 0.85}
            
    Returns:
        Dictionary mapping scenario names to forecast DataFrames
    """
    scenarios = {}
    
    # Add base case
    scenarios['base'] = base_forecast.copy()
    
    # Generate adjusted scenarios
    for scenario_name, multiplier in scenario_adjustments.items():
        scenario_df = base_forecast.copy()
        scenario_df['forecast'] = scenario_df['forecast'] * multiplier
        scenario_df['lower_ci'] = scenario_df['lower_ci'] * multiplier
        scenario_df['upper_ci'] = scenario_df['upper_ci'] * multiplier
        scenarios[scenario_name] = scenario_df
    
    return scenarios


def calculate_confidence_intervals(forecasts: List[np.ndarray], 
                                   confidence_level: float = 0.95) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate confidence intervals from multiple forecast realizations.
    
    Args:
        forecasts: List of forecast arrays (from different models or simulations)
        confidence_level: Confidence level (0-1)
        
    Returns:
        Tuple of (lower_bound, upper_bound) arrays
    """
    forecasts_array = np.array(forecasts)
    
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    lower_bound = np.percentile(forecasts_array, lower_percentile, axis=0)
    upper_bound = np.percentile(forecasts_array, upper_percentile, axis=0)
    
    return lower_bound, upper_bound


def ensemble_forecast(model_results_list: List[dict], periods: int,
                     weights: Optional[List[float]] = None) -> pd.DataFrame:
    """
    Combine multiple model forecasts using weighted averaging.
    
    Args:
        model_results_list: List of model result dictionaries
        periods: Number of periods to forecast
        weights: Optional weights for each model (must sum to 1)
        
    Returns:
        Combined forecast DataFrame
    """
    if not model_results_list:
        print("No models provided")
        return pd.DataFrame()
    
    # Default to equal weights
    if weights is None:
        weights = [1.0 / len(model_results_list)] * len(model_results_list)
    
    if len(weights) != len(model_results_list):
        print("Number of weights must match number of models")
        return pd.DataFrame()
    
    # Generate forecasts from each model
    forecasts = []
    for model_result in model_results_list:
        forecast = generate_forecast(model_result, periods)
        if not forecast.empty:
            forecasts.append(forecast)
    
    if not forecasts:
        print("No valid forecasts generated")
        return pd.DataFrame()
    
    # Combine forecasts
    ensemble_df = forecasts[0][['date']].copy()
    
    # Weighted average of point forecasts
    ensemble_df['forecast'] = sum(
        forecasts[i]['forecast'] * weights[i] for i in range(len(forecasts))
    )
    
    # Use widest confidence intervals (conservative approach)
    ensemble_df['lower_ci'] = np.minimum.reduce([f['lower_ci'] for f in forecasts])
    ensemble_df['upper_ci'] = np.maximum.reduce([f['upper_ci'] for f in forecasts])
    
    return ensemble_df


def validate_forecast(actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
    """
    Calculate forecast accuracy metrics.
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        Dictionary with MAE, RMSE, MAPE metrics
    """
    errors = actual - predicted
    
    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors ** 2))
    mape = np.mean(np.abs(errors / actual)) * 100
    
    metrics = {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape
    }
    
    return metrics


def create_event_indicators(dates: pd.DatetimeIndex, event_dates: Dict[str, datetime],
                           lag_months: int = 6) -> pd.DataFrame:
    """
    Create binary event indicator variables for use as exogenous regressors.
    
    Args:
        dates: DatetimeIndex for the time series
        event_dates: Dictionary mapping event names to dates
        lag_months: Months after event to keep indicator active
        
    Returns:
        DataFrame with event indicators
    """
    indicators = pd.DataFrame(index=dates)
    
    for event_name, event_date in event_dates.items():
        event_date = pd.to_datetime(event_date)
        lag_date = event_date + timedelta(days=lag_months * 30)
        
        # Create binary indicator (1 from event date to lag_date, 0 otherwise)
        indicators[f'event_{event_name}'] = (
            (indicators.index >= event_date) & (indicators.index <= lag_date)
        ).astype(int)
    
    return indicators
