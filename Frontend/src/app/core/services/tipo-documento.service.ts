import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';

/**
 * Interfaz para Tipo de Documento
 */
export interface TipoDocumento {
  id_tipo_documento?: string;
  codigo: string;
  nombre: string;
  descripcion?: string;
  activo?: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

/**
 * Servicio para gestión de tipos de documento
 */
@Injectable({
  providedIn: 'root'
})
export class TipoDocumentoService {
  private endpoint = '/tipos-documento';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todos los tipos de documento con paginación
   */
  obtenerTiposDocumento(skip: number = 0, limit: number = 10): Observable<TipoDocumento[]> {
    return this.apiService.get<TipoDocumento[]>(this.endpoint, { skip, limit });
  }

  /**
   * Obtiene todos los tipos de documento activos
   */
  obtenerTiposDocumentoActivos(skip: number = 0, limit: number = 100): Observable<TipoDocumento[]> {
    return this.apiService.get<TipoDocumento[]>(`${this.endpoint}/activos`, { skip, limit });
  }

  /**
   * Obtiene un tipo de documento por ID
   */
  obtenerTipoDocumentoPorId(id: string): Observable<TipoDocumento> {
    return this.apiService.get<TipoDocumento>(`${this.endpoint}/${id}`);
  }

  /**
   * Obtiene un tipo de documento por código
   */
  obtenerPorCodigo(codigo: string): Observable<TipoDocumento> {
    return this.apiService.get<TipoDocumento>(`${this.endpoint}/codigo/${codigo}`);
  }

  /**
   * Busca tipos de documento por nombre
   */
  buscarPorNombre(nombre: string): Observable<TipoDocumento[]> {
    return this.apiService.get<TipoDocumento[]>(`${this.endpoint}/buscar/nombre/${nombre}`);
  }

  /**
   * Crea un nuevo tipo de documento
   */
  crearTipoDocumento(tipoDocumento: TipoDocumento): Observable<TipoDocumento> {
    return this.apiService.post<TipoDocumento>(this.endpoint, tipoDocumento);
  }

  /**
   * Actualiza un tipo de documento existente
   */
  actualizarTipoDocumento(id: string, tipoDocumento: Partial<TipoDocumento>): Observable<TipoDocumento> {
    return this.apiService.put<TipoDocumento>(`${this.endpoint}/${id}`, tipoDocumento);
  }

  /**
   * Elimina (desactiva) un tipo de documento
   */
  eliminarTipoDocumento(id: string): Observable<ApiResponse> {
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`);
  }

  /**
   * Reactiva un tipo de documento
   */
  reactivarTipoDocumento(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }
}
