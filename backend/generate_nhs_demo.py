#!/usr/bin/env python3
"""
Generate realistic NHS A&E demo dataset with seasonal patterns, regional variation,
and some anomalies to showcase the AI analysis capabilities.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducible results
np.random.seed(42)
random.seed(42)

# NHS Trust data - real trust names and regions for authenticity
NHS_TRUSTS = [
    ("Royal London Hospital", "London", "North East London"),
    ("Manchester Royal Infirmary", "North West", "Greater Manchester"), 
    ("Birmingham Heartlands Hospital", "Midlands", "West Midlands"),
    ("Leeds General Infirmary", "North East", "West Yorkshire"),
    ("Bristol Royal Infirmary", "South West", "Avon"),
    ("Addenbrooke's Hospital", "East", "Cambridgeshire"),
    ("Queen Elizabeth Hospital", "South East", "Kent"),
    ("Royal Victoria Infirmary", "North East", "Tyne and Wear"),
    ("Southampton General Hospital", "South Central", "Hampshire"),
    ("Nottingham University Hospital", "Midlands", "Nottinghamshire"),
    ("St Mary's Hospital", "London", "Central London"),
    ("Royal Derby Hospital", "Midlands", "Derbyshire"),
    ("Plymouth Derriford Hospital", "South West", "Devon"),
    ("Blackpool Victoria Hospital", "North West", "Lancashire"),
    ("Norfolk and Norwich Hospital", "East", "Norfolk")
]

def generate_base_metrics(trust_name, region, base_date):
    """Generate base metrics for a trust with regional variation"""
    
    # Base attendance levels vary by region and trust size
    region_multipliers = {
        "London": 1.3,
        "North West": 1.1, 
        "Midlands": 1.0,
        "North East": 0.9,
        "South West": 0.8,
        "East": 0.9,
        "South East": 1.0,
        "South Central": 0.9
    }
    
    base_attendances = 12000 * region_multipliers.get(region.split()[0], 1.0)
    
    # London and major cities have higher baseline activity
    if "London" in trust_name or "Manchester" in trust_name or "Birmingham" in trust_name:
        base_attendances *= 1.2
    
    return {
        'base_attendances': base_attendances,
        'base_4hr_pct': 85.0,  # Starting around 85% target compliance
        'base_emergency_admissions': base_attendances * 0.25,
        'base_12hr_waits': base_attendances * 0.05,
        'base_handover_delays': base_attendances * 0.08
    }

def apply_seasonal_patterns(value, month, metric_type):
    """Apply realistic seasonal patterns to metrics"""
    
    # Winter months are significantly worse for NHS
    winter_months = [12, 1, 2, 3]
    summer_months = [6, 7, 8]
    
    if metric_type == 'attendances':
        if month in winter_months:
            return value * random.uniform(1.15, 1.35)  # 15-35% higher in winter
        elif month in summer_months:
            return value * random.uniform(0.85, 0.95)  # 5-15% lower in summer
        else:
            return value * random.uniform(0.95, 1.1)
    
    elif metric_type == 'within_4hrs_pct':
        if month in winter_months:
            return value * random.uniform(0.75, 0.9)  # Much worse performance in winter
        elif month in summer_months:
            return value * random.uniform(1.05, 1.15)  # Better in summer
        else:
            return value * random.uniform(0.9, 1.05)
    
    elif metric_type in ['twelve_hr_waits', 'handover_delays']:
        if month in winter_months:
            return value * random.uniform(1.5, 2.5)  # Much worse in winter
        elif month in summer_months:
            return value * random.uniform(0.4, 0.7)  # Better in summer
        else:
            return value * random.uniform(0.8, 1.3)
    
    elif metric_type == 'emergency_admissions':
        if month in winter_months:
            return value * random.uniform(1.1, 1.25)  # More admissions in winter
        else:
            return value * random.uniform(0.9, 1.1)
    
    return value

def add_covid_impact(date, value, metric_type):
    """Add COVID-19 impact patterns (March 2020 - late 2021)"""
    
    # Define COVID waves
    first_wave = (datetime(2020, 3, 1), datetime(2020, 6, 30))
    second_wave = (datetime(2020, 10, 1), datetime(2021, 2, 28))
    delta_wave = (datetime(2021, 6, 1), datetime(2021, 10, 31))
    
    covid_periods = [first_wave, second_wave, delta_wave]
    
    for start, end in covid_periods:
        if start <= date <= end:
            if metric_type == 'attendances':
                # Reduced attendances during COVID (people avoiding hospitals)
                impact = random.uniform(0.6, 0.8)
            elif metric_type == 'within_4hrs_pct':
                # Worse performance due to COVID protocols
                impact = random.uniform(0.7, 0.85)
            elif metric_type in ['twelve_hr_waits', 'handover_delays']:
                # Much worse delays due to COVID protocols
                impact = random.uniform(1.5, 2.2)
            else:
                impact = random.uniform(0.8, 1.2)
            
            return value * impact
    
    return value

def add_anomalies(data):
    """Add some realistic anomalies to make the data interesting"""
    
    # Add a few random "crisis" periods
    anomaly_dates = random.sample(range(len(data)), 8)  # 8 anomalous periods
    
    for idx in anomaly_dates:
        anomaly_type = random.choice(['staffing_crisis', 'flu_outbreak', 'system_failure', 'major_incident'])
        
        if anomaly_type == 'staffing_crisis':
            # Worse performance, higher waits
            data.iloc[idx, data.columns.get_loc('within_4hrs_pct')] *= random.uniform(0.6, 0.8)
            data.iloc[idx, data.columns.get_loc('twelve_hr_waits')] *= random.uniform(2.0, 3.5)
            data.iloc[idx, data.columns.get_loc('ambulance_handover_delays')] *= random.uniform(1.8, 2.5)
            
        elif anomaly_type == 'flu_outbreak':
            # Much higher attendances
            data.iloc[idx, data.columns.get_loc('attendances')] *= random.uniform(1.4, 1.8)
            data.iloc[idx, data.columns.get_loc('emergency_admissions')] *= random.uniform(1.3, 1.6)
            data.iloc[idx, data.columns.get_loc('within_4hrs_pct')] *= random.uniform(0.7, 0.85)
            
        elif anomaly_type == 'system_failure':
            # IT/system issues causing delays
            data.iloc[idx, data.columns.get_loc('within_4hrs_pct')] *= random.uniform(0.5, 0.7)
            data.iloc[idx, data.columns.get_loc('twelve_hr_waits')] *= random.uniform(3.0, 5.0)
            
        elif anomaly_type == 'major_incident':
            # Major incident bringing many casualties
            data.iloc[idx, data.columns.get_loc('attendances')] *= random.uniform(1.2, 1.5)
            data.iloc[idx, data.columns.get_loc('emergency_admissions')] *= random.uniform(1.4, 1.8)
    
    return data

def generate_nhs_dataset():
    """Generate the complete NHS A&E demo dataset"""
    
    # Generate 36 months of data (Jan 2021 - Dec 2023)
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    data = []
    
    current_date = start_date
    while current_date <= end_date:
        for trust_name, region, sub_region in NHS_TRUSTS:
            
            # Get base metrics for this trust
            base_metrics = generate_base_metrics(trust_name, region, current_date)
            
            # Apply seasonal patterns
            attendances = apply_seasonal_patterns(
                base_metrics['base_attendances'], 
                current_date.month, 
                'attendances'
            )
            
            within_4hrs_pct = apply_seasonal_patterns(
                base_metrics['base_4hr_pct'], 
                current_date.month, 
                'within_4hrs_pct'
            )
            
            emergency_admissions = apply_seasonal_patterns(
                base_metrics['base_emergency_admissions'], 
                current_date.month, 
                'emergency_admissions'
            )
            
            twelve_hr_waits = apply_seasonal_patterns(
                base_metrics['base_12hr_waits'], 
                current_date.month, 
                'twelve_hr_waits'
            )
            
            handover_delays = apply_seasonal_patterns(
                base_metrics['base_handover_delays'], 
                current_date.month, 
                'handover_delays'
            )
            
            # Apply COVID impact
            attendances = add_covid_impact(current_date, attendances, 'attendances')
            within_4hrs_pct = add_covid_impact(current_date, within_4hrs_pct, 'within_4hrs_pct')
            twelve_hr_waits = add_covid_impact(current_date, twelve_hr_waits, 'twelve_hr_waits')
            handover_delays = add_covid_impact(current_date, handover_delays, 'handover_delays')
            
            # Add some random noise
            attendances *= random.uniform(0.95, 1.05)
            within_4hrs_pct *= random.uniform(0.95, 1.05)
            
            # Ensure realistic bounds
            within_4hrs_pct = max(45, min(95, within_4hrs_pct))  # Between 45% and 95%
            attendances = max(5000, attendances)  # At least 5000 attendances per month
            emergency_admissions = min(attendances * 0.4, emergency_admissions)  # Max 40% admission rate
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'trust_name': trust_name,
                'region': region,
                'attendances': int(attendances),
                'within_4hrs_pct': round(within_4hrs_pct, 1),
                'emergency_admissions': int(emergency_admissions),
                'twelve_hr_waits': int(twelve_hr_waits),
                'ambulance_handover_delays': int(handover_delays)
            })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Add anomalies
    df = add_anomalies(df)
    
    # Sort by date and trust name
    df = df.sort_values(['date', 'trust_name']).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    print("Generating NHS A&E demo dataset...")
    df = generate_nhs_dataset()
    
    # Save to CSV
    output_path = "data/nhs_ae_demo.csv"
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    
    print(f"Dataset generated successfully!")
    print(f"Rows: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Trusts: {df['trust_name'].nunique()}")
    print(f"Saved to: {output_path}")
    
    # Show sample data
    print("\nSample data:")
    print(df.head(10))
    
    # Show basic statistics
    print(f"\nBasic statistics:")
    print(df.describe())