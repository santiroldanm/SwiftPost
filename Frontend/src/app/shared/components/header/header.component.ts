import { Component, OnInit, DestroyRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { filter, map } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService, UsuarioResponse } from '../../../core/services/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
  private destroyRef = inject(DestroyRef);
  
  showNotifications = false;
  showProfile = false;
  title = "";
  currentUser: UsuarioResponse | null = null;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private authService: AuthService
  ) {
    this.router.events
      .pipe(
        filter(event => event instanceof NavigationEnd),
        map(() => {
          let current = this.route;
          while (current.firstChild) {
            current = current.firstChild;
          }
          return current.snapshot.data['title'] || 'Dashboard';
        }),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe(title => this.title = title);
  }

  ngOnInit(): void {
    // Suscribirse a cambios en el usuario actual
    this.authService.currentUser$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(user => {
        this.currentUser = user;
      });
    
    // Cargar usuario inicial
    this.currentUser = this.authService.getCurrentUser();
  }

  notifications = [
    { id: 1, title: 'Nueva orden recibida', message: 'Orden #1234 ha sido creada', time: 'Hace 5 min', unread: true },
    { id: 2, title: 'Producto bajo en stock', message: 'El producto XYZ tiene solo 5 unidades', time: 'Hace 1 hora', unread: true },
    { id: 3, title: 'Pago confirmado', message: 'Pago de orden #1230 confirmado', time: 'Hace 2 horas', unread: false }
  ];

  get user() {
    if (this.currentUser) {
      const nombre = this.currentUser.nombre_usuario;
      const iniciales = nombre.substring(0, 2).toUpperCase();
      return {
        name: nombre,
        email: this.currentUser.rol?.nombre_rol || 'Usuario',
        avatar: iniciales
      };
    }
    return {
      name: 'Usuario',
      email: 'No autenticado',
      avatar: 'U'
    };
  }

  toggleNotifications(): void {
    this.showNotifications = !this.showNotifications;
    this.showProfile = false;
  }

  toggleProfile(): void {
    this.showProfile = !this.showProfile;
    this.showNotifications = false;
  }

  logout(): void {
    this.authService.logout();
  }

  get unreadCount(): number {
    return this.notifications.filter(n => n.unread).length;
  }
}
