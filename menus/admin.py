"""
Módulo para el menú de administradores.
"""

from entities.cliente import ClienteCreate
from cruds.cliente_crud import cliente as cliente_crud
from entities.usuario import UsuarioCreate, Usuario
from datetime import datetime, date
from typing import Any
from sqlalchemy.orm import Session
from cruds import usuario_crud
from entities.usuario import Usuario
from entities.rol import Rol
from menus.base import mostrar_encabezado, obtener_input, confirmar_accion
from cruds.usuario_crud import usuario as usuario_crud
from cruds.rol_crud import rol as rol_crud
from cruds.empleado_crud import empleado as empleado_crud
from entities.empleado import EmpleadoCreate
from cruds.sede_crud import sede as sede_crud
from cruds.tipo_documento_crud import tipo_documento as tipo_documento_crud
from cruds.paquete_crud import paquete as paquete_crud
from cruds.transporte_crud import transporte as transporte_crud
from .reportes import mostrar_reportes


def gestionar_usuarios(db: Session, admin_actual: Any) -> None:
    """
    Permite al administrador gestionar usuarios del sistema.
    """
    while True:
        mostrar_encabezado("GESTIÓN DE USUARIOS")
        print("1. Listar usuarios")
        print("2. Crear usuario")
        print("3. Editar usuario")
        print("4. Cambiar estado de usuario")
        print("0. Volver al menú principal")
        print("=" * 60)

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            listar_usuarios(db)
        elif opcion == "2":
            crear_usuario(db, admin_actual)
        elif opcion == "3":
            editar_usuario(db)
        elif opcion == "4":
            cambiar_estado_usuario(db)
        elif opcion == "0":
            break
        else:
            input("\nOpción inválida. Presione Enter para continuar...")


def editar_usuario(db: Session) -> None:
    """Permite editar la información de un usuario existente."""
    try:
        mostrar_encabezado("EDITAR USUARIO")

        # Listar usuarios primero
        usuarios = db.query(Usuario).all()
        if not usuarios:
            print("No hay usuarios registrados.")
            input("Presione Enter para volver...")
            return

        print("\nLista de usuarios:")
        for i, user in enumerate(usuarios, 1):
            print(f"{i}. {user.nombre_usuario} ({user.rol.nombre_rol})")

        try:
            opcion = int(
                input("\nSeleccione el número del usuario a editar (0 para cancelar): ")
            )
            if opcion == 0:
                return

            usuario = usuarios[opcion - 1] if 1 <= opcion <= len(usuarios) else None
            if not usuario:
                print("Opción inválida.")
                input("Presione Enter para continuar...")
                return

            print(f"\nEditando usuario: {usuario.nombre_usuario}")
            print("Deje en blanco los campos que no desea modificar.")

            nuevo_nombre = input(
                f"Nuevo nombre de usuario [{usuario.nombre_usuario}]: "
            ).strip()

            cambiar_password = (
                input("¿Desea cambiar la contraseña? (s/n): ").strip().lower()
            )
            nueva_password = None

            if cambiar_password == "s":
                while True:
                    nueva_password = obtener_input(
                        "Contraseña: ", requerido=True, password=True
                    )
                    confirmacion = obtener_input(
                        "Confirmar contraseña: ", requerido=True, password=True
                    )

                    if nueva_password != confirmacion:
                        print("Las contraseñas no coinciden. Intente de nuevo.")
                        continue
                    if len(nueva_password) < 8:
                        print("La contraseña debe tener al menos 8 caracteres.")
                        continue
                    break

            # Preparar datos de actualización
            update_data = {}
            if nuevo_nombre and nuevo_nombre != usuario.nombre_usuario:
                update_data["nombre_usuario"] = nuevo_nombre

            if nueva_password:
                update_data["password"] = nueva_password

            if not update_data:
                print("No se realizaron cambios.")
                input("Presione Enter para continuar...")
                return

            usuario_actualizado = usuario_crud.actualizar(
                db=db,
                objeto_db=usuario,
                datos_entrada=update_data,
                fecha_actualizacion=datetime.now(),
            )

            if usuario_actualizado:
                print("\n¡Usuario actualizado exitosamente!")
            else:
                raise Exception("No se pudo actualizar el usuario")

        except (ValueError, IndexError):
            print("Opción inválida.")

    except Exception as e:
        db.rollback()
        print(f"Error al editar el usuario: {e}")

    input("\nPresione Enter para continuar...")


