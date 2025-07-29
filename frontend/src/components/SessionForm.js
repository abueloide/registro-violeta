import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { FileText, Save, Calendar, User, Target, ClipboardList } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

const SessionForm = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: {
      fecha: new Date().toISOString().split('T')[0],
      terapeuta: `${user?.nombre} ${user?.apellido}`,
      fundacion: user?.fundacion
    }
  });

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await axios.post('/api/sessions', data);
      toast.success('Sesión registrada exitosamente');
      reset();
      navigate('/sesiones');
    } catch (error) {
      console.error('Error creating session:', error);
      toast.error('Error al registrar la sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <div className="bg-violeta-gradient p-2 rounded-lg">
              <FileText className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Nueva Sesión Terapéutica</h1>
          </div>
          <p className="text-gray-600">
            Registro de seguimiento del proceso terapéutico
          </p>
        </div>

        {/* Formulario */}
        <div className="violeta-form p-8 max-w-4xl mx-auto">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            
            {/* Información básica */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Calendar className="inline h-4 w-4 mr-2" />
                  Sesión No.
                </label>
                <input
                  {...register('sesion_no', {
                    required: 'El número de sesión es requerido'
                  })}
                  type="text"
                  className="violeta-input"
                  placeholder="Ej: 001, 002, etc."
                />
                {errors.sesion_no && (
                  <p className="mt-1 text-sm text-red-600">{errors.sesion_no.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Calendar className="inline h-4 w-4 mr-2" />
                  Fecha
                </label>
                <input
                  {...register('fecha', {
                    required: 'La fecha es requerida'
                  })}
                  type="date"
                  className="violeta-input"
                />
                {errors.fecha && (
                  <p className="mt-1 text-sm text-red-600">{errors.fecha.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <User className="inline h-4 w-4 mr-2" />
                  Código Usuaria
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
            </div>

            {/* Terapeuta */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User className="inline h-4 w-4 mr-2" />
                Terapeuta
              </label>
              <input
                {...register('terapeuta', {
                  required: 'El nombre del terapeuta es requerido'
                })}
                type="text"
                className="violeta-input"
                readOnly
              />
            </div>

            {/* Objetivo de la sesión */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Target className="inline h-4 w-4 mr-2" />
                Objetivo de la sesión
              </label>
              <textarea
                {...register('objetivo_sesion', {
                  required: 'El objetivo de la sesión es requerido',
                  minLength: {
                    value: 10,
                    message: 'Mínimo 10 caracteres'
                  }
                })}
                rows={3}
                className="violeta-input resize-none"
                placeholder="Describe el objetivo principal de esta sesión terapéutica..."
              />
              {errors.objetivo_sesion && (
                <p className="mt-1 text-sm text-red-600">{errors.objetivo_sesion.message}</p>
              )}
            </div>

            {/* Desarrollo del objetivo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <ClipboardList className="inline h-4 w-4 mr-2" />
                Desarrollo del objetivo
              </label>
              <textarea
                {...register('desarrollo_objetivo', {
                  required: 'El desarrollo del objetivo es requerido',
                  minLength: {
                    value: 20,
                    message: 'Mínimo 20 caracteres'
                  }
                })}
                rows={4}
                className="violeta-input resize-none"
                placeholder="Describe cómo se desarrolló el objetivo durante la sesión..."
              />
              {errors.desarrollo_objetivo && (
                <p className="mt-1 text-sm text-red-600">{errors.desarrollo_objetivo.message}</p>
              )}
            </div>

            {/* Ejercicios y actividades */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <ClipboardList className="inline h-4 w-4 mr-2" />
                Ejercicios y actividades
              </label>
              <textarea
                {...register('ejercicios_actividades', {
                  required: 'Los ejercicios y actividades son requeridos'
                })}
                rows={3}
                className="violeta-input resize-none"
                placeholder="Describe los ejercicios y actividades realizados..."
              />
              {errors.ejercicios_actividades && (
                <p className="mt-1 text-sm text-red-600">{errors.ejercicios_actividades.message}</p>
              )}
            </div>

            {/* Herramientas entregadas */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <ClipboardList className="inline h-4 w-4 mr-2" />
                Herramientas entregadas
              </label>
              <textarea
                {...register('herramientas_entregadas')}
                rows={3}
                className="violeta-input resize-none"
                placeholder="Describe las herramientas o recursos entregados a la usuaria..."
              />
            </div>

            {/* Avances del proceso terapéutico */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Target className="inline h-4 w-4 mr-2" />
                Avances del proceso terapéutico
              </label>
              <textarea
                {...register('avances_proceso_terapeutico', {
                  required: 'Los avances del proceso son requeridos'
                })}
                rows={4}
                className="violeta-input resize-none"
                placeholder="Describe los avances observados en el proceso terapéutico..."
              />
              {errors.avances_proceso_terapeutico && (
                <p className="mt-1 text-sm text-red-600">{errors.avances_proceso_terapeutico.message}</p>
              )}
            </div>

            {/* Cierre de la sesión */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <ClipboardList className="inline h-4 w-4 mr-2" />
                Cierre de la sesión
              </label>
              <textarea
                {...register('cierre_sesion', {
                  required: 'El cierre de la sesión es requerido'
                })}
                rows={3}
                className="violeta-input resize-none"
                placeholder="Describe cómo se cerró la sesión y las tareas asignadas..."
              />
              {errors.cierre_sesion && (
                <p className="mt-1 text-sm text-red-600">{errors.cierre_sesion.message}</p>
              )}
            </div>

            {/* Observaciones */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <FileText className="inline h-4 w-4 mr-2" />
                Observaciones
              </label>
              <textarea
                {...register('observaciones')}
                rows={3}
                className="violeta-input resize-none"
                placeholder="Observaciones adicionales sobre la sesión..."
              />
            </div>

            {/* Firma del terapeuta */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User className="inline h-4 w-4 mr-2" />
                Firma del terapeuta
              </label>
              <input
                {...register('firma_terapeuta', {
                  required: 'La firma del terapeuta es requerida'
                })}
                type="text"
                className="violeta-input"
                placeholder="Nombre completo del terapeuta"
              />
              {errors.firma_terapeuta && (
                <p className="mt-1 text-sm text-red-600">{errors.firma_terapeuta.message}</p>
              )}
            </div>

            {/* Botones */}
            <div className="flex space-x-4 pt-6">
              <button
                type="submit"
                disabled={loading}
                className="violeta-button flex items-center space-x-2 px-6 py-3"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Guardando...</span>
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    <span>Guardar sesión</span>
                  </>
                )}
              </button>
              
              <button
                type="button"
                onClick={() => navigate('/sesiones')}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SessionForm;