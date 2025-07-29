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

# Resto de endpoints (manteniendo los existentes)
# ... [aquí irían todos los otros endpoints del archivo original]

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
