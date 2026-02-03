import pandas as pd
import os
from typing import Optional, Tuple, List
from datetime import datetime, timedelta

def load_data(data_path: str = 'data/ethiopia_fi_unified_data.xlsx', 
              codes_path: str = 'data/reference_codes.xlsx') -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Loads the unified data and reference codes.
    
    Args:
        data_path: Path to unified data Excel file
        codes_path: Path to reference codes Excel file
        
    Returns:
        Tuple of (unified_df, codes_df) or (None, None) if error
    """
    try:
        df_unified = pd.read_excel(data_path)
        df_codes = pd.read_excel(codes_path)
        print(f"Successfully loaded {data_path} and {codes_path}")
        return df_unified, df_codes
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None

def load_enriched_data(data_path: str = 'data/ethiopia_fi_unified_data_enriched.csv') -> Optional[pd.DataFrame]:
    """
    Load enriched dataset with proper date parsing.
    
    Args:
        data_path: Path to enriched CSV file
        
    Returns:
        DataFrame with parsed dates or None if error
    """
    try:
        df = pd.read_csv(data_path)
        df['observation_date'] = pd.to_datetime(df['observation_date'], errors='coerce')
        print(f"Successfully loaded {data_path} with {len(df)} records")
        return df
    except FileNotFoundError as e:
        print(f"Error loading file: {e}")
        return None

def inspect_schema(df: pd.DataFrame) -> None:
    """
    Prints schema information and value counts for key columns to demonstrate understanding.
    
    Args:
        df: DataFrame to inspect
    """
    if df is not None:
        print("\n--- Columns ---")
        print(df.columns.tolist())
        print("\n--- Schema Inspection ---")
        print(df.info())
        print("\n--- Record Type Distribution ---")
        if 'record_type' in df.columns:
            print(df['record_type'].value_counts())
        else:
            print("Column 'record_type' not found.")
        
        print("\n--- Impact Links Demonstration ---")
        # Check for impact_link and parent_id
        if 'record_type' in df.columns:
            impact_links = df[df['record_type'] == 'impact_link']
            if not impact_links.empty:
                print(f"Found {len(impact_links)} impact_link records.")
                print("Sample impact_links:")
                print(impact_links.head())
            else:
                print("No impact_link records found.")

def filter_by_event_window(df: pd.DataFrame, event_date: datetime, 
                           window_before_days: int = 365, 
                           window_after_days: int = 365) -> pd.DataFrame:
    """
    Filter data to a window around an event date.
    
    Args:
        df: DataFrame with 'observation_date' column
        event_date: Date of the event
        window_before_days: Days before event to include
        window_after_days: Days after event to include
        
    Returns:
        Filtered DataFrame
    """
    if 'observation_date' not in df.columns:
        raise ValueError("DataFrame must have 'observation_date' column")
    
    event_date = pd.to_datetime(event_date)
    start_date = event_date - timedelta(days=window_before_days)
    end_date = event_date + timedelta(days=window_after_days)
    
    filtered = df[(df['observation_date'] >= start_date) & 
                  (df['observation_date'] <= end_date)].copy()
    
    return filtered

def calculate_pre_post_statistics(df: pd.DataFrame, event_date: datetime, 
                                  indicator_code: str, 
                                  value_column: str = 'value_numeric') -> dict:
    """
    Calculate statistics before and after an event for a specific indicator.
    
    Args:
        df: DataFrame with observations
        event_date: Date of the event
        indicator_code: Indicator code to analyze
        value_column: Column containing numeric values
        
    Returns:
        Dictionary with pre/post statistics
    """
    event_date = pd.to_datetime(event_date)
    
    # Filter to specific indicator
    indicator_data = df[df['indicator_code'] == indicator_code].copy()
    indicator_data = indicator_data[indicator_data[value_column].notna()]
    
    # Split into pre and post
    pre_event = indicator_data[indicator_data['observation_date'] < event_date]
    post_event = indicator_data[indicator_data['observation_date'] >= event_date]
    
    stats = {
        'indicator_code': indicator_code,
        'event_date': event_date,
        'pre_event_count': len(pre_event),
        'post_event_count': len(post_event),
        'pre_event_mean': pre_event[value_column].mean() if len(pre_event) > 0 else None,
        'post_event_mean': post_event[value_column].mean() if len(post_event) > 0 else None,
        'pre_event_last': pre_event[value_column].iloc[-1] if len(pre_event) > 0 else None,
        'post_event_first': post_event[value_column].iloc[0] if len(post_event) > 0 else None,
    }
    
    # Calculate change
    if stats['pre_event_last'] and stats['post_event_first']:
        stats['immediate_change'] = stats['post_event_first'] - stats['pre_event_last']
        stats['immediate_change_pct'] = (stats['immediate_change'] / stats['pre_event_last']) * 100
    
    return stats

def get_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract all event records from the dataset.
    
    Args:
        df: DataFrame with 'record_type' column
        
    Returns:
        DataFrame containing only event records, sorted by date
    """
    events = df[df['record_type'] == 'event'].copy()
    if 'observation_date' in events.columns:
        events = events.sort_values('observation_date')
    return events

def get_observations(df: pd.DataFrame, indicator_codes: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Extract observation records, optionally filtered by indicator codes.
    
    Args:
        df: DataFrame with 'record_type' column
        indicator_codes: Optional list of indicator codes to filter
        
    Returns:
        DataFrame containing only observation records with numeric values
    """
    observations = df[df['record_type'] == 'observation'].copy()
    observations = observations[observations['value_numeric'].notna()]
    
    if indicator_codes:
        observations = observations[observations['indicator_code'].isin(indicator_codes)]
    
    if 'observation_date' in observations.columns:
        observations = observations.sort_values('observation_date')
    
    return observations

if __name__ == "__main__":
    # Ensure paths are correct relative to where the script is run
    # Assuming script is run from project root, or we handle path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    
    data_file = os.path.join(project_root, 'data', 'ethiopia_fi_unified_data.xlsx')
    codes_file = os.path.join(project_root, 'data', 'reference_codes.xlsx')
    
    df, codes = load_data(data_file, codes_file)
    inspect_schema(df)
