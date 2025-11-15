import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PaqueteService } from '../../core/services/paquete.service';
import { ClienteService } from '../../core/services/cliente.service';
import { EmpleadoService } from '../../core/services/empleado.service';
import { forkJoin } from 'rxjs';

interface StatCard {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon: string;
  color: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  stats: StatCard[] = [
    {
      title: 'Paquetes',
      value: '0',
      change: '0%',
      trend: 'up',
      icon: 'inventory_2',
      color: '#FFB347'
    },
    {
      title: 'Clientes',
      value: '0',
      change: '0%',
      trend: 'up',
      icon: 'people',
      color: '#a96920'
    },
    {
      title: 'Empleados',
      value: '0',
      change: '0',
      trend: 'up',
      icon: 'trending_up',
      color: '#d48f34'
    }
  ];

  isLoading = false;

  constructor(
    private paqueteService: PaqueteService,
    private clienteService: ClienteService,
    private empleadoService: EmpleadoService
  ) {}

  ngOnInit(): void {
    this.cargarEstadisticas();
  }

  cargarEstadisticas(): void {
    this.isLoading = true;

    forkJoin({
      paquetes: this.paqueteService.obtenerPaquetes(0, 1000),
      clientes: this.clienteService.obtenerClientes(0, 1000),
      empleados: this.empleadoService.obtenerEmpleados(0, 1000)
    }).subscribe({
      next: (data) => {
        // Los servicios ahora devuelven arrays directamente gracias al manejo de respuestas
        this.stats[0].value = data.paquetes.length.toString();
        this.stats[1].value = data.clientes.length.toString();
        this.stats[2].value = data.empleados.length.toString();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar estadísticas:', error);
        this.isLoading = false;
      }
    });
  }
}
