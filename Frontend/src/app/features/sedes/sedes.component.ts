import { Component, OnInit, DestroyRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { SedeService, Sede } from '../../core/services/sede.service';
import { AuthService } from '../../core/services/auth.service';
import { FormStorageService } from '../../core/services/form-storage.service';

@Component({
  selector: 'app-sedes',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './sedes.component.html',
  styleUrls: ['./sedes.component.scss']
})
export class SedesComponent implements OnInit {
  private destroyRef = inject(DestroyRef);
  searchTerm = '';
  showModal = false;
  showFiltros = false;
  isEditMode = false;
  isLoading = false;
  errorMessage = '';
  selectedSede: Sede | null = null;
  filtroEstado = 'todos';
  hoveredSede: Sede | null = null;

  sedeForm: Sede = {
    nombre: '',
    ciudad: '',
    direccion: '',
    telefono: ''
  };

  sedes: Sede[] = [];

  constructor(
    private sedeService: SedeService,
    private authService: AuthService,
    private formStorage: FormStorageService
  ) {}

  ngOnInit(): void {
    this.cargarSedes();
  }

  cargarSedes(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    // Construir filtros para el backend
    const filtros: any = {};
    if (this.filtroEstado === 'activas') {
      filtros.activo = true;
    }
    
    console.log('Cargando sedes con filtros:', filtros);
    
    this.sedeService.obtenerSedes(0, 100, filtros)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (sedes) => {
          // El backend ahora devuelve correctamente el campo activo
          this.sedes = sedes;
          this.isLoading = false;
          console.log('Sedes cargadas desde backend:', this.sedes.length, 'registros');
        },
        error: (error) => {
          console.error('Error al cargar sedes:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al cargar las sedes';
          this.isLoading = false;
        }
      });
  }


  get filteredSedes() {
    let filtered = this.sedes;
    
    // Filtrar por búsqueda (solo en frontend para búsqueda en tiempo real)
    if (this.searchTerm.trim()) {
      filtered = filtered.filter(s =>
        s.nombre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        s.ciudad.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        s.direccion.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }
    
    // El filtro por estado ahora se hace en el backend al cargar
    // Pero mantenemos filtro local para inactivas
    if (this.filtroEstado === 'inactivas') {
      filtered = filtered.filter(s => !s.activo);
    }
    
    return filtered;
  }

  get activeSedes() {
    return this.sedes.filter(s => s.activo).length;
  }

  get totalEmpleados() {
    // Campo no disponible en backend
    return 0;
  }

  get totalPaquetes() {
    // Campo no disponible en backend
    return 0;
  }

  selectSede(sede: Sede) {
    const sedeId = sede.id_sede;
    const selectedId = this.selectedSede?.id_sede;
    this.selectedSede = selectedId === sedeId ? null : sede;
  }

  onMapHover(sede: Sede | null) {
    this.hoveredSede = sede;
  }

  openNewSedeModal(): void {
    this.isEditMode = false;
    this.selectedSede = null;
    
    // Intentar recuperar datos guardados
    const savedData = this.formStorage.getFormData('sede_nueva');
    
    if (savedData) {
      this.sedeForm = savedData;
      console.log('Datos del formulario de sede recuperados');
    } else {
      this.sedeForm = {
        nombre: '',
        ciudad: '',
        direccion: '',
        telefono: ''
      };
    }
    this.showModal = true;
  }

  openEditSedeModal(sede: Sede) {
    this.isEditMode = true;
    this.sedeForm = { ...sede };
    this.showModal = true;
  }

  closeModal(): void {
    // Guardar datos del formulario antes de cerrar si no está en modo edición
    if (!this.isEditMode) {
      this.formStorage.saveFormData('sede_nueva', this.sedeForm);
    }
    this.showModal = false;
    this.selectedSede = null;
  }

  saveSede() {
    this.isLoading = true;
    this.errorMessage = '';
    const currentUser = this.authService.getCurrentUser();
    
    if (this.isEditMode && this.sedeForm.id_sede) {
      // Actualizar sede existente
      if (!currentUser?.id_usuario) {
        this.errorMessage = 'Usuario no autenticado';
        this.isLoading = false;
        return;
      }

      // Limpiar datos: remover campos que no deben enviarse
      const { id_sede, fecha_creacion, fecha_actualizacion, creado_por, ...updateData } = this.sedeForm;
      
      this.sedeService.actualizarSede(this.sedeForm.id_sede, updateData, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          this.cargarSedes();
          this.closeModal();
          this.isLoading = false;
          this.errorMessage = '';
        },
        error: (error) => {
          console.error('Error al actualizar sede:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al actualizar la sede';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nueva sede
      if (!currentUser?.id_usuario) {
        this.errorMessage = 'Usuario no autenticado';
        this.isLoading = false;
        return;
      }

      // Limpiar datos: remover campos que no deben enviarse en creación
      const { id_sede, fecha_creacion, fecha_actualizacion, actualizado_por, creado_por, ...newSede } = this.sedeForm as any;
      
      this.sedeService.crearSede(newSede, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          // Limpiar datos guardados después de guardar exitosamente
          this.formStorage.clearFormData('sede_nueva');
          this.cargarSedes();
          this.closeModal();
          this.isLoading = false;
          this.errorMessage = '';
        },
        error: (error) => {
          console.error('Error al crear sede:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al crear la sede';
          this.isLoading = false;
        }
      });
    }
  }

  deleteSede(id: string | undefined) {
    if (!id) return;
    
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser?.id_usuario) {
      this.errorMessage = 'Usuario no autenticado';
      return;
    }
    
    if (confirm('¿Estás seguro de eliminar esta sede?')) {
      this.isLoading = true;
      this.sedeService.eliminarSede(id, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          this.cargarSedes();
          const selectedId = this.selectedSede?.id_sede;
          if (selectedId === id) {
            this.selectedSede = null;
          }
          this.errorMessage = '';
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al eliminar sede:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al eliminar la sede';
          this.isLoading = false;
        }
      });
    }
  }

  exportarDatos(): void {
    const csv = this.convertirACSV(this.filteredSedes);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `sedes_${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  private convertirACSV(data: any[]): string {
    if (data.length === 0) return '';
    
    const headers = ['ID', 'Nombre', 'Ciudad', 'Dirección', 'Teléfono', 'Estado'];
    const rows = data.map(s => [
      s.id_sede?.substring(0, 8) || '',
      s.nombre,
      s.ciudad,
      s.direccion,
      s.telefono,
      s.activo ? 'Activa' : 'Inactiva'
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  toggleFiltros(): void {
    this.showFiltros = !this.showFiltros;
  }

  aplicarFiltros(): void {
    this.showFiltros = false;
    // Recargar datos con los nuevos filtros
    console.log('Aplicando filtros, recargando desde backend...');
    this.cargarSedes();
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'todos';
    this.searchTerm = '';
    // Recargar datos sin filtros
    console.log('Limpiando filtros, recargando desde backend...');
    this.cargarSedes();
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
