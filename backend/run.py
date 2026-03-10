#!/usr/bin/env python3
"""
Startup script for the AI Decision Support Dashboard backend
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting AI Decision Support Dashboard API...")
    print("API will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )