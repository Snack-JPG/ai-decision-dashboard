#!/usr/bin/env python3

# Quick test of analysis module
print("Testing analysis module import...")

try:
    from analysis import AnalysisEngine
    print("✅ AnalysisEngine imported")
    
    # Test with simple data
    test_data = [
        {"date": "2024-01-01", "value": 100},
        {"date": "2024-01-02", "value": 110},
        {"date": "2024-01-03", "value": 105},
        {"date": "2024-01-04", "value": 115},
        {"date": "2024-01-05", "value": 120}
    ]
    
    columns_metadata = [
        {"name": "date", "data_type": "datetime", "role": "time"},
        {"name": "value", "data_type": "numeric", "role": "metric"}
    ]
    
    engine = AnalysisEngine()
    print("✅ AnalysisEngine created")
    
    results = engine.analyze_dataset(test_data, columns_metadata)
    print("✅ Analysis completed")
    print(f"Results keys: {list(results.keys())}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()