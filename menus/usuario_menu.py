"""
Módulo que contiene las funciones del menú de gestión de usuarios.
"""
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from cruds.usuario_crud import usuario as usuario_crud
from entities.usuario import Usuario
from entities.rol import Rol


def mostrar_menu_usuarios() -> None:
    """Muestra el menú de gestión de usuarios."""
    print("\n" + "=" * 80)
    print("GESTIÓN DE USUARIOS".center(80))
    print("=" * 80)
    print("1. Listar todos los usuarios")
    print("2. Buscar usuario")
    print("3. Editar usuario")
    print("4. Desactivar/activar usuario")
    print("0. Volver al menú principal")
    print("=" * 80)


def listar_usuarios(db: Session) -> None:
    """Lista todos los usuarios del sistema."""
    try:
        # Obtener usuarios con información de rol
        usuarios = db.query(
            Usuario,
            Rol.nombre_rol.label('rol_nombre')
        ).join(
            Rol, Usuario.id_rol == Rol.id_rol
        ).all()
        
        if not usuarios:
            print("\nNo hay usuarios registrados en el sistema.")
            return
        
        # Definir anchos de columna
        column_widths = [36, 20, 20, 10, 16, 16]  # Ajusta según necesidad
        
        # Encabezados
        headers = ["ID", "Nombre de Usuario", "Rol", "Estado", "Creado", "Último Acceso"]
        
        # Imprimir encabezados
        header_row = ""
        for i, header in enumerate(headers):
            header_row += f"{header:{column_widths[i]}} | "
        print(header_row)
        print("-" * 120)
        
        # Imprimir datos
        for usuario, rol_nombre in usuarios:
            # Formatear los datos
            id_usuario = (usuario.id_usuario or '')[:column_widths[0]]
            nombre = (usuario.nombre_usuario or '')[:column_widths[1]]
            rol = (rol_nombre or 'Sin rol')[:column_widths[2]]
            estado = 'Activo' if usuario.activo else 'Inactivo'
            fecha_creacion = usuario.fecha_creacion.strftime('%Y-%m-%d %H:%M') if usuario.fecha_creacion else 'N/A'
            
            # Crear fila formateada
            row = (
                f"{id_usuario:{column_widths[0]}} | "
                f"{nombre:{column_widths[1]}} | "
                f"{rol:{column_widths[2]}} | "
                f"{estado:{column_widths[3]}} | "
                f"{fecha_creacion:{column_widths[4]}} | "
            )
            print(row)
        
        print("=" * 120)
        
    except Exception as e:
        print(f"\nError al listar usuarios: {str(e)}")
    
    input("\nPresione Enter para continuar...")


def buscar_usuario(db: Session) -> None:
    """Busca un usuario por nombre de usuario o ID y muestra información detallada."""
    try:
        termino = input("\nIngrese el ID o nombre de usuario a buscar: ").strip()
        
        if not termino:
            print("\nError: Debe ingresar un término de búsqueda.")
            input("Presione Enter para continuar...")
            return
        
        # Cargar relaciones de cliente y empleado junto con el usuario
        usuario = (
            db.query(Usuario)
            .options(
                joinedload(Usuario.cliente),
                joinedload(Usuario.empleado),
                joinedload(Usuario.rol)
            )
            .filter(
                (Usuario.id_usuario == termino) | 
                (Usuario.nombre_usuario.ilike(f'%{termino}%'))
            )
            .first()
        )
        
        if not usuario:
            print("\nNo se encontró ningún usuario con ese criterio de búsqueda.")
            input("Presione Enter para continuar...")
            return
        
        # Determinar si es cliente o empleado
        tipo_cuenta = "Cliente" if hasattr(usuario, 'cliente') and usuario.cliente else \
                     ("Empleado" if hasattr(usuario, 'empleado') and usuario.empleado else "Usuario")
        
        # Obtener correo según el tipo de cuenta
        correo = ""
        if hasattr(usuario, 'cliente') and usuario.cliente:
            correo = usuario.cliente.correo if hasattr(usuario.cliente, 'correo') else 'No especificado'
        elif hasattr(usuario, 'empleado') and usuario.empleado:
            correo = usuario.empleado.correo if hasattr(usuario.empleado, 'correo') else 'No especificado'
        
        # Mostrar detalles del usuario
        print("\n" + "=" * 80)
        print("DETALLES DEL USUARIO".center(80))
        print("=" * 80)
        print(f"ID: {usuario.id_usuario}")
        print(f"Tipo de cuenta: {tipo_cuenta}")
        print(f"Nombre de usuario: {usuario.nombre_usuario}")
        print(f"Rol: {usuario.rol.nombre_rol if usuario.rol else 'Sin rol'}")
        print(f"Estado: {'Activo' if usuario.activo else 'Inactivo'}")
        print(f"Correo electrónico: {correo}")
        print(f"Fecha de creación: {usuario.fecha_creacion.strftime('%Y-%m-%d %H:%M') if usuario.fecha_creacion else 'N/A'}")
        
        # Mostrar información adicional según el tipo de cuenta
        if tipo_cuenta == "Cliente" and hasattr(usuario, 'cliente') and usuario.cliente:
            print("\nINFORMACIÓN DEL CLIENTE")
            print("-" * 40)
            print(f"Nombres: {getattr(usuario.cliente, 'nombres', 'No especificado')}")
            print(f"Apellidos: {getattr(usuario.cliente, 'apellidos', 'No especificado')}")
            print(f"Teléfono: {getattr(usuario.cliente, 'telefono', 'No especificado')}")
            
        elif tipo_cuenta == "Empleado" and hasattr(usuario, 'empleado') and usuario.empleado:
            print("\nINFORMACIÓN DEL EMPLEADO")
            print("-" * 40)
            print(f"Nombres: {getattr(usuario.empleado, 'nombres', 'No especificado')}")
            print(f"Apellidos: {getattr(usuario.empleado, 'apellidos', 'No especificado')}")
            print(f"Cargo: {getattr(usuario.empleado, 'cargo', 'No especificado')}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError al buscar usuario: {str(e)}")
    
    input("\nPresione Enter para continuar...")


