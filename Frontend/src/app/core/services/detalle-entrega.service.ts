import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';

/**
 * Interfaz para Detalle de Entrega - Alineada con el backend
 */
export interface DetalleEntrega {
  id_detalle?: string;
  id_sede_remitente: string;
  id_sede_receptora: string;
  id_paquete: string;
  id_cliente_remitente: string;
  id_cliente_receptor: string;
  estado_envio: string;
  fecha_envio: string;
  fecha_entrega?: string;
  observaciones?: string;
  activo?: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  creado_por?: string;
  actualizado_por?: string;
}

/**
 * Servicio para gestión de detalles de entrega
 */
@Injectable({
  providedIn: 'root'
})
export class DetalleEntregaService {
  private endpoint = '/detalles-entrega';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todos los detalles de entrega con paginación y filtros opcionales
   */
  obtenerDetallesEntrega(skip: number = 0, limit: number = 10, filtros?: { estado?: string }): Observable<any> {
    // Si hay filtro de estado, usar el endpoint específico
    if (filtros?.estado && filtros.estado !== 'todos') {
      return this.obtenerPorEstado(filtros.estado, skip, limit);
    }
    
    // Sin filtros, obtener todas
    return this.apiService.get<any>(this.endpoint, { skip, limit });
  }

  /**
   * Obtiene entregas por estado
   */
  obtenerPorEstado(estado: string, skip: number = 0, limit: number = 10): Observable<any> {
    console.log(`Obteniendo entregas con estado: ${estado}`);
    return this.apiService.get<any>(`${this.endpoint}/estado/${estado}`, { skip, limit });
  }

  /**
   * Obtiene entregas pendientes
   */
  obtenerEntregasPendientes(skip: number = 0, limit: number = 10): Observable<any> {
    return this.apiService.get<any>(`${this.endpoint}/pendientes`, { skip, limit });
  }

  /**
   * Obtiene un detalle de entrega por ID
   */
  obtenerDetalleEntregaPorId(id: string): Observable<DetalleEntrega> {
    return this.apiService.get<DetalleEntrega>(`${this.endpoint}/${id}`);
  }

  /**
   * Obtiene detalle de entrega por paquete
   */
  obtenerPorPaquete(idPaquete: string): Observable<DetalleEntrega> {
    return this.apiService.get<DetalleEntrega>(`${this.endpoint}/paquete/${idPaquete}`);
  }

  /**
   * Obtiene entregas por cliente (remitente o receptor)
   */
  obtenerPorCliente(idCliente: string, tipo: string = 'remitente', skip: number = 0, limit: number = 10): Observable<any> {
    return this.apiService.get<any>(`${this.endpoint}/cliente/${idCliente}`, { tipo, skip, limit });
  }


  /**
   * Crea un nuevo detalle de entrega
   */
  crearDetalleEntrega(detalleEntrega: DetalleEntrega): Observable<DetalleEntrega> {
    return this.apiService.post<DetalleEntrega>(this.endpoint, detalleEntrega);
  }

  /**
   * Actualiza un detalle de entrega existente
   */
  actualizarDetalleEntrega(id: string, detalleEntrega: Partial<DetalleEntrega>): Observable<DetalleEntrega> {
    return this.apiService.put<DetalleEntrega>(`${this.endpoint}/${id}`, detalleEntrega);
  }


  /**
   * Elimina (desactiva) un detalle de entrega
   */
  eliminarDetalleEntrega(id: string): Observable<ApiResponse> {
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`);
  }
}
