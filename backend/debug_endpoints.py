from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import traceback
from datetime import datetime

# Endpoint temporal de diagnóstico super detallado
@app.get("/api/debug-login")
async def debug_login_endpoint():
    """Diagnóstico súper detallado del problema de login"""
    debug_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "debug_checks": {}
    }
    
    # 1. Variables de entorno
    try:
        mongo_url = os.getenv("MONGO_URL", "NOT_SET")
        jwt_secret = os.getenv("JWT_SECRET_KEY", "NOT_SET")
        
        debug_info["debug_checks"]["environment"] = {
            "mongo_url_set": mongo_url != "NOT_SET",
            "mongo_url_length": len(mongo_url) if mongo_url != "NOT_SET" else 0,
            "mongo_url_preview": mongo_url[:50] + "..." if len(mongo_url) > 50 else mongo_url,
            "mongo_url_has_db_name": "/registro_violeta?" in mongo_url,
            "jwt_secret_set": jwt_secret != "NOT_SET",
            "jwt_secret_length": len(jwt_secret) if jwt_secret != "NOT_SET" else 0
        }
    except Exception as e:
        debug_info["debug_checks"]["environment"] = {"error": str(e)}
    
    # 2. Conexión MongoDB
    try:
        from pymongo import MongoClient
        client = MongoClient(os.getenv("MONGO_URL"), serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        db = client.registro_violeta
        users_collection = db.users
        
        user_count = users_collection.count_documents({})
        admin_count = users_collection.count_documents({"rol": "admin"})
        admin_user = users_collection.find_one({"email": "admin@registrovioleta.org"})
        
        debug_info["debug_checks"]["database"] = {
            "connection": "success",
            "total_users": user_count,
            "admin_users": admin_count,
            "specific_admin_exists": admin_user is not None,
            "admin_fields": list(admin_user.keys()) if admin_user else []
        }
    except Exception as e:
        debug_info["debug_checks"]["database"] = {
            "connection": "failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    
    # 3. Test de contraseña
    try:
        if admin_user:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            password_valid = pwd_context.verify("RegistroVioleta2025!", admin_user["password"])
            
            debug_info["debug_checks"]["password"] = {
                "admin_password_hash_exists": bool(admin_user.get("password")),
                "password_verification": password_valid,
                "hash_preview": admin_user.get("password", "")[:20] + "..." if admin_user.get("password") else ""
            }
    except Exception as e:
        debug_info["debug_checks"]["password"] = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    
    # 4. Test de JWT
    try:
        from jose import jwt
        from datetime import timedelta
        
        test_payload = {"sub": "test_user_id", "exp": datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(test_payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")
        decoded = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        
        debug_info["debug_checks"]["jwt"] = {
            "encoding": "success",
            "decoding": "success",
            "token_preview": token[:30] + "..."
        }
    except Exception as e:
        debug_info["debug_checks"]["jwt"] = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    
    # 5. Imports disponibles
    try:
        import sys
        available_modules = []
        required_modules = ['pymongo', 'passlib', 'jose', 'fastapi', 'bcrypt']
        
        for module in required_modules:
            try:
                __import__(module)
                available_modules.append(module)
            except ImportError:
                pass
        
        debug_info["debug_checks"]["imports"] = {
            "python_version": sys.version,
            "available_modules": available_modules,
            "missing_modules": [m for m in required_modules if m not in available_modules]
        }
    except Exception as e:
        debug_info["debug_checks"]["imports"] = {"error": str(e)}
    
    return JSONResponse(content=debug_info)

# Test específico de login
@app.post("/api/debug-test-login")
async def debug_test_login():
    """Test específico del proceso de login paso a paso"""
    steps = []
    
    try:
        # Paso 1: Verificar conexión DB
        steps.append({"step": 1, "description": "Testing database connection"})
        from pymongo import MongoClient
        client = MongoClient(os.getenv("MONGO_URL"))
        client.admin.command('ping')
        steps.append({"step": 1, "status": "success"})
        
        # Paso 2: Buscar usuario
        steps.append({"step": 2, "description": "Finding user admin@registrovioleta.org"})
        db = client.registro_violeta
        users_collection = db.users
        user = users_collection.find_one({"email": "admin@registrovioleta.org"})
        
        if not user:
            steps.append({"step": 2, "status": "failed", "error": "User not found"})
            return JSONResponse(content={"steps": steps})
        
        steps.append({"step": 2, "status": "success", "user_fields": list(user.keys())})
        
        # Paso 3: Verificar contraseña
        steps.append({"step": 3, "description": "Verifying password"})
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        password_valid = pwd_context.verify("RegistroVioleta2025!", user["password"])
        
        if not password_valid:
            steps.append({"step": 3, "status": "failed", "error": "Invalid password"})
            return JSONResponse(content={"steps": steps})
        
        steps.append({"step": 3, "status": "success"})
        
        # Paso 4: Crear JWT
        steps.append({"step": 4, "description": "Creating JWT token"})
        from jose import jwt
        from datetime import timedelta
        
        access_token_expires = timedelta(minutes=43200)
        access_token = jwt.encode(
            {"sub": str(user["_id"]), "exp": datetime.utcnow() + access_token_expires},
            os.getenv("JWT_SECRET_KEY"),
            algorithm="HS256"
        )
        
        steps.append({"step": 4, "status": "success", "token_length": len(access_token)})
        
        # Paso 5: Preparar respuesta
        steps.append({"step": 5, "description": "Preparing response"})
        user_data = {
            "id": str(user["_id"]),
            "email": user["email"],
            "nombre": user["nombre"],
            "apellido": user["apellido"],
            "rol": user["rol"],
            "fundacion": user["fundacion"]
        }
        
        steps.append({"step": 5, "status": "success"})
        
        return JSONResponse(content={
            "overall_status": "LOGIN_SHOULD_WORK",
            "steps": steps,
            "simulated_response": {
                "access_token": access_token[:30] + "...",
                "token_type": "bearer",
                "user": user_data
            }
        })
        
    except Exception as e:
        steps.append({
            "step": "ERROR",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        
        return JSONResponse(content={
            "overall_status": "LOGIN_WILL_FAIL",
            "steps": steps
        })
