import { Component, OnInit, AfterViewInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { PaqueteService, Paquete } from '../../../core/services/paquete.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-paquete-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [PaqueteService, AuthService],
  templateUrl: './paquete-list.component.html',
  styleUrls: ['./paquete-list.component.scss'],
  changeDetection: ChangeDetectionStrategy.Default
})
export class PaqueteListComponent implements OnInit, AfterViewInit {
  searchTerm = '';
  selectedCategory = 'all';
  showModal = false;
  showFiltros = false;
  isEditMode = false;
  isLoading = false;
  errorMessage = '';
  filtroEstado = 'todos';
  filtroFragilidad = 'todos';

  paqueteForm: Paquete = {
    peso: 0,
    tamaño: '',
    fragilidad: 'No',
    contenido: '',
    tipo: '',
    valor_declarado: 0,
    estado: 'Registrado'
  };

  paquetes: Paquete[] = [];

  constructor(
    private paqueteService: PaqueteService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.cargarPaquetes();
    
    // Escuchar cambios de ruta para recargar datos
    this.route.params.subscribe(() => {
      this.cargarPaquetes();
    });
  }

  ngAfterViewInit(): void {
    // Forzar recarga de datos después de que la vista esté inicializada
    setTimeout(() => {
      this.cargarPaquetes();
    }, 100);
  }

  cargarPaquetes(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    this.paqueteService.obtenerPaquetes(0, 50).subscribe({
      next: (paquetes) => {
        this.paquetes = paquetes;
        this.isLoading = false;
        this.cdr.detectChanges(); // Forzar actualización de la vista
      },
      error: (error) => {
        console.error('Error al cargar paquetes:', error);
        this.errorMessage = 'Error al cargar los paquetes';
        this.isLoading = false;
        this.cdr.detectChanges(); // Forzar actualización de la vista
      }
    });
  }

  getStatusClass(status: string | undefined): string {
    if (!status) return 'default';
    const statusMap: { [key: string]: string } = {
      'Entregado': 'success',
      'En tránsito': 'warning',
      'En Tránsito': 'warning',
      'Registrado': 'info',
      'No entregado': 'danger',
      'Activo': 'success',
      'Inactivo': 'danger'
    };
    return statusMap[status] || 'default';
  }

  openNewPaqueteModal() {
    this.isEditMode = false;
    this.paqueteForm = {
      peso: 0,
      tamaño: '',
      fragilidad: 'No',
      contenido: '',
      tipo: '',
      valor_declarado: 0,
      estado: 'Registrado'
    };
    this.showModal = true;
  }

  openEditPaqueteModal(paquete: Paquete) {
    this.isEditMode = true;
    this.paqueteForm = { ...paquete };
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
  }

  savePaquete() {
    this.isLoading = true;
    const currentUser = this.authService.getCurrentUser();
    
    if (this.isEditMode && this.paqueteForm.id_paquete) {
      // Actualizar paquete existente
      const updateData = {
        ...this.paqueteForm,
        actualizado_por: currentUser?.id_usuario
      };
      
      this.paqueteService.actualizarPaquete(this.paqueteForm.id_paquete, updateData).subscribe({
        next: (paquete) => {
          this.cargarPaquetes();
          this.closeModal();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al actualizar paquete:', error);
          this.errorMessage = 'Error al actualizar el paquete';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nuevo paquete
      const newPaquete = {
        ...this.paqueteForm,
        creado_por: currentUser?.id_usuario
      };
      
      this.paqueteService.crearPaquete(newPaquete).subscribe({
        next: (paquete) => {
          this.cargarPaquetes();
          this.closeModal();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al crear paquete:', error);
          this.errorMessage = 'Error al crear el paquete';
          this.isLoading = false;
        }
      });
    }
  }

  deletePaquete(id: string | undefined) {
    if (!id) return;
    
    if (confirm('¿Estás seguro de eliminar este paquete?')) {
      this.paqueteService.eliminarPaquete(id).subscribe({
        next: () => {
          this.cargarPaquetes();
        },
        error: (error) => {
          console.error('Error al eliminar paquete:', error);
          this.errorMessage = 'Error al eliminar el paquete';
        }
      });
    }
  }

  exportarDatos(): void {
    const csv = this.convertirACSV(this.paquetes);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `paquetes_${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  private convertirACSV(data: any[]): string {
    if (data.length === 0) return '';
    
    const headers = ['ID', 'Peso', 'Tamaño', 'Fragilidad', 'Contenido', 'Tipo', 'Valor Declarado', 'Estado'];
    const rows = data.map(p => [
      p.id_paquete?.substring(0, 8) || '',
      p.peso,
      p['tamaño'] || p.tamaño,
      p.fragilidad,
      p.contenido,
      p.tipo,
      p.valor_declarado || 0,
      p.estado
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  get filteredPaquetes() {
    let filtered = this.paquetes;
    
    // Filtrar por búsqueda
    if (this.searchTerm.trim()) {
      filtered = filtered.filter(p =>
        p.contenido?.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        p.tipo?.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        p.estado?.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }
    
    // Filtrar por estado
    if (this.filtroEstado !== 'todos') {
      filtered = filtered.filter(p => p.estado === this.filtroEstado);
    }
    
    // Filtrar por fragilidad
    if (this.filtroFragilidad !== 'todos') {
      filtered = filtered.filter(p => p.fragilidad === this.filtroFragilidad);
    }
    
    return filtered;
  }

  toggleFiltros(): void {
    this.showFiltros = !this.showFiltros;
  }

  aplicarFiltros(): void {
    this.showFiltros = false;
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'todos';
    this.filtroFragilidad = 'todos';
    this.searchTerm = '';
  }
}
