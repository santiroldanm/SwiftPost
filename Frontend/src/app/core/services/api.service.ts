import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

/**
 * Servicio base para realizar peticiones HTTP a la API
 */
@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8000'; // URL base del backend

  constructor(private http: HttpClient) {}

  /**
   * Obtiene las cabeceras HTTP por defecto
   */
  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
  }

  /**
   * Realiza una petición GET
   */
  get<T>(endpoint: string, params?: any): Observable<T> {
    const url = `${this.apiUrl}${endpoint}`;
    const httpParams = this.buildParams(params);
    
    return this.http.get<T>(url, {
      headers: this.getHeaders(),
      params: httpParams
    });
  }

  /**
   * Realiza una petición POST
   */
  post<T>(endpoint: string, body: any): Observable<T> {
    const url = `${this.apiUrl}${endpoint}`;
    
    return this.http.post<T>(url, body, {
      headers: this.getHeaders()
    });
  }

  /**
   * Realiza una petición PUT
   */
  put<T>(endpoint: string, body: any): Observable<T> {
    const url = `${this.apiUrl}${endpoint}`;
    
    return this.http.put<T>(url, body, {
      headers: this.getHeaders()
    });
  }

  /**
   * Realiza una petición PATCH
   */
  patch<T>(endpoint: string, body: any): Observable<T> {
    const url = `${this.apiUrl}${endpoint}`;
    
    return this.http.patch<T>(url, body, {
      headers: this.getHeaders()
    });
  }

  /**
   * Realiza una petición DELETE
   */
  delete<T>(endpoint: string): Observable<T> {
    const url = `${this.apiUrl}${endpoint}`;
    
    return this.http.delete<T>(url, {
      headers: this.getHeaders()
    });
  }

  /**
   * Construye los parámetros HTTP desde un objeto
   */
  private buildParams(params?: any): HttpParams {
    let httpParams = new HttpParams();
    
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    
    return httpParams;
  }

  /**
   * Obtiene la URL completa de un endpoint
   */
  getFullUrl(endpoint: string): string {
    return `${this.apiUrl}${endpoint}`;
  }
}
