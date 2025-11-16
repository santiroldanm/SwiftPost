import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

/**
 * Guard para evitar que usuarios autenticados accedan al login
 */
export const loginGuard: CanActivateFn = (): boolean => {
  const router = inject(Router);
  const platformId = inject(PLATFORM_ID);
  
  // Solo verificar en el navegador
  if (!isPlatformBrowser(platformId)) {
    return true;
  }
  
  // Verificar si existe un token de autenticación
  const token = localStorage.getItem('auth_token');
  const userId = localStorage.getItem('user_id');
  
  if (token && userId) {
    // Usuario ya autenticado, redirigir al dashboard
    console.log('Usuario ya autenticado. Redirigiendo al inicio...');
    router.navigate(['/inicio']);
    return false;
  }
  
  // Usuario no autenticado, permitir acceso al login
  return true;
};
