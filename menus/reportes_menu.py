"""
Módulo para las funciones del menú de reportes.
"""

from sqlalchemy.orm import Session
from datetime import datetime, date


def mostrar_encabezado(titulo: str = ""):
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 80)
    if titulo:
        print(f"{titulo:^80}")
        print("=" * 80)


def reporte_envios_por_periodo(db: Session) -> None:
    """Genera un reporte de envíos por período de tiempo."""
    mostrar_encabezado("REPORTE DE ENVÍOS POR PERÍODO")
    try:
        fecha_inicio_str = input("Fecha de inicio (YYYY-MM-DD): ").strip()
        fecha_fin_str = input("Fecha de fin (YYYY-MM-DD): ").strip()
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
        print(f"Generando reporte de envíos desde {fecha_inicio} hasta {fecha_fin}...")
    except ValueError:
        print("Formato de fecha incorrecto.")
    except Exception as e:
        print(f"Error: {e}")
    input("\nPresione Enter para continuar...")


def reporte_ingresos(db: Session) -> None:
    """Genera un reporte de ingresos."""
    print("Función de reporte de ingresos en desarrollo...")
    input("\nPresione Enter para continuar...")


def reporte_paquetes_por_estado(db: Session) -> None:
    """Genera un reporte de paquetes por estado."""
    print("Función de reporte de paquetes por estado en desarrollo...")
    input("\nPresione Enter para continuar...")


def reporte_clientes_frecuentes(db: Session) -> None:
    """Genera un reporte de clientes frecuentes."""
    print("Función de reporte de clientes frecuentes en desarrollo...")
    input("\nPresione Enter para continuar...")


def reporte_eficiencia_transportes(db: Session) -> None:
    """Genera un reporte de eficiencia de transportes."""
    print("Función de reporte de eficiencia de transportes en desarrollo...")
    input("\nPresione Enter para continuar...")


def manejar_menu_reportes_admin(db: Session) -> None:
    """Maneja el menú de reportes para administradores."""
    while True:
        mostrar_encabezado("REPORTES (ADMIN)")
        print("1. Reporte de envíos por período")
        print("2. Reporte de ingresos")
        print("3. Reporte de paquetes por estado")
        print("4. Reporte de clientes frecuentes")
        print("5. Reporte de eficiencia de transportes")
        print("0. Volver al menú principal")

        opcion = input("\nSeleccione una opción: ")
        if opcion == "1":
            reporte_envios_por_periodo(db)
        elif opcion == "2":
            reporte_ingresos(db)
        elif opcion == "3":
            reporte_paquetes_por_estado(db)
        elif opcion == "4":
            reporte_clientes_frecuentes(db)
        elif opcion == "5":
            reporte_eficiencia_transportes(db)
        elif opcion == "0":
            break
        else:
            print("Opción no válida.")
