"""
Módulo para las funciones del menú de gestión de paquetes.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from uuid import uuid4

from cruds.paquete_crud import paquete as paquete_crud
from cruds.cliente_crud import cliente as cliente_crud
from entities.paquete import PaqueteCreate


def mostrar_encabezado(titulo: str = ""):
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 80)
    if titulo:
        print(f"{titulo:^80}")
        print("=" * 80)


def registrar_paquete(db: Session, id_creador: str) -> None:
    """Registra un nuevo paquete en el sistema."""
    mostrar_encabezado("REGISTRAR NUEVO PAQUETE")
    try:
        print("\nFuncionalidad de registro de paquetes en desarrollo...")
    except Exception as e:
        print(f"\nError al registrar el paquete: {str(e)}")
    input("\nPresione Enter para continuar...")


def listar_paquetes(db: Session) -> None:
    """Lista todos los paquetes del sistema."""
    mostrar_encabezado("LISTADO DE PAQUETES")
    try:
        paquetes = paquete_crud.obtener_todos(db)
        if not paquetes:
            print("No hay paquetes registrados.")
        else:
            col_id = 10
            col_cliente = 25
            col_contenido = 30
            col_estado = 15
            col_fecha = 15

            print(
                f"{'ID':<{col_id}} | {'CLIENTE':<{col_cliente}} | {'CONTENIDO':<{col_contenido}} | {'ESTADO':<{col_estado}} | {'FECHA REGISTRO':<{col_fecha}}"
            )
            print(
                "-"
                * (col_id + col_cliente + col_contenido + col_estado + col_fecha + 12)
            )

            for p in paquetes:

                cliente = getattr(p, "cliente", None)
                cliente_nombre = (
                    f"{getattr(cliente, 'primer_nombre', '')} {getattr(cliente, 'primer_apellido', '')}".strip()
                    if cliente
                    else "N/A"
                )
                id_paquete = str(getattr(p, "id_paquete", "N/A"))
                print(
                    f"{id_paquete:<{col_id}} | "
                    f"{cliente_nombre:<{col_cliente}} | "
                    f"{getattr(p, 'contenido', 'N/A'):<{col_contenido}} | "
                    f"{getattr(p, 'estado', 'N/A'):<{col_estado}} | "
                    f"{getattr(p, 'fecha_registro', None).strftime('%Y-%m-%d') if getattr(p, 'fecha_registro', None) else 'N/A':<{col_fecha}}"
                )
    except Exception as e:
        print(f"\nError al listar paquetes: {str(e)}")
    input("\nPresione Enter para continuar...")


def buscar_paquete(db: Session) -> None:
    """Busca un paquete por su ID."""
    mostrar_encabezado("BUSCAR PAQUETE")
    id_paquete = input("Ingrese el ID del paquete: ").strip()
    if not id_paquete:
        print("Debe ingresar un ID.")
        input("\nPresione Enter para continuar...")
        return

    paquete = paquete_crud.obtener_por_id_paquete(db, id_paquete=id_paquete)
    if paquete:
        print(f"Paquete encontrado: {paquete.contenido}")
    else:
        print("Paquete no encontrado.")
    input("\nPresione Enter para continuar...")


def actualizar_estado_paquete(db: Session) -> None:
    """Actualiza el estado de un paquete."""
    mostrar_encabezado("ACTUALIZAR ESTADO DE PAQUETE")
    id_paquete = input("Ingrese el ID del paquete: ").strip()
    paquete = paquete_crud.obtener_por_id_paquete(db, id_paquete=id_paquete)
    if not paquete:
        print("Paquete no encontrado.")
        input("\nPresione Enter para continuar...")
        return

    nuevo_estado = input(f"Nuevo estado para el paquete [{paquete.estado}]: ").strip()
    if nuevo_estado:
        paquete_crud.actualizar(db, db_obj=paquete, obj_in={"estado": nuevo_estado})
        print("Estado actualizado.")
    else:
        print("No se realizaron cambios.")
    input("\nPresione Enter para continuar...")


def manejar_menu_paquetes_admin(db: Session, id_administrador: str) -> None:
    """Maneja el menú de gestión de paquetes para administradores."""
    while True:
        mostrar_encabezado("GESTIÓN DE PAQUETES (ADMIN)")
        print("1. Registrar nuevo paquete")
        print("2. Listar todos los paquetes")
        print("3. Buscar paquete")
        print("4. Actualizar estado de paquete")
        print("0. Volver al menú principal")

        opcion = input("\nSeleccione una opción: ")
        if opcion == "1":
            registrar_paquete(db, id_creador=id_administrador)
        elif opcion == "2":
            listar_paquetes(db)
        elif opcion == "3":
            buscar_paquete(db)
        elif opcion == "4":
            actualizar_estado_paquete(db)
        elif opcion == "0":
            break
        else:
            print("Opción no válida.")


def manejar_menu_paquetes_empleado(db: Session, id_empleado: str) -> None:
    """Maneja el menú de gestión de paquetes para empleados."""
    while True:
        mostrar_encabezado("GESTIÓN DE PAQUETES (EMPLEADO)")
        print("1. Registrar nuevo paquete")
        print("2. Actualizar estado de paquete")
        print("3. Buscar paquete")
        print("0. Volver al menú principal")

        opcion = input("\nSeleccione una opción: ")
        if opcion == "1":
            registrar_paquete(db, id_creador=id_empleado)
        elif opcion == "2":
            actualizar_estado_paquete(db)
        elif opcion == "3":
            buscar_paquete(db)
        elif opcion == "0":
            break
        else:
            print("Opción no válida.")


def solicitar_recogida(db: Session, usuario_data: Dict[str, Any]) -> None:
    """Permite a un cliente solicitar la recogida de un paquete."""
    mostrar_encabezado("SOLICITAR RECOGIDA")
    try:
        cliente = cliente_crud.obtener_por_usuario(
            db, usuario_id=usuario_data["id_usuario"]
        )
        if not cliente:
            print("\nError: No se encontró la información del cliente.")
            input("\nPresione Enter para continuar...")
            return

        descripcion = input("Descripción del contenido: ")
        peso = float(input("Peso (kg): "))
        tamaño = input("Tamaño (pequeño, mediano, grande): ").lower()
        fragilidad = input("Nivel de fragilidad (baja, normal, alta): ").lower()

        paquete_data = PaqueteCreate(
            peso=peso,
            tamaño=tamaño,
            fragilidad=fragilidad,
            contenido=descripcion,
            tipo="normal",
        )

        paquete_datos = paquete_data.model_dump()
        paquete_datos["id_cliente"] = cliente.id_cliente

        paquete_crud.crear_registro(
            db=db, datos_entrada=paquete_datos, creado_por=usuario_data["id_usuario"]
        )
        print("\n¡Solicitud de recogida enviada exitosamente!")
    except ValueError:
        print("\nError: El peso debe ser un número.")
    except Exception as e:
        print(f"\nError al solicitar la recogida: {str(e)}")
    input("\nPresione Enter para continuar...")


def rastrear_envio(db: Session, usuario_data: Dict[str, Any]) -> None:
    """Permite a un cliente rastrear un envío."""
    mostrar_encabezado("RASTREAR ENVÍO")
    id_paquete = input("Ingrese el número de seguimiento del paquete: ").strip()
    try:
        paquete = paquete_crud.obtener_por_id_paquete(db, id_paquete)
    except Exception as e:
        print(f"\nError al buscar el paquete: {str(e)}")
        input("\nPresione Enter para continuar...")
        return
    if (
        paquete
        and paquete.id_cliente
        == cliente_crud.obtener_por_usuario(
            db, usuario_id=usuario_data["id_usuario"]
        ).id_cliente
    ):
        print(f"\nEstado del paquete: {paquete.estado.upper()}")
    else:
        print("\nPaquete no encontrado o no pertenece a este usuario.")
    input("\nPresione Enter para continuar...")


def historial_envios(db: Session, usuario_data: Dict[str, Any]) -> None:
    """Muestra el historial de envíos de un cliente."""
    mostrar_encabezado("HISTORIAL DE ENVÍOS")
    try:
        cliente = cliente_crud.obtener_por_usuario(
            db, usuario_id=usuario_data["id_usuario"]
        )
        if not cliente:
            print("\nCliente no encontrado.")
            input("\nPresione Enter para continuar...")
            return

        paquetes, total = paquete_crud.obtener_por_cliente(
            db, id_cliente=cliente.id_cliente
        )
        if not paquetes or total == 0:
            print("\nNo hay envíos registrados para este cliente.")
        else:
            col_id = 15
            col_contenido = 40
            col_estado = 20
            col_fecha = 15

            print(
                f"\n{'ID PAQUETE':<{col_id}} | {'CONTENIDO':<{col_contenido}} | {'ESTADO':<{col_estado}} | {'FECHA ENVÍO':<{col_fecha}}"
            )
            print("-" * (col_id + col_contenido + col_estado + col_fecha + 9))

            for p in paquetes:
                fecha_envio = getattr(p, "fecha_envio", None)
                id_paquete = str(getattr(p, "id_paquete", "N/A"))
                contenido = getattr(p, "contenido", "N/A")
                estado = getattr(p, "estado", "N/A")
                fecha = fecha_envio.strftime("%Y-%m-%d") if fecha_envio else "N/A"

                if contenido != "N/A" and len(contenido) > col_contenido - 3:
                    contenido = contenido[: col_contenido - 3] + "..."
                print(
                    f"{id_paquete:<{col_id}} | {contenido:<{col_contenido}} | {estado:<{col_estado}} | {fecha:<{col_fecha}}"
                )
    except Exception as e:
        print(f"\nError al obtener el historial de envíos: {str(e)}")
        import traceback

        traceback.print_exc()
    input("\nPresione Enter para continuar...")
    print("\nNo tienes envíos registrados.")
    input("\nPresione Enter para continuar...")
