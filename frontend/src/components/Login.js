import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Heart, Lock, Mail, AlertTriangle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState({ checking: true, healthy: null });
  const { login, checkBackendHealth, API_BASE_URL } = useAuth();
  const navigate = useNavigate();
  
  const { register, handleSubmit, formState: { errors } } = useForm();

  // Verificar estado del backend al cargar
  useEffect(() => {
    const checkBackend = async () => {
      setBackendStatus({ checking: true, healthy: null });
      const result = await checkBackendHealth();
      setBackendStatus({ 
        checking: false, 
        healthy: result.healthy,
        error: result.error,
        data: result.data
      });
    };
    
    checkBackend();
  }, [checkBackendHealth]);

  const onSubmit = async (data) => {
    // Verificar backend antes de intentar login
    if (!backendStatus.healthy) {
      const result = await checkBackendHealth();
      if (!result.healthy) {
        return;
      }
      setBackendStatus({ checking: false, healthy: true, data: result.data });
    }

    setLoading(true);
    const result = await login(data.email, data.password);
    setLoading(false);
    
    if (result.success) {
      navigate('/');
    }
  };

  const retryConnection = async () => {
    setBackendStatus({ checking: true, healthy: null });
    const result = await checkBackendHealth();
    setBackendStatus({ 
      checking: false, 
      healthy: result.healthy,
      error: result.error,
      data: result.data
    });
  };

  // Componente de estado del backend
  const BackendStatus = () => {
    if (backendStatus.checking) {
      return (
        <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center">
            <RefreshCw className="h-5 w-5 text-blue-500 animate-spin mr-2" />
            <span className="text-sm text-blue-700">Verificando conexión al servidor...</span>
          </div>
        </div>
      );
    }

    if (backendStatus.healthy) {
      return (
        <div className="mb-6 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
            <span className="text-sm text-green-700">
              Servidor conectado correctamente
            </span>
          </div>
        </div>
      );
    }

    return (
      <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center mb-2">
          <XCircle className="h-5 w-5 text-red-500 mr-2" />
          <span className="text-sm font-medium text-red-700">
            Error de conexión al servidor
          </span>
        </div>
        <div className="text-xs text-red-600 mb-3">
          <div>URL: {API_BASE_URL}</div>
          <div>Error: {backendStatus.error}</div>
        </div>
        <button
          onClick={retryConnection}
          className="text-xs bg-red-100 hover:bg-red-200 text-red-700 px-3 py-1 rounded"
        >
          Reintentar conexión
        </button>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo y título */}
        <div className="flex justify-center">
          <div className="bg-violeta-gradient p-3 rounded-full">
            <Heart className="h-8 w-8 text-white" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
          Registro Violeta
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Herramienta digital para el acompañamiento terapéutico
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="violeta-form py-8 px-4 shadow sm:rounded-lg sm:px-10">
          
          {/* Estado del backend */}
          <BackendStatus />

          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Correo electrónico
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('email', {
                    required: 'El correo es requerido',
                    pattern: {
                      value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                      message: 'Correo electrónico inválido'
                    }
                  })}
                  type="email"
                  className="violeta-input pl-10"
                  placeholder="admin@registrovioleta.org"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            {/* Contraseña */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Contraseña
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('password', {
                    required: 'La contraseña es requerida',
                    minLength: {
                      value: 6,
                      message: 'Mínimo 6 caracteres'
                    }
                  })}
                  type="password"
                  className="violeta-input pl-10"
                  placeholder="••••••••"
                />
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* Credenciales por defecto */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-amber-500 mt-0.5 mr-2" />
                <div className="text-sm">
                  <p className="font-medium text-amber-800">Credenciales de prueba:</p>
                  <p className="text-amber-700 mt-1">
                    <strong>Email:</strong> admin@registrovioleta.org<br />
                    <strong>Contraseña:</strong> RegistroVioleta2025!
                  </p>
                  <p className="text-xs text-amber-600 mt-2">
                    Cambiar estas credenciales después del primer login
                  </p>
                </div>
              </div>
            </div>

            {/* Botón de inicio de sesión */}
            <div>
              <button
                type="submit"
                disabled={loading || !backendStatus.healthy}
                className="violeta-button w-full flex justify-center py-3 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Iniciando sesión...
                  </div>
                ) : (
                  'Iniciar sesión'
                )}
              </button>
            </div>

            {/* Link para registro */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                ¿No tienes cuenta?{' '}
                <Link to="/register" className="font-medium text-violeta-600 hover:text-violeta-500">
                  Regístrate aquí
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
