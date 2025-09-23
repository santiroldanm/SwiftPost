import sys
import logging
from getpass import getpass
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importación de CRUDs
try:
    from cruds.cliente_crud import cliente as cliente_crud
    from cruds.usuario_crud import usuario as usuario_crud
    from cruds.empleado_crud import empleado as empleado_crud
    from cruds.rol_crud import rol as rol_crud
    logger.info("Importación de CRUDs exitosa")
except ImportError as e:
    logger.error(f"Error al importar CRUDs: {e}")
    raise

# Importación de modelos y esquemas
try:
    from entities.cliente import ClienteCreate, ClienteUpdate
    from entities.usuario import Usuario, UsuarioCreate, UsuarioResponse
    from entities.rol import Rol, RolBase
    logger.info("Importación de modelos exitosa")
except ImportError as e:
    logger.error(f"Error al importar modelos: {e}")
    raise

# Configuración de base de datos
try:
    from database.config  import SessionLocal, get_db, create_tables
    from scripts.init_roles import init_roles
    logger.info("Importación de configuración de base de datos exitosa")
except ImportError as e:
    logger.error(f"Error al importar configuración de base de datos: {e}")
    raise

# Seguridad
try:
    from auth.security import authenticate_user, get_current_active_user
    logger.info("Importación de módulos de seguridad exitosa")
except ImportError as e:
    logger.error(f"Error al importar módulos de seguridad: {e}")
    raise

# Constantes
MENU_OPCIONES = {
    'sin_sesion': {
        '1': 'Iniciar sesión',
        '2': 'Registrarse',
        '0': 'Salir'
    },
    'con_sesion': {
        '1': 'Registrar cliente',
        '2': 'Buscar cliente',
        '3': 'Listar clientes activos',
        '4': 'Gestionar paquetes',
        '5': 'Reportes',
        '6': 'Mi perfil',
        '0': 'Cerrar sesión'
    },
    'admin': {
        '7': 'Administrar usuarios',
        '8': 'Configuración del sistema'
    }
}


def mostrar_encabezado(titulo: str = ""):
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 60)
    if titulo:
        print(f"{titulo:^60}")
        print("=" * 60)

def mostrar_menu(usuario_actual: Optional[Usuario] = None) -> str:
    """Muestra el menú principal y devuelve la opción seleccionada."""
    mostrar_encabezado("SWIFTPOST - SISTEMA DE MENSAJERÍA")
    
    if usuario_actual:
        print(f"Usuario: {usuario_actual.nombre_usuario}")
        try:
            rol_nombre = usuario_actual.rol.nombre_rol if usuario_actual.rol else "(sin rol)"
        except Exception:
            rol_nombre = str(usuario_actual.rol)
        print(f"Rol: {rol_nombre}")
        print("-" * 60)
        
        # Mostrar opciones básicas para usuarios autenticados
        for key, value in MENU_OPCIONES['con_sesion'].items():
            print(f"| {key:>2} | {value}")
            
        # Mostrar opciones adicionales para administradores
        if hasattr(usuario_actual, 'rol') and getattr(usuario_actual.rol, 'nombre_rol', '').lower() == "administrador":
            for key, value in MENU_OPCIONES['admin'].items():
                print(f"| {key:>2} | {value}")
    else:
        # Mostrar opciones para usuarios no autenticados
        for key, value in MENU_OPCIONES['sin_sesion'].items():
            print(f"| {key:>2} | {value}")
    
    print("=" * 60)
    return input("\nSeleccione una opción: ")
def login(db: Session) -> Optional[Usuario]:
    """Maneja el proceso de inicio de sesión."""
    mostrar_encabezado("INICIO DE SESIÓN")
    
    try:
        usuario = input("Nombre de usuario: ")
        contrasena = getpass("Contraseña: ")
        
        # Autenticar al usuario
        usuario_autenticado = authenticate_user(db, usuario, contrasena)
        
        if not usuario_autenticado:
            input("\n¡Error! Usuario o contraseña incorrectos. Presione Enter para continuar...")
            return None
            
        if not usuario_autenticado.activo:
            input("\n¡Error! Este usuario está inactivo. Contacte al administrador. Presione Enter para continuar...")
            return None
            
        input(f"\n¡Bienvenido, {usuario_autenticado.nombre_usuario}! Presione Enter para continuar...")
        return usuario_autenticado
        
    except Exception as e:
        input(f"\nError al iniciar sesión: {str(e)}. Presione Enter para continuar...")
        return None

