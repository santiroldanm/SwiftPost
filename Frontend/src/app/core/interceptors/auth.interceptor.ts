import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

/**
 * Interceptor para agregar el token de autenticación a las peticiones HTTP
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const platformId = inject(PLATFORM_ID);
  
  // Solo acceder a localStorage si estamos en el navegador
  if (!isPlatformBrowser(platformId)) {
    return next(req);
  }
  
  // Obtener el token del localStorage
  const token = localStorage.getItem('auth_token');
  const userId = localStorage.getItem('user_id');
  
  // Si existe el token, clonar la petición y agregar el header de autorización
  if (token) {
    const clonedReq = req.clone({
      setHeaders: {
        'Authorization': `Bearer ${token}`,
        ...(userId && { 'X-User-ID': userId })
      }
    });
    
    return next(clonedReq);
  }
  
  // Si no hay token, continuar con la petición original
  return next(req);
};
