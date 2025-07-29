import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Determinar URL del backend
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 
                      process.env.REACT_APP_API_URL || 
                      'http://localhost:8001';

  console.log('🔗 Backend URL:', API_BASE_URL);

  // Configurar axios interceptor para incluir token
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }

    // Interceptor para manejar errores de autenticación
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('🚨 API Error:', error.response?.status, error.response?.data);
        
        if (error.response?.status === 401) {
          logout();
          toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.');
        } else if (error.code === 'NETWORK_ERROR' || !error.response) {
          toast.error('Error de conexión. Verifica tu internet y que el servidor esté funcionando.');
        }
        return Promise.reject(error);
      }
    );

    return () => axios.interceptors.response.eject(interceptor);
  }, []);

  // Verificar si hay usuario autenticado al cargar
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          console.log('🔍 Verificando token existente...');
          const response = await axios.get(`${API_BASE_URL}/api/auth/me`, {
            timeout: 10000 // 10 segundos timeout
          });
          setUser(response.data);
          console.log('✅ Usuario autenticado:', response.data.email);
        } catch (error) {
          console.error('❌ Token inválido:', error.message);
          localStorage.removeItem('token');
          delete axios.defaults.headers.common['Authorization'];
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [API_BASE_URL]);

  const login = async (email, password) => {
    try {
      console.log('🔑 Intentando login para:', email);
      console.log('🌐 URL de login:', `${API_BASE_URL}/api/auth/login`);
      
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        email,
        password
      }, {
        timeout: 15000, // 15 segundos timeout
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setUser(userData);
      toast.success(`¡Bienvenida, ${userData.nombre}!`);
      
      console.log('✅ Login exitoso para:', userData.email);
      return { success: true };
    } catch (error) {
      console.error('❌ Error en login:', error);
      
      let message = 'Error al iniciar sesión';
      
      if (error.code === 'NETWORK_ERROR' || !error.response) {
        message = 'Error de conexión. Verifica que el servidor esté funcionando.';
      } else if (error.response?.status === 401) {
        message = 'Email o contraseña incorrectos';
      } else if (error.response?.status === 500) {
        message = 'Error del servidor. Intenta más tarde.';
      } else if (error.response?.data?.detail) {
        message = error.response.data.detail;
      }
      
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const register = async (userData) => {
    try {
      console.log('📝 Registrando usuario:', userData.email);
      
      await axios.post(`${API_BASE_URL}/api/auth/register`, userData, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      toast.success('Cuenta creada exitosamente. Ahora puedes iniciar sesión.');
      return { success: true };
    } catch (error) {
      console.error('❌ Error en registro:', error);
      
      let message = 'Error al crear la cuenta';
      
      if (error.code === 'NETWORK_ERROR' || !error.response) {
        message = 'Error de conexión. Verifica que el servidor esté funcionando.';
      } else if (error.response?.status === 400) {
        message = 'Email ya registrado o datos inválidos';
      } else if (error.response?.data?.detail) {
        message = error.response.data.detail;
      }
      
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    toast.success('Sesión cerrada exitosamente');
    console.log('👋 Usuario desconectado');
  };

  // Función para verificar conexión al backend
  const checkBackendHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`, {
        timeout: 5000
      });
      return { healthy: true, data: response.data };
    } catch (error) {
      return { healthy: false, error: error.message };
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    checkBackendHealth,
    API_BASE_URL
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
