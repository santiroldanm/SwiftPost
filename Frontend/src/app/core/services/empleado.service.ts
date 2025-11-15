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
  documento: string; // Cambiado de numero_documento a documento
  id_tipo_documento: string;
  usuario_id: string;
  tipo_empleado: string; // Cambiado de cargo a tipo_empleado (mensajero, logistico, secretario)
  salario: number;
  fecha_ingreso: string; // Cambiado de fecha_contratacion a fecha_ingreso
  fecha_nacimiento: string; // Nuevo campo requerido
  telefono: string; // Nuevo campo requerido
  correo: string; // Nuevo campo requerido
  direccion: string; // Nuevo campo requerido
  id_sede?: string; // Opcional según el schema
  activo?: boolean; // Campo para indicar si el empleado está activo
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  creado_por?: string;
  actualizado_por?: string;
}

/**
 * Servicio para gestión de empleados
 */
@Injectable({
  providedIn: 'root'
})
export class EmpleadoService {
  private endpoint = '/empleados';

  constructor(private apiService: ApiService) {}

  /**
   * Obtiene todos los empleados con paginación
   */
  obtenerEmpleados(skip: number = 0, limit: number = 10): Observable<Empleado[]> {
    return this.apiService.get<any>(`${this.endpoint}/`, { skip, limit }).pipe(
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
    return this.apiService.get<any>(`${this.endpoint}/tipo/${cargo}`, { skip, limit }).pipe(
      map((response: any) => Array.isArray(response) ? response : (response?.empleados || response || []))
    );
  }

  /**
   * Busca empleados por número de documento
   */
  buscarPorDocumento(numeroDocumento: string): Observable<Empleado[]> {
    return this.apiService.get<any>(`${this.endpoint}/documento/${numeroDocumento}`).pipe(
      map((response: any) => Array.isArray(response) ? [response] : (response?.empleados || [response] || []))
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
  crearEmpleado(empleado: Empleado, creadoPor?: string): Observable<Empleado> {
    const params = creadoPor ? { creado_por: creadoPor } : {};
    return this.apiService.post<Empleado>(`${this.endpoint}/`, empleado, params);
  }

  /**
   * Actualiza un empleado existente
   */
  actualizarEmpleado(id: string, empleado: Partial<Empleado>, actualizadoPor?: string): Observable<Empleado> {
    const params = actualizadoPor ? { actualizado_por: actualizadoPor } : {};
    // Remover actualizado_por del body si está presente
    const { actualizado_por, ...body } = empleado as any;
    return this.apiService.put<Empleado>(`${this.endpoint}/${id}`, body, params);
  }

  /**
   * Elimina (desactiva) un empleado
   */
  eliminarEmpleado(id: string, actualizadoPor?: string): Observable<ApiResponse> {
    const params = actualizadoPor ? { actualizado_por: actualizadoPor } : {};
    return this.apiService.delete<ApiResponse>(`${this.endpoint}/${id}`, params);
  }

  /**
   * Reactiva un empleado
   */
  reactivarEmpleado(id: string): Observable<ApiResponse> {
    return this.apiService.patch<ApiResponse>(`${this.endpoint}/${id}/reactivar`, {});
  }
}
