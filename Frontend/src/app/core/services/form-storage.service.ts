import { Injectable } from '@angular/core';

/**
 * Servicio para persistir datos de formularios en localStorage
 * Permite guardar y recuperar datos de formularios para que no se pierdan
 * cuando el usuario cierra el modal sin guardar
 */
@Injectable({
  providedIn: 'root'
})
export class FormStorageService {
  private readonly PREFIX = 'swiftpost_form_';

  constructor() {}

  /**
   * Guarda los datos de un formulario en localStorage
   * @param formName Nombre único del formulario
   * @param data Datos a guardar
   */
  saveFormData(formName: string, data: any): void {
    try {
      const key = this.PREFIX + formName;
      localStorage.setItem(key, JSON.stringify(data));
      console.log(`Formulario ${formName} guardado en localStorage`);
    } catch (error) {
      console.error('Error al guardar formulario:', error);
    }
  }

  /**
   * Recupera los datos de un formulario desde localStorage
   * @param formName Nombre único del formulario
   * @returns Los datos guardados o null si no existen
   */
  getFormData(formName: string): any {
    try {
      const key = this.PREFIX + formName;
      const data = localStorage.getItem(key);
      if (data) {
        console.log(`Formulario ${formName} recuperado de localStorage`);
        return JSON.parse(data);
      }
      return null;
    } catch (error) {
      console.error('Error al recuperar formulario:', error);
      return null;
    }
  }

  /**
   * Limpia los datos de un formulario de localStorage
   * @param formName Nombre único del formulario
   */
  clearFormData(formName: string): void {
    try {
      const key = this.PREFIX + formName;
      localStorage.removeItem(key);
      console.log(`Formulario ${formName} eliminado de localStorage`);
    } catch (error) {
      console.error('Error al limpiar formulario:', error);
    }
  }

  /**
   * Limpia todos los formularios guardados
   */
  clearAllForms(): void {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.PREFIX)) {
          localStorage.removeItem(key);
        }
      });
      console.log('Todos los formularios eliminados de localStorage');
    } catch (error) {
      console.error('Error al limpiar todos los formularios:', error);
    }
  }

  /**
   * Verifica si existe un formulario guardado
   * @param formName Nombre único del formulario
   * @returns true si existe, false si no
   */
  hasFormData(formName: string): boolean {
    const key = this.PREFIX + formName;
    return localStorage.getItem(key) !== null;
  }
}
