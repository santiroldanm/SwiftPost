import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { filter, map } from 'rxjs/operators';
@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  showNotifications = false;
  showProfile = false;

  title = "";
  constructor(private router: Router, private route: ActivatedRoute) {
    this.router.events
      .pipe(
        filter(event => event instanceof NavigationEnd),
        map(() => {
          let current = this.route;
          while (current.firstChild) {
            current = current.firstChild;
          }
          return current.snapshot.data['title'] || 'Dashboard';
        })
      )
      .subscribe(title => this.title = title);
  }

  notifications = [
    { id: 1, title: 'Nueva orden recibida', message: 'Orden #1234 ha sido creada', time: 'Hace 5 min', unread: true },
    { id: 2, title: 'Producto bajo en stock', message: 'El producto XYZ tiene solo 5 unidades', time: 'Hace 1 hora', unread: true },
    { id: 3, title: 'Pago confirmado', message: 'Pago de orden #1230 confirmado', time: 'Hace 2 horas', unread: false }
  ];

  user = {
    name: 'Santiago Roldán',
    email: 'santiago@swiftpost.com',
    avatar: 'SR'
  };

  toggleNotifications(): void {
    this.showNotifications = !this.showNotifications;
    this.showProfile = false;
  }

  toggleProfile(): void {
    this.showProfile = !this.showProfile;
    this.showNotifications = false;
  }

  get unreadCount(): number {
    return this.notifications.filter(n => n.unread).length;
  }
}
