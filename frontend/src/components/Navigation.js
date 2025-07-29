import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Heart, Home, FileText, Users, LogOut, Plus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Navigation = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo y título */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <div className="bg-violeta-gradient p-2 rounded-lg">
                <Heart className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Registro Violeta</h1>
                <p className="text-xs text-gray-500">{user?.fundacion}</p>
              </div>
            </Link>
          </div>

          {/* Enlaces de navegación */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/') 
                  ? 'bg-violeta-100 text-violeta-700' 
                  : 'text-gray-600 hover:text-violeta-600 hover:bg-gray-100'
              }`}
            >
              <Home className="h-4 w-4" />
              <span>Dashboard</span>
            </Link>

            <Link
              to="/nueva-sesion"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/nueva-sesion') 
                  ? 'bg-violeta-100 text-violeta-700' 
                  : 'text-gray-600 hover:text-violeta-600 hover:bg-gray-100'
              }`}
            >
              <Plus className="h-4 w-4" />
              <span>Nueva sesión</span>
            </Link>

            <Link
              to="/sesiones"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/sesiones') 
                  ? 'bg-violeta-100 text-violeta-700' 
                  : 'text-gray-600 hover:text-violeta-600 hover:bg-gray-100'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Sesiones</span>
            </Link>

            <Link
              to="/perfiles"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/perfiles') 
                  ? 'bg-violeta-100 text-violeta-700' 
                  : 'text-gray-600 hover:text-violeta-600 hover:bg-gray-100'
              }`}
            >
              <Users className="h-4 w-4" />
              <span>Perfiles</span>
            </Link>
          </div>

          {/* Información del usuario y logout */}
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {user?.nombre} {user?.apellido}
              </p>
              <p className="text-xs text-gray-500 capitalize">{user?.rol}</p>
            </div>
            
            <button
              onClick={logout}
              className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span>Salir</span>
            </button>
          </div>
        </div>

        {/* Navegación móvil */}
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 border-t border-gray-200">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/') 
                  ? 'bg-violeta-100 text-violeta-700' 
                  : 'text-gray-600 hover:text-violeta-600 hover:bg-gray-100'
              }`}
            >
              <Home className="h-4 w-4" />
              <span>Dashboard</span>
            </Link>

            <Link
              to="/nueva-sesion"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/nueva-sesion') 
                  ? 'bg-violeta-100 text-violeta-700' 
                  : 'text-gray-600 hover:text-violeta-600 hover:bg-gray-100'
              }`}
            >
              <Plus className="h-4 w-4" />
              <span>Nueva sesión</span>
            </Link>

            <Link
              to="/sesiones"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/sesiones') 
                  ? 'bg-violeta-100 text-violeta-700' 
                  : 'text-gray-600 hover:text-violeta-600 hover:bg-gray-100'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Sesiones</span>
            </Link>

            <Link
              to="/perfiles"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/perfiles') 
                  ? 'bg-violeta-100 text-violeta-700' 
                  : 'text-gray-600 hover:text-violeta-600 hover:bg-gray-100'
              }`}
            >
              <Users className="h-4 w-4" />
              <span>Perfiles</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;