import pandas as pd
import datetime

def enrich_data(input_path='data/ethiopia_fi_unified_data.xlsx', output_path='data/ethiopia_fi_unified_data_enriched.csv'):
    try:
        df = pd.read_excel(input_path)
        print(f"Loaded {len(df)} records from {input_path}")
    except FileNotFoundError:
        print("Input file not found.")
        return

    # Define new records
    new_records = [
        {
            # New Event: Launch of National Digital ID
            'record_id': 'EVT_2024_001',
            'record_type': 'event',
            'category': 'REGULATION',
            'pillar': 'INFRASTRUCTURE',
            'indicator': 'Digital ID Launch',
            'indicator_code': 'DIG_ID_LAUNCH',
            'observation_date': '2024-01-25',
            'source_name': 'NID Program',
            'source_url': 'https://fayda.et/',
            'confidence': 'high',
            'original_text': 'Launch of Fayda ID registration countrywide.',
            'notes': 'Enriched data point'
        },
        {
            # New Observation: Estimated Account Ownership for 2024
            'record_id': 'OBS_2024_001',
            'record_type': 'observation',
            'pillar': 'ACCESS',
            'indicator': 'Account Ownership Rate',
            'indicator_code': 'ACC_OWNERSHIP',
            'indicator_direction': 'higher_better',
            'value_numeric': 48.5,
            'unit': '%',
            'observation_date': '2024-06-30',
            'source_name': 'NBE Estimate',
            'confidence': 'medium',
            'notes': 'Projected based on recent trends.'
        },
        {
            # Impact Link: ID Launch -> Account Ownership
            'record_id': 'IMP_2024_001',
            'record_type': 'impact_link',
            'related_indicator': 'ACC_OWNERSHIP', # The target
            'relationship_type': 'causal',
            'impact_direction': 'positive',
            'impact_estimate': 'High',
            'evidence_basis': 'Global experience',
            'notes': 'Digital ID expected to boost account opening',
            # Ideally this links an Event ID to an Indicator Code or another ID
            # Based on schema inference, we use related_indicator or similar fields
            'original_text': 'Digital ID implementation is a key driver for financial inclusion.'
        }
    ]

    df_new = pd.DataFrame(new_records)
    
    # Concatenate
    df_enriched = pd.concat([df, df_new], ignore_index=True)
    
    # Save as CSV
    df_enriched.to_csv(output_path, index=False)
    print(f"Saved enriched data to {output_path} with {len(df_enriched)} records.")

if __name__ == "__main__":
    enrich_data()
