"""
Módulo para el menú de clientes.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from .base import mostrar_encabezado, obtener_input, confirmar_accion
from cruds.cliente_crud import cliente as cliente_crud
from cruds.paquete_crud import paquete as paquete_crud
from entities.cliente import ClienteCreate, ClienteUpdate


def ver_perfil(db: Session, usuario_actual: Any) -> None:
    """Muestra el perfil del cliente."""
    mostrar_encabezado("MI PERFIL")

    try:
        cliente = cliente_crud.obtener_por_usuario_id(db, usuario_actual.id_usuario)
        if not cliente:
            input(
                "\nNo se encontró información del cliente. Presione Enter para continuar..."
            )
            return

        print(
            f"\n{'Nombre:':<20} {cliente.primer_nombre} {cliente.segundo_nombre or ''} {cliente.primer_apellido} {cliente.segundo_apellido or ''}"
        )
        print(f"{'Documento:':<20} {cliente.numero_documento}")
        print(f"{'Correo:':<20} {cliente.correo}")
        print(f"{'Teléfono:':<20} {cliente.telefono}")
        print(f"{'Dirección:':<20} {cliente.direccion}")
        print(f"{'Tipo:':<20} {cliente.tipo}")

        input("\nPresione Enter para continuar...")

    except Exception as e:
        input(
            f"\nError al cargar el perfil: {str(e)}. Presione Enter para continuar..."
        )


def actualizar_perfil(db: Session, usuario_actual: Any) -> None:
    """Permite al cliente actualizar su perfil."""
    mostrar_encabezado("ACTUALIZAR PERFIL")

    try:
        cliente = cliente_crud.obtener_por_usuario_id(db, usuario_actual.id_usuario)
        if not cliente:
            input(
                "\nNo se encontró información del cliente. Presione Enter para continuar..."
            )
            return

        print("\nDeje en blanco los campos que no desee modificar.")

        # Obtener nuevos valores
        datos_actualizados = {}

        # Solo permitir actualizar ciertos campos
        campos_permitidos = {
            "telefono": "Nuevo teléfono: ",
            "correo": "Nuevo correo electrónico: ",
            "direccion": "Nueva dirección: ",
        }

        for campo, mensaje in campos_permitidos.items():
            nuevo_valor = input(f"{mensaje}").strip()
            if nuevo_valor:
                datos_actualizados[campo] = nuevo_valor

        if not datos_actualizados:
            input("\nNo se realizaron cambios. Presione Enter para continuar...")
            return

        # Validar correo si se actualizó
        if "correo" in datos_actualizados:
            # Validación simple de correo
            if (
                "@" not in datos_actualizados["correo"]
                or "." not in datos_actualizados["correo"]
            ):
                input(
                    "\nEl correo electrónico no es válido. Presione Enter para continuar..."
                )
                return

        # Actualizar el cliente
        cliente_actualizado = cliente_crud.actualizar(
            db=db, db_obj=cliente, obj_in=datos_actualizados
        )

        if cliente_actualizado:
            db.commit()
            input("\nPerfil actualizado exitosamente. Presione Enter para continuar...")
        else:
            db.rollback()
            input("\nNo se pudo actualizar el perfil. Presione Enter para continuar...")

    except Exception as e:
        db.rollback()
        input(
            f"\nError al actualizar el perfil: {str(e)}. Presione Enter para continuar..."
        )


def menu_cliente(db: Session, usuario_actual: Any) -> bool:
    """
    Muestra el menú principal para clientes.

    Args:
        db: Sesión de base de datos
        usuario_actual: Usuario autenticado

    Returns:
        bool: True si el usuario cierra sesión, False si sale de la aplicación
    """
    while True:
        mostrar_encabezado("MENÚ PRINCIPAL - CLIENTE")
        print("1. Ver mi perfil")
        print("2. Actualizar perfil")
        print("3. Gestionar paquetes")
        print("4. Ver historial de envíos")
        print("0. Cerrar sesión")
        print("=" * 60)

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            ver_perfil(db, usuario_actual)
        elif opcion == "2":
            actualizar_perfil(db, usuario_actual)
        elif opcion == "3":
            # Implementar gestión de paquetes
            input(
                "\nMódulo de gestión de paquetes en desarrollo. Presione Enter para continuar..."
            )
        elif opcion == "4":
            # Implementar historial de envíos
            input(
                "\nMódulo de historial de envíos en desarrollo. Presione Enter para continuar..."
            )
        elif opcion == "0":
            if confirmar_accion("\n¿Está seguro que desea cerrar sesión? (s/n): "):
                return True
        else:
            input("\nOpción inválida. Presione Enter para continuar...")
