#!/usr/bin/env python3
"""
Script para crear el usuario administrador inicial de Registro Violeta
Ejecutar después del deploy para crear el primer usuario
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_admin_user():
    """Crear usuario administrador inicial"""
    
    # Conexión MongoDB
    MONGO_URL = os.getenv("MONGO_URL")
    if not MONGO_URL:
        print("❌ Error: MONGO_URL no configurada")
        return False
    
    try:
        client = MongoClient(MONGO_URL)
        db = client.registro_violeta
        users_collection = db.users
        
        # Verificar conexión
        client.admin.command('ping')
        print("✅ Conexión a base de datos exitosa")
        
        # Datos del admin inicial
        admin_email = "admin@registrovioleta.org"
        admin_password = "RegistroVioleta2025!"  # Cambiar después del primer login
        
        # Verificar si ya existe un admin
        existing_admin = users_collection.find_one({"email": admin_email})
        if existing_admin:
            print(f"⚠️  El usuario admin {admin_email} ya existe")
            return True
        
        # Crear usuario admin
        admin_user = {
            "email": admin_email,
            "password": get_password_hash(admin_password),
            "nombre": "Admin",
            "apellido": "Sistema",
            "rol": "admin",
            "fundacion": "Registro Violeta",
            "created_at": datetime.utcnow(),
            "active": True
        }
        
        result = users_collection.insert_one(admin_user)
        
        if result.inserted_id:
            print("🎉 Usuario administrador creado exitosamente!")
            print(f"📧 Email: {admin_email}")
            print(f"🔑 Contraseña: {admin_password}")
            print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
            return True
        else:
            print("❌ Error al crear el usuario administrador")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        return False

def verify_environment():
    """Verificar que las variables de entorno estén configuradas"""
    required_vars = [
        "MONGO_URL",
        "JWT_SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ Variables de entorno configuradas correctamente")
    return True

if __name__ == "__main__":
    print("🟣 Registro Violeta - Inicialización de Usuario Admin")
    print("=" * 50)
    
    # Verificar variables de entorno
    if not verify_environment():
        sys.exit(1)
    
    # Crear usuario admin
    if create_admin_user():
        print("\n✅ Inicialización completada exitosamente")
        print("🚀 Ya puedes iniciar sesión en la aplicación")
    else:
        print("\n❌ Error en la inicialización")
        sys.exit(1)
