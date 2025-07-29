import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Users, 
  Calendar, 
  TrendingUp, 
  Plus,
  Heart,
  Shield,
  Clock,
  Download,
  Cloud,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalSessions: 0,
    totalProfiles: 0,
    sessionsThisMonth: 0,
    activeProfiles: 0
  });
  const [recentSessions, setRecentSessions] = useState([]);
  const [systemHealth, setSystemHealth] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    checkSystemHealth();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Obtener estadísticas del dashboard
      const statsRes = await axios.get('/api/dashboard/stats');
      setStats(statsRes.data);

      // Obtener sesiones recientes
      const sessionsRes = await axios.get('/api/sessions');
      setRecentSessions(sessionsRes.data.sessions.slice(0, 5));
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Error cargando datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  const checkSystemHealth = async () => {
    try {
      const healthRes = await axios.get('/api/health');
      setSystemHealth(healthRes.data);
    } catch (error) {
      console.error('Error checking system health:', error);
    }
  };

  const downloadSessionPDF = async (sessionId, sessionNo) => {
    try {
      const response = await axios.get(`/api/sessions/${sessionId}/pdf`, {
        responseType: 'blob'
      });
      
      // Crear enlace de descarga
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Sesion_${sessionNo}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('PDF descargado correctamente');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error('Error descargando PDF');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-violeta-600"></div>
      </div>
    );
  }

  const StatCard = ({ icon: Icon, title, value, subtitle, color = "violeta" }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      <div className="flex items-center">
        <div className={`bg-${color}-100 p-3 rounded-full`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
        </div>
      </div>
    </div>
  );

  const SystemStatusCard = () => (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Estado del sistema</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Shield className="h-4 w-4 mr-2 text-green-500" />
            <span className="text-sm text-gray-600">Base de datos</span>
          </div>
          <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
            Conectada
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Cloud className="h-4 w-4 mr-2" />
            <span className="text-sm text-gray-600">Google Drive</span>
          </div>
          {systemHealth.drive_service ? (
            <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
              <CheckCircle className="h-3 w-3 inline mr-1" />
              Activo
            </span>
          ) : (
            <span className="text-xs font-medium text-yellow-600 bg-yellow-100 px-2 py-1 rounded-full">
              <AlertCircle className="h-3 w-3 inline mr-1" />
              Inactivo
            </span>
          )}
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <FileText className="h-4 w-4 mr-2 text-blue-500" />
            <span className="text-sm text-gray-600">Generador PDF</span>
          </div>
          <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
            <CheckCircle className="h-3 w-3 inline mr-1" />
            Activo
          </span>
        </div>
      </div>
      
      {!systemHealth.drive_service && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-xs text-yellow-700">
            ⚠️ Google Drive no configurado. Los PDFs se generarán localmente.
          </p>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                ¡Bienvenida, {user?.nombre}! 
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Dashboard de seguimiento - {user?.fundacion}
              </p>
            </div>
            <div className="mt-4 flex md:mt-0 md:ml-4">
              <Link
                to="/nueva-sesion"
                className="violeta-button inline-flex items-center space-x-2"
              >
                <Plus className="h-4 w-4" />
                <span>Nueva sesión</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Stats grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <StatCard
            icon={FileText}
            title="Total de sesiones"
            value={stats.totalSessions || 0}
            subtitle="Registro histórico"
          />
          <StatCard
            icon={Users}
            title="Perfiles registrados"
            value={stats.totalProfiles || 0}
            subtitle="Usuarias en seguimiento"
          />
          <StatCard
            icon={Calendar}
            title="Sesiones este mes"
            value={stats.sessionsThisMonth || 0}
            subtitle="Actividad reciente"
            color="green"
          />
          <StatCard
            icon={TrendingUp}
            title="Casos activos"
            value={stats.activeProfiles || 0}
            subtitle="En proceso terapéutico"
            color="blue"
          />
        </div>

        {/* Content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Sesiones recientes */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Sesiones recientes</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {recentSessions.length > 0 ? (
                  recentSessions.map((session) => (
                    <div key={session._id} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <p className="text-sm font-medium text-gray-900">
                              Código: {session.codigo_usuaria}
                            </p>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-violeta-100 text-violeta-800">
                              Sesión #{session.sesion_no}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mt-1">
                            {session.objetivo_sesion.substring(0, 80)}...
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {format(new Date(session.created_at || session.fecha), 'dd MMM yyyy', { locale: es })} - {session.terapeuta}
                          </p>
                        </div>
                        <div className="ml-4 flex items-center space-x-2">
                          <button
                            onClick={() => downloadSessionPDF(session._id, session.sesion_no)}
                            className="inline-flex items-center px-2 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 bg-white hover:bg-gray-50"
                            title="Descargar PDF"
                          >
                            <Download className="h-3 w-3" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="px-6 py-12 text-center">
                    <FileText className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No hay sesiones</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Comienza creando tu primera sesión terapéutica.
                    </p>
                    <div className="mt-6">
                      <Link
                        to="/nueva-sesion"
                        className="violeta-button inline-flex items-center space-x-2"
                      >
                        <Plus className="h-4 w-4" />
                        <span>Nueva sesión</span>
                      </Link>
                    </div>
                  </div>
                )}
              </div>
              {recentSessions.length > 0 && (
                <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
                  <Link
                    to="/sesiones"
                    className="text-sm font-medium text-violeta-600 hover:text-violeta-500"
                  >
                    Ver todas las sesiones →
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            
            {/* Acciones rápidas */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Acciones rápidas</h3>
              <div className="space-y-3">
                <Link
                  to="/nueva-sesion"
                  className="flex items-center p-3 text-sm font-medium rounded-lg bg-violeta-50 text-violeta-700 hover:bg-violeta-100 transition-colors"
                >
                  <Plus className="h-5 w-5 mr-3" />
                  Registrar nueva sesión
                </Link>
                <Link
                  to="/perfiles"
                  className="flex items-center p-3 text-sm font-medium rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
                >
                  <Users className="h-5 w-5 mr-3" />
                  Gestionar perfiles
                </Link>
                <Link
                  to="/sesiones"
                  className="flex items-center p-3 text-sm font-medium rounded-lg bg-green-50 text-green-700 hover:bg-green-100 transition-colors"
                >
                  <FileText className="h-5 w-5 mr-3" />
                  Ver historial completo
                </Link>
              </div>
            </div>

            {/* Estado del sistema */}
            <SystemStatusCard />

            {/* Información del sistema */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Acerca del sistema</h3>
              <div className="space-y-4">
                <div className="flex items-center text-sm text-gray-600">
                  <Heart className="h-4 w-4 mr-2 text-violeta-500" />
                  Registro Violeta v2.0
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Shield className="h-4 w-4 mr-2 text-green-500" />
                  Datos protegidos y confidenciales
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="h-4 w-4 mr-2 text-blue-500" />
                  Sistema operativo 24/7
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
