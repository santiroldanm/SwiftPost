import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { ApiService } from './api.service';
import { ApiResponse } from '../models/api-response.model';
import { PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

/**
 * Interfaz para los datos de login
 */
export interface LoginData {
  nombre_usuario: string;
  contraseña: string;
}

/**
 * Interfaz para la respuesta de usuario
 */
export interface UsuarioResponse {
  id_usuario: string;
  nombre_usuario: string;
  activo: boolean;
  fecha_creacion: string;
  id_rol: string;
  rol?: {
    id_rol: string;
    nombre_rol: string;
    descripcion?: string;
  };
}

/**
 * Servicio de autenticación
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<UsuarioResponse | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private apiService: ApiService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: object
  ) {
    // Cargar usuario desde localStorage si existe
    this.loadUserFromStorage();
  }

  /**
   * Realiza el login del usuario
   */
  login(loginData: LoginData): Observable<UsuarioResponse> {
    return this.apiService.post<UsuarioResponse>('/auth/login', loginData).pipe(
      tap(usuario => {
        // Guardar datos del usuario en localStorage solo si estamos en el navegador
        if (isPlatformBrowser(this.platformId)) {
          localStorage.setItem('user_id', usuario.id_usuario);
          localStorage.setItem('user_data', JSON.stringify(usuario));
          localStorage.setItem('auth_token', usuario.id_usuario); // Usando el ID como token
        }
        
        // Actualizar el subject
        this.currentUserSubject.next(usuario);
      })
    );
  }

  /**
   * Cierra la sesión del usuario
   */
  logout(): void {
    // Limpiar localStorage solo si estamos en el navegador
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_data');
    }
    
    // Actualizar el subject
    this.currentUserSubject.next(null);
    
    // Redirigir al login
    this.router.navigate(['/login']);
  }

  /**
   * Verifica si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    if (!isPlatformBrowser(this.platformId)) {
      return false;
    }
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');
    return !!(token && userId);
  }

  /**
   * Obtiene el usuario actual
   * Si el usuario no está en el subject, intenta cargarlo desde localStorage
   */
  getCurrentUser(): UsuarioResponse | null {
    let user = this.currentUserSubject.value;
    
    // Si no hay usuario en el subject, intentar cargar desde localStorage
    if (!user && isPlatformBrowser(this.platformId)) {
      const userData = localStorage.getItem('user_data');
      if (userData) {
        try {
          user = JSON.parse(userData);
          this.currentUserSubject.next(user);
        } catch (error) {
          console.error('Error al cargar datos del usuario:', error);
        }
      }
    }
    
    return user;
  }

  /**
   * Verifica un usuario por ID
   */
  verificarUsuario(usuarioId: string): Observable<ApiResponse> {
    return this.apiService.get<ApiResponse>(`/auth/verificar/${usuarioId}`);
  }

  /**
   * Obtiene el estado del sistema de autenticación
   */
  getEstadoAutenticacion(): Observable<ApiResponse> {
    return this.apiService.get<ApiResponse>('/auth/estado');
  }

  /**
   * Crea el usuario administrador por defecto
   */
  crearAdmin(): Observable<ApiResponse> {
    return this.apiService.post<ApiResponse>('/auth/crear-admin', {});
  }

  /**
   * Carga el usuario desde localStorage
   */
  private loadUserFromStorage(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }
    const userData = localStorage.getItem('user_data');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        this.currentUserSubject.next(user);
      } catch (error) {
        console.error('Error al cargar datos del usuario:', error);
        this.logout();
      }
    }
  }

  /**
   * Obtiene el rol del usuario actual
   */
  getUserRole(): string | null {
    const user = this.getCurrentUser();
    return user?.rol?.nombre_rol || null;
  }

  /**
   * Verifica si el usuario tiene un rol específico
   */
  hasRole(roleName: string): boolean {
    const userRole = this.getUserRole();
    return userRole?.toLowerCase() === roleName.toLowerCase();
  }
}
