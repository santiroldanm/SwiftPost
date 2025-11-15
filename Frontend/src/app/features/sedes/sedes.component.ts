import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { SedeService, Sede } from '../../core/services/sede.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-sedes',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './sedes.component.html',
  styleUrls: ['./sedes.component.scss']
})
export class SedesComponent implements OnInit {
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
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.cargarSedes();
  }

  cargarSedes(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    this.sedeService.obtenerSedes(0, 100).subscribe({
      next: (sedes) => {
        // Asegurar que todas las sedes tengan el campo activo definido
        this.sedes = sedes.map(sede => ({
          ...sede,
          activo: sede.activo !== undefined ? sede.activo : true
        }));
        console.log('Sedes cargadas:', this.sedes); // Debug
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar sedes:', error);
        this.errorMessage = 'Error al cargar las sedes';
        this.isLoading = false;
      }
    });
  }


  get filteredSedes() {
    let filtered = this.sedes;
    
    // Filtrar por búsqueda
    if (this.searchTerm.trim()) {
      filtered = filtered.filter(s =>
        s.nombre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        s.ciudad.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        s.direccion.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }
    
    // Filtrar por estado
    if (this.filtroEstado === 'activas') {
      filtered = filtered.filter(s => s.activo);
    } else if (this.filtroEstado === 'inactivas') {
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

  openNewSedeModal() {
    this.isEditMode = false;
    this.sedeForm = {
      nombre: '',
      ciudad: '',
      direccion: '',
      telefono: ''
    };
    this.showModal = true;
  }

  openEditSedeModal(sede: Sede) {
    this.isEditMode = true;
    this.sedeForm = { ...sede };
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
  }

  saveSede() {
    this.isLoading = true;
    const currentUser = this.authService.getCurrentUser();
    
    if (this.isEditMode && this.sedeForm.id_sede) {
      // Actualizar sede existente
      const updateData = {
        ...this.sedeForm,
        actualizado_por: currentUser?.id_usuario
      };
      
      this.sedeService.actualizarSede(this.sedeForm.id_sede, updateData).subscribe({
        next: () => {
          this.cargarSedes();
          this.closeModal();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al actualizar sede:', error);
          this.errorMessage = 'Error al actualizar la sede';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nueva sede
      const newSede = {
        ...this.sedeForm,
        creado_por: currentUser?.id_usuario
      };
      
      this.sedeService.crearSede(newSede).subscribe({
        next: () => {
          this.cargarSedes();
          this.closeModal();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al crear sede:', error);
          this.errorMessage = 'Error al crear la sede';
          this.isLoading = false;
        }
      });
    }
  }

  deleteSede(id: string | undefined) {
    if (!id) return;
    
    if (confirm('¿Estás seguro de eliminar esta sede?')) {
      this.sedeService.eliminarSede(id).subscribe({
        next: () => {
          this.cargarSedes();
          const selectedId = this.selectedSede?.id_sede;
          if (selectedId === id) {
            this.selectedSede = null;
          }
        },
        error: (error) => {
          console.error('Error al eliminar sede:', error);
          this.errorMessage = 'Error al eliminar la sede';
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
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'todos';
    this.searchTerm = '';
  }
}
