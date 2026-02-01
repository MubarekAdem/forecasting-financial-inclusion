import pandas as pd
import os

def load_data(data_path='data/ethiopia_fi_unified_data.xlsx', codes_path='data/reference_codes.xlsx'):
    """
    Loads the unified data and reference codes.
    """
    try:
        df_unified = pd.read_excel(data_path)
        df_codes = pd.read_excel(codes_path)
        print(f"Successfully loaded {data_path} and {codes_path}")
        return df_unified, df_codes
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None

def inspect_schema(df):
    """
    Prints schema information and value counts for key columns to demonstrate understanding.
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

if __name__ == "__main__":
    # Ensure paths are correct relative to where the script is run
    # Assuming script is run from project root, or we handle path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    
    data_file = os.path.join(project_root, 'data', 'ethiopia_fi_unified_data.xlsx')
    codes_file = os.path.join(project_root, 'data', 'reference_codes.xlsx')
    
    df, codes = load_data(data_file, codes_file)
    inspect_schema(df)
