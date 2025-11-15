import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';

/**
 * Interceptor para manejar errores HTTP globalmente
 */
@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  
  constructor(private router: Router) {}
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'Ha ocurrido un error desconocido';
        
        if (error.error instanceof ErrorEvent) {
          // Error del lado del cliente
          errorMessage = `Error: ${error.error.message}`;
        } else {
          // Error del lado del servidor
          switch (error.status) {
            case 400:
              errorMessage = error.error?.mensaje || error.error?.detail || 'Solicitud incorrecta';
              break;
            case 401:
              errorMessage = 'No autorizado. Por favor, inicie sesión nuevamente';
              // Limpiar el localStorage y redirigir al login
              localStorage.removeItem('auth_token');
              localStorage.removeItem('user_id');
              localStorage.removeItem('user_data');
              this.router.navigate(['/login']);
              break;
            case 403:
              errorMessage = 'No tiene permisos para realizar esta acción';
              break;
            case 404:
              errorMessage = error.error?.mensaje || error.error?.detail || 'Recurso no encontrado';
              break;
            case 500:
              errorMessage = error.error?.mensaje || error.error?.detail || 'Error interno del servidor';
              break;
            case 503:
              errorMessage = 'Servicio no disponible. Intente más tarde';
              break;
            default:
              errorMessage = error.error?.mensaje || error.error?.detail || `Error ${error.status}: ${error.statusText}`;
          }
        }
        
        // Mostrar el error en consola para debugging
        console.error('Error HTTP:', {
          status: error.status,
          message: errorMessage,
          error: error.error,
          url: req.url
        });
        
        // Retornar el error para que pueda ser manejado por el componente
        return throwError(() => ({
          status: error.status,
          message: errorMessage,
          error: error.error
        }));
      })
    );
  }
}
