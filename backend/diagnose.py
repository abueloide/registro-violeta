#!/usr/bin/env python3
"""
Script de diagnóstico para Registro Violeta
Identifica problemas comunes de conexión y configuración
"""

import os
import sys
import traceback
from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

def log(message, level="INFO"):
    """Log con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_environment_variables():
    """Verificar variables de entorno críticas"""
    log("🔧 Verificando variables de entorno...")
    
    required_vars = {
        "MONGO_URL": os.getenv("MONGO_URL"),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY")
    }
    
    all_good = True
    for var, value in required_vars.items():
        if not value:
            log(f"❌ {var} no está configurada", "ERROR")
            all_good = False
        else:
            # Mostrar solo parte de la variable por seguridad
            if var == "MONGO_URL":
                display_value = value[:30] + "..." if len(value) > 30 else value
            elif var == "JWT_SECRET_KEY":
                display_value = f"{'*' * len(value)} (longitud: {len(value)})"
            else:
                display_value = value
            log(f"✅ {var}: {display_value}")
    
    return all_good

def test_database_connection():
    """Probar conexión a MongoDB"""
    log("🗄️  Probando conexión a MongoDB...")
    
    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url:
        log("❌ MONGO_URL no configurada", "ERROR")
        return False
    
    try:
        # Conectar a MongoDB
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=10000)
        
        # Test de ping
        client.admin.command('ping')
        log("✅ Ping a MongoDB exitoso")
        
        # Verificar base de datos
        db = client.registro_violeta
        log(f"✅ Conectado a base de datos: {db.name}")
        
        # Verificar colecciones
        collections = db.list_collection_names()
        log(f"📋 Colecciones disponibles: {collections}")
        
        # Contar documentos en colecciones principales
        users_count = db.users.count_documents({})
        sessions_count = db.sessions.count_documents({})
        profiles_count = db.profiles.count_documents({})
        
        log(f"👥 Usuarios: {users_count}")
        log(f"📝 Sesiones: {sessions_count}")
        log(f"📁 Perfiles: {profiles_count}")
        
        # Verificar si existe usuario admin
        admin_user = db.users.find_one({"rol": "admin"})
        if admin_user:
            log(f"✅ Usuario admin encontrado: {admin_user.get('email', 'N/A')}")
        else:
            log("⚠️  No se encontró usuario admin", "WARNING")
        
        return True
        
    except Exception as e:
        log(f"❌ Error de conexión a MongoDB: {str(e)}", "ERROR")
        log(f"💡 Verifica que MONGO_URL sea correcta y que el cluster esté activo", "ERROR")
        return False

def test_password_hashing():
    """Verificar funcionalidad de hashing de contraseñas"""
    log("🔐 Probando sistema de contraseñas...")
    
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        test_password = "RegistroVioleta2025!"
        hashed = pwd_context.hash(test_password)
        verified = pwd_context.verify(test_password, hashed)
        
        if verified:
            log("✅ Sistema de hashing funciona correctamente")
            return True
        else:
            log("❌ Error en verificación de contraseña", "ERROR")
            return False
            
    except Exception as e:
        log(f"❌ Error en sistema de contraseñas: {str(e)}", "ERROR")
        return False

def create_admin_user_if_needed():
    """Crear usuario admin si no existe"""
    log("👤 Verificando/creando usuario admin...")
    
    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url:
        log("❌ No se puede crear admin sin MONGO_URL", "ERROR")
        return False
    
    try:
        client = MongoClient(mongo_url)
        db = client.registro_violeta
        users_collection = db.users
        
        # Verificar si ya existe admin
        admin_exists = users_collection.find_one({"email": "admin@registrovioleta.org"})
        if admin_exists:
            log("✅ Usuario admin ya existe")
            return True
        
        # Crear usuario admin
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin_user = {
            "email": "admin@registrovioleta.org",
            "password": pwd_context.hash("RegistroVioleta2025!"),
            "nombre": "Admin",
            "apellido": "Sistema",
            "rol": "admin",
            "fundacion": "Registro Violeta",
            "created_at": datetime.utcnow(),
            "active": True
        }
        
        result = users_collection.insert_one(admin_user)
        
        if result.inserted_id:
            log("🎉 Usuario admin creado exitosamente!")
            log("📧 Email: admin@registrovioleta.org")
            log("🔑 Contraseña: RegistroVioleta2025!")
            return True
        else:
            log("❌ Error al crear usuario admin", "ERROR")
            return False
            
    except Exception as e:
        log(f"❌ Error creando usuario admin: {str(e)}", "ERROR")
        log(f"🔍 Detalle del error: {traceback.format_exc()}", "ERROR")
        return False

def test_login_simulation():
    """Simular proceso de login para identificar problemas"""
    log("🔑 Simulando proceso de login...")
    
    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url:
        log("❌ No se puede simular login sin MONGO_URL", "ERROR")
        return False
    
    try:
        client = MongoClient(mongo_url)
        db = client.registro_violeta
        users_collection = db.users
        
        # Buscar usuario admin
        admin_user = users_collection.find_one({"email": "admin@registrovioleta.org"})
        if not admin_user:
            log("❌ Usuario admin no encontrado", "ERROR")
            return False
        
        log("✅ Usuario admin encontrado en base de datos")
        
        # Verificar contraseña
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_valid = pwd_context.verify("RegistroVioleta2025!", admin_user["password"])
        
        if password_valid:
            log("✅ Contraseña del admin es válida")
        else:
            log("❌ Contraseña del admin no es válida", "ERROR")
            return False
        
        # Verificar estructura del usuario
        required_fields = ["email", "nombre", "apellido", "rol", "fundacion"]
        for field in required_fields:
            if field not in admin_user:
                log(f"❌ Campo faltante en usuario: {field}", "ERROR")
                return False
        
        log("✅ Estructura del usuario admin es correcta")
        log("✅ Simulación de login exitosa - El login debería funcionar")
        
        return True
        
    except Exception as e:
        log(f"❌ Error en simulación de login: {str(e)}", "ERROR")
        log(f"🔍 Detalle del error: {traceback.format_exc()}", "ERROR")
        return False

def main():
    """Ejecutar todos los diagnósticos"""
    log("🟣 REGISTRO VIOLETA - DIAGNÓSTICO COMPLETO")
    log("=" * 60)
    
    # Lista de pruebas
    tests = [
        ("Variables de Entorno", test_environment_variables),
        ("Conexión a Base de Datos", test_database_connection),
        ("Sistema de Contraseñas", test_password_hashing),
        ("Usuario Administrador", create_admin_user_if_needed),
        ("Simulación de Login", test_login_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        log(f"\n🧪 Ejecutando: {test_name}")
        log("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            log(f"💥 Error inesperado en {test_name}: {str(e)}", "ERROR")
            results.append((test_name, False))
    
    # Resumen final
    log("\n📊 RESUMEN DE DIAGNÓSTICO")
    log("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        log(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        log("\n🎉 ¡TODOS LOS TESTS PASARON!")
        log("💜 El login debería funcionar correctamente ahora")
        log("🔗 Intenta hacer login con:")
        log("   📧 admin@registrovioleta.org")
        log("   🔑 RegistroVioleta2025!")
    else:
        log("\n🚨 ALGUNOS TESTS FALLARON")
        log("📝 Revisa los errores arriba y corrige la configuración")
        log("🆘 Si necesitas ayuda, comparte estos logs")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
