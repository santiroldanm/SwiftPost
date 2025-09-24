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
        
        # Mostrar encabezado
        print("\n" + "=" * 120)
        print("LISTADO DE SEDES".center(120))
        print("=" * 120)
        
        # Encabezados
        print(f"{'ID':<5} | {'NOMBRE':<20} | {'CIUDAD':<20} | {'DIRECCIÓN':<30} | {'TELÉFONO':<15} | {'ESTADO':<10}")
        print("-" * 120)
        
        # Datos
        for sede in sedes:
            estado = 'Activa' if sede.activo else 'Inactiva'
            print(f"{str(sede.id_sede)[:5]:<5} | {sede.nombre[:18]:<20} | {sede.ciudad[:18]:<20} | {sede.direccion[:28]:<30} | {sede.telefono[:15]:<15} | {estado:<10}")
        
        print("=" * 120)
        
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
        
        sedes = sede_crud.buscar_por_ciudad(db, ciudad=ciudad)
        
        if not sedes:
            print(f"\nNo se encontraron sedes en la ciudad de {ciudad}.")
            input("Presione Enter para continuar...")
            return
        
        # Mostrar resultados
        print("\n" + "=" * 120)
        print(f"SEDES EN {ciudad.upper()}".center(120))
        print("=" * 120)
        
        # Encabezados
        print(f"{'ID':<5} | {'NOMBRE':<20} | {'CIUDAD':<20} | {'DIRECCIÓN':<30} | {'TELÉFONO':<15} | {'ESTADO':<10}")
        print("-" * 120)
        
        # Datos
        for sede in sedes:
            estado = 'Activa' if sede.activo else 'Inactiva'
            print(f"{str(sede.id_sede)[:5]:<5} | {sede.nombre[:18]:<20} | {sede.ciudad[:18]:<20} | {sede.direccion[:28]:<30} | {sede.telefono[:15]:<15} | {estado:<10}")
        
        print("=" * 120)
        
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
        
        # Solicitar datos
        print("\nIngrese los datos de la nueva sede:")
        print("-" * 40)
        
        nombre = input("Nombre de la sede: ").strip()
        ciudad = input("Ciudad: ").strip()
        direccion = input("Dirección: ").strip()
        telefono = input("Teléfono: ").strip()
        
        # Validar campos obligatorios
        if not all([nombre, ciudad, direccion, telefono]):
            print("\nError: Todos los campos son obligatorios.")
            input("Presione Enter para continuar...")
            return
        
        # Crear diccionario con los datos
        sede_data = {
            "nombre": nombre,
            "ciudad": ciudad,
            "direccion": direccion,
            "telefono": telefono,
            "activo": True
        }
        
        # Crear una instancia de SedeCreate
        sede_obj = SedeCreate(**sede_data)

        # Crear la sede con el ID del administrador
        sede = sede_crud.crear(db, obj_in=sede_obj, creado_por=id_administrador)
        
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
        
        # Obtener la sede
        sede = sede_crud.obtener_por_id(db, id=id_sede)
        
        if not sede:
            print("\nError: No se encontró ninguna sede con ese ID.")
            input("Presione Enter para continuar...")
            return
        
        # Mostrar datos actuales
        print("\n" + "=" * 80)
        print("EDITAR SEDE".center(80))
        print("=" * 80)
        print(f"ID: {sede.id_sede}")
        print(f"Ciudad actual: {sede.ciudad}")
        print(f"Dirección actual: {sede.direccion}")
        print(f"Teléfono actual: {sede.telefono}")
        print("-" * 40)
        print("Ingrese los nuevos valores (deje en blanco para mantener el actual):")
        print("-" * 40)
        
        # Solicitar nuevos datos
        nueva_ciudad = input(f"Nueva ciudad [{sede.ciudad}]: ").strip()
        nueva_direccion = input(f"Nueva dirección [{sede.direccion}]: ").strip()
        nuevo_telefono = input(f"Nuevo teléfono [{sede.telefono}]: ").strip()
        
        # Actualizar solo los campos que cambiaron
        datos_actualizados = {}
            
        if nueva_ciudad and nueva_ciudad != sede.ciudad:
            datos_actualizados["ciudad"] = nueva_ciudad
            
        if nueva_direccion and nueva_direccion != sede.direccion:
            datos_actualizados["direccion"] = nueva_direccion
            
        if nuevo_telefono and nuevo_telefono != sede.telefono:
            datos_actualizados["telefono"] = nuevo_telefono
        
        # Si hay datos para actualizar, proceder
        if datos_actualizados:
            sede_actualizada = sede_crud.actualizar(db, db_obj=sede, obj_in=datos_actualizados)
            print("\nSede actualizada correctamente.")
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
        
        # Obtener la sede
        sede = sede_crud.obtener_por_id(db, id=id_sede)
        
        if not sede:
            print("\nError: No se encontró ninguna sede con ese ID.")
            input("Presione Enter para continuar...")
            return
        
        # Mostrar estado actual
        print("\n" + "=" * 80)
        print("CAMBIAR ESTADO DE SEDE".center(80))
        print("=" * 80)
        print(f"ID: {sede.id_sede}")
        print(f"Ciudad: {sede.ciudad}")
        print(f"Dirección: {sede.direccion}")
        print(f"Estado actual: {'ACTIVA' if sede.activo else 'INACTIVA'}")
        print("=" * 80)
        
        # Confirmar cambio de estado
        confirmar = input(f"\n¿Desea {'DESACTIVAR' if sede.activo else 'ACTIVAR'} esta sede? (s/n): ").strip().lower()
        
        if confirmar == 's':
            nuevo_estado = not sede.activo
            sede_actualizada = sede_crud.actualizar(
                db, 
                db_obj=sede, 
                obj_in={"activo": nuevo_estado}
            )
            
            print(f"\nSede {'activada' if nuevo_estado else 'desactivada'} correctamente.")
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
        
        if opcion == '1':
            listar_sedes(db)
        elif opcion == '2':
            buscar_sede_por_ciudad(db)
        elif opcion == '3':
            if not usuario_actual:
                print("\nError: No se pudo identificar al administrador actual.")
                input("Presione Enter para continuar...")
                continue
            agregar_sede(db, id_administrador=usuario_actual.get('id_usuario'))
        elif opcion == '4':
            editar_sede(db)
        elif opcion == '5':
            cambiar_estado_sede(db)
        elif opcion == '0':
            break
        else:
            print("\nOpción no válida. Intente de nuevo.")
            input("Presione Enter para continuar...")
