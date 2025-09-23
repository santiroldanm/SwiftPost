"""
Módulo para generar reportes del sistema.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from cruds import cliente_crud, empleado_crud, paquete_crud, transporte_crud, sede_crud


def mostrar_reportes(db: Session) -> None:
    """
    Muestra diferentes reportes del sistema.
    """
    while True:
        print("\n" + "=" * 60)
        print("REPORTES DEL SISTEMA".center(60))
        print("=" * 60)
        print("1. Resumen general")
        print("2. Reporte de clientes")
        print("3. Reporte de empleados")
        print("4. Reporte de paquetes")
        print("5. Estadísticas de transporte")
        print("0. Volver al menú principal")
        print("=" * 60)

        opcion = input("\nSeleccione un reporte: ").strip()

        if opcion == "1":
            mostrar_resumen_general(db)
        elif opcion == "2":
            mostrar_reporte_clientes(db)
        elif opcion == "3":
            mostrar_reporte_empleados(db)
        elif opcion == "4":
            mostrar_reporte_paquetes(db)
        elif opcion == "5":
            mostrar_estadisticas_transporte(db)
        elif opcion == "0":
            break
        else:
            input("\nOpción inválida. Presione Enter para continuar...")


def mostrar_resumen_general(db: Session) -> None:
    """Muestra un resumen general del sistema."""
    total_clientes = len(cliente_crud.get_multi(db))
    total_empleados = len(empleado_crud.get_multi(db))
    total_paquetes = len(paquete_crud.get_multi(db))
    total_transportes = len(transporte_crud.get_multi(db))
    total_sedes = len(sede_crud.get_multi(db))

    print("\n" + "=" * 60)
    print("RESUMEN GENERAL DEL SISTEMA".center(60))
    print("=" * 60)
    print(f"\n{'Clientes:':<20} {total_clientes:>10}")
    print(f"{'Empleados:':<20} {total_empleados:>10}")
    print(f"{'Paquetes registrados:':<20} {total_paquetes:>10}")
    print(f"{'Transportes:':<20} {total_transportes:>10}")
    print(f"{'Sedes:':<20} {total_sedes:>10}")
    print("\n" + "=" * 60)
    input("\nPresione Enter para continuar...")


def mostrar_reporte_clientes(db: Session) -> None:
    """Muestra un reporte de clientes."""

    clientes = cliente_crud.get_multi(db)
    print("\n" + "=" * 60)
    print("REPORTE DE CLIENTES".center(60))
    print("=" * 60)
    if not clientes:
        print("\nNo hay clientes registrados.")
    else:
        print(f"\n{'ID':<8} {'NOMBRE':<30} {'EMAIL':<20}")
        print("-" * 60)
        for cliente in clientes[:20]:  # Mostrar solo los primeros 20
            nombre_completo = f"{cliente.nombres} {cliente.apellidos}"
            print(f"{cliente.id:<8} {nombre_completo:<30} {cliente.email:<20}")
        if len(clientes) > 20:
            print(f"\n... y {len(clientes) - 20} clientes más")
    print("\n" + "=" * 60)
    input("\nPresione Enter para continuar...")


def mostrar_reporte_empleados(db: Session) -> None:
    """Muestra un reporte de empleados."""
    from cruds import empleado_crud

    empleados = empleado_crud.get_multi(db)
    print("\n" + "=" * 60)
    print("REPORTE DE EMPLEADOS".center(60))
    print("=" * 60)
    if not empleados:
        print("\nNo hay empleados registrados.")
    else:
        print(
            f"\n{'NOMBRE':<10} {'APELLIDO':<10} {'TIPO EMPLEADO':<15} {'FECHA INGRESO':<10}"
        )
        print("-" * 60)
        for emp in empleados:
            fecha_ingreso = (
                emp.fecha_ingreso.strftime("%d/%m/%Y") if emp.fecha_ingreso else "N/A"
            )
            print(
                f"{emp.primer_nombre:<10} {emp.primer_apellido:<10} {emp.tipo_empleado:<15} {fecha_ingreso:<10}"
            )
    print("\n" + "=" * 60)
    input("\nPresione Enter para continuar...")


def mostrar_reporte_paquetes(db: Session) -> None:
    """Muestra un reporte de paquetes."""
    from cruds import paquete_crud

    paquetes = paquete_crud.get_multi(db)
    print("\n" + "=" * 60)
    print("REPORTE DE PAQUETES".center(60))
    print("=" * 60)
    if not paquetes:
        print("\nNo hay paquetes registrados.")
    else:
        print(f"\n{'ID':<8} {'PESO (kg)':<12} {'ESTADO':<20} {'FECHA REGISTRO'}")
        print("-" * 60)
        for p in paquetes[:20]:  # Mostrar solo los primeros 20
            fecha_reg = (
                p.fecha_registro.strftime("%d/%m/%Y") if p.fecha_registro else "N/A"
            )
            print(
                f"{p.id:<8} {p.peso or 'N/A':<12} {p.estado or 'N/A':<20} {fecha_reg}"
            )
        if len(paquetes) > 20:
            print(f"\n... y {len(paquetes) - 20} paquetes más")
    print("\n" + "=" * 60)
    input("\nPresione Enter para continuar...")


def mostrar_estadisticas_transporte(db: Session) -> None:
    """Muestra estadísticas de transporte."""
    from cruds import transporte_crud

    transportes = transporte_crud.get_multi(db)
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DE TRANSPORTE".center(60))
    print("=" * 60)
    if not transportes:
        print("\nNo hay transportes registrados.")
    else:
        # Agrupar por tipo de transporte
        tipos = {}
        for t in transportes:
            if t.tipo not in tipos:
                tipos[t.tipo] = 0
            tipos[t.tipo] += 1

        print("\nCANTIDAD POR TIPO DE TRANSPORTE:")
        print("-" * 60)
        for tipo, cantidad in tipos.items():
            print(f"{tipo.capitalize()}: {cantidad}")

        # Capacidad total
        capacidad_total = sum(t.capacidad for t in transportes if t.capacidad)
        print(f"\nCapacidad total de carga: {capacidad_total} kg")

        # Promedio de capacidad
        if transportes:
            promedio = capacidad_total / len(transportes)
            print(f"Capacidad promedio por transporte: {promedio:.1f} kg")

    print("\n" + "=" * 60)
    input("\nPresione Enter para continuar...")
