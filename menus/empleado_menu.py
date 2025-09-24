"""
Módulo que contiene las funciones del menú de gestión de empleados.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError
from cruds.empleado_crud import empleado as empleado_crud
from cruds.usuario_crud import usuario as usuario_crud
from cruds.rol_crud import rol as rol_crud


def mostrar_menu_empleados() -> None:
    """Muestra el menú de gestión de empleados."""
    print("\n" + "=" * 80)
    print("GESTIÓN DE EMPLEADOS".center(80))
    print("=" * 80)
    print("1. Listar empleados")
    print("2. Buscar empleado")
    print("3. Registrar nuevo empleado")
    print("4. Editar empleado")
    print("5. Desactivar/activar empleado")
    print("0. Volver al menú principal")
    print("=" * 80)


def listar_empleados(db: Session) -> None:
    """Lista todos los empleados del sistema."""
    try:
        empleados = empleado_crud.obtener_activos(db)

        if not empleados:
            print("\nNo hay empleados registrados en el sistema.")
            return

        datos_empleados = []
        for empleado in empleados:
            nombre_tipo_doc = "N/A"
            if hasattr(empleado, "tipo_documento_rel") and empleado.tipo_documento_rel:
                nombre_tipo_doc = empleado.tipo_documento_rel.nombre

            datos_empleados.append(
                [
                    empleado.id_empleado,
                    f"{empleado.primer_nombre} {empleado.primer_apellido}",
                    empleado.documento,
                    nombre_tipo_doc,
                    empleado.correo,
                    empleado.telefono,
                    "Activo" if empleado.activo else "Inactivo",
                ]
            )

        col_id = 38
        col_nombre = 25
        col_documento = 15
        col_tipo_doc = 10
        col_correo = 30
        col_telefono = 15
        col_estado = 10

        headers = [
            "ID",
            "Nombre Completo",
            "Documento",
            "Tipo Doc.",
            "Correo",
            "Teléfono",
            "Estado",
        ]
        header_line = (
            f"{headers[0]:<{col_id}} | "
            f"{headers[1]:<{col_nombre}} | "
            f"{headers[2]:<{col_documento}} | "
            f"{headers[3]:<{col_tipo_doc}} | "
            f"{headers[4]:<{col_correo}} | "
            f"{headers[5]:<{col_telefono}} | "
            f"{headers[6]:<{col_estado}}"
        )
        print(header_line)
        print("-" * len(header_line))

        for empleado_data in datos_empleados:
            row_line = (
                f"{str(empleado_data[0]):<{col_id}} | "
                f"{empleado_data[1]:<{col_nombre}} | "
                f"{empleado_data[2]:<{col_documento}} | "
                f"{empleado_data[3]:<{col_tipo_doc}} | "
                f"{empleado_data[4]:<{col_correo}} | "
                f"{empleado_data[5]:<{col_telefono}} | "
                f"{empleado_data[6]:<{col_estado}}"
            )
            print(row_line)

    except Exception as e:
        print(f"\nError al listar empleados: {str(e)}")

    input("\nPresione Enter para continuar...")


def buscar_empleado(db: Session) -> None:
    """Busca un empleado por documento o nombre."""
    try:
        termino = input("\nIngrese el número de documento del empleado: ").strip()

        if not termino:
            print("\nError: Debe ingresar un término de búsqueda.")
            input("Presione Enter para continuar...")
            return

        empleados = empleado_crud.obtener_por_documento(db, termino)

        if not empleados:
            print("\nNo se encontraron empleados con el criterio de búsqueda.")
            input("Presione Enter para continuar...")
            return
        print("\n" + "=" * 100)
        print("RESULTADOS DE BÚSQUEDA".center(100))
        print("=" * 100)

        print(f"{'ID':<38} | {'NOMBRE COMPLETO':<40} | {'TIPO EMPLEADO':<15} | ESTADO")
        print("-" * 100)

        for empleado in empleados:
            nombres = [empleado.primer_nombre or "", empleado.segundo_nombre or ""]
            apellidos = [
                empleado.primer_apellido or "",
                empleado.segundo_apellido or "",
            ]
            nombre_completo = " ".join(filter(None, [*nombres, *apellidos]))

            tipo_doc = getattr(
                getattr(empleado, "tipo_documento_rel", None), "nombre", "N/A"
            )

            print(
                f"{str(empleado.id_empleado):<38} | {nombre_completo[:38]:<40} | {getattr(empleado, 'tipo_empleado', 'N/A')[:13]:<15} | {'✅ Activo' if empleado.activo else '❌ Inactivo'}"
            )

            print(f"   Documento: {tipo_doc} {getattr(empleado, 'documento', 'N/A')}")
            print(f"   Correo: {getattr(empleado, 'correo', 'Sin correo')}")
            print(f"   Teléfono: {getattr(empleado, 'telefono', 'Sin teléfono')}")

            if hasattr(empleado, "sede") and empleado.sede:
                print(f"   Sede: {empleado.sede.nombre} ({empleado.sede.ciudad})")

            print("-" * 100)

        print(f"\nTotal de empleados encontrados: {len(empleados)}")
        print("=" * 100)

    except Exception as e:
        print(f"\nError al buscar empleado: {str(e)}")

    input("\nPresione Enter para continuar...")


def registrar_empleado(db: Session, id_administrador: str = None) -> None:
    """
    Registra un nuevo empleado en el sistema.

    Args:
        db: Sesión de base de datos
        id_administrador: ID del administrador que está realizando el registro
    """
    if not id_administrador:
        print("\nError: Se requiere el ID del administrador para realizar esta acción.")
        input("Presione Enter para continuar...")
        return

    try:
        from cruds.tipo_documento_crud import tipo_documento as tipo_documento_crud

        print("\n" + "=" * 80)
        print("REGISTRAR NUEVO EMPLEADO".center(80))
        print("=" * 80)

        tipos_documento = tipo_documento_crud.obtener_todos(db)
        if not tipos_documento:
            print("\nError: No hay tipos de documento registrados en el sistema.")
            input("Presione Enter para continuar...")
            return

        print("\nTipos de documento disponibles:")
        print("-" * 40)
        for i, tipo in enumerate(tipos_documento, 1):
            print(f"{i}. ID: {tipo.id_tipo_documento}")
            print(f"   Nombre: {getattr(tipo, 'nombre', 'No disponible')}")
            print(f"   Código: {getattr(tipo, 'codigo', 'No disponible')}")
            print(f"   Activo: {'Sí' if getattr(tipo, 'activo', False) else 'No'}")
            print("-" * 40)

        while True:
            try:
                opcion = int(input("\nSeleccione el tipo de documento: ")) - 1
                if 0 <= opcion < len(tipos_documento):
                    tipo_documento = tipos_documento[opcion]
                    break
                print("Opción no válida. Intente de nuevo.")
            except ValueError:
                print("Por favor ingrese un número válido.")

        # Función para validar todos los campos
        def validar_datos_empleado(datos):
            errores = []
            import re

            # Validar número de documento
            if not datos["numero_documento"] or len(datos["numero_documento"]) < 5:
                errores.append("Número de documento: Debe tener al menos 5 dígitos")
            elif not datos["numero_documento"].isdigit():
                errores.append("Número de documento: Solo debe contener números")

            # Validar primer nombre
            if not datos["primer_nombre"] or len(datos["primer_nombre"]) < 2:
                errores.append("Primer nombre: Debe tener al menos 2 caracteres")
            elif not datos["primer_nombre"].replace(" ", "").isalpha():
                errores.append("Primer nombre: Solo debe contener letras")

            # Validar segundo nombre (opcional)
            if datos["segundo_nombre"] and len(datos["segundo_nombre"]) < 2:
                errores.append("Segundo nombre: Debe tener al menos 2 caracteres")
            elif (
                datos["segundo_nombre"]
                and not datos["segundo_nombre"].replace(" ", "").isalpha()
            ):
                errores.append("Segundo nombre: Solo debe contener letras")

            # Validar primer apellido
            if not datos["primer_apellido"] or len(datos["primer_apellido"]) < 2:
                errores.append("Primer apellido: Debe tener al menos 2 caracteres")
            elif not datos["primer_apellido"].replace(" ", "").isalpha():
                errores.append("Primer apellido: Solo debe contener letras")

            # Validar segundo apellido (opcional)
            if datos["segundo_apellido"] and len(datos["segundo_apellido"]) < 2:
                errores.append("Segundo apellido: Debe tener al menos 2 caracteres")
            elif (
                datos["segundo_apellido"]
                and not datos["segundo_apellido"].replace(" ", "").isalpha()
            ):
                errores.append("Segundo apellido: Solo debe contener letras")

            # Validar correo
            patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not datos["correo"] or not re.match(patron_email, datos["correo"]):
                errores.append("Correo: Formato de correo electrónico inválido")

            # Validar teléfono
            if not datos["telefono"] or len(datos["telefono"]) < 7:
                errores.append("Teléfono: Debe tener al menos 7 dígitos")
            elif not datos["telefono"].isdigit():
                errores.append("Teléfono: Solo debe contener números")

            # Validar dirección
            if not datos["direccion"] or len(datos["direccion"]) < 5:
                errores.append("Dirección: Debe tener al menos 5 caracteres")

            # Validar salario
            try:
                salario_val = float(datos["salario"])
                if salario_val <= 0:
                    errores.append("Salario: Debe ser mayor a cero")
                elif salario_val > 50000000:
                    errores.append("Salario: No puede exceder 50,000,000")
            except (ValueError, TypeError):
                errores.append("Salario: Debe ser un número válido")

            return errores

        # Bucle principal para capturar datos con validación
        while True:
            print("\nIngrese los datos del empleado:")
            print("-" * 40)

            numero_documento = input("Número de documento: ").strip()
            primer_nombre = input("Primer nombre: ").strip()
            segundo_nombre = (
                input("Segundo nombre (opcional, presione Enter para omitir): ").strip()
                or None
            )
            primer_apellido = input("Primer apellido: ").strip()
            segundo_apellido = (
                input(
                    "Segundo apellido (opcional, presione Enter para omitir): "
                ).strip()
                or None
            )

            while True:
                try:
                    fecha_nac_str = input("Fecha de nacimiento (YYYY-MM-DD): ").strip()
                    from datetime import datetime

                    fecha_nacimiento = datetime.strptime(
                        fecha_nac_str, "%Y-%m-%d"
                    ).date()
                    break
                except ValueError:
                    print("Formato de fecha inválido. Use YYYY-MM-DD.")

            correo = input("Correo electrónico: ").strip().lower()
            telefono = input("Teléfono: ").strip()
            direccion = input("Dirección: ").strip()
            salario = input("Salario: ").strip()

            # Validar todos los datos
            datos_temp = {
                "numero_documento": numero_documento,
                "primer_nombre": primer_nombre,
                "segundo_nombre": segundo_nombre,
                "primer_apellido": primer_apellido,
                "segundo_apellido": segundo_apellido,
                "correo": correo,
                "telefono": telefono,
                "direccion": direccion,
                "salario": salario,
            }

            errores = validar_datos_empleado(datos_temp)

            if errores:
                print("\n❌ Errores encontrados:")
                for i, error in enumerate(errores, 1):
                    print(f"  {i}. {error}")
                print("\nPor favor corrija los errores e intente nuevamente.")
                continuar = (
                    input("\n¿Desea intentar nuevamente? (s/n): ").strip().lower()
                )
                if continuar != "s":
                    print("Operación cancelada.")
                    return
                continue
            else:
                print("\n✅ Todos los datos son válidos.")
                # Convertir salario a float después de validación
                salario = float(salario)
                break

        print("\nTipos de empleado disponibles:")
        print("1. Mensajero")
        print("2. Logístico")
        print("3. Secretario")
        print("4. Administrativo")

        tipo_empleado_opciones = {
            "1": "mensajero",
            "2": "logistico",
            "3": "secretario",
            "4": "administrativo",
        }

        while True:
            opcion = input("Seleccione el tipo de empleado (1-4): ").strip()
            if opcion in tipo_empleado_opciones:
                tipo_empleado = tipo_empleado_opciones[opcion]
                break
            print("Opción no válida. Intente nuevamente.")

        from datetime import date

        fecha_ingreso = date.today()
        print(f"Fecha de ingreso: {fecha_ingreso} (fecha actual)")

        print("\nResumen de datos:")
        print(
            f"Nombre: {primer_nombre} {segundo_nombre or ''} {primer_apellido} {segundo_apellido or ''}"
        )
        print(f"Documento: {numero_documento}")
        print(f"Fecha de nacimiento: {fecha_nacimiento}")
        print(f"Correo: {correo}")
        print(f"Teléfono: {telefono}")
        print(f"Dirección: {direccion}")
        print(f"Tipo de empleado: {tipo_empleado}")
        print(f"Salario: {salario}")
        print(f"Fecha de ingreso: {fecha_ingreso}")

        print("\n" + "=" * 50)
        print("DATOS DE ACCESO AL SISTEMA")
        print("=" * 50)

        # Solicitar nombre de usuario
        while True:
            nombre_usuario = input(
                "Nombre de usuario (solo letras, números, _ y .): "
            ).strip()
            if not nombre_usuario:
                print("El nombre de usuario no puede estar vacío.")
                continue
            if len(nombre_usuario) < 3:
                print("El nombre de usuario debe tener al menos 3 caracteres.")
                continue
            # Validación básica del formato
            import re

            if not re.match(r"^[a-zA-Z0-9._]+$", nombre_usuario):
                print(
                    "El nombre de usuario solo puede contener letras, números, guiones bajos (_) y puntos (.)."
                )
                continue

            # Verificar que no exista ya el usuario
            from cruds.usuario_crud import usuario as usuario_crud_temp

            usuario_existente = usuario_crud_temp.obtener_por_nombre_usuario(
                db, nombre_usuario
            )
            if usuario_existente:
                print("Error: Ya existe un usuario con ese nombre. Intente con otro.")
                continue
            break

        # Solicitar contraseña
        while True:
            from getpass import getpass

            password = getpass(
                "Contraseña (mín. 8 caracteres, 1 mayúscula, 1 número): "
            )
            if not password:
                print("La contraseña no puede estar vacía.")
                continue
            if len(password) < 8:
                print("La contraseña debe tener al menos 8 caracteres.")
                continue
            if not re.search(r"[A-Z]", password):
                print("La contraseña debe contener al menos una letra mayúscula.")
                continue
            if not re.search(r"[0-9]", password):
                print("La contraseña debe contener al menos un número.")
                continue

            # Confirmar contraseña
            password_confirm = getpass("Confirme la contraseña: ")
            if password != password_confirm:
                print("Las contraseñas no coinciden. Intente de nuevo.")
                continue
            break

        print("\n" + "=" * 50)
        print("RESUMEN COMPLETO")
        print("=" * 50)
        print(
            f"Nombre: {primer_nombre} {segundo_nombre or ''} {primer_apellido} {segundo_apellido or ''}".strip()
        )
        print(f"Documento: {numero_documento}")
        print(f"Correo: {correo}")
        print(f"Teléfono: {telefono}")
        print(f"Tipo de empleado: {tipo_empleado}")
        print(f"Salario: {salario}")
        print(f"Nombre de usuario: {nombre_usuario}")

        confirmar = input("\n¿Los datos son correctos? (s/n): ").strip().lower()
        if confirmar != "s":
            print("Operación cancelada por el usuario.")
            return

        from uuid import uuid4
        from cruds.usuario_crud import usuario as usuario_crud
        from entities.usuario import UsuarioCreate

        # Primero obtener el rol de empleado
        from entities.rol import Rol

        rol_empleado = db.query(Rol).filter(Rol.nombre_rol == "empleado").first()
        if not rol_empleado:
            print("Error: No se encontró el rol de empleado en el sistema.")
            input("Presione Enter para continuar...")
            return

        # Crear el usuario
        try:
            usuario_data = UsuarioCreate(
                nombre_usuario=nombre_usuario,
                password=password,
                id_rol=str(rol_empleado.id_rol),
            )

            usuario = usuario_crud.crear_usuario(db=db, datos_usuario=usuario_data)
            id_usuario = str(usuario.id_usuario)
        except ValidationError as e:
            print(f"\n❌ Error de validación en datos del usuario:")
            for error in e.errors():
                field = error["loc"][0] if error["loc"] else "campo"
                message = error["msg"]
                print(f"  - {field}: {message}")
            input("Presione Enter para continuar...")
            return
        except Exception as e:
            print(f"❌ Error al crear usuario: {str(e)}")
            input("Presione Enter para continuar...")
            return

        empleado_data = {
            "tipo_documento": str(tipo_documento.id_tipo_documento),
            "documento": numero_documento,
            "primer_nombre": primer_nombre,
            "segundo_nombre": segundo_nombre,
            "primer_apellido": primer_apellido,
            "segundo_apellido": segundo_apellido,
            "fecha_nacimiento": fecha_nacimiento,
            "correo": correo,
            "telefono": telefono,
            "direccion": direccion,
            "tipo_empleado": tipo_empleado,
            "salario": salario,
            "fecha_ingreso": fecha_ingreso,
        }

        from entities.empleado import EmpleadoCreate
        from uuid import UUID

        try:
            empleado_create = EmpleadoCreate(**empleado_data)
        except ValidationError as e:
            print(f"\n❌ Error de validación en datos del empleado:")
            for error in e.errors():
                field = error["loc"][0] if error["loc"] else "campo"
                message = error["msg"]
                print(f"  - {field}: {message}")
            input("Presione Enter para continuar...")
            return
        except Exception as e:
            print(f"\n❌ Error al crear modelo EmpleadoCreate: {str(e)}")
            input("Presione Enter para continuar...")
            return

        try:

            empleado = empleado_crud.crear_registro(
                db=db,
                datos_entrada=empleado_create,
                usuario_id=UUID(id_usuario),
                creado_por=UUID(id_administrador),
            )

            if not empleado:
                print("\n Error: El método crear_registro devolvió None.")
                print("Posibles causas:")
                print("- El usuario ya tiene un empleado asociado")
                print("- Error en la validación de datos")
                print("- Problema con la base de datos")
                input("Presione Enter para continuar...")
                return

            print(f"\n Empleado creado exitosamente!")
            print(f"ID Empleado: {empleado.id_empleado}")
            print(f"Nombre: {empleado.primer_nombre} {empleado.primer_apellido}")

        except Exception as e:
            print(f"\n Error al crear el empleado: {str(e)}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback

            print("Detalles del error:")
            traceback.print_exc()
            input("Presione Enter para continuar...")
            return

        print(f"\n ¡Empleado y usuario creados exitosamente!")
        print(f"ID Empleado: {empleado.id_empleado}")
        print(f"Usuario: {nombre_usuario}")
        print(f"El empleado puede iniciar sesión con sus credenciales.")

    except Exception as e:
        print(f"\nError general al registrar empleado: {str(e)}")

    input("\nPresione Enter para continuar...")


def editar_empleado(db: Session) -> None:
    """Permite editar los datos de un empleado."""
    try:
        id_empleado = input("\nIngrese el ID del empleado a editar: ").strip()

        if not id_empleado:
            print("\nError: Debe ingresar un ID de empleado.")
            input("Presione Enter para continuar...")
            return

        empleado = empleado_crud.obtener_por_id(db, id=id_empleado)

        if not empleado:
            print("\nError: No se encontró ningún empleado con ese ID.")
            input("Presione Enter para continuar...")
            return

        print("\n" + "=" * 80)
        print("EDITAR EMPLEADO".center(80))
        print("=" * 80)
        print(
            f"Nombre: {empleado.primer_nombre} {empleado.segundo_nombre or ''} {empleado.primer_apellido} {empleado.segundo_apellido or ''}"
        )
        print(
            f"Documento: {empleado.tipo_documento.nombre if empleado.tipo_documento else 'N/A'} {empleado.numero_documento}"
        )
        print(f"Correo: {empleado.correo}")
        print(f"Teléfono: {empleado.telefono}")
        print(f"Dirección: {empleado.direccion}")
        print(
            "\nIngrese los nuevos valores (deje en blanco para mantener el valor actual):"
        )
        print("-" * 40)

        nuevo_correo = input(f"Nuevo correo [{empleado.correo}]: ").strip()
        nuevo_telefono = input(f"Nuevo teléfono [{empleado.telefono}]: ").strip()
        nueva_direccion = input(f"Nueva dirección [{empleado.direccion}]: ").strip()

        datos_actualizados = {}

        if nuevo_correo and nuevo_correo != empleado.correo:
            datos_actualizados["correo"] = nuevo_correo

        if nuevo_telefono and nuevo_telefono != empleado.telefono:
            datos_actualizados["telefono"] = nuevo_telefono

        if nueva_direccion and nueva_direccion != empleado.direccion:
            datos_actualizados["direccion"] = nueva_direccion

        if datos_actualizados:
            empleado_actualizado = empleado_crud.update(
                db, db_obj=empleado, obj_in=datos_actualizados
            )
            print("\nEmpleado actualizado correctamente.")
        else:
            print("\nNo se realizaron cambios.")

    except Exception as e:
        print(f"\nError al editar empleado: {str(e)}")

    input("\nPresione Enter para continuar...")


def cambiar_estado_empleado(db: Session) -> None:
    """Activa o desactiva un empleado."""
    try:
        id_empleado = input(
            "\nIngrese el ID del empleado a activar/desactivar: "
        ).strip()

        if not id_empleado:
            print("\nError: Debe ingresar un ID de empleado.")
            input("Presione Enter para continuar...")
            return

        empleado = empleado_crud.obtener_por_id(db, id=id_empleado)

        if not empleado:
            print("\nError: No se encontró ningún empleado con ese ID.")
            input("Presione Enter para continuar...")
            return

        print("\n" + "=" * 80)
        print("CAMBIAR ESTADO DE EMPLEADO".center(80))
        print("=" * 80)
        print(f"Empleado: {empleado.primer_nombre} {empleado.primer_apellido}")
        print(
            f"Documento: {empleado.tipo_documento.nombre if empleado.tipo_documento else 'N/A'} {empleado.numero_documento}"
        )
        print(f"Estado actual: {'ACTIVO' if empleado.activo else 'INACTIVO'}")
        print("=" * 80)

        confirmar = (
            input(
                f"\n¿Desea {'DESACTIVAR' if empleado.activo else 'ACTIVAR'} este empleado? (s/n): "
            )
            .strip()
            .lower()
        )

        if confirmar == "s":
            nuevo_estado = not empleado.activo
            empleado_actualizado = empleado_crud.actualizar(
                db, db_obj=empleado, obj_in={"activo": nuevo_estado}
            )

            if not nuevo_estado and empleado.usuario:
                from cruds.usuario_crud import usuario as usuario_crud

                usuario_crud.actualizar_usuario(
                    db, db_obj=empleado.usuario, obj_in={"activo": False}
                )
                print("\nUsuario asociado también ha sido desactivado.")

            print(
                f"\nEmpleado {'activado' if nuevo_estado else 'desactivado'} correctamente."
            )
        else:
            print("\nOperación cancelada.")

    except Exception as e:
        print(f"\nError al cambiar el estado del empleado: {str(e)}")

    input("\nPresione Enter para continuar...")


def manejar_menu_empleados(db: Session, id_administrador: str = None) -> None:
    """
    Maneja el menú de gestión de empleados.

    Args:
        db: Sesión de base de datos
        id_administrador: ID del administrador que está realizando las acciones
    """
    while True:
        mostrar_menu_empleados()

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            listar_empleados(db)
        elif opcion == "2":
            buscar_empleado(db)
        elif opcion == "3":
            admin_id = id_administrador
            if not admin_id:
                admin_id = input("\nIngrese el ID del administrador: ").strip()
                if not admin_id:
                    print("Error: Se requiere el ID del administrador.")
                    input("Presione Enter para continuar...")
                    continue
            registrar_empleado(db, id_administrador=admin_id)
        elif opcion == "4":
            editar_empleado(db)
        elif opcion == "5":
            cambiar_estado_empleado(db)
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida. Intente de nuevo.")
            input("Presione Enter para continuar...")

        print(f"\nError al cambiar el estado del empleado: {str(e)}")

    input("\nPresione Enter para continuar...")


def manejar_menu_empleados(db: Session, id_administrador: str = None) -> None:
    """
    Maneja el menú de gestión de empleados.

    Args:
        db: Sesión de base de datos
        id_administrador: ID del administrador que está realizando las acciones
    """
    while True:
        mostrar_menu_empleados()

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            listar_empleados(db)
        elif opcion == "2":
            buscar_empleado(db)
        elif opcion == "3":
            admin_id = id_administrador
            if not admin_id:
                admin_id = input("\nIngrese el ID del administrador: ").strip()
                if not admin_id:
                    print("Error: Se requiere el ID del administrador.")
                    input("Presione Enter para continuar...")
                    continue
            registrar_empleado(db, id_administrador=admin_id)
        elif opcion == "4":
            editar_empleado(db)
        elif opcion == "5":
            cambiar_estado_empleado(db)
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida. Intente de nuevo.")
            input("Presione Enter para continuar...")
