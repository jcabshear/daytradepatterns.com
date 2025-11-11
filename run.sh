#!/bin/bash

echo "🚀 Starting NASDAQ Pattern Scanner..."
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🌐 Starting web server..."
echo "Open your browser to: http://localhost:8000"
echo ""

python main.py