def registrar_usuario(db: Session) -> bool:
    """Maneja el registro de nuevos usuarios."""
    mostrar_encabezado("REGISTRO DE NUEVO USUARIO")
    
    try:
        print("Complete los siguientes datos:")
        
        # Captura de credenciales básicas
        while True:
            nombre_usuario = input("Nombre de usuario: ").strip().lower()
            if not nombre_usuario:
                print("El nombre de usuario es obligatorio.")
                continue
                
            usuario_existente = usuario_crud.get_by_username(db, nombre_usuario)
            if usuario_existente:
                print("Este nombre de usuario ya está en uso. Por favor elija otro.")
            else:
                break
        
        # Validar contraseña
        while True:
            password = getpass("Contraseña (mínimo 8 caracteres): ")
            if len(password) < 8:
                print("La contraseña debe tener al menos 8 caracteres.")
            else:
                confirmar = getpass("Confirme la contraseña: ")
                if password == confirmar:
                    break
                print("Las contraseñas no coinciden. Intente nuevamente.")

        # Selección de rol
        print("\nRoles disponibles: cliente, empleado, administrador")
        rol_nombre = input("Rol del usuario: ").strip().lower()
        rol_obj = db.query(Rol).filter(Rol.nombre_rol == rol_nombre).first()
        if not rol_obj:
            input("\nError: El rol especificado no existe. Presione Enter para continuar...")
            return False

        # Crear el usuario base
        usuario_data = UsuarioCreate(
            nombre_usuario=nombre_usuario,
            password=password,
            id_rol=str(rol_obj.id_rol),
        )

        usuario = usuario_crud.create(db, obj_in=usuario_data)

        # Si el rol es cliente, crear perfil Cliente
        if rol_nombre == "cliente":
            cliente_data = obtener_datos_cliente(db)
            if not cliente_data:
                input("\nError: Datos de cliente inválidos. Presione Enter para continuar...")
                return False
            from entities.cliente import ClienteCreate as ClienteCreateSchema
            datos_entrada = ClienteCreateSchema(**cliente_data)
            cliente = cliente_crud.crear(
                db=db,
                datos_entrada=datos_entrada,
                usuario_id=usuario.id_usuario,
            )
            if not cliente:
                input("\nError al crear el perfil de cliente. Presione Enter para continuar...")
                return False

        # Nota: Para rol empleado, se podría solicitar datos de empleado y usar empleado_crud.crear(...)

        db.commit()
        input(f"\n¡Usuario {usuario.nombre_usuario} registrado exitosamente! Presione Enter para continuar...")
        return True
        
    except Exception as e:
        db.rollback()
        input(f"\nError al registrar usuario: {str(e)}. Presione Enter para continuar...")
        return False

