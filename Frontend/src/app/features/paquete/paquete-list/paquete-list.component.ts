import { Component, OnInit, AfterViewInit, DestroyRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { PaqueteService, Paquete } from '../../../core/services/paquete.service';
import { AuthService } from '../../../core/services/auth.service';
import { ClienteService, Cliente } from '../../../core/services/cliente.service';
import { FormStorageService } from '../../../core/services/form-storage.service';

@Component({
  selector: 'app-paquete-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './paquete-list.component.html',
  styleUrls: ['./paquete-list.component.scss']
})
export class PaqueteListComponent implements OnInit, AfterViewInit {
  private destroyRef = inject(DestroyRef);
  searchTerm = '';
  selectedCategory = 'all';
  showModal = false;
  showFiltros = false;
  isEditMode = false;
  isLoading = false;
  errorMessage = '';
  filtroEstado = 'todos';
  filtroFragilidad = 'todos';

  paqueteForm: Paquete & { id_cliente?: string } = {
    peso: 0,
    tamaño: '',
    fragilidad: 'normal',
    contenido: '',
    tipo: '',
    valor_declarado: 0,
    estado: 'registrado'
  };

  paquetes: Paquete[] = [];
  clientes: Cliente[] = [];

  constructor(
    private paqueteService: PaqueteService,
    private authService: AuthService,
    private clienteService: ClienteService,
    private route: ActivatedRoute,
    private formStorage: FormStorageService
  ) {}

  ngOnInit(): void {
    this.cargarPaquetes();
    this.cargarClientes();
    
    // Escuchar cambios de ruta para recargar datos
    this.route.params
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.cargarPaquetes();
      });
  }

  cargarClientes(): void {
    this.clienteService.obtenerClientes(0, 100)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (clientes) => {
          this.clientes = Array.isArray(clientes) ? clientes : [];
        },
        error: (error) => console.error('Error al cargar clientes:', error)
      });
  }

  ngAfterViewInit(): void {
    // Ya no es necesario el setTimeout, Angular maneja esto automáticamente
  }

  cargarPaquetes(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    // Construir filtros para el backend
    const filtros: any = {};
    if (this.filtroEstado !== 'todos') {
      filtros.estado = this.filtroEstado;
    }
    if (this.filtroFragilidad !== 'todos') {
      filtros.fragilidad = this.filtroFragilidad;
    }
    if (this.searchTerm.trim()) {
      filtros.search = this.searchTerm.trim();
    }
    
    console.log('Cargando paquetes con filtros:', filtros);
    
    this.paqueteService.obtenerPaquetes(0, 50, filtros)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (paquetes) => {
          this.paquetes = paquetes;
          this.isLoading = false;
          console.log('Paquetes cargados desde backend:', this.paquetes.length, 'registros');
        },
        error: (error) => {
          console.error('Error al cargar paquetes:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al cargar los paquetes';
          this.isLoading = false;
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
    
    // Intentar recuperar datos guardados
    const savedData = this.formStorage.getFormData('paquete_nuevo');
    
    if (savedData) {
      this.paqueteForm = savedData;
      console.log('Datos del formulario de paquete recuperados');
    } else {
      this.paqueteForm = {
        peso: 1, // Debe ser > 0
        tamaño: 'pequeño',
        fragilidad: 'baja',
        contenido: '',
        tipo: 'normal',
        valor_declarado: 0,
        estado: 'registrado',
        id_cliente: ''
      };
    }
    this.showModal = true;
  }

  openEditPaqueteModal(paquete: Paquete) {
    this.isEditMode = true;
    this.paqueteForm = { ...paquete };
    this.showModal = true;
  }

  closeModal() {
    // Guardar datos del formulario antes de cerrar si no está en modo edición
    if (!this.isEditMode) {
      this.formStorage.saveFormData('paquete_nuevo', this.paqueteForm);
    }
    this.showModal = false;
  }

  savePaquete() {
    this.isLoading = true;
    const currentUser = this.authService.getCurrentUser();
    
    if (this.isEditMode && this.paqueteForm.id_paquete) {
      // Actualizar paquete existente
      if (!currentUser?.id_usuario) {
        this.errorMessage = 'Usuario no autenticado';
        this.isLoading = false;
        return;
      }
      
      // Normalizar valores a minúsculas según el backend
      const updateData: any = {};
      if (this.paqueteForm.peso !== undefined && this.paqueteForm.peso !== null) updateData.peso = Number(this.paqueteForm.peso);
      if (this.paqueteForm.tamaño) updateData.tamaño = this.paqueteForm.tamaño.toLowerCase().trim();
      if (this.paqueteForm.fragilidad) updateData.fragilidad = this.paqueteForm.fragilidad.toLowerCase().trim();
      if (this.paqueteForm.contenido) updateData.contenido = this.paqueteForm.contenido.trim();
      if (this.paqueteForm.tipo) updateData.tipo = this.paqueteForm.tipo.toLowerCase().trim();
      if (this.paqueteForm.valor_declarado !== undefined && this.paqueteForm.valor_declarado !== null) updateData.valor_declarado = Number(this.paqueteForm.valor_declarado);
      if (this.paqueteForm.estado) updateData.estado = this.paqueteForm.estado.toLowerCase().trim();
      
      const cleanData = updateData;
      
      this.paqueteService.actualizarPaquete(
        this.paqueteForm.id_paquete, 
        cleanData, 
        currentUser.id_usuario
      )
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: (paquete) => {
          this.cargarPaquetes();
          this.closeModal();
          this.isLoading = false;
          this.errorMessage = '';
        },
        error: (error) => {
          console.error('Error al actualizar paquete:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al actualizar el paquete';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nuevo paquete
      if (!currentUser?.id_usuario) {
        this.errorMessage = 'Usuario no autenticado';
        this.isLoading = false;
        return;
      }
      
      if (!this.paqueteForm.id_cliente) {
        this.errorMessage = 'Debe seleccionar un cliente';
        this.isLoading = false;
        return;
      }
      
      // Validar campos requeridos
      if (!this.paqueteForm.peso || this.paqueteForm.peso <= 0) {
        this.errorMessage = 'El peso debe ser mayor a 0';
        this.isLoading = false;
        return;
      }
      if (!this.paqueteForm.tamaño || !this.paqueteForm.fragilidad || !this.paqueteForm.contenido || !this.paqueteForm.tipo) {
        this.errorMessage = 'Por favor complete todos los campos requeridos';
        this.isLoading = false;
        return;
      }

      // Normalizar valores a minúsculas según el backend
      const newPaquete = {
        peso: Number(this.paqueteForm.peso),
        tamaño: this.paqueteForm.tamaño.toLowerCase().trim(),
        fragilidad: this.paqueteForm.fragilidad.toLowerCase().trim(),
        contenido: this.paqueteForm.contenido.trim(),
        tipo: this.paqueteForm.tipo.toLowerCase().trim(),
        valor_declarado: Number(this.paqueteForm.valor_declarado || 0),
        estado: (this.paqueteForm.estado || 'registrado').toLowerCase().trim()
      };

      // El backend acepta id_cliente en el body o como query parameter
      // Lo enviamos como query parameter para mayor claridad
      console.log('Creando paquete con datos:', newPaquete);
      console.log('ID Cliente:', this.paqueteForm.id_cliente);
      console.log('Creado por:', currentUser.id_usuario);
      
      this.paqueteService.crearPaquete(newPaquete, currentUser.id_usuario, this.paqueteForm.id_cliente)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: (paquete) => {
          console.log('Paquete creado exitosamente:', paquete);
          // Limpiar datos guardados después de guardar exitosamente
          this.formStorage.clearFormData('paquete_nuevo');
          this.cargarPaquetes();
          this.closeModal();
          this.isLoading = false;
          this.errorMessage = '';
        },
        error: (error) => {
          console.error('Error al crear paquete:', error);
          console.error('Detalles del error:', error.error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al crear el paquete';
          this.isLoading = false;
        }
      });
    }
  }

  deletePaquete(id: string | undefined) {
    if (!id) return;
    
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser?.id_usuario) {
      this.errorMessage = 'Usuario no autenticado';
      return;
    }
    
    if (confirm('¿Estás seguro de eliminar este paquete?')) {
      this.isLoading = true;
      this.paqueteService.eliminarPaquete(id, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          this.cargarPaquetes();
          this.isLoading = false;
          this.errorMessage = '';
        },
        error: (error) => {
          console.error('Error al eliminar paquete:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al eliminar el paquete';
          this.isLoading = false;
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

  get filteredPaquetes(): Paquete[] {
    // La filtración ahora se hace en el backend
    return this.paquetes;
  }

  toggleFiltros(): void {
    this.showFiltros = !this.showFiltros;
  }

  aplicarFiltros(): void {
    this.showFiltros = false;
    // Recargar datos con los nuevos filtros
    console.log('Aplicando filtros, recargando desde backend...');
    this.cargarPaquetes();
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'todos';
    this.filtroFragilidad = 'todos';
    this.searchTerm = '';
    // Recargar datos sin filtros
    console.log('Limpiando filtros, recargando desde backend...');
    this.cargarPaquetes();
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
