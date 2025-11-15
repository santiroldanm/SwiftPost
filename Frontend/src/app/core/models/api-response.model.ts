/**
 * Modelo base para las respuestas de la API
 */
export interface ApiResponse<T = any> {
  mensaje: string;
  exito: boolean;
  datos?: T;
}

/**
 * Modelo para respuestas de error de la API
 */
export interface ApiErrorResponse {
  mensaje: string;
  exito: boolean;
  error: string;
  codigo: number;
}

/**
 * Modelo para respuestas paginadas
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  pagina: number;
  por_pagina: number;
}
