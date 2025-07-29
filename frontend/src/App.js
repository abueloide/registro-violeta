import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import './App.css';

// Componentes
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import SessionForm from './components/SessionForm';  
import ProfilesManager from './components/ProfilesManager';
import SessionsList from './components/SessionsList';
import Navigation from './components/Navigation';

// Contexto de autenticación  
import { AuthProvider, useAuth } from './context/AuthContext';

// Componente para rutas protegidas
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-violeta-600"></div>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/login" />;
};

// Componente principal de la aplicación
function AppContent() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      
      {user && <Navigation />}
      
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="/nueva-sesion" element={
          <ProtectedRoute>
            <SessionForm />
          </ProtectedRoute>
        } />
        <Route path="/sesiones" element={
          <ProtectedRoute>
            <SessionsList />
          </ProtectedRoute>
        } />
        <Route path="/perfiles" element={
          <ProtectedRoute>
            <ProfilesManager />
          </ProtectedRoute>
        } />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;