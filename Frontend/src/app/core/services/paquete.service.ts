import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';

/**
 * Interfaz para Paquete - Alineada con el backend
 */
export interface Paquete {
  id_paquete?: string;
  peso: number;
  tamaño: string; // Cambiado de tamanio a tamaño para coincidir con backend
  fragilidad: string;
  contenido: string;
  tipo: string;
  valor_declarado?: number;
  estado?: string;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  creado_por?: string;
  actualizado_por?: string;
}

/**
 * Servicio para gestión de paquetes
 */
@Injectable({
  providedIn: 'root'
})
export class PaqueteService {
  private endpoint = '/paquetes/';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todos los paquetes con paginación
   */
  obtenerPaquetes(skip: number = 0, limit: number = 10): Observable<Paquete[]> {
    return this.apiService.get<any>(this.endpoint, { skip, limit }).pipe(
      map(response => response?.paquetes || response || [])
    );
  }

  /**
   * Obtiene todos los paquetes activos
   */
  obtenerPaquetesActivos(skip: number = 0, limit: number = 10): Observable<Paquete[]> {
    return this.apiService.get<any>(`${this.endpoint}/activos`, { skip, limit }).pipe(
      map(response => response?.paquetes || response || [])
    );
  }

  /**
   * Obtiene un paquete por ID
   */
  obtenerPaquetePorId(id: string): Observable<Paquete> {
    return this.apiService.get<Paquete>(`${this.endpoint}/${id}`);
  }

  /**
   * Obtiene paquetes por estado
   */
  obtenerPaquetesPorEstado(estado: string, skip: number = 0, limit: number = 10): Observable<Paquete[]> {
    return this.apiService.get<any>(`${this.endpoint}/estado/${estado}`, { skip, limit }).pipe(
      map(response => response?.paquetes || response || [])
    );
  }

  /**
   * Obtiene paquetes por tipo
   */
  obtenerPaquetesPorTipo(tipo: string, skip: number = 0, limit: number = 10): Observable<Paquete[]> {
    return this.apiService.get<any>(`${this.endpoint}/tipo/${tipo}`, { skip, limit }).pipe(
      map(response => response?.paquetes || response || [])
    );
  }

  /**
   * Obtiene paquetes por fragilidad
   */
  obtenerPaquetesPorFragilidad(fragilidad: string, skip: number = 0, limit: number = 10): Observable<Paquete[]> {
    return this.apiService.get<any>(`${this.endpoint}/fragilidad/${fragilidad}`, { skip, limit }).pipe(
      map(response => response?.paquetes || response || [])
    );
  }

  /**
   * Crea un nuevo paquete
   */
  crearPaquete(paquete: Paquete): Observable<Paquete> {
    return this.apiService.post<Paquete>(this.endpoint, paquete);
  }

  /**
   * Actualiza un paquete existente
   */
  actualizarPaquete(id: string, paquete: Partial<Paquete>): Observable<Paquete> {
    return this.apiService.put<Paquete>(`${this.endpoint}/${id}`, paquete);
  }

  /**
   * Actualiza el estado de un paquete
   */
  actualizarEstado(id: string, estado: string): Observable<Paquete> {
    return this.apiService.patch<Paquete>(`${this.endpoint}/${id}/estado`, { estado });
  }

  /**
   * Elimina (desactiva) un paquete
   */
  eliminarPaquete(id: string): Observable<ApiResponse> {
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`);
  }

  /**
   * Reactiva un paquete
   */
  reactivarPaquete(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }
}
