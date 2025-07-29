import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Search, Filter, Calendar, User, Eye, Plus } from 'lucide-react';
import axios from 'axios';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const SessionsList = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCode, setFilterCode] = useState('');
  const [selectedSession, setSelectedSession] = useState(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await axios.get('/api/sessions');
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSessions = sessions.filter(session => {
    const matchesSearch = session.codigo_usuaria.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         session.objetivo_sesion.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         session.terapeuta.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterCode === '' || session.codigo_usuaria === filterCode;
    
    return matchesSearch && matchesFilter;
  });

  const uniqueCodes = [...new Set(sessions.map(session => session.codigo_usuaria))];

  const SessionModal = ({ session, onClose }) => {
    if (!session) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">
                Sesión #{session.sesion_no} - {session.codigo_usuaria}
              </h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
          </div>
          
          <div className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-600">Fecha</p>
                <p className="text-sm text-gray-900">{session.fecha}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Terapeuta</p>
                <p className="text-sm text-gray-900">{session.terapeuta}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Código Usuaria</p>
                <p className="text-sm text-gray-900">{session.codigo_usuaria}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Objetivo de la sesión</h3>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{session.objetivo_sesion}</p>
              </div>

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Desarrollo del objetivo</h3>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{session.desarrollo_objetivo}</p>
              </div>

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Ejercicios y actividades</h3>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{session.ejercicios_actividades}</p>
              </div>

              {session.herramientas_entregadas && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Herramientas entregadas</h3>
                  <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{session.herramientas_entregadas}</p>
                </div>
              )}

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Avances del proceso terapéutico</h3>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{session.avances_proceso_terapeutico}</p>
              </div>

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Cierre de la sesión</h3>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{session.cierre_sesion}</p>
              </div>

              {session.observaciones && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Observaciones</h3>
                  <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{session.observaciones}</p>
                </div>
              )}

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Firma del terapeuta</h3>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{session.firma_terapeuta}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-violeta-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-3 mb-2">
                <div className="bg-violeta-gradient p-2 rounded-lg">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900">Sesiones Terapéuticas</h1>
              </div>
              <p className="text-gray-600">
                Historial completo de sesiones registradas
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

        {/* Filtros */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Search className="inline h-4 w-4 mr-2" />
                Buscar
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="violeta-input"
                placeholder="Buscar por código, objetivo o terapeuta..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Filter className="inline h-4 w-4 mr-2" />
                Filtrar por código
              </label>
              <select
                value={filterCode}
                onChange={(e) => setFilterCode(e.target.value)}
                className="violeta-input"
              >
                <option value="">Todos los códigos</option>
                {uniqueCodes.map(code => (
                  <option key={code} value={code}>{code}</option>
                ))}
              </select>
            </div>

            <div className="flex items-end">
              <div className="text-sm text-gray-600">
                <strong>{filteredSessions.length}</strong> sesiones encontradas
              </div>
            </div>
          </div>
        </div>

        {/* Lista de sesiones */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {filteredSessions.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {filteredSessions.map((session) => (
                <div
                  key={session._id}
                  className="session-card p-6 hover:bg-gray-50 cursor-pointer"
                  onClick={() => setSelectedSession(session)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-violeta-100 text-violeta-800">
                          Sesión #{session.sesion_no}
                        </span>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {session.codigo_usuaria}
                        </span>
                      </div>
                      
                      <h3 className="text-lg font-medium text-gray-900 mb-1">
                        {session.objetivo_sesion.length > 100 
                          ? `${session.objetivo_sesion.substring(0, 100)}...`
                          : session.objetivo_sesion
                        }
                      </h3>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {format(new Date(session.created_at), 'dd MMM yyyy', { locale: es })}
                        </div>
                        <div className="flex items-center">
                          <User className="h-4 w-4 mr-1" />
                          {session.terapeuta}
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      <button className="flex items-center space-x-2 text-violeta-600 hover:text-violeta-800">
                        <Eye className="h-4 w-4" />
                        <span>Ver detalles</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay sesiones</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm || filterCode ? 'No se encontraron sesiones con los filtros aplicados.' : 'Comienza creando tu primera sesión terapéutica.'}
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

        {/* Modal de detalles */}
        <SessionModal 
          session={selectedSession} 
          onClose={() => setSelectedSession(null)} 
        />
      </div>
    </div>
  );
};

export default SessionsList;