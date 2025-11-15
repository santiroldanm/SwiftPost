import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { EmpleadoService, Empleado } from '../../core/services/empleado.service';
import { AuthService } from '../../core/services/auth.service';
import { TipoDocumentoService, TipoDocumento } from '../../core/services/tipo-documento.service';
import { SedeService, Sede } from '../../core/services/sede.service';

@Component({
  selector: 'app-empleados',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './empleados.component.html',
  styleUrls: ['./empleados.component.scss']
})
export class EmpleadosComponent implements OnInit {
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
    numero_documento: '',
    id_tipo_documento: '',
    usuario_id: '',
    cargo: '',
    salario: 0,
    fecha_contratacion: '',
    id_sede: ''
  };

  employees: Empleado[] = [];
  tiposDocumento: TipoDocumento[] = [];
  sedes: Sede[] = [];

  constructor(
    private empleadoService: EmpleadoService,
    private authService: AuthService,
    private tipoDocumentoService: TipoDocumentoService,
    private sedeService: SedeService
  ) {}

  ngOnInit(): void {
    this.cargarEmpleados();
    this.cargarTiposDocumento();
    this.cargarSedes();
  }

  cargarEmpleados(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    this.empleadoService.obtenerEmpleados(0, 100).subscribe({
      next: (empleados) => {
        this.employees = empleados;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar empleados:', error);
        this.errorMessage = 'Error al cargar los empleados';
        this.isLoading = false;
      }
    });
  }

  cargarTiposDocumento(): void {
    this.tipoDocumentoService.obtenerTiposDocumentoActivos(0, 100).subscribe({
      next: (tipos) => {
        this.tiposDocumento = tipos;
      },
      error: (error) => console.error('Error al cargar tipos de documento:', error)
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

  get filteredEmployees() {
    let filtered = this.employees;
    
    // Filtrar por búsqueda
    if (this.searchTerm.trim()) {
      filtered = filtered.filter(e => {
        const nombreCompleto = `${e.primer_nombre} ${e.segundo_nombre || ''} ${e.primer_apellido} ${e.segundo_apellido || ''}`.toLowerCase();
        return nombreCompleto.includes(this.searchTerm.toLowerCase()) ||
               e.numero_documento?.includes(this.searchTerm) ||
               e.cargo?.toLowerCase().includes(this.searchTerm.toLowerCase());
      });
    }
    
    // Filtrar por cargo
    if (this.filtroCargo !== 'todos') {
      filtered = filtered.filter(e => e.cargo === this.filtroCargo);
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
    this.employeeForm = {
      primer_nombre: '',
      segundo_nombre: '',
      primer_apellido: '',
      segundo_apellido: '',
      numero_documento: '',
      id_tipo_documento: '',
      usuario_id: currentUser?.id_usuario || '',
      cargo: '',
      salario: 0,
      fecha_contratacion: today,
      id_sede: ''
    };
    this.showModal = true;
  }

  openEditEmployeeModal(employee: Empleado) {
    this.isEditMode = true;
    this.employeeForm = { ...employee };
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
  }

  saveEmployee() {
    this.isLoading = true;
    const currentUser = this.authService.getCurrentUser();
    
    if (this.isEditMode && this.employeeForm.id_empleado) {
      // Actualizar empleado existente
      const updateData = {
        ...this.employeeForm,
        actualizado_por: currentUser?.id_usuario
      };
      
      this.empleadoService.actualizarEmpleado(this.employeeForm.id_empleado, updateData).subscribe({
        next: () => {
          this.cargarEmpleados();
          this.closeModal();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al actualizar empleado:', error);
          this.errorMessage = 'Error al actualizar el empleado';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nuevo empleado
      this.empleadoService.crearEmpleado(this.employeeForm).subscribe({
        next: () => {
          this.cargarEmpleados();
          this.closeModal();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al crear empleado:', error);
          this.errorMessage = 'Error al crear el empleado';
          this.isLoading = false;
        }
      });
    }
  }

  deleteEmployee(id: string | undefined) {
    if (!id) return;
    
    if (confirm('¿Estás seguro de eliminar este empleado?')) {
      this.empleadoService.eliminarEmpleado(id).subscribe({
        next: () => {
          this.cargarEmpleados();
        },
        error: (error) => {
          console.error('Error al eliminar empleado:', error);
          this.errorMessage = 'Error al eliminar el empleado';
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
    
    const headers = ['ID', 'Nombre Completo', 'Documento', 'Cargo', 'Salario', 'Fecha Contratación'];
    const rows = data.map(e => [
      e.id_empleado?.substring(0, 8) || '',
      this.getNombreCompleto(e),
      e.numero_documento,
      e.cargo,
      e.salario,
      e.fecha_contratacion
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
}
