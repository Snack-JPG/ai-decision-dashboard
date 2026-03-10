#!/usr/bin/env python3
"""
Test script for the AI analysis engine
"""

import sys
import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

try:
    from analysis import analyze_dataset_full
    from ingestion import get_dataset_data, get_dataset_summary
    from database import init_database, DATABASE_URL
    print("✅ Analysis engine imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def create_test_data():
    """Create test time series data for analysis"""
    # Generate sample NHS waiting time data
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    np.random.seed(42)  # For reproducible results
    
    data = []
    base_waiting_time = 180  # minutes
    
    for i, date in enumerate(dates):
        # Add trend (slight increase over time)
        trend = i * 0.5
        
        # Add weekly seasonality (higher on weekends)
        seasonal = 20 * np.sin(2 * np.pi * i / 7) if date.weekday() >= 5 else 0
        
        # Add noise
        noise = np.random.normal(0, 15)
        
        # Add some anomalies
        anomaly = 0
        if i in [30, 60]:  # Days with major incidents
            anomaly = 80
        
        waiting_time = base_waiting_time + trend + seasonal + noise + anomaly
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'department': 'A&E',
            'waiting_time_minutes': round(waiting_time, 1),
            'attendances': round(200 + np.random.normal(0, 30)),
            'category': 'urgent'
        })
    
    return data

def test_analysis_engine():
    """Test the analysis engine with synthetic data"""
    print("\n🔬 Testing Analysis Engine")
    
    # Create test data
    print("📊 Creating test dataset...")
    try:
        test_data = create_test_data()
        print(f"✅ Created {len(test_data)} data points")
    except Exception as e:
        print(f"❌ Failed to create test data: {e}")
        return False
    
    # Define column metadata
    columns_metadata = [
        {"name": "date", "data_type": "datetime", "role": "time"},
        {"name": "department", "data_type": "categorical", "role": "dimension"},
        {"name": "waiting_time_minutes", "data_type": "numeric", "role": "metric"},
        {"name": "attendances", "data_type": "numeric", "role": "metric"},
        {"name": "category", "data_type": "categorical", "role": "dimension"}
    ]
    
    # Run analysis
    print("🤖 Running comprehensive analysis...")
    try:
        results = analyze_dataset_full(test_data, columns_metadata)
        print("✅ Analysis completed successfully!")
        
        # Print summary
        print("\n📋 Analysis Results Summary:")
        print(f"  Dataset rows: {results.get('dataset_summary', {}).get('total_rows', 0)}")
        print(f"  Key insights found: {len(results.get('key_insights', []))}")
        print(f"  Trends analyzed: {len(results.get('trends', {}))}")
        print(f"  Anomalies detected: {sum(len(a.get('anomalies', [])) for a in results.get('anomalies', {}).values())}")
        print(f"  Correlations found: {len(results.get('correlations', {}).get('significant_correlations', []))}")
        
        # Print top insights
        if results.get('key_insights'):
            print("\n🎯 Top Insights:")
            for i, insight in enumerate(results['key_insights'][:3], 1):
                print(f"  {i}. [{insight['type'].upper()}] {insight['title']}")
                print(f"     Confidence: {insight['confidence']:.2f}")
                if 'ai_explanation' in insight:
                    print(f"     AI: {insight['ai_explanation']}")
                else:
                    print(f"     Explanation: {insight['explanation']}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_integration():
    """Test database integration"""
    print("\n💾 Testing Database Integration")
    
    try:
        init_database()
        print("✅ Database initialized")
        
        # Check if database file exists
        if DATABASE_URL.startswith("sqlite:///./"):
            db_file = DATABASE_URL.replace("sqlite:///./", "", 1)
            db_path = os.path.join(os.getcwd(), db_file)
        else:
            db_path = os.path.join(os.getcwd(), "ai_dashboard.db")
        if os.path.exists(db_path):
            print(f"✅ Database file exists: {os.path.getsize(db_path)} bytes")
        else:
            print("❌ Database file not found")
            return False
        
        # Test database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        expected_tables = ['datasets', 'dataset_columns', 'data_rows', 'analysis_results', 'query_history']
        
        print(f"📋 Database tables: {[t[0] for t in tables]}")
        
        for expected_table in expected_tables:
            if expected_table in [t[0] for t in tables]:
                print(f"✅ Table '{expected_table}' exists")
            else:
                print(f"❌ Table '{expected_table}' missing")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AI Decision Support Dashboard - Analysis Engine Test")
    print("=" * 60)
    
    # Test database
    db_ok = test_database_integration()
    
    # Test analysis engine
    analysis_ok = test_analysis_engine()
    
    print("\n" + "=" * 60)
    if db_ok and analysis_ok:
        print("🎉 All tests passed! Phase 3 implementation is ready.")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
