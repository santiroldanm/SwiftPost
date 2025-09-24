"""
Módulo que contiene las funciones del menú de gestión de sedes.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from cruds.sede_crud import sede as sede_crud
from entities.sede import SedeCreate


def mostrar_menu_sedes() -> None:
    """Muestra el menú de gestión de sedes."""
    print("\n" + "=" * 80)
    print("GESTIÓN DE SEDES".center(80))
    print("=" * 80)
    print("1. Listar todas las sedes")
    print("2. Buscar sede por ciudad")
    print("3. Agregar nueva sede")
    print("4. Editar sede")
    print("5. Cambiar estado de sede")
    print("0. Volver al menú principal")
    print("=" * 80)


def listar_sedes(db: Session) -> None:
    """Lista todas las sedes del sistema."""
    try:
        sedes = sede_crud.obtener_activas(db)

        if not sedes:
            print("\nNo hay sedes registradas en el sistema.")
            return

        print("\n" + "=" * 160)
        print("LISTADO DE SEDES".center(160))
        print("=" * 160)

        print(
            f"{'ID':<5} | {'NOMBRE':<25} | {'CIUDAD':<15} | {'DIRECCIÓN':<30} | {'TELÉFONO':<12} | {'COORDENADAS':<25} | {'ESTADO':<8}"
        )
        print("-" * 160)

        for sede in sedes:
            estado = "Activa" if sede.activo else "Inactiva"
            nombre = getattr(sede, 'nombre', 'Sin nombre')[:23]
            
            # Formatear coordenadas
            coordenadas = "Sin coordenadas"
            if hasattr(sede, 'latitud') and sede.latitud is not None:
                lat = round(sede.latitud, 4)
                lng = round(sede.longitud, 4) if sede.longitud else 0
                alt = round(sede.altitud, 0) if sede.altitud else 0
                coordenadas = f"{lat},{lng},{alt}m"[:23]
            
            print(
                f"{str(sede.id_sede)[:5]:<5} | {nombre:<25} | {sede.ciudad[:13]:<15} | {sede.direccion[:28]:<30} | {sede.telefono[:10]:<12} | {coordenadas:<25} | {estado:<8}"
            )

        print("=" * 160)

    except Exception as e:
        print(f"\nError al listar sedes: {str(e)}")

    input("\nPresione Enter para continuar...")


def buscar_sede_por_ciudad(db: Session) -> None:
    """Busca sedes por ciudad."""
    try:
        ciudad = input("\nIngrese la ciudad a buscar: ").strip()

        if not ciudad:
            print("\nError: Debe ingresar una ciudad.")
            input("Presione Enter para continuar...")
            return

        sedes = sede_crud.obtener_por_ciudad(db, ciudad=ciudad)

        if not sedes:
            print(f"\nNo se encontraron sedes en la ciudad de {ciudad}.")
            input("Presione Enter para continuar...")
            return

        print("\n" + "=" * 140)
        print(f"SEDES EN {ciudad.upper()}".center(140))
        print("=" * 140)

        print(
            f"{'ID':<5} | {'NOMBRE':<30} | {'CIUDAD':<20} | {'DIRECCIÓN':<35} | {'TELÉFONO':<15} | {'ESTADO':<10}"
        )
        print("-" * 140)

        for sede in sedes:
            estado = "Activa" if sede.activo else "Inactiva"
            nombre = getattr(sede, 'nombre', 'Sin nombre')[:28]
            print(
                f"{str(sede.id_sede)[:5]:<5} | {nombre:<30} | {sede.ciudad[:18]:<20} | {sede.direccion[:33]:<35} | {sede.telefono[:13]:<15} | {estado:<10}"
            )

        print("=" * 140)

    except Exception as e:
        print(f"\nError al buscar sedes: {str(e)}")

    input("\nPresione Enter para continuar...")


def agregar_sede(db: Session, id_administrador: UUID) -> None:
    """Agrega una nueva sede.

    Args:
        db: Sesión de base de datos
        id_administrador: ID del administrador que está creando la sede
    """
    try:
        print("\n" + "=" * 80)
        print("AGREGAR NUEVA SEDE".center(80))
        print("=" * 80)

        print("\nIngrese los datos de la nueva sede:")
        print("-" * 40)

        nombre = input("Nombre de la sede: ").strip()
        ciudad = input("Ciudad: ").strip()
        direccion = input("Dirección: ").strip()
        telefono = input("Teléfono: ").strip()
        
        # Capturar coordenadas (opcional)
        print("\nCoordenadas para cálculo de costos de envío (opcional):")
        print("Puede buscar las coordenadas en Google Maps")
        
        latitud_str = input("Latitud (ej: 6.2442): ").strip()
        longitud_str = input("Longitud (ej: -75.5812): ").strip()
        altitud_str = input("Altitud en metros (ej: 1495): ").strip()
        
        # Validar y convertir coordenadas
        latitud = None
        longitud = None
        altitud = None
        
        try:
            if latitud_str:
                latitud = float(latitud_str)
                if not (-90 <= latitud <= 90):
                    print(" Advertencia: Latitud fuera del rango válido (-90 a 90)")
                    latitud = None
        except ValueError:
            print(" Advertencia: Latitud inválida, se omitirá")
            
        try:
            if longitud_str:
                longitud = float(longitud_str)
                if not (-180 <= longitud <= 180):
                    print(" Advertencia: Longitud fuera del rango válido (-180 a 180)")
                    longitud = None
        except ValueError:
            print(" Advertencia: Longitud inválida, se omitirá")
            
        try:
            if altitud_str:
                altitud = float(altitud_str)
        except ValueError:
            print(" Advertencia: Altitud inválida, se omitirá")

        if not all([nombre, ciudad, direccion, telefono]):
            print("\nError: Los campos básicos (nombre, ciudad, dirección, teléfono) son obligatorios.")
            input("Presione Enter para continuar...")
            return

        sede_data = {
            "nombre": nombre,
            "ciudad": ciudad,
            "direccion": direccion,
            "telefono": telefono,
            "latitud": latitud,
            "longitud": longitud,
            "altitud": altitud,
            "activo": True,
        }

        sede_create = SedeCreate(**sede_data)
        sede = sede_crud.crear_registro(
            db=db,
            datos_entrada=sede_create,
            creado_por=id_administrador
        )

        print(f"\nSede registrada exitosamente con ID: {sede.id_sede}")

    except Exception as e:
        print(f"\nError al registrar sede: {str(e)}")

    input("\nPresione Enter para continuar...")


def editar_sede(db: Session) -> None:
    """Permite editar los datos de una sede."""
    try:
        id_sede = input("\nIngrese el ID de la sede a editar: ").strip()

        if not id_sede:
            print("\nError: Debe ingresar un ID de sede.")
            input("Presione Enter para continuar...")
            return

        sede = sede_crud.obtener_por_id(db, id=id_sede)

        if not sede:
            print("\nError: No se encontró ninguna sede con ese ID.")
            input("Presione Enter para continuar...")
            return

        print("\n" + "=" * 80)
        print("EDITAR SEDE".center(80))
        print("=" * 80)
        print(f"ID: {sede.id_sede}")
        print(f"Nombre actual: {getattr(sede, 'nombre', 'Sin nombre')}")
        print(f"Ciudad actual: {sede.ciudad}")
        print(f"Dirección actual: {sede.direccion}")
        print(f"Teléfono actual: {sede.telefono}")
        print("-" * 40)
        print("Ingrese los nuevos valores (deje en blanco para mantener el actual):")
        print("-" * 40)

        nuevo_nombre = input(f"Nuevo nombre [{getattr(sede, 'nombre', 'Sin nombre')}]: ").strip()
        nueva_ciudad = input(f"Nueva ciudad [{sede.ciudad}]: ").strip()
        nueva_direccion = input(f"Nueva dirección [{sede.direccion}]: ").strip()
        nuevo_telefono = input(f"Nuevo teléfono [{sede.telefono}]: ").strip()

        datos_actualizados = {}

        if nuevo_nombre and nuevo_nombre != getattr(sede, 'nombre', ''):
            datos_actualizados["nombre"] = nuevo_nombre

        if nueva_ciudad and nueva_ciudad != sede.ciudad:
            datos_actualizados["ciudad"] = nueva_ciudad

        if nueva_direccion and nueva_direccion != sede.direccion:
            datos_actualizados["direccion"] = nueva_direccion

        if nuevo_telefono and nuevo_telefono != sede.telefono:
            datos_actualizados["telefono"] = nuevo_telefono

        if datos_actualizados:
            from uuid import uuid4
            sede_actualizada = sede_crud.actualizar(
                db=db, 
                objeto_db=sede, 
                datos_entrada=datos_actualizados,
                actualizado_por=uuid4()
            )
            if sede_actualizada:
                print("\nSede actualizada correctamente.")
            else:
                print("\nError al actualizar la sede.")
        else:
            print("\nNo se realizaron cambios.")

    except Exception as e:
        print(f"\nError al editar sede: {str(e)}")

    input("\nPresione Enter para continuar...")


def cambiar_estado_sede(db: Session) -> None:
    """Activa o desactiva una sede."""
    try:
        id_sede = input("\nIngrese el ID de la sede a activar/desactivar: ").strip()

        if not id_sede:
            print("\nError: Debe ingresar un ID de sede.")
            input("Presione Enter para continuar...")
            return

        sede = sede_crud.obtener_por_id(db, id=id_sede)

        if not sede:
            print("\nError: No se encontró ninguna sede con ese ID.")
            input("Presione Enter para continuar...")
            return

        print("\n" + "=" * 80)
        print("CAMBIAR ESTADO DE SEDE".center(80))
        print("=" * 80)
        print(f"ID: {sede.id_sede}")
        print(f"Nombre: {getattr(sede, 'nombre', 'Sin nombre')}")
        print(f"Ciudad: {sede.ciudad}")
        print(f"Dirección: {sede.direccion}")
        print(f"Estado actual: {'ACTIVA' if sede.activo else 'INACTIVA'}")
        print("=" * 80)

        confirmar = (
            input(
                f"\n¿Desea {'DESACTIVAR' if sede.activo else 'ACTIVAR'} esta sede? (s/n): "
            )
            .strip()
            .lower()
        )

        if confirmar == "s":
            nuevo_estado = not sede.activo
            from uuid import uuid4
            sede_actualizada = sede_crud.actualizar(
                db=db, 
                objeto_db=sede, 
                datos_entrada={"activo": nuevo_estado},
                actualizado_por=uuid4()
            )

            if sede_actualizada:
                print(
                    f"\nSede {'activada' if nuevo_estado else 'desactivada'} correctamente."
                )
            else:
                print("\nError al cambiar el estado de la sede.")
        else:
            print("\nOperación cancelada.")

    except Exception as e:
        print(f"\nError al cambiar el estado de la sede: {str(e)}")

    input("\nPresione Enter para continuar...")


def manejar_menu_sedes(db: Session, usuario_actual: Dict[str, Any] = None) -> None:
    """Maneja el menú de gestión de sedes.

    Args:
        db: Sesión de base de datos
        usuario_actual: Diccionario con los datos del usuario administrador actual
    """
    while True:
        mostrar_menu_sedes()
        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            listar_sedes(db)
        elif opcion == "2":
            buscar_sede_por_ciudad(db)
        elif opcion == "3":
            if not usuario_actual:
                print("\nError: No se pudo identificar al administrador actual.")
                input("Presione Enter para continuar...")
                continue
            agregar_sede(db, id_administrador=usuario_actual.get("id_usuario"))
        elif opcion == "4":
            editar_sede(db)
        elif opcion == "5":
            cambiar_estado_sede(db)
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida. Intente de nuevo.")
            input("Presione Enter para continuar...")
