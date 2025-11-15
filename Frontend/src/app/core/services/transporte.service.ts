import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';

/**
 * Interfaz para Transporte - Alineada con el backend
 */
export interface Transporte {
  id_transporte?: string;
  tipo_vehiculo: string;
  capacidad_carga: number;
  id_sede: string;
  placa: string;
  modelo: string;
  marca: string;
  año: number;
  estado?: string;
  activo?: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  creado_por?: string;
  actualizado_por?: string;
}

/**
 * Servicio para gestión de transportes
 */
@Injectable({
  providedIn: 'root'
})
export class TransporteService {
  private endpoint = '/transportes/';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todos los transportes con paginación
   */
  obtenerTransportes(skip: number = 0, limit: number = 10): Observable<Transporte[]> {
    return this.apiService.get<any>(this.endpoint, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.transportes || response || []))
    );
  }

  /**
   * Obtiene todos los transportes activos
   */
  obtenerTransportesActivos(skip: number = 0, limit: number = 10): Observable<Transporte[]> {
    return this.apiService.get<any>(`${this.endpoint}/activos`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.transportes || response || []))
    );
  }

  /**
   * Obtiene un transporte por ID
   */
  obtenerTransportePorId(id: string): Observable<Transporte> {
    return this.apiService.get<Transporte>(`${this.endpoint}/${id}`);
  }

  /**
   * Obtiene transportes por sede
   */
  obtenerTransportesPorSede(idSede: string, skip: number = 0, limit: number = 10): Observable<Transporte[]> {
    return this.apiService.get<any>(`${this.endpoint}/sede/${idSede}`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.transportes || response || []))
    );
  }

  /**
   * Obtiene transportes por tipo
   */
  obtenerTransportesPorTipo(tipo: string, skip: number = 0, limit: number = 10): Observable<Transporte[]> {
    return this.apiService.get<any>(`${this.endpoint}/tipo/${tipo}`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.transportes || response || []))
    );
  }

  /**
   * Obtiene transportes por estado
   */
  obtenerTransportesPorEstado(estado: string, skip: number = 0, limit: number = 10): Observable<Transporte[]> {
    return this.apiService.get<any>(`${this.endpoint}/estado/${estado}`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.transportes || response || []))
    );
  }

  /**
   * Busca transportes por placa
   */
  buscarPorPlaca(placa: string): Observable<Transporte[]> {
    return this.apiService.get<any>(`${this.endpoint}/buscar/placa/${placa}`).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.transportes || response || []))
    );
  }

  /**
   * Crea un nuevo transporte
   */
  crearTransporte(transporte: Transporte): Observable<Transporte> {
    return this.apiService.post<Transporte>(this.endpoint, transporte);
  }

  /**
   * Actualiza un transporte existente
   */
  actualizarTransporte(id: string, transporte: Partial<Transporte>): Observable<Transporte> {
    return this.apiService.put<Transporte>(`${this.endpoint}/${id}`, transporte);
  }

  /**
   * Actualiza el estado de un transporte
   */
  actualizarEstado(id: string, estado: string): Observable<Transporte> {
    return this.apiService.patch<Transporte>(`${this.endpoint}/${id}/estado`, { estado });
  }

  /**
   * Elimina (desactiva) un transporte
   */
  eliminarTransporte(id: string): Observable<ApiResponse> {
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`);
  }

  /**
   * Reactiva un transporte
   */
  reactivarTransporte(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }
}
