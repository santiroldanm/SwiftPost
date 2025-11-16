import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';

/**
 * Interfaz para Sede - Alineada con el backend
 */
export interface Sede {
  id_sede?: string;
  nombre: string;
  ciudad: string;
  direccion: string;
  telefono: string;
  latitud?: number;
  longitud?: number;
  altitud?: number;
  activo?: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  creado_por?: string;
  actualizado_por?: string;
}

/**
 * Servicio para gestión de sedes
 */
@Injectable({
  providedIn: 'root'
})
export class SedeService {
  private endpoint = '/sedes';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todas las sedes con paginación y filtros opcionales
   */
  obtenerSedes(skip: number = 0, limit: number = 10, filtros?: { activo?: boolean, ciudad?: string }): Observable<Sede[]> {
    // Si hay filtro de activo, usar el endpoint específico
    if (filtros?.activo === true) {
      return this.obtenerSedesActivas(skip, limit);
    }
    
    // Si hay filtro de ciudad, usar el endpoint específico
    if (filtros?.ciudad) {
      return this.obtenerSedesPorCiudad(filtros.ciudad, skip, limit);
    }
    
    // Sin filtros, obtener todas
    return this.apiService.get<any>(`${this.endpoint}/`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.sedes || response || []))
    );
  }

  /**
   * Obtiene todas las sedes activas
   */
  obtenerSedesActivas(skip: number = 0, limit: number = 10): Observable<Sede[]> {
    return this.apiService.get<Sede[]>(`${this.endpoint}/activos`, { skip, limit });
  }

  /**
   * Obtiene una sede por ID
   */
  obtenerSedePorId(id: string): Observable<Sede> {
    return this.apiService.get<Sede>(`${this.endpoint}/${id}`);
  }

  /**
   * Obtiene sedes por ciudad
   */
  obtenerSedesPorCiudad(ciudad: string, skip: number = 0, limit: number = 10): Observable<Sede[]> {
    return this.apiService.get<any>(`${this.endpoint}/ciudad/${ciudad}`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.sedes || response || []))
    );
  }

  /**
   * Crea una nueva sede
   */
  crearSede(sede: Sede, creadoPor?: string): Observable<Sede> {
    const params = creadoPor ? { creado_por: creadoPor } : {};
    return this.apiService.post<Sede>(`${this.endpoint}/`, sede, params);
  }

  /**
   * Actualiza una sede existente
   */
  actualizarSede(id: string, sede: Partial<Sede>, actualizadoPor?: string): Observable<Sede> {
    const params = actualizadoPor ? { actualizado_por: actualizadoPor } : {};
    // Remover actualizado_por del body si está presente
    const { actualizado_por, ...body } = sede as any;
    return this.apiService.put<Sede>(`${this.endpoint}/${id}`, body, params);
  }

  /**
   * Elimina (desactiva) una sede
   */
  eliminarSede(id: string, actualizadoPor?: string): Observable<ApiResponse> {
    const params = actualizadoPor ? { actualizado_por: actualizadoPor } : {};
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`, params);
  }

  /**
   * Reactiva una sede
   */
  reactivarSede(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }
}
