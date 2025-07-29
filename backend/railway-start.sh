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
    echo "💡 Should look like: mongodb+srv://user:pass@cluster.mongodb.net/registro_violeta?retryWrites=true&w=majority"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ Error: JWT_SECRET_KEY environment variable is not set"
    echo "   Please configure a secure JWT secret key (minimum 32 characters)"
    echo "💡 Example: registro-violeta-R3gistroVi0let4-super-secret-2024"
    exit 1
fi

echo "✅ Required environment variables are set"

# Test database connection and run quick fix
echo "🔧 Running quick fix to ensure everything is configured..."
python quick_fix.py

if [ $? -ne 0 ]; then
    echo "❌ Quick fix failed - check configuration"
    echo "📋 Common issues:"
    echo "   1. MONGO_URL format incorrect (should include /registro_violeta?)"
    echo "   2. MongoDB Atlas cluster not accessible"
    echo "   3. IP whitelist not set to 0.0.0.0/0"
    exit 1
fi

echo "✅ Quick fix completed successfully"

# Additional database verification
echo "🗄️  Final database verification..."
python -c "
import os
from pymongo import MongoClient
try:
    client = MongoClient(os.getenv('MONGO_URL'))
    client.admin.command('ping')
    
    db = client.registro_violeta
    user_count = db.users.count_documents({})
    admin_count = db.users.count_documents({'rol': 'admin'})
    
    print(f'✅ Database connected successfully')
    print(f'👥 Total users: {user_count}')
    print(f'🔑 Admin users: {admin_count}')
    
    if admin_count == 0:
        print('⚠️  No admin users found')
        exit(1)
    else:
        print('✅ Admin user exists - login should work')
        
except Exception as e:
    print(f'❌ Database verification failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database verification failed"
    exit 1
fi

echo "🌟 Starting Registro Violeta API..."
echo "🔗 Backend will be available at: https://\$RAILWAY_PUBLIC_DOMAIN"
echo "📱 Make sure frontend REACT_APP_BACKEND_URL points to this URL"
echo ""
echo "🔑 Default login credentials:"
echo "   📧 Email: admin@registrovioleta.org" 
echo "   🔐 Password: RegistroVioleta2025!"
echo ""

# Start the application
exec uvicorn server:app --host 0.0.0.0 --port $PORT
