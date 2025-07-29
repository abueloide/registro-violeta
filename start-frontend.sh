#!/bin/bash
export HOST=0.0.0.0
export PORT=3000
export DANGEROUSLY_DISABLE_HOST_CHECK=true
export WDS_SOCKET_HOST=0.0.0.0
export REACT_APP_BACKEND_URL=http://localhost:8001
export BROWSER=none
export FAST_REFRESH=false

cd /app/frontend

# Iniciar con configuración forzada para aceptar todos los hosts
exec npx react-scripts start