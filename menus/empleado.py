"""
Módulo para el menú de empleados.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from .base import mostrar_encabezado, obtener_input, confirmar_accion
from cruds.cliente_crud import cliente as cliente_crud
from cruds.paquete_crud import paquete as paquete_crud
from cruds.empleado_crud import empleado as empleado_crud
from entities.detalle_entrega import DetalleEntrega


def gestionar_envios(db: Session, empleado_id: str) -> None:
    """
    Permite al empleado gestionar los envíos.
    """
    while True:
        mostrar_encabezado("GESTIÓN DE ENVÍOS")
        print("1. Ver envíos pendientes")
        print("2. Actualizar estado de envío")
        print("3. Buscar envío")
        print("0. Volver al menú principal")
        print("=" * 60)

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            ver_envios_pendientes(db)
        elif opcion == "2":
            actualizar_estado_envio(db, empleado_id)
        elif opcion == "3":
            buscar_envio(db)
        elif opcion == "0":
            break
        else:
            input("\nOpción inválida. Presione Enter para continuar...")


def ver_envios_pendientes(db: Session) -> None:
    """Muestra los envíos pendientes de procesar."""
    try:
        mostrar_encabezado("ENVÍOS PENDIENTES")

        # Obtener envíos pendientes (estado = 'pendiente' o 'en_ruta')
        envios = paquete_crud.obtener_por_estado(
            db, estado=DetalleEntrega.PENDIENTE, skip=0, limit=20
        )

        if not envios:
            input("\nNo hay envíos pendientes. Presione Enter para continuar...")
            return

        # Mostrar lista de envíos
        print(f"\n{'ID':<10} {'Remitente':<30} {'Receptor':<30} {'Estado':<15}")
        print("-" * 85)

        for envio in envios:
            remitente = (
                f"{envio.remitente.primer_nombre} {envio.remitente.primer_apellido}"
            )
            receptor = f"{envio.destinatario.primer_nombre} {envio.destinatario.primer_apellido}"
            print(
                f"{envio.id_paquete:<10} {remitente[:28]:<30} {receptor[:28]:<30} {envio.estado.value:<15}"
            )

        input("\nPresione Enter para continuar...")

    except Exception as e:
        input(
            f"\nError al obtener los envíos: {str(e)}. Presione Enter para continuar..."
        )


def actualizar_estado_envio(db: Session, empleado_id: str) -> None:
    """Permite actualizar el estado de un envío."""
    try:
        mostrar_encabezado("ACTUALIZAR ESTADO DE ENVÍO")

        id_envio = obtener_input("ID del envío: ")
        if not id_envio:
            return

        # Obtener el envío
        envio = paquete_crud.obtener_por_id(db, id_envio)
        if not envio:
            input("\nNo se encontró el envío. Presione Enter para continuar...")
            return

        # Mostrar información del envío
        print("\nInformación del envío:")
        print(f"ID: {envio.id_paquete}")
        print(
            f"Remitente: {envio.remitente.primer_nombre} {envio.remitente.primer_apellido}"
        )
        print(
            f"Destinatario: {envio.destinatario.primer_nombre} {envio.destinatario.primer_apellido}"
        )
        print(f"Estado actual: {envio.estado.value}")

        # Mostrar opciones de estado según el estado actual
        print("\nNuevo estado:")
        estados = list(DetalleEntrega)
        for i, estado in enumerate(estados, 1):
            print(f"{i}. {estado.value}")

        opcion = obtener_input("\nSeleccione el nuevo estado: ")
        try:
            nuevo_estado = estados[int(opcion) - 1]
        except (ValueError, IndexError):
            input("\nOpción inválida. Presione Enter para continuar...")
            return

        # Actualizar el estado
        envio.estado = nuevo_estado
        envio.fecha_actualizacion = datetime.utcnow()

        # Registrar el cambio de estado
        # (asumiendo que existe un modelo para el historial de estados)

        db.commit()
        input(
            f"\nEstado del envío actualizado a '{nuevo_estado.value}'. Presione Enter para continuar..."
        )

    except Exception as e:
        db.rollback()
        input(
            f"\nError al actualizar el estado: {str(e)}. Presione Enter para continuar..."
        )


def buscar_cliente(db: Session) -> None:
    """Permite buscar clientes."""
    try:
        mostrar_encabezado("BUSCAR CLIENTE")

        termino = obtener_input("Ingrese nombre, documento o correo del cliente: ")
        if not termino:
            return

        clientes = cliente_crud.buscar(db, termino=termino, limit=10)

        if not clientes:
            input("\nNo se encontraron clientes. Presione Enter para continuar...")
            return

        print(
            f"\n{'ID':<10} {'Nombre':<30} {'Documento':<15} {'Correo':<30} {'Teléfono':<15}"
        )
        print("-" * 85)

        for cliente in clientes:
            nombre_completo = f"{cliente.primer_nombre} {cliente.primer_apellido}"
            print(
                f"{cliente.id_cliente:<10} {nombre_completo[:28]:<30} {cliente.numero_documento:<15} {cliente.correo[:28]:<30} {cliente.telefono:<15}"
            )

        input("\nPresione Enter para continuar...")

    except Exception as e:
        input(f"\nError al buscar clientes: {str(e)}. Presione Enter para continuar...")


def menu_empleado(db: Session, empleado_actual: Any) -> bool:
    """
    Muestra el menú principal para empleados.

    Args:
        db: Sesión de base de datos
        empleado_actual: Empleado autenticado

    Returns:
        bool: True si el usuario cierra sesión, False si sale de la aplicación
    """
    while True:
        mostrar_encabezado("MENÚ PRINCIPAL - EMPLEADO")
        print("1. Gestionar envíos")
        print("2. Buscar cliente")
        print("3. Reportes")
        print("0. Cerrar sesión")
        print("=" * 60)

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            gestionar_envios(db, str(empleado_actual.id_empleado))
        elif opcion == "2":
            buscar_cliente(db)
        elif opcion == "3":
            # Implementar reportes
            input(
                "\nMódulo de reportes en desarrollo. Presione Enter para continuar..."
            )
        elif opcion == "0":
            if confirmar_accion("\n¿Está seguro que desea cerrar sesión? (s/n): "):
                return True
        else:
            input("\nOpción inválida. Presione Enter para continuar...")
