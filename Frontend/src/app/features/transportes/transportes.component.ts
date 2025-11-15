import { Component, OnInit, AfterViewInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { TransporteService, Transporte } from '../../core/services/transporte.service';
import { AuthService } from '../../core/services/auth.service';
import { SedeService, Sede } from '../../core/services/sede.service';

@Component({
  selector: 'app-transportes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [TransporteService, AuthService],
  templateUrl: './transportes.component.html',
  styleUrls: ['./transportes.component.scss'],
  changeDetection: ChangeDetectionStrategy.Default
})
export class TransportesComponent implements OnInit, AfterViewInit {
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
    private cdr: ChangeDetectorRef,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.cargarTransportes();
    this.cargarSedes();
    
    // Escuchar cambios de ruta para recargar datos
    this.route.params.subscribe(() => {
      this.cargarTransportes();
    });
  }

  ngAfterViewInit(): void {
    // Forzar recarga de datos después de que la vista esté inicializada
    setTimeout(() => {
      this.cargarTransportes();
    }, 100);
  }

  cargarTransportes(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    this.transporteService.obtenerTransportes(0, 100).subscribe({
      next: (transportes) => {
        this.transports = transportes;
        this.isLoading = false;
        this.cdr.detectChanges(); // Forzar actualización de la vista
      },
      error: (error) => {
        console.error('Error al cargar transportes:', error);
        this.errorMessage = 'Error al cargar los transportes';
        this.isLoading = false;
        this.cdr.detectChanges(); // Forzar actualización de la vista
      }
    });
  }

  cargarSedes(): void {
    this.sedeService.obtenerSedes(0, 100).subscribe({
      next: (sedes) => {
        this.sedes = Array.isArray(sedes) ? sedes : [];
      },
      error: (error) => console.error('Error al cargar sedes:', error)
    });
  }


  get filteredTransports() {
    let filtered = this.transports;
    
    // Filtrar por búsqueda
    if (this.searchTerm.trim()) {
      filtered = filtered.filter(t =>
        t.tipo_vehiculo.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        t.placa.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        t.marca.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        t.modelo.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }
    
    // Filtrar por estado
    if (this.filtroEstado !== 'todos') {
      filtered = filtered.filter(t => t.estado === this.filtroEstado);
    }
    
    return filtered;
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
    const currentUser = this.authService.getCurrentUser();
    
    if (this.isEditMode && this.transportForm.id_transporte) {
      // Actualizar transporte existente
      const updateData = {
        ...this.transportForm,
        actualizado_por: currentUser?.id_usuario
      };
      
      this.transporteService.actualizarTransporte(this.transportForm.id_transporte, updateData).subscribe({
        next: () => {
          this.cargarTransportes();
          this.closeModal();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al actualizar transporte:', error);
          this.errorMessage = 'Error al actualizar el transporte';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nuevo transporte
      const newTransporte = {
        ...this.transportForm,
        creado_por: currentUser?.id_usuario
      };
      
      this.transporteService.crearTransporte(newTransporte).subscribe({
        next: () => {
          this.cargarTransportes();
          this.closeModal();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al crear transporte:', error);
          this.errorMessage = 'Error al crear el transporte';
          this.isLoading = false;
        }
      });
    }
  }

  deleteTransport(id: string | undefined) {
    if (!id) return;
    
    if (confirm('¿Estás seguro de eliminar este transporte?')) {
      this.transporteService.eliminarTransporte(id).subscribe({
        next: () => {
          this.cargarTransportes();
          if (this.currentSlide >= this.transports.length && this.currentSlide > 0) {
            this.currentSlide--;
          }
        },
        error: (error) => {
          console.error('Error al eliminar transporte:', error);
          this.errorMessage = 'Error al eliminar el transporte';
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
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'todos';
    this.searchTerm = '';
  }
}
