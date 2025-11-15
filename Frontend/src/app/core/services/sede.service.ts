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
  private endpoint = '/sedes/';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todas las sedes con paginación
   */
  obtenerSedes(skip: number = 0, limit: number = 10): Observable<Sede[]> {
    return this.apiService.get<any>(this.endpoint, { skip, limit }).pipe(
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
  crearSede(sede: Sede): Observable<Sede> {
    return this.apiService.post<Sede>(this.endpoint, sede);
  }

  /**
   * Actualiza una sede existente
   */
  actualizarSede(id: string, sede: Partial<Sede>): Observable<Sede> {
    return this.apiService.put<Sede>(`${this.endpoint}/${id}`, sede);
  }

  /**
   * Elimina (desactiva) una sede
   */
  eliminarSede(id: string): Observable<ApiResponse> {
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`);
  }

  /**
   * Reactiva una sede
   */
  reactivarSede(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }
}
