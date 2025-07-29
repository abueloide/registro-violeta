#!/usr/bin/env python3
"""
🔧 QUICK FIX - Registro Violeta Login Issue
Ejecutar este script para resolver problemas de login rápidamente
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext
from dotenv import load_dotenv

def main():
    print("🟣 REGISTRO VIOLETA - QUICK FIX")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # 1. Verificar MONGO_URL
    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url:
        print("❌ MONGO_URL no configurada")
        print("💡 Configura en Railway:")
        print("   MONGO_URL=mongodb+srv://registrovioleta:R3gistroVi0let4@registrovioleta.cjt2jxf.mongodb.net/registro_violeta?retryWrites=true&w=majority&appName=registrovioleta")
        return False
    
    # Verificar formato correcto de MONGO_URL
    if "/registro_violeta?" not in mongo_url:
        print("⚠️  MONGO_URL parece incorrecta")
        print("🔧 URL actual:", mongo_url[:50] + "...")
        print("💡 Debería incluir '/registro_violeta?' antes de los parámetros")
        correct_url = mongo_url.replace("/?", "/registro_violeta?")
        print("💡 URL corregida:", correct_url[:50] + "...")
        return False
    
    print("✅ MONGO_URL configurada correctamente")
    
    # 2. Verificar JWT_SECRET_KEY
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret or len(jwt_secret) < 32:
        print("❌ JWT_SECRET_KEY no configurada o muy corta")
        print("💡 Configura en Railway:")
        print("   JWT_SECRET_KEY=registro-violeta-R3gistroVi0let4-super-secret-2024")
        return False
    
    print("✅ JWT_SECRET_KEY configurada correctamente")
    
    # 3. Probar conexión a MongoDB
    try:
        print("🔍 Probando conexión a MongoDB...")
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✅ Conexión a MongoDB exitosa")
        
        db = client.registro_violeta
        users_collection = db.users
        
        # 4. Verificar/crear usuario admin
        admin_user = users_collection.find_one({"email": "admin@registrovioleta.org"})
        
        if admin_user:
            print("✅ Usuario admin ya existe")
            
            # Verificar contraseña
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            if pwd_context.verify("RegistroVioleta2025!", admin_user["password"]):
                print("✅ Contraseña del admin es correcta")
                print("🎉 ¡Todo está configurado correctamente!")
                print("")
                print("🔑 Credenciales de login:")
                print("   📧 Email: admin@registrovioleta.org")
                print("   🔐 Contraseña: RegistroVioleta2025!")
                print("")
                print("🌐 Intenta hacer login en tu frontend")
                return True
            else:
                print("❌ Contraseña del admin incorrecta, recreando...")
                users_collection.delete_one({"email": "admin@registrovioleta.org"})
                admin_user = None
        
        if not admin_user:
            print("🔧 Creando usuario admin...")
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            admin_data = {
                "email": "admin@registrovioleta.org",
                "password": pwd_context.hash("RegistroVioleta2025!"),
                "nombre": "Admin",
                "apellido": "Sistema",
                "rol": "admin", 
                "fundacion": "Registro Violeta",
                "created_at": datetime.utcnow(),
                "active": True
            }
            
            result = users_collection.insert_one(admin_data)
            
            if result.inserted_id:
                print("🎉 Usuario admin creado exitosamente!")
                print("")
                print("🔑 Credenciales de login:")
                print("   📧 Email: admin@registrovioleta.org")
                print("   🔐 Contraseña: RegistroVioleta2025!")
                print("")
                print("✅ ¡El problema de login está RESUELTO!")
                print("🌐 Ve a tu frontend e intenta hacer login")
                return True
            else:
                print("❌ Error al crear usuario admin")
                return False
                
    except Exception as e:
        print(f"❌ Error de conexión a MongoDB: {e}")
        print("")
        print("🔧 Posibles soluciones:")
        print("1. Verifica que MONGO_URL sea correcta en Railway")
        print("2. Verifica que el cluster de MongoDB Atlas esté activo")
        print("3. Verifica que la IP esté whitelistada (0.0.0.0/0)")
        print("4. Verifica usuario/contraseña de MongoDB Atlas")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n💜 ¡QUICK FIX COMPLETADO EXITOSAMENTE!")
    else:
        print("\n🚨 QUICK FIX FALLÓ - Revisa los errores arriba")
    
    sys.exit(0 if success else 1)
