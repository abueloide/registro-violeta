from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Registro Violeta API", version="1.0.0")

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
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 43200))

# Conexión MongoDB
MONGO_URL = os.getenv("MONGO_URL")
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
    herramientas_entregadas: str
    avances_proceso_terapeutico: str
    cierre_sesion: str
    observaciones: str
    firma_terapeuta: str
    fundacion: str
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
        db_user = users_collection.find_one({"email": user.email})
        if not db_user or not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user["_id"])}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(db_user["_id"]),
                "email": db_user["email"],
                "nombre": db_user["nombre"],
                "apellido": db_user["apellido"],
                "rol": db_user["rol"],
                "fundacion": db_user["fundacion"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Rutas de sesiones terapéuticas
@app.post("/api/sessions")
async def create_session(session: SesionTerapeutica, current_user: dict = Depends(get_current_user)):
    try:
        session_dict = session.dict()
        session_dict["created_at"] = datetime.utcnow()
        session_dict["updated_at"] = datetime.utcnow()
        session_dict["created_by"] = str(current_user["_id"])
        
        result = sessions_collection.insert_one(session_dict)
        
        return {"message": "Session created successfully", "session_id": str(result.inserted_id)}
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
            
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    try:
        session = sessions_collection.find_one({"_id": ObjectId(session_id), "fundacion": current_user["fundacion"]})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session["_id"] = str(session["_id"])
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Rutas de perfiles
@app.post("/api/profiles")
async def create_profile(profile: ProfileCreate, current_user: dict = Depends(get_current_user)):
    try:
        profile_dict = profile.dict()
        profile_dict["created_at"] = datetime.utcnow()
        profile_dict["updated_at"] = datetime.utcnow()
        profile_dict["created_by"] = str(current_user["_id"])
        
        result = profiles_collection.insert_one(profile_dict)
        
        return {"message": "Profile created successfully", "profile_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/profiles")
async def get_profiles(current_user: dict = Depends(get_current_user)):
    try:
        profiles = list(profiles_collection.find({"fundacion": current_user["fundacion"]}).sort("created_at", -1))
        
        # Convertir ObjectId a string
        for profile in profiles:
            profile["_id"] = str(profile["_id"])
            
        return {"profiles": profiles}
    except Exception as e:
        logger.error(f"Error getting profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Ruta de salud
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

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