def editar_usuario(db: Session) -> None:
    """Permite editar los datos de un usuario."""
    try:
        id_usuario = input("\nIngrese el ID del usuario a editar: ").strip()
        
        if not id_usuario:
            print("\nError: Debe ingresar un ID de usuario.")
            input("Presione Enter para continuar...")
            return
        
        # Obtener el usuario
        usuario = usuario_crud.obtener_por_id(db, id=id_usuario)
        
        if not usuario:
            print("\nError: No se encontró ningún usuario con ese ID.")
            input("Presione Enter para continuar...")
            return
        
        # Mostrar datos actuales
        print("\n" + "=" * 80)
        print("EDITAR USUARIO".center(80))
        print("=" * 80)
        print(f"Usuario: {usuario.nombre_usuario}")
        print(f"Rol actual: {getattr(usuario, 'rol_nombre', 'Sin rol')}")
        print(f"Estado actual: {'Activo' if usuario.activo else 'Inactivo'}")
        print(f"Correo electrónico: {getattr(usuario, 'email', 'No especificado')}")
        print("\nDeje en blanco los campos que no desee modificar.")
        print("=" * 80)
        
        # Solicitar nuevos datos
        nuevo_nombre = input("\nNuevo nombre de usuario: ").strip()
        nuevo_email = input("Nuevo correo electrónico: ").strip()
        
        # Actualizar datos si se proporcionaron
        datos_actualizados = {}
        
        if nuevo_nombre:
            datos_actualizados["nombre_usuario"] = nuevo_nombre
            
        if nuevo_email:
            datos_actualizados["email"] = nuevo_email
        
        # Preguntar por cambio de contraseña
        cambiar_password = input("\n¿Desea cambiar la contraseña? (s/n): ").strip().lower()
        if cambiar_password == 's':
            from getpass import getpass
            nueva_password = getpass("Nueva contraseña: ")
            confirmar_password = getpass("Confirmar contraseña: ")
            
            if nueva_password == confirmar_password:
                datos_actualizados["password"] = nueva_password
                print("\nContraseña actualizada correctamente.")
            else:
                print("\nError: Las contraseñas no coinciden. No se actualizó la contraseña.")
        
        # Si hay datos para actualizar, proceder
        if datos_actualizados:
            usuario_actualizado = usuario_crud.actualizar_usuario(db, db_obj=usuario, obj_in=datos_actualizados)
            print("\nUsuario actualizado correctamente.")
        else:
            print("\nNo se realizaron cambios.")
        
    except Exception as e:
        print(f"\nError al editar usuario: {str(e)}")
    
    input("\nPresione Enter para continuar...")


def cambiar_estado_usuario(db: Session) -> None:
    """Activa o desactiva un usuario."""
    try:
        id_usuario = input("\nIngrese el ID del usuario a activar/desactivar: ").strip()
        
        if not id_usuario:
            print("\nError: Debe ingresar un ID de usuario.")
            input("Presione Enter para continuar...")
            return
        
        # Obtener el usuario
        usuario = usuario_crud.obtener_por_id(db, id=id_usuario)
        
        if not usuario:
            print("\nError: No se encontró ningún usuario con ese ID.")
            input("Presione Enter para continuar...")
            return
        
        # Mostrar estado actual
        print("\n" + "=" * 80)
        print("CAMBIAR ESTADO DE USUARIO".center(80))
        print("=" * 80)
        print(f"Usuario: {usuario.nombre_usuario}")
        print(f"Estado actual: {'ACTIVO' if usuario.activo else 'INACTIVO'}")
        print("=" * 80)
        
        # Confirmar cambio de estado
        confirmar = input(f"\n¿Desea {'DESACTIVAR' if usuario.activo else 'ACTIVAR'} este usuario? (s/n): ").strip().lower()
        
        if confirmar == 's':
            nuevo_estado = not usuario.activo
            usuario_actualizado = usuario_crud.actualizar_usuario(
                db, 
                db_obj=usuario, 
                obj_in={"activo": nuevo_estado}
            )
            
            print(f"\nUsuario {'activado' if nuevo_estado else 'desactivado'} correctamente.")
        else:
            print("\nOperación cancelada.")
        
    except Exception as e:
        print(f"\nError al cambiar el estado del usuario: {str(e)}")
    
    input("\nPresione Enter para continuar...")


def manejar_menu_usuarios(db: Session) -> None:
    """Maneja el menú de gestión de usuarios."""
    while True:
        mostrar_menu_usuarios()
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            listar_usuarios(db)
        elif opcion == '2':
            buscar_usuario(db)
        elif opcion == '3':
            editar_usuario(db)
        elif opcion == '4':
            cambiar_estado_usuario(db)
        elif opcion == '0':
            break
        else:
            print("\nOpción no válida. Intente de nuevo.")
            input("Presione Enter para continuar...")
