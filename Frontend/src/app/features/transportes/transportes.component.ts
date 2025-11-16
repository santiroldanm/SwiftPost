import { Component, OnInit, AfterViewInit, DestroyRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { TransporteService, Transporte } from '../../core/services/transporte.service';
import { AuthService } from '../../core/services/auth.service';
import { SedeService, Sede } from '../../core/services/sede.service';

@Component({
  selector: 'app-transportes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './transportes.component.html',
  styleUrls: ['./transportes.component.scss']
})
export class TransportesComponent implements OnInit, AfterViewInit {
  private destroyRef = inject(DestroyRef);
  searchTerm = '';
  showModal = false;
  showFiltros = false;
  isEditMode = false;
  isLoading = false;
  errorMessage = '';
  currentSlide = 0;
  maxYear = new Date().getFullYear() + 1;
  filtroEstado = 'todos';
  
  transportForm: Transporte = {
    tipo_vehiculo: '',
    capacidad_carga: 0,
    id_sede: '',
    placa: '',
    modelo: '',
    marca: '',
    año: new Date().getFullYear()
  };

  transports: Transporte[] = [];
  sedes: Sede[] = [];

  constructor(
    private transporteService: TransporteService,
    private authService: AuthService,
    private sedeService: SedeService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.cargarTransportes();
    this.cargarSedes();
    
    // Escuchar cambios de ruta para recargar datos
    this.route.params
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.cargarTransportes();
      });
  }

  ngAfterViewInit(): void {
    // Ya no es necesario el setTimeout, Angular maneja esto automáticamente
  }

  cargarTransportes(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    // Construir filtros para el backend
    const filtros: any = {};
    if (this.filtroEstado !== 'todos') {
      filtros.estado = this.filtroEstado;
    }
    if (this.searchTerm.trim()) {
      filtros.search = this.searchTerm.trim();
    }
    
    console.log('Cargando transportes con filtros:', filtros);
    
    this.transporteService.obtenerTransportes(0, 100, filtros)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (transportes) => {
          // Filtrar solo transportes activos
          this.transports = transportes.filter(t => t.activo !== false);
          this.isLoading = false;
          console.log('Transportes activos cargados:', this.transports.length, 'registros');
        },
        error: (error) => {
          console.error('Error al cargar transportes:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al cargar los transportes';
          this.isLoading = false;
        }
      });
  }

  cargarSedes(): void {
    this.sedeService.obtenerSedes(0, 100)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (sedes) => {
          this.sedes = Array.isArray(sedes) ? sedes : [];
        },
        error: (error) => console.error('Error al cargar sedes:', error)
      });
  }


  get filteredTransports(): Transporte[] {
    // La filtración se hace en el backend y además filtramos por activo en el frontend
    // Solo mostramos transportes activos
    return this.transports.filter(t => t.activo !== false);
  }

  get totalSlides() {
    return this.filteredTransports.length;
  }

  nextSlide() {
    if (this.currentSlide < this.totalSlides - 1) {
      this.currentSlide++;
    } else {
      this.currentSlide = 0;
    }
  }

  prevSlide() {
    if (this.currentSlide > 0) {
      this.currentSlide--;
    } else {
      this.currentSlide = this.totalSlides - 1;
    }
  }

  goToSlide(index: number) {
    this.currentSlide = index;
  }

  openNewTransportModal() {
    this.isEditMode = false;
    this.transportForm = {
      tipo_vehiculo: '',
      capacidad_carga: 0,
      id_sede: '',
      placa: '',
      modelo: '',
      marca: '',
      año: new Date().getFullYear()
    };
    this.showModal = true;
  }

  openEditTransportModal(transport: Transporte) {
    this.isEditMode = true;
    this.transportForm = { ...transport };
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
  }

  saveTransport() {
    this.isLoading = true;
    this.errorMessage = '';
    const currentUser = this.authService.getCurrentUser();
    
    if (this.isEditMode && this.transportForm.id_transporte) {
      // Actualizar transporte existente
      if (!currentUser?.id_usuario) {
        this.errorMessage = 'Usuario no autenticado';
        this.isLoading = false;
        return;
      }

      // Limpiar datos: remover campos que no deben enviarse
      const { id_transporte, fecha_creacion, fecha_actualizacion, creado_por, ...updateData } = this.transportForm;
      
      this.transporteService.actualizarTransporte(this.transportForm.id_transporte, updateData, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          this.cargarTransportes();
          this.closeModal();
          this.isLoading = false;
          this.errorMessage = '';
        },
        error: (error) => {
          console.error('Error al actualizar transporte:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al actualizar el transporte';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nuevo transporte
      if (!currentUser?.id_usuario) {
        this.errorMessage = 'Usuario no autenticado';
        this.isLoading = false;
        return;
      }

      if (!this.transportForm.id_sede) {
        this.errorMessage = 'Debe seleccionar una sede';
        this.isLoading = false;
        return;
      }

      // Limpiar datos: remover campos que no deben enviarse en creación
      const { id_transporte, fecha_creacion, fecha_actualizacion, actualizado_por, creado_por, ...newTransporte } = this.transportForm as any;
      
      this.transporteService.crearTransporte(newTransporte, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          this.cargarTransportes();
          this.closeModal();
          this.isLoading = false;
          this.errorMessage = '';
        },
        error: (error) => {
          console.error('Error al crear transporte:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al crear el transporte';
          this.isLoading = false;
        }
      });
    }
  }

  deleteTransport(id: string | undefined) {
    if (!id) return;
    
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser?.id_usuario) {
      this.errorMessage = 'Usuario no autenticado';
      return;
    }
    
    if (confirm('¿Estás seguro de eliminar este transporte?')) {
      this.isLoading = true;
      this.transporteService.eliminarTransporte(id, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          this.cargarTransportes();
          if (this.currentSlide >= this.transports.length && this.currentSlide > 0) {
            this.currentSlide--;
          }
          this.errorMessage = '';
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al eliminar transporte:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al eliminar el transporte';
          this.isLoading = false;
        }
      });
    }
  }

  getStatusClass(status: string | undefined): string {
    if (!status) return '';
    switch(status) {
      case 'disponible': return 'status-available';
      case 'en_uso': return 'status-in-route';
      case 'mantenimiento': return 'status-maintenance';
      case 'fuera_servicio': return 'status-maintenance';
      default: return '';
    }
  }

  getAvailableCount(): number {
    return this.transports.filter(t => t.estado === 'disponible').length;
  }

  getInRouteCount(): number {
    return this.transports.filter(t => t.estado === 'en_uso').length;
  }

  getMaintenanceCount(): number {
    return this.transports.filter(t => t.estado === 'mantenimiento' || t.estado === 'fuera_servicio').length;
  }

  exportarDatos(): void {
    const csv = this.convertirACSV(this.filteredTransports);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `transportes_${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  private convertirACSV(data: any[]): string {
    if (data.length === 0) return '';
    
    const headers = ['ID', 'Tipo Vehículo', 'Marca', 'Modelo', 'Año', 'Placa', 'Capacidad Carga', 'Estado', 'Sede'];
    const rows = data.map(t => [
      t.id_transporte?.substring(0, 8) || '',
      t.tipo_vehiculo,
      t.marca,
      t.modelo,
      t['año'] || t.año,
      t.placa,
      t.capacidad_carga,
      t.estado,
      this.obtenerNombreSede(t.id_sede)
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  private obtenerNombreSede(idSede: string): string {
    const sede = this.sedes.find(s => s.id_sede === idSede);
    return sede ? sede.nombre : 'N/A';
  }

  toggleFiltros(): void {
    this.showFiltros = !this.showFiltros;
  }

  aplicarFiltros(): void {
    this.showFiltros = false;
    // Recargar datos con los nuevos filtros
    console.log('Aplicando filtros, recargando desde backend...');
    this.cargarTransportes();
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'todos';
    this.searchTerm = '';
    // Recargar datos sin filtros
    console.log('Limpiando filtros, recargando desde backend...');
    this.cargarTransportes();
  }

  private getErrorMessage(error: any): string {
    const errorDetail = error?.error?.detail || error?.error?.message || error?.message;
    if (typeof errorDetail === 'string') {
      return errorDetail;
    } else if (errorDetail && typeof errorDetail === 'object') {
      if (Array.isArray(errorDetail)) {
        return errorDetail.join(', ');
      }
      return JSON.stringify(errorDetail);
    }
    return 'Error desconocido';
  }
}