def cambiar_estado_usuario(db: Session) -> None:
    """Permite activar o desactivar un usuario."""
    try:
        mostrar_encabezado("CAMBIAR ESTADO DE USUARIO")

        # Listar usuarios
        usuarios = db.query(Usuario).all()
        if not usuarios:
            print("No hay usuarios registrados.")
            input("Presione Enter para volver...")
            return

        print("\nLista de usuarios:")
        for i, user in enumerate(usuarios, 1):
            estado = "ACTIVO" if user.activo else "INACTIVO"
            print(f"{i}. {user.nombre_usuario} - Estado: {estado}")

        try:
            opcion = int(
                input("\nSeleccione el número del usuario (0 para cancelar): ")
            )
            if opcion == 0:
                return

            usuario = usuarios[opcion - 1] if 1 <= opcion <= len(usuarios) else None
            if not usuario:
                print("Opción inválida.")
                input("Presione Enter para continuar...")
                return

            # Mostrar estado actual y pedir confirmación
            accion = "desactivar" if usuario.activo else "activar"
            confirmacion = input(
                f"¿Está seguro de que desea {accion} al usuario {usuario.nombre_usuario}? (s/n): "
            )

            if confirmacion.lower() == "s":
                usuario.activo = not usuario.activo
                db.commit()
                estado = "activado" if usuario.activo else "desactivado"
                print(f"\n¡Usuario {estado} exitosamente!")
            else:
                print("Operación cancelada.")

        except (ValueError, IndexError):
            print("Opción inválida.")

    except Exception as e:
        db.rollback()
        print(f"Error al cambiar el estado del usuario: {e}")

    input("\nPresione Enter para continuar...")


def listar_usuarios(db: Session) -> None:
    """Muestra una lista de usuarios del sistema."""
    try:
        mostrar_encabezado("LISTA DE USUARIOS")

        # Obtener todos los usuarios con información de sus roles
        usuarios = usuario_crud.get_activos(db)

        if not usuarios:
            input("\nNo hay usuarios registrados. Presione Enter para continuar...")
            return

        print(f"\n{'Usuario':<20} {'Rol':<20} {'Estado':<10}")
        print("-" * 60)

        for usuario in usuarios:
            rol_nombre = usuario.rol.nombre_rol if usuario.rol else "Sin rol"
            estado = "Activo" if usuario.activo else "Inactivo"
            print(f"{usuario.nombre_usuario:<20} {rol_nombre:<20} {estado:<10}")

        input("\nPresione Enter para continuar...")

    except Exception as e:
        input(
            f"\nError al obtener la lista de usuarios: {str(e)}. Presione Enter para continuar..."
        )


