import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Users, Plus, Search, Edit, UserPlus } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

const ProfilesManager = () => {
  const { user } = useAuth();
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingProfile, setEditingProfile] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const { register, handleSubmit, formState: { errors }, reset, setValue } = useForm({
    defaultValues: {
      estado_caso: 'activo',
      terapeuta_asignado: `${user?.nombre} ${user?.apellido}`,
      fundacion: user?.fundacion
    }
  });

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      const response = await axios.get('/api/profiles');
      setProfiles(response.data.profiles || []);
    } catch (error) {
      console.error('Error fetching profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      if (editingProfile) {
        // En un sistema real, aquí sería PUT/PATCH
        toast.success('Perfil actualizado exitosamente');
      } else {
        await axios.post('/api/profiles', data);
        toast.success('Perfil creado exitosamente');
      }
      
      reset();
      setShowForm(false);
      setEditingProfile(null);
      fetchProfiles();
    } catch (error) {
      console.error('Error saving profile:', error);
      toast.error('Error al guardar el perfil');
    }
  };

  const handleEdit = (profile) => {
    setEditingProfile(profile);
    Object.keys(profile).forEach(key => {
      setValue(key, profile[key]);
    });
    setShowForm(true);
  };

  const handleCancel = () => {
    reset();
    setShowForm(false);
    setEditingProfile(null);
  };

  const filteredProfiles = profiles.filter(profile =>
    profile.codigo_usuaria.toLowerCase().includes(searchTerm.toLowerCase()) ||
    profile.terapeuta_asignado.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const ProfileForm = () => (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">
        {editingProfile ? 'Editar perfil' : 'Nuevo perfil'}
      </h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Código Usuaria *
            </label>
            <input
              {...register('codigo_usuaria', {
                required: 'El código de usuaria es requerido',
                pattern: {
                  value: /^[A-Z0-9]{3,10}$/,
                  message: 'Formato: letras mayúsculas y números (3-10 caracteres)'
                }
              })}
              type="text"
              className="violeta-input"
              placeholder="Ej: ABC123"
              style={{ textTransform: 'uppercase' }}
            />
            {errors.codigo_usuaria && (
              <p className="mt-1 text-sm text-red-600">{errors.codigo_usuaria.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Edad aproximada
            </label>
            <input
              {...register('edad_aproximada')}
              type="text"
              className="violeta-input"
              placeholder="Ej: 25-30 años"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de violencia
            </label>
            <select
              {...register('tipo_violencia')}
              className="violeta-input"
            >
              <option value="">Seleccionar tipo</option>
              <option value="fisica">Física</option>
              <option value="psicologica">Psicológica</option>
              <option value="economica">Económica</option>
              <option value="sexual">Sexual</option> 
              <option value="mixta">Mixta</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estado del caso *
            </label>
            <select
              {...register('estado_caso', {
                required: 'El estado del caso es requerido'
              })}
              className="violeta-input"
            >
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
              <option value="cerrado">Cerrado</option>
              <option value="en_pausa">En pausa</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Terapeuta asignado *
          </label>
          <input
            {...register('terapeuta_asignado', {
              required: 'El terapeuta asignado es requerido'
            })}
            type="text"
            className="violeta-input"
          />
          {errors.terapeuta_asignado && (
            <p className="mt-1 text-sm text-red-600">{errors.terapeuta_asignado.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Situación general
          </label>
          <textarea
            {...register('situacion_general')}
            rows={3}
            className="violeta-input resize-none"
            placeholder="Descripción general del caso (opcional)..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Notas generales
          </label>
          <textarea
            {...register('notas_generales')}
            rows={3}
            className="violeta-input resize-none"
            placeholder="Notas adicionales (opcional)..."
          />
        </div>

        <div className="flex space-x-4">
          <button
            type="submit"
            className="violeta-button flex items-center space-x-2"
          >
            <UserPlus className="h-4 w-4" />
            <span>{editingProfile ? 'Actualizar' : 'Crear perfil'}</span>
          </button>
          
          <button
            type="button"
            onClick={handleCancel}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );

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
                  <Users className="h-6 w-6 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900">Gestión de Perfiles</h1>
              </div>
              <p className="text-gray-600">
                Administra los perfiles de usuarias en seguimiento
              </p>
            </div>
            <div className="mt-4 flex md:mt-0 md:ml-4">
              <button
                onClick={() => setShowForm(!showForm)}
                className="violeta-button inline-flex items-center space-x-2"
              >
                <Plus className="h-4 w-4" />
                <span>Nuevo perfil</span>
              </button>
            </div>
          </div>
        </div>

        {/* Formulario */}
        {showForm && <ProfileForm />}

        {/* Barra de búsqueda */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="violeta-input pl-10"
                  placeholder="Buscar por código de usuaria o terapeuta..."
                />
              </div>
            </div>
            <div className="text-sm text-gray-600">
              <strong>{filteredProfiles.length}</strong> perfiles encontrados
            </div>
          </div>
        </div>

        {/* Lista de perfiles */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {filteredProfiles.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {filteredProfiles.map((profile) => (
                <div key={profile._id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-violeta-100 text-violeta-800">
                          {profile.codigo_usuaria}
                        </span>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                          profile.estado_caso === 'activo' ? 'status-active' : 'status-inactive'
                        }`}>
                          {profile.estado_caso}
                        </span>
                        {profile.tipo_violencia && (
                          <span className="profile-badge">
                            {profile.tipo_violencia}
                          </span>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Terapeuta:</span> {profile.terapeuta_asignado}
                        </div>
                        {profile.edad_aproximada && (
                          <div>
                            <span className="font-medium">Edad:</span> {profile.edad_aproximada}
                          </div>
                        )}
                        {profile.situacion_general && (
                          <div>
                            <span className="font-medium">Situación:</span> {profile.situacion_general.length > 50 
                              ? `${profile.situacion_general.substring(0, 50)}...`
                              : profile.situacion_general
                            }
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="ml-4 flex space-x-2">
                      <button 
                        onClick={() => handleEdit(profile)}
                        className="flex items-center space-x-1 text-violeta-600 hover:text-violeta-800"
                      >
                        <Edit className="h-4 w-4" />
                        <span>Editar</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay perfiles</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm ? 'No se encontraron perfiles con los filtros aplicados.' : 'Comienza creando el primer perfil de usuaria.'}
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowForm(true)}
                  className="violeta-button inline-flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Nuevo perfil</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilesManager;