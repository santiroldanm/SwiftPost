import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable } from 'rxjs';

/**
 * Guard para proteger rutas que requieren autenticación
 */
@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  
  constructor(private router: Router) {}
  
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    
    // Verificar si existe un token de autenticación
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');
    
    if (token && userId) {
      // Usuario autenticado, permitir acceso
      return true;
    }
    
    // Usuario no autenticado, redirigir al login
    console.warn('Acceso denegado. Redirigiendo al login...');
    this.router.navigate(['/login'], {
      queryParams: { returnUrl: state.url }
    });
    
    return false;
  }
}
