#!/bin/bash

# Railway deployment script for Registro Violeta Backend
echo "🚀 Starting Registro Violeta Backend deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if critical environment variables are set
echo "🔧 Checking environment variables..."
if [ -z "$MONGO_URL" ]; then
    echo "❌ Error: MONGO_URL environment variable is not set"
    echo "   Please configure MongoDB Atlas connection string"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ Error: JWT_SECRET_KEY environment variable is not set"
    echo "   Please configure a secure JWT secret key"
    exit 1
fi

# Test database connection
echo "🗄️  Testing database connection..."
python -c "
import os
from pymongo import MongoClient
try:
    client = MongoClient(os.getenv('MONGO_URL'))
    client.admin.command('ping')
    print('✅ Database connection successful')
    
    # Check if we have any users in the database
    db = client.registro_violeta
    user_count = db.users.count_documents({})
    print(f'👥 Users in database: {user_count}')
    
    if user_count == 0:
        print('⚠️  No users found. Run init_admin.py to create initial admin user')
    
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('   Check your MONGO_URL configuration')
    exit(1)
"

# Check if this is the first deployment (no users exist)
echo "🔍 Checking for initial admin user..."
python -c "
import os
from pymongo import MongoClient

try:
    client = MongoClient(os.getenv('MONGO_URL'))
    db = client.registro_violeta
    
    admin_exists = db.users.find_one({'rol': 'admin'})
    if not admin_exists:
        print('🚨 No admin user found. Creating initial admin...')
        # Auto-create admin on first deploy
        exec(open('init_admin.py').read())
    else:
        print('✅ Admin user exists')
        
except Exception as e:
    print(f'⚠️  Could not check for admin user: {e}')
"

echo "🌟 Starting Registro Violeta API..."
echo "🔗 Backend will be available at: https://\$RAILWAY_PUBLIC_DOMAIN"
echo "📱 Make sure frontend REACT_APP_BACKEND_URL points to this URL"

# Start the application
exec uvicorn server:app --host 0.0.0.0 --port $PORT