def crear_usuario(db: Session, admin_actual: Any) -> None:
    """Permite crear un nuevo usuario."""
    try:

        mostrar_encabezado("CREAR NUEVO USUARIO")

        # Obtener datos del usuario
        nombre_usuario = obtener_input("Nombre de usuario: ", requerido=True)

        # Verificar si el usuario ya existe
        if usuario_crud.get_by_username(db, nombre_usuario):
            input(
                "\n¡Error! Este nombre de usuario ya está en uso. Presione Enter para continuar..."
            )
            return

        # Obtener contraseña
        while True:
            contrasena = obtener_input("Contraseña: ", requerido=True, password=True)
            confirmacion = obtener_input(
                "Confirmar contraseña: ", requerido=True, password=True
            )

            if contrasena != confirmacion:
                print("Las contraseñas no coinciden. Intente de nuevo.")
                continue
            if len(contrasena) < 8:
                print("La contraseña debe tener al menos 8 caracteres.")
                continue
            break

        # Mostrar roles disponibles
        print("\nRoles disponibles:")
        roles = rol_crud.obtener_todos(db)
        for i, rol in enumerate(roles, 1):
            print(f"{i}. {rol.nombre_rol}")

        # Seleccionar rol
        while True:
            try:
                opcion = (
                    int(
                        obtener_input(
                            "\nSeleccione el rol del usuario: ", requerido=True
                        )
                    )
                    - 1
                )
                if 0 <= opcion < len(roles):
                    rol_id = roles[opcion].id_rol
                    break
                print("Opción inválida. Intente de nuevo.")
            except ValueError:
                print("Por favor ingrese un número válido.")

        # Crear el objeto UsuarioCreate
        usuario_data = UsuarioCreate(
            nombre_usuario=nombre_usuario,
            password=contrasena,
            id_rol=str(rol_id),
            activo=True,
        )

        # Crear el usuario
        usuario = usuario_crud.crear(db=db, datos_entrada=usuario_data)

        # Si el rol es de empleado, crear también el registro de empleado
        if roles[opcion].nombre_rol.lower() == "empleado":
            mostrar_encabezado("INFORMACIÓN DEL EMPLEADO")

            # Obtener información personal
            primer_nombre = obtener_input("Primer nombre: ", requerido=True)
            segundo_nombre = obtener_input(
                "Segundo nombre (opcional): ", requerido=False
            )
            primer_apellido = obtener_input("Primer apellido: ", requerido=True)
            segundo_apellido = obtener_input(
                "Segundo apellido (opcional): ", requerido=False
            )

            tipos_doc = tipo_documento_crud.get_activos(db=db)

            if not tipos_doc:
                print(
                    "Error: No se encontraron tipos de documento en la base de datos."
                )
                return

            # Mostrar menú de tipos de documento
            print("\nSeleccione el tipo de documento:")
            for i, tipo in enumerate(tipos_doc, 1):
                print(f"{i}. {tipo.nombre}")

            # Seleccionar tipo de documento
            while True:
                try:
                    opcion_tipo = (
                        int(
                            obtener_input(
                                "\nSeleccione el tipo de documento: ", requerido=True
                            )
                        )
                        - 1
                    )
                    if 0 <= opcion_tipo < len(tipos_doc):
                        id_tipo_documento = tipos_doc[opcion_tipo].id_tipo_documento
                        break
                    print("Opción inválida. Intente de nuevo.")
                except ValueError:
                    print("Por favor ingrese un número válido.")

            # Obtener número de documento
            while True:
                documento = obtener_input("Número de documento: ", requerido=True)
                if documento.strip():
                    break
                print("El número de documento no puede estar vacío.")

            # Obtener fecha de nacimiento
            while True:
                try:
                    fecha_nac_str = obtener_input(
                        "Fecha de nacimiento (YYYY-MM-DD): ", requerido=True
                    )
                    fecha_nacimiento = datetime.strptime(
                        fecha_nac_str, "%Y-%m-%d"
                    ).date()
                    break
                except ValueError:
                    print("Formato de fecha inválido. Use YYYY-MM-DD")

            # Obtener información de contacto
            telefono = obtener_input("Teléfono: ", requerido=True)
            correo = obtener_input("Correo electrónico: ", requerido=True)
            direccion = obtener_input("Dirección: ", requerido=True)

            # Obtener lista de sedes activas
            sedes = sede_crud.get_activas(db)
            if not sedes:
                input(
                    "\nNo hay sedes activas. Debe crear una sede primero. Presione Enter para continuar..."
                )
                return

            # Mostrar menú de sedes
            print("\nSeleccione la sede del empleado:")
            for i, sede in enumerate(sedes, 1):
                print(f"{i}. {sede.ciudad} - {sede.direccion}")
            # Seleccionar sede
            while True:
                try:
                    opcion_sede = (
                        int(obtener_input("\nSeleccione una sede: ", requerido=True))
                        - 1
                    )
                    if 0 <= opcion_sede < len(sedes):
                        id_sede = sedes[opcion_sede].id_sede
                        break
                    print("Opción inválida. Intente de nuevo.")
                except ValueError:
                    print("Por favor ingrese un número válido.")

            # Obtener tipo de empleado
            print("\nTipos de empleado disponibles:")
            print("1. Mensajero")
            print("2. Logístico")
            print("3. Secretario")
            while True:
                try:
                    tipo_opcion = int(
                        obtener_input(
                            "\nSeleccione el tipo de empleado: ", requerido=True
                        )
                    )
                    if 1 <= tipo_opcion <= 3:
                        tipo_empleado = ["mensajero", "logistico", "secretario"][
                            tipo_opcion - 1
                        ]
                        break
                    print("Opción inválida. Intente de nuevo.")
                except ValueError:
                    print("Por favor ingrese un número válido.")

            # Obtener salario
            while True:
                try:
                    salario = float(obtener_input("Salario: ", requerido=True))
                    if salario <= 0:
                        print("El salario debe ser mayor a 0")
                        continue
                    break
                except ValueError:
                    print("Por favor ingrese un número válido.")

            # Usar la fecha actual como fecha de ingreso (solo la fecha, sin hora)
            fecha_ingreso = datetime.now().date()

            # Crear el objeto EmpleadoCreate con todos los campos requeridos
            empleado_data = {
                "primer_nombre": primer_nombre,
                "segundo_nombre": segundo_nombre if segundo_nombre else None,
                "primer_apellido": primer_apellido,
                "segundo_apellido": segundo_apellido if segundo_apellido else None,
                "fecha_nacimiento": fecha_nacimiento,
                "telefono": telefono,
                "correo": correo,
                "direccion": direccion,
                "tipo_empleado": tipo_empleado,
                "salario": float(salario),
                "fecha_ingreso": fecha_ingreso,
                "id_sede": id_sede,
                "tipo_documento": id_tipo_documento,
                "numero_documento": int(documento),
                "activo": True,
            }

            # Convertir a EmpleadoCreate para validación
            empleado_create = EmpleadoCreate(**empleado_data)

            # Crear el empleado
            empleado_creado = empleado_crud.crear(
                db=db,
                datos_entrada=empleado_create,
                creado_por=admin_actual.id_usuario,
                usuario_id=usuario.id_usuario,
            )

            if not empleado_creado:
                db.rollback()
                input(
                    "\nError al crear el empleado. Verifique los datos e intente nuevamente. Presione Enter para continuar..."
                )
                return

            db.commit()
            input(
                f"\n¡Usuario {usuario.nombre_usuario} y empleado {empleado_creado.primer_nombre} creados exitosamente! Presione Enter para continuar..."
            )
        else:
            # Si el rol es de cliente, crear también el registro de cliente
            if roles[opcion].nombre_rol.lower() == "cliente":
                mostrar_encabezado("INFORMACIÓN DEL CLIENTE")

                # Obtener información personal
                primer_nombre = obtener_input("Primer nombre: ", requerido=True)
                segundo_nombre = obtener_input(
                    "Segundo nombre (opcional): ", requerido=False
                )
                primer_apellido = obtener_input("Primer apellido: ", requerido=True)
                segundo_apellido = obtener_input(
                    "Segundo apellido (opcional): ", requerido=False
                )

                # Obtener tipos de documento
                tipos_doc = tipo_documento_crud.get_activos(db=db)

                if not tipos_doc:
                    print(
                        "Error: No se encontraron tipos de documento en la base de datos."
                    )
                    return

                # Mostrar menú de tipos de documento
                print("\nSeleccione el tipo de documento:")
                for i, tipo in enumerate(tipos_doc, 1):
                    print(f"{i}. {tipo.nombre}")

                # Seleccionar tipo de documento
                while True:
                    try:
                        opcion_tipo = (
                            int(
                                obtener_input(
                                    "\nSeleccione el tipo de documento: ",
                                    requerido=True,
                                )
                            )
                            - 1
                        )
                        if 0 <= opcion_tipo < len(tipos_doc):
                            id_tipo_documento = tipos_doc[opcion_tipo].id_tipo_documento
                            break
                        print("Opción inválida. Intente de nuevo.")
                    except ValueError:
                        print("Por favor ingrese un número válido.")

                # Obtener número de documento
                while True:
                    documento = obtener_input("Número de documento: ", requerido=True)
                    if documento.strip():
                        break
                    print("El número de documento no puede estar vacío.")

                # Obtener información de contacto
                telefono = obtener_input("Teléfono: ", requerido=True)
                correo = obtener_input("Correo electrónico: ", requerido=True)
                direccion = obtener_input("Dirección: ", requerido=True)

                # Obtener tipo de cliente (remitente/receptor)
                print("\nTipo de cliente:")
                print("1. Remitente")
                print("2. Receptor")
                while True:
                    try:
                        tipo_opcion = int(
                            obtener_input(
                                "\nSeleccione el tipo de cliente: ", requerido=True
                            )
                        )
                        if 1 <= tipo_opcion <= 2:
                            tipo_cliente = ["remitente", "receptor"][tipo_opcion - 1]
                            break
                        print("Opción inválida. Intente de nuevo.")
                    except ValueError:
                        print("Por favor ingrese un número válido.")

                # Crear el diccionario con los datos del cliente
                cliente_data = {
                    "primer_nombre": primer_nombre,
                    "segundo_nombre": segundo_nombre if segundo_nombre else None,
                    "primer_apellido": primer_apellido,
                    "segundo_apellido": segundo_apellido if segundo_apellido else None,
                    "numero_documento": documento,
                    "id_tipo_documento": id_tipo_documento,
                    "telefono": int(telefono),
                    "correo": correo,
                    "direccion": direccion,
                    "tipo": tipo_cliente.lower(),
                    "activo": True,
                }

                # Convertir a ClienteCreate para validación
                cliente_create = ClienteCreate(**cliente_data)

                # Crear el cliente
                cliente_creado = cliente_crud.crear(
                    db=db,
                    datos_entrada=cliente_create,
                    usuario_id=usuario.id_usuario,
                )

                if not cliente_creado:
                    db.rollback()
                    input(
                        "\nError al crear el cliente. Verifique los datos e intente nuevamente. Presione Enter para continuar..."
                    )
                    return

                db.commit()
                input(
                    f"\n¡Usuario {usuario.nombre_usuario} y cliente creados exitosamente! Presione Enter para continuar..."
                )
            else:
                db.commit()
                input(
                    f"\n¡Usuario {usuario.nombre_usuario} creado exitosamente! Presione Enter para continuar..."
                )

    except Exception as e:
        db.rollback()
        input(
            f"\nError al crear el usuario: {str(e)}. Presione Enter para continuar..."
        )


def menu_admin(db: Session, admin_actual: Any) -> bool:
    """
    Muestra el menú principal para administradores.

    Args:
        db: Sesión de base de datos
        admin_actual: Administrador autenticado

    Returns:
        bool: True si el usuario cierra sesión, False si sale de la aplicación
    """
    while True:
        mostrar_encabezado("MENÚ PRINCIPAL - ADMINISTRADOR")
        print("1. Gestionar usuarios")
        print("2. Configuración del sistema")
        print("3. Reportes")
        print("0. Cerrar sesión")
        print("=" * 60)

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            gestionar_usuarios(db, admin_actual)
        elif opcion == "2":
            # Implementar configuración del sistema
            input(
                "\nMódulo de configuración del sistema en desarrollo. Presione Enter para continuar..."
            )
        elif opcion == "3":
            mostrar_reportes(db)
        elif opcion == "0":
            if confirmar_accion("\n¿Está seguro que desea cerrar sesión? (s/n): "):
                return True
        else:
            input("\nOpción inválida. Presione Enter para continuar...")
