from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv
import uuid
import json
from pydantic import BaseModel, Field
from bson import ObjectId
import logging
import traceback

# Importar servicios
from services.drive_service import drive_service
from services.pdf_service import pdf_service

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Registro Violeta API", version="2.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de seguridad
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 43200))

# Conexión MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/registro_violeta")
client = MongoClient(MONGO_URL)
db = client.registro_violeta

# Colecciones
users_collection = db.users
sessions_collection = db.sessions
profiles_collection = db.profiles

# Modelos Pydantic
class UserCreate(BaseModel):
    email: str
    password: str
    nombre: str
    apellido: str
    rol: str = "terapeuta"  # terapeuta, psicologo, abogado, admin
    fundacion: str

class UserLogin(BaseModel):
    email: str
    password: str

class SesionTerapeutica(BaseModel):
    sesion_no: str
    fecha: str
    codigo_usuaria: str
    terapeuta: str
    objetivo_sesion: str
    desarrollo_objetivo: str
    ejercicios_actividades: str
    herramientas_entregadas: Optional[str] = ""
    avances_proceso_terapeutico: str
    cierre_sesion: str
    observaciones: Optional[str] = ""
    firma_terapeuta: str
    fundacion: str
    tipo_sesion: Optional[str] = "seguimiento"  # seguimiento, primera, crisis, cierre
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProfileCreate(BaseModel):
    codigo_usuaria: str
    edad_aproximada: Optional[str] = None
    situacion_general: Optional[str] = None
    tipo_violencia: Optional[str] = None
    estado_caso: str = "activo"
    terapeuta_asignado: str
    fundacion: str
    notas_generales: Optional[str] = None

class ProfileUpdate(BaseModel):
    edad_aproximada: Optional[str] = None
    situacion_general: Optional[str] = None
    tipo_violencia: Optional[str] = None
    estado_caso: Optional[str] = None
    terapeuta_asignado: Optional[str] = None
    notas_generales: Optional[str] = None

# Funciones de utilidad
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    return user

# Rutas de autenticación
@app.post("/api/auth/register")
async def register(user: UserCreate):
    try:
        # Verificar si el usuario ya existe
        if users_collection.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Crear nuevo usuario
        user_dict = user.dict()
        user_dict["password"] = get_password_hash(user.password)
        user_dict["created_at"] = datetime.utcnow()
        user_dict["active"] = True
        
        result = users_collection.insert_one(user_dict)
        
        return {"message": "User created successfully", "user_id": str(result.inserted_id)}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/login")
