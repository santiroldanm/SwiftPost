import { Component, OnInit, DestroyRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService, LoginData } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  private destroyRef = inject(DestroyRef);
  
  loginForm: LoginData = {
    nombre_usuario: '',
    contraseña: ''
  };
  
  isLoading = false;
  errorMessage = '';
  showPassword = false;
  returnUrl = '/inicio';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // Obtener la URL de retorno si existe
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/inicio';
    
    // Si ya está autenticado, redirigir
    if (this.authService.isAuthenticated()) {
      this.router.navigate([this.returnUrl]);
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {
    // Validar formulario
    if (!this.loginForm.nombre_usuario || !this.loginForm['contraseña']) {
      this.errorMessage = 'Por favor complete todos los campos';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.login(this.loginForm)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (usuario) => {
          // Login exitoso
          this.isLoading = false;
          
          // Verificar si el usuario está activo
          if (!usuario.activo) {
            this.errorMessage = 'Su cuenta está inactiva. Contacte al administrador.';
            this.authService.logout();
            return;
          }

          // Redirigir a la URL de retorno o al dashboard
          this.router.navigate([this.returnUrl]);
        },
        error: (error) => {
          console.error('Error en login:', error);
          this.isLoading = false;
          
          // Extraer mensaje de error
          if (error?.error?.detail) {
            this.errorMessage = error.error.detail;
          } else if (error?.error?.message) {
            this.errorMessage = error.error.message;
          } else if (error?.message) {
            this.errorMessage = error.message;
          } else {
            this.errorMessage = 'Error al iniciar sesión. Verifique sus credenciales.';
          }
        }
      });
  }
}

