import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';

/**
 * Interfaz para Empleado
 */
export interface Empleado {
  id_empleado?: string;
  primer_nombre: string;
  segundo_nombre?: string;
  primer_apellido: string;
  segundo_apellido?: string;
  numero_documento: string;
  id_tipo_documento: string;
  usuario_id: string;
  cargo: string;
  salario: number;
  fecha_contratacion: string;
  id_sede: string;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  actualizado_por?: string;
}

/**
 * Servicio para gestión de empleados
 */
@Injectable({
  providedIn: 'root'
})
export class EmpleadoService {
  private endpoint = '/empleados/';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todos los empleados con paginación
   */
  obtenerEmpleados(skip: number = 0, limit: number = 10): Observable<Empleado[]> {
    return this.apiService.get<any>(this.endpoint, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.empleados || response || []))
    );
  }

  /**
   * Obtiene todos los empleados activos
   */
  obtenerEmpleadosActivos(skip: number = 0, limit: number = 10): Observable<Empleado[]> {
    return this.apiService.get<any>(`${this.endpoint}/activos`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.empleados || response || []))
    );
  }

  /**
   * Obtiene un empleado por ID
   */
  obtenerEmpleadoPorId(id: string): Observable<Empleado> {
    return this.apiService.get<Empleado>(`${this.endpoint}/${id}`);
  }

  /**
   * Obtiene empleados por sede
   */
  obtenerEmpleadosPorSede(idSede: string, skip: number = 0, limit: number = 10): Observable<Empleado[]> {
    return this.apiService.get<any>(`${this.endpoint}/sede/${idSede}`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.empleados || response || []))
    );
  }

  /**
   * Obtiene empleados por cargo
   */
  obtenerEmpleadosPorCargo(cargo: string, skip: number = 0, limit: number = 10): Observable<Empleado[]> {
    return this.apiService.get<any>(`${this.endpoint}/cargo/${cargo}`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.empleados || response || []))
    );
  }

  /**
   * Busca empleados por número de documento
   */
  buscarPorDocumento(numeroDocumento: string): Observable<Empleado[]> {
    return this.apiService.get<any>(`${this.endpoint}/buscar/documento/${numeroDocumento}`).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.empleados || response || []))
    );
  }

  /**
   * Busca empleados por nombre
   */
  buscarPorNombre(nombre: string): Observable<Empleado[]> {
    return this.apiService.get<Empleado[]>(`${this.endpoint}/buscar/nombre/${nombre}`);
  }

  /**
   * Crea un nuevo empleado
   */
  crearEmpleado(empleado: Empleado): Observable<Empleado> {
    return this.apiService.post<Empleado>(this.endpoint, empleado);
  }

  /**
   * Actualiza un empleado existente
   */
  actualizarEmpleado(id: string, empleado: Partial<Empleado>): Observable<Empleado> {
    return this.apiService.put<Empleado>(`${this.endpoint}/${id}`, empleado);
  }

  /**
   * Elimina (desactiva) un empleado
   */
  eliminarEmpleado(id: string): Observable<ApiResponse> {
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`);
  }

  /**
   * Reactiva un empleado
   */
  reactivarEmpleado(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }
}
