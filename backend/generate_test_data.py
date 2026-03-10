#!/usr/bin/env python3

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv

# Set seed for reproducibility
np.random.seed(42)

# Generate 90 days of NHS emergency department data
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(90)]

data = []
base_waiting_time = 180  # Base waiting time in minutes

for i, date in enumerate(dates):
    # Add weekly trend (slight increase over time)
    trend = i * 0.8
    
    # Add weekly seasonality (higher on weekends)
    day_of_week = date.weekday()
    if day_of_week >= 5:  # Weekend
        seasonal = 25
    elif day_of_week in [0, 4]:  # Monday and Friday
        seasonal = 15
    else:
        seasonal = 0
    
    # Add some random noise
    noise = np.random.normal(0, 12)
    
    # Add occasional anomalies (system failures, major incidents)
    anomaly = 0
    if i in [20, 45, 70]:  # Three major incidents
        anomaly = np.random.normal(120, 20)
    elif i in [30, 60]:  # Two minor incidents
        anomaly = np.random.normal(60, 10)
    
    # Calculate metrics
    waiting_time = max(30, base_waiting_time + trend + seasonal + noise + anomaly)
    patients = max(50, int(150 + seasonal*2 + np.random.normal(0, 25) + (anomaly*0.3)))
    
    # Satisfaction inversely related to waiting time
    satisfaction = max(1.0, min(5.0, 5.5 - (waiting_time - 120) / 60))
    satisfaction += np.random.normal(0, 0.2)
    
    # Staff count affects waiting time
    base_staff = 12
    staff_variance = np.random.normal(0, 2)
    staff_on_duty = max(6, int(base_staff + staff_variance))
    
    # Adjust waiting time based on staff ratio
    patient_per_staff = patients / staff_on_duty
    if patient_per_staff > 15:
        waiting_time *= 1.3
    elif patient_per_staff > 12:
        waiting_time *= 1.1
    
    data.append({
        'date': date.strftime('%Y-%m-%d'),
        'waiting_time_minutes': round(waiting_time, 1),
        'patient_count': patients,
        'satisfaction_score': round(satisfaction, 2),
        'staff_on_duty': staff_on_duty,
        'department': 'Emergency',
        'day_of_week': date.strftime('%A')
    })

# Save to CSV
df = pd.DataFrame(data)
df.to_csv('/Users/austin/Desktop/ai-decision-dashboard/backend/nhs_sample_data.csv', index=False)

print(f"Generated {len(data)} rows of NHS sample data")
print(f"Date range: {data[0]['date']} to {data[-1]['date']}")
print(f"Waiting time range: {df['waiting_time_minutes'].min():.1f} - {df['waiting_time_minutes'].max():.1f} minutes")
print(f"Patient count range: {df['patient_count'].min()} - {df['patient_count'].max()}")
print(f"File saved to: nhs_sample_data.csv")