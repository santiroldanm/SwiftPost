import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DetalleEntregaService, DetalleEntrega } from '../../core/services/detalle-entrega.service';
import { SedeService, Sede } from '../../core/services/sede.service';
import { ClienteService, Cliente } from '../../core/services/cliente.service';
import { PaqueteService, Paquete } from '../../core/services/paquete.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-entregas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './entregas.component.html',
  styleUrls: ['./entregas.component.scss']
})
export class EntregasComponent implements OnInit {
  entregas: any[] = [];
  sedes: Sede[] = []; // Todas las sedes para mostrar nombres
  sedesActivas: Sede[] = []; // Solo sedes activas para el formulario
  clientes: Cliente[] = [];
  paquetes: Paquete[] = [];
  
  filtroEstado: string = 'todos';
  searchTerm: string = '';
  cargando: boolean = false;
  error: string = '';
  
  // Modal
  mostrarModal: boolean = false;
  modoEdicion: boolean = false;
  entregaSeleccionada: DetalleEntrega | null = null;
  
  // Formulario
  formulario: DetalleEntrega = {
    id_sede_remitente: '',
    id_sede_receptora: '',
    id_paquete: '',
    id_cliente_remitente: '',
    id_cliente_receptor: '',
    estado_envio: 'Pendiente',
    fecha_envio: new Date().toISOString().split('T')[0],
    observaciones: ''
  };

  constructor(
    private detalleEntregaService: DetalleEntregaService,
    private sedeService: SedeService,
    private clienteService: ClienteService,
    private paqueteService: PaqueteService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.cargarEntregas();
    this.cargarSedes();
    this.cargarClientes();
    this.cargarPaquetes();
  }

  cargarEntregas(): void {
    this.cargando = true;
    this.error = '';
    
    // Construir filtros para el backend
    const filtros: any = {};
    if (this.filtroEstado !== 'todos') {
      filtros.estado = this.filtroEstado;
    }
    if (this.searchTerm.trim()) {
      filtros.search = this.searchTerm.trim();
    }
    
    console.log('Cargando entregas con filtros:', filtros);
    
    this.detalleEntregaService.obtenerDetallesEntrega(0, 100, filtros).subscribe({
      next: (response) => {
        this.entregas = response?.detalles || [];
        this.cargando = false;
        console.log('Entregas cargadas desde backend:', this.entregas.length, 'registros');
      },
      error: (err) => {
        this.error = 'Error al cargar entregas';
        console.error('Error:', err);
        this.cargando = false;
      }
    });
  }

  cargarSedes(): void {
    // Cargar todas las sedes para mostrar nombres en la tabla
    this.sedeService.obtenerSedes(0, 1000).subscribe({
      next: (sedes) => {
        this.sedes = Array.isArray(sedes) ? sedes : [];
        // Filtrar solo las activas para el formulario
        this.sedesActivas = this.sedes.filter(s => s.activo !== false);
        console.log('Sedes cargadas:', this.sedes.length, '| Activas:', this.sedesActivas.length);
      },
      error: (err) => console.error('Error al cargar sedes:', err)
    });
  }

  cargarClientes(): void {
    // Cargar solo clientes activos
    this.clienteService.obtenerClientesActivos(0, 100).subscribe({
      next: (clientes) => {
        this.clientes = Array.isArray(clientes) ? clientes : [];
        console.log('Clientes activos cargados:', this.clientes.length);
      },
      error: (err) => console.error('Error al cargar clientes:', err)
    });
  }

  cargarPaquetes(): void {
    // Cargar solo paquetes registrados (disponibles para envío)
    const filtros = { estado: 'registrado' };
    this.paqueteService.obtenerPaquetes(0, 100, filtros).subscribe({
      next: (paquetes) => {
        this.paquetes = Array.isArray(paquetes) ? paquetes : [];
        console.log('Paquetes disponibles cargados:', this.paquetes.length);
      },
      error: (err) => console.error('Error al cargar paquetes:', err)
    });
  }

  get entregasFiltradas(): any[] {
    let filtradas = this.entregas;
    
    // Filtrar solo entregas activas por defecto
    filtradas = filtradas.filter(e => e.activo !== false);
    
    // El filtro por estado ahora se hace en el backend al cargar
    // Solo mantenemos el filtro de búsqueda en frontend para búsqueda en tiempo real
    
    // Filtrar por búsqueda
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtradas = filtradas.filter(e => {
        const sedeRemitente = this.obtenerNombreSede(e.id_sede_remitente).toLowerCase();
        const sedeReceptora = this.obtenerNombreSede(e.id_sede_receptora).toLowerCase();
        const clienteRemitente = this.obtenerNombreCliente(e.id_cliente_remitente).toLowerCase();
        const clienteReceptor = this.obtenerNombreCliente(e.id_cliente_receptor).toLowerCase();
        const estado = e.estado_envio.toLowerCase();
        
        return sedeRemitente.includes(term) || 
               sedeReceptora.includes(term) || 
               clienteRemitente.includes(term) || 
               clienteReceptor.includes(term) ||
               estado.includes(term);
      });
    }
    
