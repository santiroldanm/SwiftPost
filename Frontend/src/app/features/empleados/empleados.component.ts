import { Component, OnInit, DestroyRef, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EmpleadoService, Empleado } from '../../core/services/empleado.service';
import { AuthService } from '../../core/services/auth.service';
import { TipoDocumentoService, TipoDocumento } from '../../core/services/tipo-documento.service';
import { SedeService, Sede } from '../../core/services/sede.service';
import { FormStorageService } from '../../core/services/form-storage.service';

@Component({
  selector: 'app-empleados',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './empleados.component.html',
  styleUrls: ['./empleados.component.scss']
})
export class EmpleadosComponent implements OnInit {
  private destroyRef = inject(DestroyRef);
  searchTerm = '';
  showModal = false;
  showFiltros = false;
  isEditMode = false;
  isLoading = false;
  errorMessage = '';
  filtroCargo = 'todos';
  
  employeeForm: Empleado = {
    primer_nombre: '',
    primer_apellido: '',
    documento: '',
    id_tipo_documento: '',
    usuario_id: '',
    tipo_empleado: '',
    salario: 0,
    fecha_ingreso: '',
    fecha_nacimiento: '',
    telefono: '',
    correo: '',
    direccion: '',
    id_sede: ''
  };

  employees: Empleado[] = [];
  tiposDocumento: TipoDocumento[] = [];
  sedes: Sede[] = [];

  constructor(
    private empleadoService: EmpleadoService,
    private authService: AuthService,
    private tipoDocumentoService: TipoDocumentoService,
    private sedeService: SedeService,
    private formStorage: FormStorageService
  ) {}

  ngOnInit(): void {
    this.cargarEmpleados();
    this.cargarTiposDocumento();
    this.cargarSedes();
  }

