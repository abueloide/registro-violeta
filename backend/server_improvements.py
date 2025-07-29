@app.post("/api/auth/login")
async def login(user: UserLogin):
    try:
        logger.info(f"Login attempt for email: {user.email}")
        
        # Verificar que la base de datos esté conectada
        try:
            client.admin.command('ping')
            logger.info("Database connection verified")
        except Exception as e:
            logger.error(f"Database connection failed during login: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Buscar usuario
        db_user = users_collection.find_one({"email": user.email})
        if not db_user:
            logger.warning(f"User not found: {user.email}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        logger.info(f"User found: {user.email}, role: {db_user.get('rol', 'unknown')}")
        
        # Verificar contraseña
        if not verify_password(user.password, db_user["password"]):
            logger.warning(f"Invalid password for user: {user.email}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        logger.info(f"Password verified for user: {user.email}")
        
        # Crear token JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user["_id"])}, expires_delta=access_token_expires
        )
        
        logger.info(f"JWT token created for user: {user.email}")
        
        user_data = {
            "id": str(db_user["_id"]),
            "email": db_user["email"],
            "nombre": db_user["nombre"],
            "apellido": db_user["apellido"],
            "rol": db_user["rol"],
            "fundacion": db_user["fundacion"]
        }
        
        logger.info(f"Login successful for user: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        logger.error(f"Login error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Ruta de salud mejorada
@app.get("/api/health")
async def health_check():
    """Health check con diagnóstico detallado"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "checks": {}
    }
    
    # Verificar base de datos
    try:
        client.admin.command('ping')
        user_count = users_collection.count_documents({})
        admin_exists = users_collection.find_one({"rol": "admin"}) is not None
        
        health_status["checks"]["database"] = {
            "status": "connected",
            "user_count": user_count,
            "admin_exists": admin_exists
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["database"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Verificar variables de entorno críticas
    env_checks = {
        "mongo_url": bool(os.getenv("MONGO_URL")),
        "jwt_secret": bool(os.getenv("JWT_SECRET_KEY"))
    }
    health_status["checks"]["environment"] = env_checks
    
    if not all(env_checks.values()):
        health_status["status"] = "degraded"
    
    # Verificar Google Drive (opcional)
    health_status["checks"]["drive_service"] = {
        "status": "available" if drive_service.service is not None else "not_configured"
    }
    
    return health_status

# Nuevo endpoint de diagnóstico
@app.get("/api/diagnose")
async def diagnostic_endpoint():
    """Endpoint de diagnóstico detallado para troubleshooting"""
    try:
        import subprocess
        import sys
        
        # Ejecutar script de diagnóstico
        result = subprocess.run([
            sys.executable, "diagnose.py"
        ], capture_output=True, text=True, cwd=".")
        
        return {
            "diagnostic_available": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except Exception as e:
        return {
            "diagnostic_available": False,
            "error": str(e),
            "message": "Run 'python backend/diagnose.py' manually for detailed diagnosis"
        }
