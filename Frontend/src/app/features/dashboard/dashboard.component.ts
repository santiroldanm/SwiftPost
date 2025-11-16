import { Component, OnInit, inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PaqueteService } from '../../core/services/paquete.service';
import { ClienteService } from '../../core/services/cliente.service';
import { EmpleadoService } from '../../core/services/empleado.service';
import { AnalyticsService } from '../../core/services/analytics.service';
import { forkJoin } from 'rxjs';
import { ChartConfiguration, ChartOptions } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { PLATFORM_ID } from '@angular/core';

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
  imports: [CommonModule, FormsModule, BaseChartDirective],
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
  private platformId = inject(PLATFORM_ID);
  isBrowser = isPlatformBrowser(this.platformId);

  daysLine = 30;
  daysStates = 90;
  daysTop = 90;
  topLimit = 5;

  // Charts data
  lineData: ChartConfiguration['data'] = { labels: [], datasets: [{ data: [], label: 'Paquetes (últimos 30 días)', borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.18)', tension: 0.35, fill: true }] };
  lineOptions: ChartOptions = { responsive: true, plugins: { legend: { display: true }}, scales: { x: {}, y: { beginAtZero: true } } };

  barData: ChartConfiguration['data'] = {
    labels: [],
    datasets: [{
      data: [],
      label: 'Sedes más activas',
      backgroundColor: '#6366f1',
      hoverBackgroundColor: '#4f46e5',
      borderRadius: 6,
      borderSkipped: false
    }]
  };
  barOptions: ChartOptions = {
    responsive: true,
    plugins: { legend: { display: false }},
    scales: {
      x: {
        grid: { display: false }
      },
      y: {
        beginAtZero: true,
        ticks: { precision: 0 },
        grid: { color: '#e5e7eb' }
      }
    }
  };

  pieData: ChartConfiguration['data'] = { labels: [], datasets: [{ data: [], backgroundColor: ['#3b82f6','#10b981','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#84cc16'] }] };
  pieOptions: ChartOptions = { responsive: true, plugins: { legend: { position: 'bottom' } } };

  constructor(
    private paqueteService: PaqueteService,
    private clienteService: ClienteService,
    private empleadoService: EmpleadoService,
    private analytics: AnalyticsService
  ) {}

  ngOnInit(): void {
    this.cargarEstadisticas();
  }

  cargarEstadisticas(): void {
    this.isLoading = true;

    forkJoin({
      paquetes: this.paqueteService.obtenerPaquetes(0, 1000),
      clientes: this.clienteService.obtenerClientes(0, 1000),
      empleados: this.empleadoService.obtenerEmpleados(0, 1000),
      ultimos30: this.analytics.paquetesUltimos30Dias(this.daysLine),
      sedesTop: this.analytics.sedesMasActivas(this.topLimit, this.daysTop),
      estados: this.analytics.estadosPaquetes(this.daysStates),
      resumen: this.analytics.resumen(),
    }).subscribe({
      next: (data) => {
        // KPI cards
        this.stats[0].value = (data.resumen?.total_paquetes ?? data.paquetes.length).toString();
        this.stats[1].value = data.clientes.length.toString();
        this.stats[2].value = data.empleados.length.toString();

        if (this.isBrowser) {
          this.lineData = {
            labels: data.ultimos30.labels,
            datasets: [{
              data: data.ultimos30.data,
              label: 'Paquetes (últimos 30 días)',
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59,130,246,0.18)',
              tension: 0.35,
              fill: true
            }]
          };

          this.barData = {
            labels: data.sedesTop.labels,
            datasets: [{
              data: data.sedesTop.data,
              label: 'Sedes más activas',
              backgroundColor: '#6366f1',
              hoverBackgroundColor: '#4f46e5',
              borderRadius: 6,
              borderSkipped: false
            }]
          };

          const colors = ['#3b82f6','#10b981','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#84cc16'];
          this.pieData = {
            labels: data.estados.labels,
            datasets: [{ data: data.estados.data, backgroundColor: colors.slice(0, data.estados.labels.length) }]
          };
        }

        console.log('[Dashboard] Datos cargados', {
          daysLine: this.daysLine,
          daysStates: this.daysStates,
          daysTop: this.daysTop,
          topLimit: this.topLimit,
        });

        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar estadísticas:', error);
        this.isLoading = false;
      }
    });
  }

  aplicarFiltros(): void {
    console.log('[Dashboard] Aplicar filtros', {
      daysLine: this.daysLine,
      daysStates: this.daysStates,
      daysTop: this.daysTop,
      topLimit: this.topLimit,
    });
    this.cargarEstadisticas();
  }

  exportarReporte(): void {
    if (!this.isBrowser) {
      return;
    }

    this.analytics
      .exportResumen(this.daysLine, this.daysStates, this.daysTop, this.topLimit)
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `reporte-analytics-${new Date().toISOString().slice(0, 10)}.pdf`;
          a.click();
          window.URL.revokeObjectURL(url);
        },
        error: (error) => {
          console.error('Error al exportar reporte:', error);
        },
      });
  }
}