  cargarEmpleados(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    this.empleadoService.obtenerEmpleados(0, 100)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (empleados) => {
          // Filtrar solo empleados activos
          this.employees = empleados.filter(e => e.activo !== false);
          this.isLoading = false;
          console.log('Empleados activos cargados:', this.employees.length);
        },
        error: (error) => {
          console.error('Error al cargar empleados:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al cargar los empleados';
          this.isLoading = false;
        }
      });
  }

  cargarTiposDocumento(): void {
    this.tipoDocumentoService.obtenerTiposDocumentoActivos(0, 100)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tipos) => {
          this.tiposDocumento = tipos;
        },
        error: (error) => console.error('Error al cargar tipos de documento:', error)
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

  get filteredEmployees() {
    let filtered = this.employees;
    
    // Filtrar por búsqueda
    if (this.searchTerm.trim()) {
      filtered = filtered.filter(e => {
        const nombreCompleto = `${e.primer_nombre} ${e.segundo_nombre || ''} ${e.primer_apellido} ${e.segundo_apellido || ''}`.toLowerCase();
        return nombreCompleto.includes(this.searchTerm.toLowerCase()) ||
               e.documento?.includes(this.searchTerm) ||
               e.tipo_empleado?.toLowerCase().includes(this.searchTerm.toLowerCase());
      });
    }
    
    // Filtrar por tipo de empleado
    if (this.filtroCargo !== 'todos') {
      // Mapear valores del filtro a los valores del backend
      const tipoEmpleadoMap: { [key: string]: string } = {
        'Mensajero': 'mensajero',
        'Mensajera': 'mensajero',
        'Administrador': 'logistico',
        'Administradora': 'logistico',
        'Operador Logistico': 'logistico',
        'Secretario': 'secretario',
        'Secretaria': 'secretario'
      };
      const tipoEmpleado = tipoEmpleadoMap[this.filtroCargo] || this.filtroCargo.toLowerCase();
      filtered = filtered.filter(e => e.tipo_empleado?.toLowerCase() === tipoEmpleado);
    }
    
    return filtered;
  }

  getNombreCompleto(empleado: Empleado): string {
    return `${empleado.primer_nombre} ${empleado.segundo_nombre || ''} ${empleado.primer_apellido} ${empleado.segundo_apellido || ''}`.trim();
  }

  openNewEmployeeModal() {
    this.isEditMode = false;
    const today = new Date().toISOString().split('T')[0];
    const currentUser = this.authService.getCurrentUser();
    
    // Intentar recuperar datos guardados
    const savedData = this.formStorage.getFormData('empleado_nuevo');
    
    if (savedData) {
      this.employeeForm = savedData;
      console.log('Datos del formulario recuperados');
    } else {
      this.employeeForm = {
        primer_nombre: '',
        segundo_nombre: '',
        primer_apellido: '',
        segundo_apellido: '',
        documento: '',
        id_tipo_documento: '',
        usuario_id: currentUser?.id_usuario || '',
        tipo_empleado: '',
        salario: 0,
        fecha_ingreso: today,
        fecha_nacimiento: '',
        telefono: '',
        correo: '',
        direccion: '',
        id_sede: ''
      };
    }
    this.showModal = true;
  }

  openEditEmployeeModal(employee: Empleado) {
    this.isEditMode = true;
    this.employeeForm = { ...employee };
    this.showModal = true;
  }

  closeModal() {
    // Guardar datos del formulario antes de cerrar si no está en modo edición
    if (!this.isEditMode) {
      this.formStorage.saveFormData('empleado_nuevo', this.employeeForm);
    }
    this.showModal = false;
  }

  saveEmployee() {
    this.isLoading = true;
    this.errorMessage = '';
    const currentUser = this.authService.getCurrentUser();
    
    if (this.isEditMode && this.employeeForm.id_empleado) {
      // Actualizar empleado existente
      if (!currentUser?.id_usuario) {
        this.errorMessage = 'Usuario no autenticado';
        this.isLoading = false;
        return;
      }

      // Limpiar datos: remover campos que no deben enviarse
      const { id_empleado, fecha_creacion, fecha_actualizacion, creado_por, actualizado_por, documento, ...restData } = this.employeeForm as any;
      
      // El backend espera numero_documento en EmpleadoUpdate, no documento
      const updateData: any = { ...restData };
      if (documento) {
        updateData.numero_documento = documento;
      }
      
      this.empleadoService.actualizarEmpleado(this.employeeForm.id_empleado, updateData, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          this.cargarEmpleados();
          this.closeModal();
          this.isLoading = false;
          this.errorMessage = '';
        },
        error: (error) => {
          console.error('Error al actualizar empleado:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al actualizar el empleado';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nuevo empleado
      if (!currentUser?.id_usuario) {
        this.errorMessage = 'Usuario no autenticado';
        this.isLoading = false;
        return;
      }

      // Validar campos requeridos
      if (!this.employeeForm.documento || !this.employeeForm.tipo_empleado || 
          !this.employeeForm.fecha_nacimiento || !this.employeeForm.telefono || 
          !this.employeeForm.correo || !this.employeeForm.direccion || 
          !this.employeeForm.fecha_ingreso) {
        this.errorMessage = 'Por favor complete todos los campos requeridos';
        this.isLoading = false;
        return;
      }

      // Limpiar datos: remover campos que no deben enviarse en creación
      const { id_empleado, fecha_creacion, fecha_actualizacion, actualizado_por, creado_por, ...newEmployee } = this.employeeForm as any;
      
      this.empleadoService.crearEmpleado(newEmployee, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          // Limpiar datos guardados después de guardar exitosamente
          this.formStorage.clearFormData('empleado_nuevo');
          this.cargarEmpleados();
          this.closeModal();
          this.isLoading = false;
          this.errorMessage = '';
        },
        error: (error) => {
          console.error('Error al crear empleado:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al crear el empleado';
          this.isLoading = false;
        }
      });
    }
  }

  deleteEmployee(id: string | undefined) {
    if (!id) return;
    
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser?.id_usuario) {
      this.errorMessage = 'Usuario no autenticado';
      return;
    }
    
    if (confirm('¿Estás seguro de eliminar este empleado?')) {
      this.isLoading = true;
      this.empleadoService.eliminarEmpleado(id, currentUser.id_usuario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
        next: () => {
          this.cargarEmpleados();
          this.errorMessage = '';
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al eliminar empleado:', error);
          this.errorMessage = this.getErrorMessage(error) || 'Error al eliminar el empleado';
        }
      });
    }
  }

  exportarDatos(): void {
    const csv = this.convertirACSV(this.filteredEmployees);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `empleados_${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  private convertirACSV(data: any[]): string {
    if (data.length === 0) return '';
    
    const headers = ['ID', 'Nombre Completo', 'Documento', 'Tipo Empleado', 'Salario', 'Fecha Ingreso'];
    const rows = data.map(e => [
      e.id_empleado?.substring(0, 8) || '',
      this.getNombreCompleto(e),
      e.documento,
      e.tipo_empleado,
      e.salario,
      e.fecha_ingreso
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
    this.filtroCargo = 'todos';
    this.searchTerm = '';
  }

  private getErrorMessage(error: any): string {
    const errorDetail = error?.error?.detail || error?.error?.message || error?.message;
    if (typeof errorDetail === 'string') {
      return errorDetail;
    } else if (errorDetail && typeof errorDetail === 'object') {
      // Si es un objeto, intentar extraer el mensaje o convertir a JSON
      if (Array.isArray(errorDetail)) {
        return errorDetail.join(', ');
      }
      return JSON.stringify(errorDetail);
    }
    return 'Error desconocido';
  }
}
