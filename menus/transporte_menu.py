"""
Módulo para las funciones del menú de gestión de transportes.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import ValidationError
from uuid import UUID

from cruds.transporte_crud import transporte as transporte_crud
from cruds.sede_crud import sede as sede_crud
from entities.transporte import TransporteCreate, TransporteUpdate


def mostrar_encabezado(titulo: str = ""):
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 80)
    if titulo:
        print(f"{titulo:^80}")
        print("=" * 80)


def listar_transportes(db: Session) -> None:
    """Lista todos los transportes en el sistema."""
    mostrar_encabezado("LISTADO DE TRANSPORTES")
    try:
        transportes, total = transporte_crud.obtener_todos(db)
        if not transportes:
            print("No hay transportes registrados.")
            input("\nPresione Enter para continuar...")
            return

        col_id = 38
        col_vehiculo = 20
        col_placa = 12
        col_tipo = 15
        col_capacidad = 15
        col_estado = 15
        col_activo = 10

        headers = ["ID", "Vehículo", "Placa", "Tipo", "Capacidad", "Estado", "Activo"]
        header_line = (
            f"{headers[0]:<{col_id}} | "
            f"{headers[1]:<{col_vehiculo}} | "
            f"{headers[2]:<{col_placa}} | "
            f"{headers[3]:<{col_tipo}} | "
            f"{headers[4]:<{col_capacidad}} | "
            f"{headers[5]:<{col_estado}} | "
            f"{headers[6]:<{col_activo}}"
        )
        print(header_line)
        print("-" * len(header_line))

        for t in transportes:
            vehiculo = f"{t.marca} {t.modelo}"
            capacidad = f"{t.capacidad_carga} kg"
            estado = t.estado.title()
            activo = "Activo" if t.activo else "Inactivo"

            row_line = (
                f"{str(t.id_transporte):<{col_id}} | "
                f"{vehiculo:<{col_vehiculo}} | "
                f"{t.placa:<{col_placa}} | "
                f"{t.tipo_vehiculo:<{col_tipo}} | "
                f"{capacidad:<{col_capacidad}} | "
                f"{estado:<{col_estado}} | "
                f"{activo:<{col_activo}}"
            )
            print(row_line)

    except Exception as e:
        print(f"\nError al listar transportes: {str(e)}")

    input("\nPresione Enter para continuar...")


def buscar_transporte_por_placa(db: Session) -> None:
    """Busca un transporte por su placa."""
    mostrar_encabezado("BUSCAR TRANSPORTE POR PLACA")
    placa = input("\nIngrese la placa del vehículo a buscar: ").strip().upper()
    if not placa:
        print("Debe ingresar una placa.")
        input("\nPresione Enter para continuar...")
        return

    transporte = transporte_crud.obtener_por_placa(db, placa=placa)
    if not transporte:
        print("\nNo se encontró ningún vehículo con esa placa.")
    else:
        print("\nDetalles del vehículo:")
        print(f"ID: {transporte.id_transporte}")
        print(f"Tipo: {transporte.tipo_vehiculo}")
        print(f"Marca: {transporte.marca}")
        print(f"Modelo: {transporte.modelo}")
        print(f"Año: {transporte.año}")
        print(f"Placa: {transporte.placa}")
        print(f"Capacidad: {transporte.capacidad_carga} kg")
        print(f"Estado: {transporte.estado.title()}")
        print(f"Activo: {'Sí' if transporte.activo else 'No'}")
        if transporte.id_sede:
            sede = sede_crud.obtener_por_id(db, id=transporte.id_sede)
            if sede:
                print(f"\nAsignado a sede: {sede.ciudad} - {sede.direccion}")

    input("\nPresione Enter para continuar...")


def agregar_transporte(db: Session, id_administrador: str) -> None:
    """Agrega un nuevo transporte."""
    mostrar_encabezado("AGREGAR NUEVO TRANSPORTE")
    tipos_vehiculo = ["moto", "furgoneta", "camioneta", "camión", "bicicleta"]

    try:
        print("\nSeleccione el tipo de vehículo:")
        for i, tipo in enumerate(tipos_vehiculo, 1):
            print(f"{i}. {tipo.capitalize()}")

        while True:
            try:
                opcion = input("\nOpción: ").strip()
                if not opcion.isdigit():
                    print("Por favor ingrese un número")
                    continue

                opcion = int(opcion)
                if 1 <= opcion <= len(tipos_vehiculo):
                    tipo_vehiculo = tipos_vehiculo[opcion - 1]
                    break
                print(f"Por favor ingrese un número entre 1 y {len(tipos_vehiculo)}")
            except Exception as e:
                print(f"Error: {str(e)}")

        marca = input("\nMarca: ").strip()
        modelo = input("Modelo: ").strip()
        placa = input("Placa: ").strip().upper()

        while True:
            año_str = input("Año: ").strip()
            try:
                año = int(año_str)
                if (
                    2002 <= año <= datetime.now().year + 1
                ):
                    break
                print(f"El año debe estar entre 2002 y {datetime.now().year + 1}")
            except ValueError:
                print("Por favor ingrese un año válido (número de 4 dígitos)")

        while True:
            capacidad_str = input("Capacidad de carga (kg): ").strip()
            try:
                capacidad_carga = float(capacidad_str)
                if capacidad_carga > 0:
                    break
                print("La capacidad de carga debe ser mayor a 0")
            except ValueError:
                print("Por favor ingrese un número válido para la capacidad")

        from cruds.sede_crud import sede as sede_crud

        sedes = sede_crud.obtener_activas(db)

        if not sedes:
            print("\nError: No hay sedes disponibles. Debe crear una sede primero.")
            return

        print("\nSeleccione la sede del vehículo:")
        for i, sede in enumerate(sedes, 1):
            print(f"{i}. {sede.ciudad} - {sede.direccion}")

        while True:
            try:
                opcion_sede = input("\nNúmero de sede: ").strip()
                if not opcion_sede.isdigit():
                    print("Por favor ingrese un número")
                    continue

                opcion_sede = int(opcion_sede)
                if 1 <= opcion_sede <= len(sedes):
                    sede_seleccionada = sedes[opcion_sede - 1]
                    break
                print(f"Por favor ingrese un número entre 1 y {len(sedes)}")
            except Exception as e:
                print(f"Error: {str(e)}")

        print(f"\nCreando transporte con sede_id: {sede_seleccionada.id_sede}")
        transporte_data = TransporteCreate(
            tipo_vehiculo=tipo_vehiculo,
            marca=marca,
            modelo=modelo,
            placa=placa,
            año=año,
            capacidad_carga=capacidad_carga,
            estado="disponible",
            activo=True,
            id_sede=str(sede_seleccionada.id_sede),
        )

        transporte_crud.crear(db, obj_in=transporte_data, creado_por=id_administrador)
        print("\n¡Transporte agregado exitosamente!")

    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
        import traceback

        traceback.print_exc()

    input("\nPresione Enter para continuar...")


def editar_transporte(db: Session) -> None:
    """Edita un transporte existente."""
    mostrar_encabezado("EDITAR TRANSPORTE")
    
    try:
        placa = input("\nIngrese la placa del vehículo a editar: ").strip().upper()
        if not placa:
            print("\nDebe ingresar una placa válida.")
            input("\nPresione Enter para continuar...")
            return
            
        transporte = transporte_crud.obtener_por_placa(db, placa=placa)

        if not transporte:
            print("\nNo se encontró ningún vehículo con esa placa.")
            input("\nPresione Enter para continuar...")
            return

        print("\nDatos actuales (deje en blanco para no modificar):")
        nuevo_estado = input(f"Estado [{transporte.estado}]: ").strip() or transporte.estado

        # Validar estado
        estados_validos = ['disponible', 'en_ruta', 'mantenimiento', 'fuera_servicio']
        if nuevo_estado.lower() not in estados_validos:
            print(f"\nEstado inválido. Estados válidos: {', '.join(estados_validos)}")
            input("\nPresione Enter para continuar...")
            return

        try:
            update_data = TransporteUpdate(estado=nuevo_estado.lower())
            
            # Usar un ID de administrador por defecto (debería venir del usuario actual)
            admin_id = UUID("00000000-0000-0000-0000-000000000000")
            
            transporte_crud.actualizar(
                db, 
                db_obj=transporte, 
                obj_in=update_data, 
                actualizado_por=admin_id
            )
            print("\n✅ ¡Transporte actualizado exitosamente!")
            
        except ValidationError as e:
            print(f"\n❌ Error de validación:")
            for error in e.errors():
                field = error['loc'][0] if error['loc'] else 'campo'
                message = error['msg']
                print(f"  - {field}: {message}")
        except Exception as e:
            print(f"\n❌ Error al actualizar transporte: {str(e)}")
            
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
    
    input("\nPresione Enter para continuar...")


def cambiar_estado_transporte(db: Session) -> None:
    """Cambia el estado (activo/inactivo) de un transporte."""
    mostrar_encabezado("CAMBIAR ESTADO DE TRANSPORTE")
    placa = input("\nIngrese la placa del vehículo: ").strip().upper()
    transporte = transporte_crud.obtener_por_placa(db, placa=placa)

    if not transporte:
        print("\nNo se encontró ningún vehículo con esa placa.")
        input("\nPresione Enter para continuar...")
        return

    nuevo_estado = not transporte.activo
    confirmar = input(
        f"¿Está seguro de {'activar' if nuevo_estado else 'desactivar'} el vehículo {placa}? (s/n): "
    ).lower()
    if confirmar == "s":
        try:
            update_data = TransporteUpdate(activo=nuevo_estado)
            admin_id = UUID("00000000-0000-0000-0000-000000000000")
            transporte_crud.actualizar(
                db, 
                db_obj=transporte, 
                obj_in=update_data, 
                actualizado_por=admin_id
            )
            print(
                f"\n✅ ¡Vehículo {placa} {'activado' if nuevo_estado else 'desactivado'} exitosamente!"
            )
        except Exception as e:
            print(f"\n❌ Error al cambiar estado del transporte: {str(e)}")
    else:
        print("\nOperación cancelada.")
    input("\nPresione Enter para continuar...")


def asignar_transporte_a_sede(db: Session) -> None:
    """Asigna un transporte a una sede."""
    mostrar_encabezado("ASIGNAR TRANSPORTE A SEDE")
    placa = input("\nIngrese la placa del vehículo: ").strip().upper()
    transporte = transporte_crud.obtener_por_placa(db, placa=placa)

    if not transporte:
        print("\nNo se encontró ningún vehículo con esa placa.")
        input("\nPresione Enter para continuar...")
        return

    sedes = sede_crud.obtener_activas(db)
    if not sedes:
        print("No hay sedes registradas.")
        input("\nPresione Enter para continuar...")
        return

    print("\nSedes disponibles:")
    for i, sede in enumerate(sedes, 1):
        print(f"{i}. {sede.ciudad} - {sede.direccion}")
    print("0. Desasignar de la sede actual")

    try:
        opcion = int(input("\nSeleccione la sede: "))
        if opcion == 0:
            transporte.id_sede = None
            print("\nVehículo desasignado.")
        elif 1 <= opcion <= len(sedes):
            transporte.id_sede = sedes[opcion - 1].id_sede
            print("\nVehículo asignado a la sede.")
        else:
            print("\nOpción no válida.")
            input("\nPresione Enter para continuar...")
            return

        db.commit()
    except ValueError:
        print("\nOpción no válida.")
    input("\nPresione Enter para continuar...")


def manejar_menu_transportes(db: Session, id_administrador: str) -> None:
    """Maneja el menú de gestión de transportes."""
    while True:
        mostrar_encabezado("GESTIÓN DE TRANSPORTES")
        print("1. Listar todos los transportes")
        print("2. Buscar transporte por placa")
        print("3. Agregar nuevo transporte")
        print("4. Editar transporte")
        print("5. Cambiar estado de transporte")
        print("6. Asignar transporte a sede")
        print("0. Volver al menú principal")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            listar_transportes(db)
        elif opcion == "2":
            buscar_transporte_por_placa(db)
        elif opcion == "3":
            agregar_transporte(db, id_administrador=id_administrador)
        elif opcion == "4":
            editar_transporte(db)
        elif opcion == "5":
            cambiar_estado_transporte(db)
        elif opcion == "6":
            asignar_transporte_a_sede(db)
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida.")
            input("Presione Enter para continuar...")
