import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';

/**
 * Interfaz para Usuario
 */
export interface Usuario {
  id_usuario?: string;
  nombre_usuario: string;
  contraseña?: string;
  id_rol: string;
  activo?: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  rol?: {
    id_rol: string;
    nombre_rol: string;
    descripcion?: string;
  };
}

/**
 * Interfaz para cambio de contraseña
 */
export interface CambioContrasena {
  contraseña_actual: string;
  contraseña_nueva: string;
  confirmar_contraseña: string;
}

/**
 * Servicio para gestión de usuarios
 */
@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private endpoint = '/usuarios';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todos los usuarios con paginación
   */
  obtenerUsuarios(skip: number = 0, limit: number = 10): Observable<Usuario[]> {
    return this.apiService.get<Usuario[]>(this.endpoint, { skip, limit });
  }

  /**
   * Obtiene todos los usuarios activos
   */
  obtenerUsuariosActivos(skip: number = 0, limit: number = 10): Observable<Usuario[]> {
    return this.apiService.get<Usuario[]>(`${this.endpoint}/activos`, { skip, limit });
  }

  /**
   * Obtiene un usuario por ID
   */
  obtenerUsuarioPorId(id: string): Observable<Usuario> {
    return this.apiService.get<Usuario>(`${this.endpoint}/${id}`);
  }

  /**
   * Obtiene usuarios por rol
   */
  obtenerUsuariosPorRol(idRol: string, skip: number = 0, limit: number = 10): Observable<Usuario[]> {
    return this.apiService.get<Usuario[]>(`${this.endpoint}/rol/${idRol}`, { skip, limit });
  }

  /**
   * Busca usuarios por nombre de usuario
   */
  buscarPorNombre(nombreUsuario: string): Observable<Usuario[]> {
    return this.apiService.get<Usuario[]>(`${this.endpoint}/buscar/nombre/${nombreUsuario}`);
  }

  /**
   * Verifica si un nombre de usuario está disponible
   */
  verificarDisponibilidad(nombreUsuario: string): Observable<ApiResponse> {
    return this.apiService.get<ApiResponse>(`${this.endpoint}/verificar-disponibilidad/${nombreUsuario}`);
  }

  /**
   * Crea un nuevo usuario
   */
  crearUsuario(usuario: Usuario): Observable<Usuario> {
    return this.apiService.post<Usuario>(this.endpoint, usuario);
  }

  /**
   * Actualiza un usuario existente
   */
  actualizarUsuario(id: string, usuario: Partial<Usuario>): Observable<Usuario> {
    return this.apiService.put<Usuario>(`${this.endpoint}/${id}`, usuario);
  }

  /**
   * Cambia la contraseña de un usuario
   */
  cambiarContrasena(id: string, cambioContrasena: CambioContrasena): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/cambiar-contrasena`, cambioContrasena);
  }

  /**
   * Restablece la contraseña de un usuario (admin)
   */
  restablecerContrasena(id: string, nuevaContrasena: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/restablecer-contrasena`, {
      contraseña_nueva: nuevaContrasena
    });
  }

  /**
   * Elimina (desactiva) un usuario
   */
  eliminarUsuario(id: string): Observable<ApiResponse> {
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`);
  }

  /**
   * Reactiva un usuario
   */
  reactivarUsuario(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }

  /**
   * Cambia el rol de un usuario
   */
  cambiarRol(id: string, idRol: string): Observable<Usuario> {
    return this.apiService.patch<Usuario>(`${this.endpoint}/${id}/cambiar-rol`, { id_rol: idRol });
  }
}