    return filtradas;
  }

  abrirModalNuevo(): void {
    this.modoEdicion = false;
    this.entregaSeleccionada = null;
    this.formulario = {
      id_sede_remitente: '',
      id_sede_receptora: '',
      id_paquete: '',
      id_cliente_remitente: '',
      id_cliente_receptor: '',
      estado_envio: 'Pendiente',
      fecha_envio: new Date().toISOString().split('T')[0],
      observaciones: ''
    };
    this.mostrarModal = true;
  }

  abrirModalEditar(entrega: any): void {
    this.modoEdicion = true;
    this.entregaSeleccionada = entrega;
    this.formulario = { ...entrega };
    this.mostrarModal = true;
  }

  cerrarModal(): void {
    this.mostrarModal = false;
    this.entregaSeleccionada = null;
  }

  guardarEntrega(): void {
    // Obtener el usuario actual
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser?.id_usuario) {
      this.error = 'No se pudo obtener el usuario actual';
      return;
    }

    // Convertir fechas a formato datetime para el backend
    const formData: any = {
      ...this.formulario
    };

    // Convertir fecha_envio a ISO string si existe
    if (this.formulario.fecha_envio) {
      const fechaEnvio = new Date(this.formulario.fecha_envio);
      formData.fecha_envio = fechaEnvio.toISOString();
    } else {
      formData.fecha_envio = new Date().toISOString();
    }

    // Convertir fecha_entrega a ISO string si existe
    if (this.formulario.fecha_entrega) {
      const fechaEntrega = new Date(this.formulario.fecha_entrega);
      formData.fecha_entrega = fechaEntrega.toISOString();
    }

    console.log('Datos a enviar:', formData);

    if (this.modoEdicion && this.entregaSeleccionada?.id_detalle) {
      this.detalleEntregaService.actualizarDetalleEntrega(
        this.entregaSeleccionada.id_detalle,
        formData
      ).subscribe({
        next: () => {
          this.cargarEntregas();
          this.cerrarModal();
        },
        error: (err) => {
          this.error = 'Error al actualizar entrega';
          console.error('Error:', err);
        }
      });
    } else {
      // No agregar creado_por al formData, se envía como parámetro separado
      this.detalleEntregaService.crearDetalleEntrega(formData, currentUser.id_usuario).subscribe({
        next: () => {
          this.cargarEntregas();
          this.cerrarModal();
          this.error = '';
        },
        error: (err) => {
          this.error = err.error?.detail || 'Error al crear entrega';
          console.error('Error completo:', err);
          console.error('Detalle del error:', err.error);
        }
      });
    }
  }

  eliminarEntrega(id: string): void {
    if (confirm('¿Está seguro de eliminar esta entrega?')) {
      const currentUser = this.authService.getCurrentUser();
      if (!currentUser?.id_usuario) {
        this.error = 'No se pudo obtener el usuario actual';
        return;
      }

      this.detalleEntregaService.eliminarDetalleEntrega(id, currentUser.id_usuario).subscribe({
        next: () => {
          this.cargarEntregas();
          this.error = '';
        },
        error: (err) => {
          this.error = err.error?.detail || 'Error al eliminar entrega';
          console.error('Error:', err);
        }
      });
    }
  }

  obtenerNombreSede(idSede: string): string {
    const sede = this.sedes.find(s => s.id_sede === idSede);
    return sede ? sede.nombre : 'N/A';
  }

  obtenerNombreCliente(idCliente: string): string {
    const cliente = this.clientes.find(c => c.id_cliente === idCliente);
    return cliente ? `${cliente.primer_nombre} ${cliente.primer_apellido}` : 'N/A';
  }

  obtenerEstadoClase(estado: string): string {
    switch (estado) {
      case 'Pendiente': return 'badge-warning';
      case 'En transito': return 'badge-info';
      case 'Entregado': return 'badge-success';
      default: return 'badge-secondary';
    }
  }

  onFiltroEstadoChange(): void {
    console.log('Filtro de estado cambiado a:', this.filtroEstado);
    console.log('Recargando entregas desde backend...');
    this.cargarEntregas();
  }

  exportarDatos(): void {
    const csv = this.convertirACSV(this.entregasFiltradas);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `entregas_${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  private convertirACSV(data: any[]): string {
    if (data.length === 0) return '';
    
    const headers = ['ID', 'Sede Remitente', 'Sede Receptora', 'Cliente Remitente', 'Cliente Receptor', 'Estado', 'Fecha Envío', 'Fecha Entrega'];
    const rows = data.map(e => [
      e.id_detalle?.substring(0, 8) || '',
      this.obtenerNombreSede(e.id_sede_remitente),
      this.obtenerNombreSede(e.id_sede_receptora),
      this.obtenerNombreCliente(e.id_cliente_remitente),
      this.obtenerNombreCliente(e.id_cliente_receptor),
      e.estado_envio,
      e.fecha_envio,
      e.fecha_entrega || 'Pendiente'
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  toggleFiltros(): void {
    // Implementar si hay un panel de filtros en el HTML
  }

  aplicarFiltros(): void {
    // Recargar datos con los nuevos filtros
    console.log('Aplicando filtros, recargando desde backend...');
    this.cargarEntregas();
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'todos';
    this.searchTerm = '';
    // Recargar datos sin filtros
    console.log('Limpiando filtros, recargando desde backend...');
    this.cargarEntregas();
  }
}