async def login(user: UserLogin):
    try:
        logger.info(f"🔑 Login attempt for email: {user.email}")
        
        # Verificar que la base de datos esté conectada
        try:
            client.admin.command('ping')
            logger.info("✅ Database connection verified during login")
        except Exception as e:
            logger.error(f"❌ Database connection failed during login: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Buscar usuario
        logger.info(f"🔍 Searching for user: {user.email}")
        db_user = users_collection.find_one({"email": user.email})
        
        if not db_user:
            logger.warning(f"❌ User not found: {user.email}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        logger.info(f"✅ User found: {user.email}, role: {db_user.get('rol', 'unknown')}")
        
        # Verificar contraseña
        logger.info(f"🔐 Verifying password for user: {user.email}")
        try:
            password_valid = verify_password(user.password, db_user["password"])
            if not password_valid:
                logger.warning(f"❌ Invalid password for user: {user.email}")
                raise HTTPException(status_code=401, detail="Incorrect email or password")
            
            logger.info(f"✅ Password verified for user: {user.email}")
        except Exception as e:
            logger.error(f"❌ Password verification error: {e}")
            raise HTTPException(status_code=500, detail="Password verification error")
        
        # Crear token JWT
        logger.info(f"🎫 Creating JWT token for user: {user.email}")
        try:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(db_user["_id"])}, expires_delta=access_token_expires
            )
            logger.info(f"✅ JWT token created for user: {user.email}")
        except Exception as e:
            logger.error(f"❌ JWT creation error: {e}")
            raise HTTPException(status_code=500, detail="Token creation error")
        
        # Preparar respuesta del usuario
        try:
            user_data = {
                "id": str(db_user["_id"]),
                "email": db_user["email"],
                "nombre": db_user["nombre"],
                "apellido": db_user["apellido"],
                "rol": db_user["rol"],
                "fundacion": db_user["fundacion"]
            }
            logger.info(f"🎉 Login successful for user: {user.email}")
        except Exception as e:
            logger.error(f"❌ User data preparation error: {e}")
            raise HTTPException(status_code=500, detail="User data error")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Unexpected error during login: {str(e)}")
        logger.error(f"📊 Login error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Rutas de sesiones terapéuticas
@app.post("/api/sessions")
async def create_session(session: SesionTerapeutica, current_user: dict = Depends(get_current_user)):
    try:
        session_dict = session.dict()
        session_dict["created_at"] = datetime.utcnow()
        session_dict["updated_at"] = datetime.utcnow()
        session_dict["created_by"] = str(current_user["_id"])
        
        # Insertar en MongoDB
        result = sessions_collection.insert_one(session_dict)
        session_id = str(result.inserted_id)
        
        # Generar PDF
        pdf_content = pdf_service.create_session_pdf(session_dict)
        
        if pdf_content and drive_service.service:
            # Obtener o crear carpetas en Drive
            folders = drive_service.get_or_create_user_folder(
                session.codigo_usuaria, 
                session.fundacion
            )
            
            if folders:
                # Subir PDF a Google Drive
                filename = f"Sesion_{session.sesion_no}_{session.fecha}.pdf"
                file_id = drive_service.upload_file(
                    pdf_content,
                    filename,
                    folders['sesiones_folder_id']
                )
                
                if file_id:
                    # Actualizar la sesión con el ID del archivo en Drive
                    sessions_collection.update_one(
                        {"_id": ObjectId(session_id)},
                        {
                            "$set": {
                                "drive_file_id": file_id,
                                "drive_folder_id": folders['sesiones_folder_id'],
                                "pdf_filename": filename
                            }
                        }
                    )
                    
                    logger.info(f"Session {session_id} saved to Drive with file ID {file_id}")
        
        return {
            "message": "Session created successfully", 
            "session_id": session_id,
            "pdf_generated": pdf_content is not None
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sessions")
async def get_sessions(current_user: dict = Depends(get_current_user), codigo_usuaria: Optional[str] = None):
    try:
        query = {"fundacion": current_user["fundacion"]}
        if codigo_usuaria:
            query["codigo_usuaria"] = codigo_usuaria
            
        sessions = list(sessions_collection.find(query).sort("created_at", -1))
        
        # Convertir ObjectId a string
        for session in sessions:
            session["_id"] = str(session["_id"])
            if "created_at" in session:
                session["created_at"] = session["created_at"].isoformat()
            if "updated_at" in session:
                session["updated_at"] = session["updated_at"].isoformat()
            
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    try:
        session = sessions_collection.find_one({
            "_id": ObjectId(session_id), 
            "fundacion": current_user["fundacion"]
        })
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session["_id"] = str(session["_id"])
        if "created_at" in session:
            session["created_at"] = session["created_at"].isoformat()
        if "updated_at" in session:
            session["updated_at"] = session["updated_at"].isoformat()
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sessions/{session_id}/pdf")
async def download_session_pdf(session_id: str, current_user: dict = Depends(get_current_user)):
    try:
        session = sessions_collection.find_one({
            "_id": ObjectId(session_id), 
            "fundacion": current_user["fundacion"]
        })
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generar PDF en tiempo real si no está en Drive
        pdf_content = pdf_service.create_session_pdf(session)
        
        if not pdf_content:
            raise HTTPException(status_code=500, detail="Error generating PDF")
        
        filename = f"Sesion_{session.get('sesion_no', 'unknown')}_{session.get('fecha', 'unknown')}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading session PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Rutas de perfiles
@app.post("/api/profiles")
async def create_profile(profile: ProfileCreate, current_user: dict = Depends(get_current_user)):
    try:
        # Verificar que no exista el código de usuaria
        existing_profile = profiles_collection.find_one({
            "codigo_usuaria": profile.codigo_usuaria,
            "fundacion": profile.fundacion
        })
        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile with this code already exists")
        
        profile_dict = profile.dict()
        profile_dict["created_at"] = datetime.utcnow()
        profile_dict["updated_at"] = datetime.utcnow()
        profile_dict["created_by"] = str(current_user["_id"])
        
        result = profiles_collection.insert_one(profile_dict)
        
        # Crear estructura de carpetas en Drive
        if drive_service.service:
            folders = drive_service.get_or_create_user_folder(
                profile.codigo_usuaria, 
                profile.fundacion
            )
            if folders:
                profiles_collection.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"drive_folders": folders}}
                )
        
        return {"message": "Profile created successfully", "profile_id": str(result.inserted_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/profiles")
async def get_profiles(current_user: dict = Depends(get_current_user)):
    try:
        profiles = list(profiles_collection.find({"fundacion": current_user["fundacion"]}).sort("created_at", -1))
        
        # Convertir ObjectId a string y agregar estadísticas
        for profile in profiles:
            profile["_id"] = str(profile["_id"])
            if "created_at" in profile:
                profile["created_at"] = profile["created_at"].isoformat()
            if "updated_at" in profile:
                profile["updated_at"] = profile["updated_at"].isoformat()
            
            # Agregar conteo de sesiones
            session_count = sessions_collection.count_documents({
                "codigo_usuaria": profile["codigo_usuaria"],
                "fundacion": current_user["fundacion"]
            })
            profile["total_sessions"] = session_count
            
            # Última sesión
            last_session = sessions_collection.find_one(
                {
                    "codigo_usuaria": profile["codigo_usuaria"],
                    "fundacion": current_user["fundacion"]
                },
                sort=[("created_at", -1)]
            )
            if last_session:
                profile["last_session_date"] = last_session["fecha"]
            
        return {"profiles": profiles}
    except Exception as e:
        logger.error(f"Error getting profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/profiles/{profile_id}")
async def get_profile(profile_id: str, current_user: dict = Depends(get_current_user)):
    try:
        profile = profiles_collection.find_one({
            "_id": ObjectId(profile_id), 
            "fundacion": current_user["fundacion"]
        })
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        profile["_id"] = str(profile["_id"])
        if "created_at" in profile:
            profile["created_at"] = profile["created_at"].isoformat()
        if "updated_at" in profile:
            profile["updated_at"] = profile["updated_at"].isoformat()
        
        # Obtener sesiones del perfil
        sessions = list(sessions_collection.find({
            "codigo_usuaria": profile["codigo_usuaria"],
            "fundacion": current_user["fundacion"]
        }).sort("created_at", -1))
        
        for session in sessions:
            session["_id"] = str(session["_id"])
            if "created_at" in session:
                session["created_at"] = session["created_at"].isoformat()
        
        profile["sessions"] = sessions
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/api/profiles/{profile_id}")
async def update_profile(profile_id: str, profile_update: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    try:
        # Verificar que el perfil existe y pertenece a la fundación
        existing_profile = profiles_collection.find_one({
            "_id": ObjectId(profile_id),
            "fundacion": current_user["fundacion"]
        })
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Preparar datos de actualización
        update_data = {k: v for k, v in profile_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Actualizar el perfil
        result = profiles_collection.update_one(
            {"_id": ObjectId(profile_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made")
        
        return {"message": "Profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/profiles/{profile_id}/pdf")
async def download_profile_pdf(profile_id: str, current_user: dict = Depends(get_current_user)):
    try:
        profile = profiles_collection.find_one({
            "_id": ObjectId(profile_id), 
            "fundacion": current_user["fundacion"]
        })
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Obtener sesiones del perfil
        sessions = list(sessions_collection.find({
            "codigo_usuaria": profile["codigo_usuaria"],
            "fundacion": current_user["fundacion"]
        }).sort("created_at", -1))
        
        # Generar PDF del perfil
        pdf_content = pdf_service.create_profile_pdf(profile, sessions)
        
        if not pdf_content:
            raise HTTPException(status_code=500, detail="Error generating PDF")
        
        filename = f"Perfil_{profile.get('codigo_usuaria', 'unknown')}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading profile PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Rutas de estadísticas y dashboard
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    try:
        # Estadísticas básicas
        total_profiles = profiles_collection.count_documents({"fundacion": current_user["fundacion"]})
        total_sessions = sessions_collection.count_documents({"fundacion": current_user["fundacion"]})
        active_profiles = profiles_collection.count_documents({
            "fundacion": current_user["fundacion"],
            "estado_caso": "activo"
        })
        
        # Sesiones por mes (últimos 6 meses)
        from datetime import datetime, timedelta
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        pipeline = [
            {
                "$match": {
                    "fundacion": current_user["fundacion"],
                    "created_at": {"$gte": six_months_ago}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        sessions_by_month = list(sessions_collection.aggregate(pipeline))
        
        return {
            "total_profiles": total_profiles,
            "total_sessions": total_sessions,
            "active_profiles": active_profiles,
            "sessions_by_month": sessions_by_month
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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

# Endpoint de debug para login
@app.post("/api/debug/test-login")
async def debug_test_login():
    """Test específico del proceso de login paso a paso"""
    steps = []
    
    try:
        # Paso 1: Verificar conexión DB
        steps.append({"step": 1, "description": "Testing database connection"})
        client.admin.command('ping')
        steps.append({"step": 1, "status": "success"})
        
        # Paso 2: Buscar usuario
        steps.append({"step": 2, "description": "Finding user admin@registrovioleta.org"})
        user = users_collection.find_one({"email": "admin@registrovioleta.org"})
        
        if not user:
            steps.append({"step": 2, "status": "failed", "error": "User not found"})
            return {"steps": steps, "overall_status": "USER_NOT_FOUND"}
        
        steps.append({"step": 2, "status": "success", "user_fields": list(user.keys())})
        
        # Paso 3: Verificar contraseña
        steps.append({"step": 3, "description": "Verifying password"})
        password_valid = verify_password("RegistroVioleta2025!", user["password"])
        
        if not password_valid:
            steps.append({"step": 3, "status": "failed", "error": "Invalid password"})
            return {"steps": steps, "overall_status": "INVALID_PASSWORD"}
        
        steps.append({"step": 3, "status": "success"})
        
        # Paso 4: Crear JWT
        steps.append({"step": 4, "description": "Creating JWT token"})
        access_token_expires = timedelta(minutes=43200)
        access_token = create_access_token(
            data={"sub": str(user["_id"])}, expires_delta=access_token_expires
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
        
        return {
            "overall_status": "LOGIN_SHOULD_WORK",
            "steps": steps,
            "message": "All login steps completed successfully"
        }
        
    except Exception as e:
        steps.append({
            "step": "ERROR",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        
        return {
            "overall_status": "LOGIN_WILL_FAIL",
            "steps": steps,
            "error": str(e)
        }

# Ruta para obtener información del usuario actual
@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "nombre": current_user["nombre"],
        "apellido": current_user["apellido"],
        "rol": current_user["rol"],
        "fundacion": current_user["fundacion"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
