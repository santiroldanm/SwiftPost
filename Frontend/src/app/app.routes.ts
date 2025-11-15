import { Routes } from '@angular/router';
import { LayoutComponent } from './shared/components/layout/layout.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { PaqueteListComponent } from './features/paquete/paquete-list/paquete-list.component';
import { EmpleadosComponent } from './features/empleados/empleados.component';
import { TransportesComponent } from './features/transportes/transportes.component';
import { SedesComponent } from './features/sedes/sedes.component';
import { EntregasComponent } from './features/entregas/entregas.component';

export const routes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      { path: '', redirectTo: 'inicio', pathMatch: 'full', data: { title: 'Inicio' } },
      { path: 'inicio', component: DashboardComponent, data: { title: 'Inicio' } },
      { path: 'paquetes', component: PaqueteListComponent, data: { title: 'Paquetes' } },
      { path: 'empleados', component: EmpleadosComponent, data: { title: 'Empleados' } },
      { path: 'transportes', component: TransportesComponent, data: { title: 'Transportes' } },
      { path: 'sedes', component: SedesComponent, data: { title: 'Sedes' } },
      { path: 'entregas', component: EntregasComponent, data: { title: 'Entregas' } }
    ]
  }
];
