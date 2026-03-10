import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import uuid
import os
from models import Dataset, DatasetColumn, DataRow
from database import get_db_session

def detect_column_type(series: pd.Series) -> Dict[str, Any]:
    """
    Detect the data type and role of a pandas Series column
    Returns dict with type, role, stats
    """
    # Remove null values for analysis
    clean_series = series.dropna()
    
    if len(clean_series) == 0:
        return {
            "data_type": "unknown", 
            "role": "unknown",
            "null_count": int(len(series)),
            "unique_count": 0,
            "sample_values": []
        }
    
    # Try to detect numeric first (before datetime)
    if _is_numeric_column(clean_series):
        # Determine if it's a metric or identifier
        unique_ratio = series.nunique() / len(series)
        role = "identifier" if unique_ratio > 0.8 else "metric"
        
        return {
            "data_type": "numeric",
            "role": role,
            "null_count": int(series.isnull().sum()),
            "unique_count": int(series.nunique()),
            "sample_values": clean_series.head(5).tolist(),
            "min": float(clean_series.min()),
            "max": float(clean_series.max()),
            "mean": float(clean_series.mean())
        }
    
    # Try to detect datetime
    if _is_datetime_column(clean_series):
        return {
            "data_type": "datetime",
            "role": "time",
            "null_count": int(series.isnull().sum()),
            "unique_count": int(series.nunique()),
            "sample_values": clean_series.head(5).astype(str).tolist()
        }
    
    # String/categorical data
    unique_ratio = series.nunique() / len(series)
    if unique_ratio < 0.1:  # Low cardinality suggests categorical
        role = "dimension"
    else:
        role = "text"
    
    return {
        "data_type": "categorical" if role == "dimension" else "text",
        "role": role,
        "null_count": int(series.isnull().sum()),
        "unique_count": int(series.nunique()),
        "sample_values": clean_series.head(5).astype(str).tolist()
    }

def _is_datetime_column(series: pd.Series) -> bool:
    """Check if series contains datetime data"""
    # Check for common date patterns first (more reliable)
    sample = series.head(20).astype(str)
    
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY or DD/MM/YYYY
        r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY or DD-MM-YYYY
        r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        r'\w+ \d{1,2}, \d{4}', # Month DD, YYYY
        r'\d{1,2} \w+ \d{4}',  # DD Month YYYY
    ]
    
    # Check if majority of values match date patterns
    matches = 0
    for pattern in date_patterns:
        matches += sample.str.match(pattern).sum()
    
    # Require at least 60% of values to match date patterns
    if matches / len(sample) >= 0.6:
        return True
    
    # Only try pandas parsing if pattern matching suggests it's a date
    # This prevents numeric values from being misidentified as dates
    return False

def _is_numeric_column(series: pd.Series) -> bool:
    """Check if series contains numeric data"""
    try:
        pd.to_numeric(series, errors='raise')
        return True
    except:
        return False

def ingest_csv_file(file_path: str, dataset_name: str, description: str = None) -> str:
    """
    Ingest a CSV file into the database
    Returns the dataset ID
    """
    # Read CSV file
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {str(e)}")
    
    if df.empty:
        raise ValueError("CSV file is empty")
    
    # Generate dataset ID
    dataset_id = str(uuid.uuid4())
    
    # Get database session
    db = get_db_session()
    
    try:
        # Analyze schema
        schema_metadata = {}
        columns_info = []
        
        for col_name in df.columns:
            col_info = detect_column_type(df[col_name])
            col_info['name'] = col_name
            columns_info.append(col_info)
            
            # Store in schema metadata
            schema_metadata[col_name] = col_info
        
        # Create dataset record
        dataset = Dataset(
            id=dataset_id,
            name=dataset_name,
            description=description,
            file_name=os.path.basename(file_path),
            file_size=os.path.getsize(file_path),
            rows_count=len(df),
            columns_count=len(df.columns),
            schema_metadata=schema_metadata
        )
        
        db.add(dataset)
        
        # Create column records
        dataset_columns = []
        for col_info in columns_info:
            dataset_columns.append(DatasetColumn(
                dataset_id=dataset_id,
                name=col_info['name'],
                data_type=col_info['data_type'],
                role=col_info['role'],
                null_count=int(col_info['null_count']),
                unique_count=int(col_info['unique_count']),
                sample_values=col_info['sample_values']
            ))
        db.add_all(dataset_columns)
        
        # Store data rows in batches to avoid per-row flush overhead
        batch = []
        for idx, row in df.iterrows():
            # Convert numpy types to native Python types for JSON serialization
            row_data = {}
            for col, val in row.items():
                if pd.isna(val):
                    row_data[col] = None
                elif isinstance(val, np.integer):
                    row_data[col] = int(val)
                elif isinstance(val, np.floating):
                    row_data[col] = float(val)
                else:
                    row_data[col] = str(val)
            
            batch.append(DataRow(
                dataset_id=dataset_id,
                row_index=idx,
                data=row_data
            ))

            if len(batch) >= 1000:
                db.add_all(batch)
                db.flush()
                batch = []

        if batch:
            db.add_all(batch)
        
        # Commit all changes
        db.commit()
        
        return dataset_id
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_dataset_summary(dataset_id: str) -> Dict[str, Any]:
    """Get summary information about a dataset"""
    db = get_db_session()
    
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError("Dataset not found")
        
        columns = db.query(DatasetColumn).filter(DatasetColumn.dataset_id == dataset_id).all()
        
        return {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "rows_count": dataset.rows_count,
            "columns_count": dataset.columns_count,
            "created_at": dataset.created_at.isoformat(),
            "columns": [
                {
                    "name": col.name,
                    "data_type": col.data_type,
                    "role": col.role,
                    "null_count": col.null_count,
                    "unique_count": col.unique_count,
                    "sample_values": col.sample_values
                }
                for col in columns
            ]
        }
    finally:
        db.close()

def get_dataset_data(dataset_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
    """Get data rows from a dataset"""
    db = get_db_session()
    
    try:
        rows = db.query(DataRow).filter(
            DataRow.dataset_id == dataset_id
        ).order_by(DataRow.row_index.asc()).limit(limit).all()
        
        return [row.data for row in rows]
    finally:
        db.close()
