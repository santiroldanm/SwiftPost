import { inject } from '@angular/core';
import { CanActivateFn, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

/**
 * Guard para proteger rutas que requieren autenticación
 */
export const authGuard: CanActivateFn = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
): boolean => {
  const router = inject(Router);
  const platformId = inject(PLATFORM_ID);
  
  // Solo verificar en el navegador
  if (!isPlatformBrowser(platformId)) {
    return false;
  }
  
  // Verificar si existe un token de autenticación
  const token = localStorage.getItem('auth_token');
  const userId = localStorage.getItem('user_id');
  
  if (token && userId) {
    // Usuario autenticado, permitir acceso
    return true;
  }
  
  // Usuario no autenticado, redirigir al login
  console.warn('Acceso denegado. Redirigiendo al login...');
  router.navigate(['/login'], {
    queryParams: { returnUrl: state.url }
  });
  
  return false;
};
