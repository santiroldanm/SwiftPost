import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface SerieXY {
  labels: string[];
  data: number[];
}

export interface TopItems {
  labels: string[];
  data: number[];
}

export interface EstadosPaquetes extends TopItems {}

export interface TiempoPromedioEntrega {
  avg_hours: number;
  avg_days: number;
}

export interface ResumenAnalytics {
  total_paquetes: number;
  paquetes_mes: number;
  sedes_activas: number;
  entregas_pendientes: number;
}

@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private base = '/analytics';

  constructor(private api: ApiService) {}

  paquetesUltimos30Dias(days = 30): Observable<SerieXY> {
    const endpoint = `${this.base}/paquetes-ultimos-30-dias`;
    const params = { days } as any;
    console.log('[Analytics] GET', this.api.getFullUrl(endpoint), params);
    return this.api.get<SerieXY>(endpoint, params);
  }

  sedesMasActivas(limit = 5, days = 90): Observable<TopItems> {
    const endpoint = `${this.base}/sedes-mas-activas`;
    const params = { limit, days } as any;
    console.log('[Analytics] GET', this.api.getFullUrl(endpoint), params);
    return this.api.get<TopItems>(endpoint, params);
  }

  estadosPaquetes(days = 90): Observable<EstadosPaquetes> {
    const endpoint = `${this.base}/estados-paquetes`;
    const params = { days } as any;
    console.log('[Analytics] GET', this.api.getFullUrl(endpoint), params);
    return this.api.get<EstadosPaquetes>(endpoint, params);
  }

  tiempoPromedioEntrega(days = 180): Observable<TiempoPromedioEntrega> {
    const endpoint = `${this.base}/tiempo-promedio-entrega`;
    const params = { days } as any;
    console.log('[Analytics] GET', this.api.getFullUrl(endpoint), params);
    return this.api.get<TiempoPromedioEntrega>(endpoint, params);
  }

  resumen(): Observable<ResumenAnalytics> {
    const endpoint = `${this.base}/resumen`;
    console.log('[Analytics] GET', this.api.getFullUrl(endpoint));
    return this.api.get<ResumenAnalytics>(endpoint);
  }

  exportResumen(daysLine = 30, daysStates = 90, daysTop = 90, topLimit = 5): Observable<Blob> {
    const endpoint = `${this.base}/export-resumen`;
    const params = {
      days_line: daysLine,
      days_states: daysStates,
      days_top: daysTop,
      top_limit: topLimit,
    } as any;
    console.log('[Analytics] GET (PDF)', this.api.getFullUrl(endpoint), params);
    return this.api.getFile(endpoint, params);
  }
}
