import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';

/**
 * Interceptor para agregar el token de autenticación a las peticiones HTTP
 */
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
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
      
      return next.handle(clonedReq);
    }
    
    // Si no hay token, continuar con la petición original
    return next.handle(req);
  }
}
