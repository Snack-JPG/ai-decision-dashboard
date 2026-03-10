from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    file_name = Column(String)
    file_size = Column(Integer)
    rows_count = Column(Integer)
    columns_count = Column(Integer)
    schema_metadata = Column(JSON)  # Store detected schema info
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    columns = relationship("DatasetColumn", back_populates="dataset")
    analysis_results = relationship("AnalysisResult", back_populates="dataset")
    
class DatasetColumn(Base):
    __tablename__ = "dataset_columns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, ForeignKey("datasets.id"))
    name = Column(String, nullable=False)
    data_type = Column(String)  # 'numeric', 'categorical', 'datetime', 'text'
    role = Column(String)  # 'metric', 'dimension', 'time', 'identifier'
    null_count = Column(Integer)
    unique_count = Column(Integer)
    sample_values = Column(JSON)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="columns")

class DataRow(Base):
    __tablename__ = "data_rows"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, ForeignKey("datasets.id"))
    row_index = Column(Integer)
    data = Column(JSON)  # Store actual row data as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, ForeignKey("datasets.id"))
    analysis_type = Column(String)  # 'trend', 'anomaly', 'correlation', 'seasonal'
    result = Column(JSON)
    confidence_score = Column(Float)
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="analysis_results")

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, ForeignKey("datasets.id"))
    query_text = Column(Text)
    response = Column(Text)
    context_used = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class UsageCounter(Base):
    __tablename__ = "usage_counters"
    __table_args__ = (UniqueConstraint("client_id", "usage_date", name="uq_usage_client_date"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String, nullable=False, index=True)
    usage_date = Column(String, nullable=False, index=True)  # YYYY-MM-DD (UTC)
    requests_count = Column(Integer, default=0, nullable=False)
    upload_bytes = Column(Integer, default=0, nullable=False)
    analysis_jobs_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
