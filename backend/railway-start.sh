#!/bin/bash

# Railway deployment script for Registro Violeta Backend
echo "🚀 Starting Registro Violeta Backend deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations if needed
echo "🗄️  Checking database connection..."
python -c "
import os
from pymongo import MongoClient
try:
    client = MongoClient(os.getenv('MONGO_URL'))
    client.admin.command('ping')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Start the application
echo "🌟 Starting Registro Violeta API..."
exec uvicorn server:app --host 0.0.0.0 --port $PORT
