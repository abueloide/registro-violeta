import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from io import BytesIO
import json
import logging

logger = logging.getLogger(__name__)

class GoogleDriveService:
    def __init__(self):
        self.service = None
        self.setup_service()
    
    def setup_service(self):
        """Configurar el servicio de Google Drive"""
        try:
            # Obtener credenciales desde variable de entorno
            creds_json = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
            if not creds_json:
                logger.warning("Google Drive credentials not found")
                return
            
            # Parsear las credenciales JSON
            creds_info = json.loads(creds_json)
            
            # Crear credenciales
            credentials = Credentials.from_service_account_info(
                creds_info,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # Construir el servicio
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up Google Drive service: {e}")
            self.service = None
    
    def create_folder(self, name, parent_folder_id=None):
        """Crear una carpeta en Google Drive"""
        if not self.service:
            logger.error("Google Drive service not available")
            return None
        
        try:
            folder_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(body=folder_metadata).execute()
            logger.info(f"Created folder: {name} with ID: {folder['id']}")
            return folder['id']
            
        except Exception as e:
            logger.error(f"Error creating folder {name}: {e}")
            return None
    
    def upload_file(self, file_content, filename, parent_folder_id=None, mime_type='application/pdf'):
        """Subir un archivo a Google Drive"""
        if not self.service:
            logger.error("Google Drive service not available")
            return None
        
        try:
            file_metadata = {'name': filename}
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            # Crear media upload desde bytes
            media = MediaIoBaseUpload(
                BytesIO(file_content),
                mimetype=mime_type
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media
            ).execute()
            
            logger.info(f"Uploaded file: {filename} with ID: {file['id']}")
            return file['id']
            
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {e}")
            return None
    
    def get_or_create_user_folder(self, codigo_usuaria, fundacion):
        """Obtener o crear la estructura de carpetas para una usuaria"""
        if not self.service:
            logger.error("Google Drive service not available")
            return None
        
        try:
            # Buscar o crear carpeta principal de la fundación
            fundacion_folder_id = self.get_or_create_folder(fundacion)
            if not fundacion_folder_id:
                return None
            
            # Buscar o crear carpeta "Usuarias"
            usuarias_folder_id = self.get_or_create_folder("Usuarias", fundacion_folder_id)
            if not usuarias_folder_id:
                return None
            
            # Buscar o crear carpeta de la usuaria específica
            user_folder_id = self.get_or_create_folder(codigo_usuaria, usuarias_folder_id)
            if not user_folder_id:
                return None
            
            # Crear subcarpetas
            sesiones_folder_id = self.get_or_create_folder("Sesiones", user_folder_id)
            documentos_folder_id = self.get_or_create_folder("Documentos", user_folder_id)
            
            return {
                'user_folder_id': user_folder_id,
                'sesiones_folder_id': sesiones_folder_id,
                'documentos_folder_id': documentos_folder_id
            }
            
        except Exception as e:
            logger.error(f"Error managing user folder for {codigo_usuaria}: {e}")
            return None
    
    def get_or_create_folder(self, folder_name, parent_folder_id=None):
        """Buscar una carpeta existente o crearla si no existe"""
        if not self.service:
            return None
        
        try:
            # Buscar carpeta existente
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            results = self.service.files().list(q=query).execute()
            items = results.get('files', [])
            
            if items:
                return items[0]['id']
            else:
                # Crear nueva carpeta
                return self.create_folder(folder_name, parent_folder_id)
                
        except Exception as e:
            logger.error(f"Error getting or creating folder {folder_name}: {e}")
            return None
    
    def list_files_in_folder(self, folder_id):
        """Listar archivos en una carpeta específica"""
        if not self.service:
            return []
        
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id, name, mimeType, createdTime, modifiedTime)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            logger.error(f"Error listing files in folder {folder_id}: {e}")
            return []
    
    def delete_file(self, file_id):
        """Eliminar un archivo de Google Drive"""
        if not self.service:
            return False
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file with ID: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False
    
    def get_file_link(self, file_id):
        """Obtener el enlace público de un archivo"""
        if not self.service:
            return None
        
        try:
            # Hacer el archivo público
            self.service.permissions().create(
                fileId=file_id,
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            
            # Retornar el enlace de visualización
            return f"https://drive.google.com/file/d/{file_id}/view"
            
        except Exception as e:
            logger.error(f"Error getting file link for {file_id}: {e}")
            return None

# Instancia global del servicio
drive_service = GoogleDriveService()
