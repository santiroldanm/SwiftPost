import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';

/**
 * Interfaz para Rol
 */
export interface Rol {
  id_rol?: string;
  nombre_rol: string;
  descripcion?: string;
  activo?: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

/**
 * Servicio para gestión de roles
 */
@Injectable({
  providedIn: 'root'
})
export class RolService {
  private endpoint = '/roles';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todos los roles con paginación
   */
  obtenerRoles(skip: number = 0, limit: number = 10): Observable<Rol[]> {
    return this.apiService.get<Rol[]>(this.endpoint, { skip, limit });
  }

  /**
   * Obtiene todos los roles activos
   */
  obtenerRolesActivos(skip: number = 0, limit: number = 10): Observable<Rol[]> {
    return this.apiService.get<Rol[]>(`${this.endpoint}/activos`, { skip, limit });
  }

  /**
   * Obtiene un rol por ID
   */
  obtenerRolPorId(id: string): Observable<Rol> {
    return this.apiService.get<Rol>(`${this.endpoint}/${id}`);
  }

  /**
   * Busca roles por nombre
   */
  buscarPorNombre(nombre: string): Observable<Rol[]> {
    return this.apiService.get<Rol[]>(`${this.endpoint}/buscar/nombre/${nombre}`);
  }

  /**
   * Crea un nuevo rol
   */
  crearRol(rol: Rol): Observable<Rol> {
    return this.apiService.post<Rol>(this.endpoint, rol);
  }

  /**
   * Actualiza un rol existente
   */
  actualizarRol(id: string, rol: Partial<Rol>): Observable<Rol> {
    return this.apiService.put<Rol>(`${this.endpoint}/${id}`, rol);
  }

  /**
   * Elimina (desactiva) un rol
   */
  eliminarRol(id: string): Observable<ApiResponse> {
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`);
  }

  /**
   * Reactiva un rol
   */
  reactivarRol(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }
}
