import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable } from 'rxjs';

/**
 * Guard para evitar que usuarios autenticados accedan al login
 */
@Injectable({
  providedIn: 'root'
})
export class LoginGuard implements CanActivate {
  
  constructor(private router: Router) {}
  
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    
    // Verificar si existe un token de autenticación
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');
    
    if (token && userId) {
      // Usuario ya autenticado, redirigir al dashboard
      console.log('Usuario ya autenticado. Redirigiendo al dashboard...');
      this.router.navigate(['/dashboard']);
      return false;
    }
    
    // Usuario no autenticado, permitir acceso al login
    return true;
  }
}
