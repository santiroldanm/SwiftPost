import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';

/**
 * Interfaz para Cliente
 */
export interface Cliente {
  id_cliente?: string;
  primer_nombre: string;
  segundo_nombre?: string;
  primer_apellido: string;
  segundo_apellido?: string;
  numero_documento: string;
  id_tipo_documento: string;
  usuario_id: string;
  direccion: string;
  telefono: string;
  correo: string;
  tipo: string;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  actualizado_por?: string;
}

/**
 * Servicio para gestión de clientes
 */
@Injectable({
  providedIn: 'root'
})
export class ClienteService {
  private endpoint = '/clientes';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todos los clientes con paginación
   */
  obtenerClientes(skip: number = 0, limit: number = 10): Observable<Cliente[]> {
    return this.apiService.get<any>(`${this.endpoint}/`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.clientes || response || []))
    );
  }

  /**
   * Obtiene todos los clientes activos
   */
  obtenerClientesActivos(skip: number = 0, limit: number = 10): Observable<Cliente[]> {
    return this.apiService.get<any>(`${this.endpoint}/activos`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.clientes || response || []))
    );
  }

  /**
   * Obtiene un cliente por ID
   */
  obtenerClientePorId(id: string): Observable<Cliente> {
    return this.apiService.get<Cliente>(`${this.endpoint}/${id}`);
  }

  /**
   * Obtiene clientes por tipo (remitente/receptor)
   */
  obtenerClientesPorTipo(tipo: string, skip: number = 0, limit: number = 10): Observable<Cliente[]> {
    return this.apiService.get<any>(`${this.endpoint}/tipo/${tipo}`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.clientes || response || []))
    );
  }

  /**
   * Busca clientes por número de documento
   */
  buscarPorDocumento(numeroDocumento: string): Observable<Cliente[]> {
    return this.apiService.get<any>(`${this.endpoint}/buscar/documento/${numeroDocumento}`).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.clientes || response || []))
    );
  }

  /**
   * Busca clientes por nombre
   */
  buscarPorNombre(nombre: string): Observable<Cliente[]> {
    return this.apiService.get<Cliente[]>(`${this.endpoint}/buscar/nombre/${nombre}`);
  }

  /**
   * Crea un nuevo cliente
   */
  crearCliente(cliente: Cliente, creadoPor?: string): Observable<Cliente> {
    const params = creadoPor ? { creado_por: creadoPor } : {};
    return this.apiService.post<Cliente>(`${this.endpoint}/`, cliente, params);
  }

  /**
   * Actualiza un cliente existente
   */
  actualizarCliente(id: string, cliente: Partial<Cliente>, actualizadoPor?: string): Observable<Cliente> {
    const params = actualizadoPor ? { actualizado_por: actualizadoPor } : {};
    // Remover actualizado_por del body si está presente
    const { actualizado_por, ...body } = cliente as any;
    return this.apiService.put<Cliente>(`${this.endpoint}/${id}`, body, params);
  }

  /**
   * Elimina (desactiva) un cliente
   */
  eliminarCliente(id: string, actualizadoPor?: string): Observable<ApiResponse> {
    const params = actualizadoPor ? { actualizado_por: actualizadoPor } : {};
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`, params);
  }

  /**
   * Reactiva un cliente
   */
  reactivarCliente(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }
}
