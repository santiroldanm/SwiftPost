import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

interface MenuItem {
  label: string;
  icon: string;
  route?: string;
  children?: MenuItem[];
  expanded?: boolean;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  isCollapsed = false;
  @Output() collapsedChange = new EventEmitter<boolean>();

  menuItems: MenuItem[] = [
    {
      label: 'Inicio',
      icon: 'house',
      route: '/inicio'
    },
    {
      label: 'Paquetes',
      icon: 'inventory_2',
      route: '/paquetes'
    },
    {
      label: 'Empleados',
      icon: 'people',
      route: '/empleados'
    },
    {
      label: 'Transportes',
      icon: 'local_shipping',
      route: '/transportes'
    },
    {
      label: 'Sedes',
      icon: 'location_on',
      route: '/sedes'
    },
    {
      label: 'Entregas',
      icon: 'assignment',
      route: '/entregas'
    },
    {
      label: 'Configuración',
      icon: 'settings',
      route: '/configuracion'
    }
  ];

  toggleSidebar(): void {
    this.isCollapsed = !this.isCollapsed;
    this.collapsedChange.emit(this.isCollapsed);
  }

  toggleSubmenu(item: MenuItem): void {
    if (item.children) {
      item.expanded = !item.expanded;
    }
  }
}
