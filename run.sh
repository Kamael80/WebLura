#!/bin/bash
echo "🚀 Starting WebLura Server..."
pip install -r requirements.txt -q
uvicorn main:app --host 0.0.0.0 --port 8765 --reload