def obtener_datos_cliente(db: Session) -> Optional[dict]:
    """Solicita al usuario los datos de un nuevo cliente."""
    try:
        print("\n--- Registro de Nuevo Cliente ---")
        
        # Primero, obtener los tipos de documento disponibles
        from cruds.tipo_documento_crud import tipo_documento
        print("\nObteniendo tipos de documento activos...")
        
        # Verificar la conexión a la base de datos primero
        try:
            # Ejecutar una consulta simple para verificar la conexión
            db.execute("SELECT 1")
            print("Conexión a la base de datos verificada correctamente.")
        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None
            
        # Obtener los tipos de documento
        tipos_doc = tipo_documento.get_activos(db)
        
        if not tipos_doc:
            print("Error: No hay tipos de documento configurados en el sistema.")
            print("Por favor, asegúrese de que existen tipos de documento activos en la base de datos.")
            return None
            
        print("\nTipos de documento disponibles:")
        for i, tipo in enumerate(tipos_doc, 1):
            print(f"{i}. {tipo.nombre} ({tipo.codigo})")
            
        while True:
            try:
                opcion_input = input("\nSeleccione el tipo de documento (número): ").strip()
                if not opcion_input:
                    print("Debe seleccionar una opción.")
                    continue
                    
                opcion = int(opcion_input)
                if 1 <= opcion <= len(tipos_doc):
                    tipo_doc = tipos_doc[opcion-1]
                    print(f"\nTipo de documento seleccionado: {tipo_doc.nombre} ({tipo_doc.codigo})")
                    break
                else:
                    print(f"Por favor, seleccione un número entre 1 y {len(tipos_doc)}")
            except ValueError:
                print("Por favor, ingrese un número válido.")
            
        # Validar que los campos requeridos no estén vacíos
        while True:
            primer_nombre = input("\nPrimer nombre: ").strip()
            if not primer_nombre:
                print("El primer nombre es obligatorio.")
                continue
            break
            
        segundo_nombre = input("Segundo nombre (opcional, presione Enter para omitir): ").strip() or None
        
        while True:
            primer_apellido = input("Primer apellido: ").strip()
            if not primer_apellido:
                print("El primer apellido es obligatorio.")
                continue
            break
            
        segundo_apellido = input("Segundo apellido (opcional, presione Enter para omitir): ").strip() or None
        
        while True:
            numero_documento = input("Número de documento: ").strip()
            if not numero_documento:
                print("El número de documento es obligatorio.")
                continue
            # Aquí podrías agregar validación del formato del documento
            break
            
        while True:
            correo = input("Correo electrónico: ").strip().lower()
            if "@" not in correo or "." not in correo:
                print("Por favor, ingrese un correo electrónico válido.")
                continue
            break
            
        while True:
            telefono = input("Teléfono: ").strip()
            if not telefono:
                print("El teléfono es obligatorio.")
                continue
            # Aquí podrías agregar validación del formato del teléfono
            break
            
        while True:
            direccion = input("Dirección completa: ").strip()
            if not direccion:
                print("La dirección es obligatoria.")
                continue
            break
            
        while True:
            tipo = input("Tipo (remitente/receptor): ").strip().lower()
            if tipo not in ["remitente", "receptor"]:
                print("Por favor, ingrese 'remitente' o 'receptor'.")
                continue
            break
            
        datos = {
            "primer_nombre": primer_nombre,
            "segundo_nombre": segundo_nombre,
            "primer_apellido": primer_apellido,
            "segundo_apellido": segundo_apellido,
            "numero_documento": numero_documento,
            "id_tipo_documento": tipo_doc.id_tipo_documento,
            "correo": correo,
            "telefono": telefono,
            "direccion": direccion,
            "tipo": tipo,
        }
        return datos
        
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
        return None
    except Exception as e:
        print(f"\nError inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None


def mostrar_cliente(cliente):
    """Muestra los datos de un cliente."""
    if not cliente:
        print("Cliente no encontrado.")
        return
    
    print("\n--- Datos del Cliente ---")
    print(f"ID: {cliente.id_cliente}")
    print(f"Nombre: {cliente.primer_nombre} {cliente.segundo_nombre or ''} {cliente.primer_apellido} {cliente.segundo_apellido or ''}")
    print(f"Documento: {cliente.numero_documento}")
    print(f"Correo: {cliente.correo}")
    print(f"Teléfono: {cliente.telefono}")
    print(f"Dirección: {cliente.direccion}")
    print(f"Tipo: {cliente.tipo}")
    print(f"Estado: {'Activo' if cliente.activo else 'Inactivo'}")


def login(db: Session):
    """Maneja el proceso de inicio de sesión."""
    print("\n--- Iniciar Sesión ---")
    username = input("Nombre de usuario: ").strip()
    password = input("Contraseña: ").strip()
    
    # Autenticar al usuario
    user = authenticate_user(db, username, password)
    if not user:
        print("\nError: Nombre de usuario o contraseña incorrectos.")
        input("Presione Enter para continuar...")
        return None
    
    # Verificar si el usuario está activo
    if not user.activo:
        print("\nError: Este usuario está desactivado.")
        input("Presione Enter para continuar...")
        return None
    
    print("\n¡Inicio de sesión exitoso!")
    input("Presione Enter para continuar...")
    return user  # Asegurarse de devolver el objeto Usuario

def listar_roles_disponibles(db: Session):
    """Muestra la lista de roles disponibles."""
    roles = rol_crud.obtener_todos(db)
    if not roles:
        print("No hay roles disponibles. Por favor, crea roles primero.")
        return None
    
    print("\n--- Roles Disponibles ---")
    for i, rol in enumerate(roles, 1):
        print(f"{i}. {rol.nombre_rol}")
    
    return roles

def seleccionar_rol(db: Session) -> Optional[str]:
    """Permite al usuario seleccionar un rol de la lista."""
    roles = listar_roles_disponibles(db)
    if not roles:
        return None
    
    while True:
        try:
            opcion = input("\nSeleccione el número del rol: ").strip()
            if not opcion:
                return None
                
            indice = int(opcion) - 1
            if 0 <= indice < len(roles):
                return str(roles[indice].id_rol)
            print("Número de rol inválido. Intente de nuevo.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

def registrar_usuario(db: Session):
    """Maneja el registro de nuevos usuarios."""
    print("\n--- Registro de Nuevo Usuario ---")

    # Obtener datos del usuario
    try:
        # Mostrar lista de roles y permitir selección
        print("\nSeleccione el rol del usuario:")
        id_rol = seleccionar_rol(db)
        if not id_rol:
            print("No se pudo determinar el rol. Operación cancelada.")
            input("Presione Enter para continuar...")
            return None
            
        usuario_data = {
           "nombre_usuario": input("Nombre de usuario: ").strip(),
            "password": getpass("Contraseña: "),
            "id_rol": id_rol,
            "activo": True,
            "fecha_creacion": datetime.now()
        }
        
        # Verificar si el nombre de usuario ya existe
        if usuario_crud.get_by_username(db, usuario_data["nombre_usuario"]):
            print("\nError: El nombre de usuario ya está en uso.")
            input("Presione Enter para continuar...")
            return None
            
        # Crear el usuario
        usuario = usuario_crud.create(
            db=db, 
            obj_in=UsuarioCreate(**usuario_data),
        )
        
        print("\n¡Usuario registrado exitosamente!")
        input("Presione Enter para continuar...")
        return usuario
        
    except Exception as e:
        print(f"\nError al registrar el usuario: {e}")
        input("Presione Enter para continuar...")
        return None


def main() -> None:
    """Función principal de la aplicación."""
    # Crear una nueva sesión para cada operación
    # Crear tablas y luego inicializar roles
    try:
        create_tables()
        db_init = SessionLocal()
        try:
            init_roles(db_init)
        finally:
            db_init.close()
    except Exception as e:
        logger.critical(f"Error durante la inicialización de la base de datos: {e}", exc_info=True)
        sys.exit(1) # Salir si la inicialización falla

    db = None
    usuario_actual = None
    
    try:
        while True:
            # Crear una nueva sesión para cada iteración del menú
            db = SessionLocal()
            
            try:
                opcion = mostrar_menu(usuario_actual)
                
                if not usuario_actual:
                    # Menú sin autenticación
                    if opcion == "1":  # Iniciar sesión
                        usuario_actual = login(db)
                        
                    elif opcion == "2":  # Registrarse
                        if registrar_usuario(db):
                            db.commit()  # Confirmar cambios
                            input("\nRegistro exitoso. Presione Enter para continuar...")
                            
                    elif opcion == "0":  # Salir
                        mostrar_encabezado("¡GRACIAS POR USAR SWIFTPOST!")
                        break
                        
                    else:
                        input("\nOpción no válida. Presione Enter para continuar...")
                        
                else:
                    # Menú con usuario autenticado
                    if opcion == "1":  # Registrar cliente
                        # Primero crear un usuario para el cliente
                        print("\n--- Crear usuario para el cliente ---")
                        while True:
                            nuevo_username = input("Nombre de usuario del cliente: ").strip().lower()
                            if not nuevo_username:
                                print("El nombre de usuario es obligatorio.")
                                continue
                            if usuario_crud.get_by_username(db, nuevo_username):
                                print("Este nombre de usuario ya está en uso. Intente otro.")
                                continue
                            break
                        while True:
                            nuevo_password = getpass("Contraseña del cliente: ")
                            if len(nuevo_password) < 8:
                                print("La contraseña debe tener al menos 8 caracteres.")
                                continue
                            confirmar = getpass("Confirme la contraseña: ")
                            if nuevo_password != confirmar:
                                print("Las contraseñas no coinciden.")
                                continue
                            break

                        rol_cliente = db.query(Rol).filter(Rol.nombre_rol == "cliente").first()
                        if not rol_cliente:
                            input("\nError: Rol 'cliente' no configurado. Presione Enter para continuar...")
                            continue

                        usuario_cliente = usuario_crud.create(
                            db=db,
                            obj_in=UsuarioCreate(
                                nombre_usuario=nuevo_username,
                                password=nuevo_password,
                                id_rol=str(rol_cliente.id_rol),
                            ),
                        )

                        cliente_data = obtener_datos_cliente(db)
                        if cliente_data:
                            try:
                                from entities.cliente import ClienteCreate as ClienteCreateSchema
                                
                                # Crear el cliente con el mismo ID que el usuario
                                cliente_data["id_cliente"] = usuario_cliente.id_usuario
                                
                                # Asegurarse de que los campos requeridos estén presentes
                                datos_entrada = ClienteCreateSchema(
                                    **cliente_data,
                                    fecha_creacion=datetime.now(),
                                    activo=True
                                )
                                
                                # Crear el cliente
                                cliente = cliente_crud.crear(
                                    db=db,
                                    datos_entrada=datos_entrada,
                                )

                                if cliente:
                                    db.commit()
                                    input(f"\nCliente registrado con ID: {cliente.id_cliente}. Presione Enter para continuar...")
                                else:
                                    db.rollback()
                                    input("\nError al crear el cliente. Puede que ya exista un cliente con ese documento o correo. Presione Enter para continuar...")
                                    
                            except Exception as e:
                                db.rollback()
                                logger.error(f"Error al crear el cliente: {str(e)}", exc_info=True)
                                input(f"\nError al crear el cliente: {str(e)}. Presione Enter para continuar...")
                                    
                    elif opcion == "2":  # Buscar cliente
                        documento = input("\nIngrese el documento del cliente: ").strip()
                        if documento:
                            cliente = cliente_crud.obtener_por_documento(db, documento=documento)
                            if cliente:
                                mostrar_cliente(cliente)
                            else:
                                clientes, total = cliente_crud.get_activos(db)
                                mostrar_encabezado("CLIENTES ACTIVOS")
                                if clientes:
                                    for cliente in clientes:
                                        mostrar_cliente(cliente)
                                        print("-" * 60)
                        else:
                            print("No hay clientes activos.")
                    elif opcion == '4':  # Gestionar paquetes
                        gestionar_paquetes(db)
                    elif opcion == '5':  # Reportes
                        generar_reportes(db)
                    elif opcion == '6':  # Mi perfil
                        ver_perfil(db, usuario_actual)
                    elif opcion == '7' and hasattr(usuario_actual, 'rol') and hasattr(usuario_actual.rol, 'nombre_rol') and usuario_actual.rol.nombre_rol.lower() == "administrador":
                        administrar_usuarios(db)
                    elif opcion == '8' and hasattr(usuario_actual, 'rol') and hasattr(usuario_actual.rol, 'nombre_rol') and usuario_actual.rol.nombre_rol.lower() == "administrador":
                        configuracion_sistema(db)
                    elif opcion == '0':  # Cerrar sesión
                        print(f"\nSesión cerrada para el usuario: {usuario_actual.nombre_usuario}")
                        usuario_actual = None
                    else:
                        print("\nOpción no válida o no tiene permisos para acceder a esta función.")
                
                input("\nPresione Enter para continuar...")
                
            except Exception as e:
                logger.error(f"Error en el bucle principal: {e}", exc_info=True)
                input("\nOcurrió un error. Presione Enter para continuar...")
                
    except KeyboardInterrupt:
        print("\n\n¡Aplicación interrumpida por el usuario!")
        logger.info("Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.critical(f"Error crítico en la aplicación: {e}", exc_info=True)
        print(f"\nError inesperado: {e}")
    finally:
        db.close()
        logger.info("Sesión de base de datos cerrada")  # Cerrar la sesión de base de datos al salir


if __name__ == "__main__":
    main()
