import sys
import logging
from getpass import getpass
from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session, joinedload
import getpass
 
from auth import is_admin, is_employee, is_client
from entities.paquete import PaqueteCreate

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importación de CRUDs
from cruds.tipo_documento_crud import TipoDocumentoCRUD
from entities.tipo_documento import TipoDocumento, TipoDocumentoCreate

# ID de usuario por defecto para inicialización
USUARIO_ADMIN_DEFAULT = "00000000-0000-0000-0000-000000000000"

def inicializar_tipos_documento(db: Session) -> None:
    """
    Inicializa los tipos de documento por defecto en la base de datos.
    Utiliza las funciones del módulo inicializar_admin_y_documentos.
    """
    try:
        from scripts.inicializar_admin_y_documentos import crear_tipos_documento_por_defecto
        
        # Llamar a la función del módulo de inicialización
        crear_tipos_documento_por_defecto(db, USUARIO_ADMIN_DEFAULT)
        
    except Exception as e:
        logger.error(f"Error al inicializar tipos de documento: {str(e)}", exc_info=True)
        db.rollback()
        raise

# Importación de CRUDs
try:
    from cruds.cliente_crud import cliente as cliente_crud
    from cruds.usuario_crud import usuario as usuario_crud
    from cruds.empleado_crud import empleado as empleado_crud
    from cruds.rol_crud import rol as rol_crud
    from cruds.sede_crud import sede as sede_crud
    from cruds.transporte_crud import transporte as transporte_crud
    from cruds.paquete_crud import paquete as paquete_crud
    from cruds.tipo_documento_crud import tipo_documento as tipo_documento_crud
    logger.info("Importación de CRUDs exitosa")
except ImportError as e:
    logger.error(f"Error al importar CRUDs: {e}")
    raise

# Importación de modelos y esquemas
try:
    from entities.cliente import ClienteCreate, ClienteUpdate
    from entities.usuario import Usuario, UsuarioCreate, UsuarioResponse
    from entities.rol import Rol, RolBase
    from entities.sede import SedeCreate, SedeUpdate
    from entities.transporte import TransporteCreate, TransporteUpdate
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
    'admin': {
        '1': 'Gestionar usuarios',
        '2': 'Gestionar empleados',
        '3': 'Gestionar clientes',
        '4': 'Gestionar sedes',
        '5': 'Gestionar transportes',
        '6': 'Gestionar paquetes',
        '7': 'Ver reportes',
        '8': 'Configuración del sistema',
        '0': 'Cerrar sesión'
    },
    'empleado': {
        '1': 'Registrar envío',
        '2': 'Buscar cliente',
        '3': 'Listar clientes activos',
        '4': 'Gestionar paquetes',
        '5': 'Ver reportes',
        '6': 'Mi perfil',
        '0': 'Cerrar sesión'
    },
    'cliente': {
        '1': 'Solicitar recogida',
        '2': 'Rastrear envío',
        '3': 'Historial de envíos',
        '4': 'Mis datos',
        '0': 'Cerrar sesión'
    }
}


def mostrar_encabezado(titulo: str = ""):
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 60)
    if titulo:
        print(f"{titulo:^60}")
        print("=" * 60)

def mostrar_menu(usuario_data: Optional[Dict[str, Any]] = None) -> str:
    """Muestra el menú principal y devuelve la opción seleccionada."""
    mostrar_encabezado("SWIFTPOST - SISTEMA DE MENSAJERÍA")
    
    if usuario_data:
        print(f"Usuario: {usuario_data.get('nombre_usuario', '')}")
        rol_nombre = usuario_data.get('rol_nombre', '(sin rol)')
        print(f"Rol: {rol_nombre}")
        print("-" * 60)
        
        # Determinar qué menú mostrar según el rol
        if is_admin(usuario_data):
            menu_tipo = 'admin'
        elif is_employee(usuario_data):
            menu_tipo = 'empleado'
        else:  # Cliente por defecto
            menu_tipo = 'cliente'
            
        # Mostrar opciones según el rol
        for key, value in MENU_OPCIONES[menu_tipo].items():
            print(f"| {key:>2} | {value}")
    else:
        # Mostrar opciones para usuarios no autenticados
        for key, value in MENU_OPCIONES['sin_sesion'].items():
            print(f"| {key:>2} | {value}")
    
    print("=" * 60)
    return input("\nSeleccione una opción: ")

def login(db: Session) -> Optional[Dict[str, Any]]:
    """Maneja el proceso de inicio de sesión."""
    from auth import authenticate_user, get_current_active_user, is_admin, is_employee, is_client
    from getpass import getpass as get_password
    
    mostrar_encabezado("INICIAR SESIÓN")
    username = input("Nombre de usuario: ")
    password = get_password("Contraseña: ")
    
    user_data = authenticate_user(db, username=username, password=password)
    if not user_data:
        print("\nError: Usuario o contraseña incorrectos.")
        input("Presione Enter para continuar...")
        return None
    
    if not user_data.get('activo', False):
        print("\nError: Este usuario está inactivo.")
        input("Presione Enter para continuar...")
        return None
    
    rol_nombre = user_data.get('rol_nombre', 'cliente')
    print(f"\n¡Bienvenido, {user_data['nombre_usuario']}! (Rol: {rol_nombre.capitalize()})")
    return user_data

def registrar_usuario(db: Session, es_empleado: bool = False) -> None:
    """
    Maneja el registro de nuevos usuarios.
    Si es_empleado es True, registra un empleado (solo para administradores).
    """
    from cruds.usuario_crud import usuario as usuario_crud
    from cruds.rol_crud import rol as rol_crud
    from entities.usuario import UsuarioCreate
    from auth import get_role_id, is_admin
    
    if es_empleado:
        mostrar_encabezado("REGISTRAR NUEVO EMPLEADO")
        rol_id = get_role_id(db, 'empleado')
    else:
        mostrar_encabezado("REGISTRAR NUEVO CLIENTE")
        rol_id = get_role_id(db, 'cliente')
    
    if not rol_id:
        print("\nError: No se pudo determinar el rol del usuario.")
        input("Presione Enter para continuar...")
        return
    
    print("\nPor favor ingrese los siguientes datos:")
    username = input("Nombre de usuario: ")
    
    # Verificar si el usuario ya existe
    if usuario_crud.obtener_por_nombre_usuario(db, nombre_usuario=username):
        print("\nError: El nombre de usuario ya está en uso.")
        input("Presione Enter para continuar...")
        return
    
    from getpass import getpass as get_password
    password = get_password("Contraseña: ")
    confirm_password = get_password("Confirmar contraseña: ")
    
    if password != confirm_password:
        print("\nError: Las contraseñas no coinciden.")
        input("Presione Enter para continuar...")
        return
    
    # Crear el usuario
    usuario_in = UsuarioCreate(
        nombre_usuario=username,
        password=password,
        id_rol=rol_id
    )
    
    try:
        # Crear el usuario
        usuario = usuario_crud.crear_usuario(db, datos_usuario=usuario_in)
        tipo_usuario = "empleado" if es_empleado else "cliente"
        
        # Si es un cliente, crear también el registro de cliente
        if not es_empleado:
            from cruds.cliente_crud import cliente as cliente_crud
            from entities.cliente import ClienteCreate
            from cruds.tipo_documento_crud import tipo_documento as tipo_documento_crud
            print("\nPor favor ingrese los datos del cliente:")
            print("-" * 40)
            
            # Solicitar datos del cliente
            primer_nombre = input("Primer nombre: ").strip()
            segundo_nombre = input("Segundo nombre (opcional, presione Enter para omitir): ").strip() or None
            primer_apellido = input("Primer apellido: ").strip()
            segundo_apellido = input("Segundo apellido (opcional, presione Enter para omitir): ").strip() or None
            
            # Validar que los campos obligatorios no estén vacíos
            if not primer_nombre or not primer_apellido:
                print("\nError: El primer nombre y el primer apellido son obligatorios.")
                db.rollback()  # Deshacer la creación del usuario
                input("\nPresione Enter para continuar...")
                return
                
            # Obtener tipos de documento activos
            tipos_documento = tipo_documento_crud.obtener_activos(db)
            
            if not tipos_documento:
                print("\nError: No hay tipos de documento disponibles en el sistema.")
                print("Por favor, contacte al administrador para que configure los tipos de documento necesarios.")
                db.rollback()
                input("\nPresione Enter para continuar...")
                return
                
            # Mostrar tipos de documento disponibles
            print("\nTipos de documento disponibles:")
            print("-" * 40)
            for i, tipo in enumerate(tipos_documento, 1):
                print(f"{i}. {tipo.nombre.upper()} ({tipo.codigo.upper()})")
            
            # Seleccionar tipo de documento
            while True:
                try:
                    opcion = int(input("\nSeleccione el número del tipo de documento: ").strip())
                    if 1 <= opcion <= len(tipos_documento):
                        tipo_seleccionado = tipos_documento[opcion-1]
                        id_tipo_documento = tipo_seleccionado.id_tipo_documento
                        break
                    print(f"Error: Por favor ingrese un número entre 1 y {len(tipos_documento)}")
                except ValueError:
                    print("Error: Por favor ingrese un número válido")
            
            # Solicitar tipo de cliente (remitente o receptor)
            while True:
                tipo_cliente = input("Tipo de cliente (remitente/receptor): ").strip().lower()
                if tipo_cliente in ['remitente', 'receptor']:
                    break
                print("Error: El tipo debe ser 'remitente' o 'receptor'")
            
            # Obtener el número de documento
            numero_documento = input("Número de documento: ").strip()
            
            # Verificar si ya existe un cliente con este número de documento
            cliente_existente = cliente_crud.obtener_por_documento(db, numero_documento)
            if cliente_existente:
                print(f"\nError: Ya existe un cliente con el documento {numero_documento}")
                db.rollback()
                input("\nPresione Enter para continuar...")
                return
                
            # Verificar si el correo ya está en uso
            correo = input("Correo electrónico: ").strip().lower()
            if cliente_crud.obtener_por_email(db, correo):
                print(f"\nError: Ya existe un cliente con el correo {correo}")
                db.rollback()
                input("\nPresione Enter para continuar...")
                return
            
            # Obtener los datos restantes
            direccion = input("Dirección: ").strip()
            
            # Validar el teléfono con reintentos
            telefono_valido = False
            while not telefono_valido:
                telefono = input("Teléfono (solo números, mínimo 7 dígitos): ").strip()
                # Limpiar cualquier carácter que no sea dígito
                telefono = ''.join(filter(str.isdigit, telefono))
                if len(telefono) >= 7:  # Mínimo 7 dígitos, sin máximo estricto
                    telefono_valido = True
                else:
                    print("Error: El teléfono debe contener al menos 7 dígitos numéricos")
            
            # Crear el cliente usando el esquema ClienteCreate
            from entities.cliente import ClienteCreate
            id_tipo_documento_str = str(id_tipo_documento) if id_tipo_documento else None
            usuario_id_str = str(usuario.id_usuario) if usuario and usuario.id_usuario else None
            
            # Crear el objeto ClienteCreate directamente con los campos requeridos
            cliente_data = ClienteCreate(
                primer_nombre=primer_nombre,
                segundo_nombre=segundo_nombre if segundo_nombre else None,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido if segundo_apellido else None,
                numero_documento=numero_documento,
                direccion=direccion,
                telefono=telefono,
                correo=correo.lower(),
                tipo=tipo_cliente.lower(),
                id_tipo_documento=id_tipo_documento_str,
                usuario_id=usuario_id_str
            )
            
            # Mostrar datos para depuración
            print("\n=== DATOS DEL CLIENTE A CREAR ===")
            print(f"Tipo de datos: {type(cliente_data).__name__}")
            print("\nContenido:")
            for campo, valor in cliente_data.model_dump().items():
                print(f"  - {campo}: {valor} ({type(valor).__name__})")
            
            # Guardar el cliente
            cliente = cliente_crud.crear(db, datos_entrada=cliente_data, usuario_id=usuario.id_usuario)
            if not cliente:
                db.rollback()  # Deshacer la creación del usuario si falla la creación del cliente
                print("\nError al crear el registro del cliente.")
                input("\nPresione Enter para continuar...")
                return
        
        # Si todo sale bien, hacer commit de la transacción
        db.commit()
        print(f"\n¡{tipo_usuario.capitalize()} {usuario.nombre_usuario} registrado exitosamente!")
        
    except Exception as e:
        db.rollback()  # Asegurarse de deshacer cualquier cambio en caso de error
        print(f"\nError al crear el usuario: {str(e)}")
        import traceback
        traceback.print_exc()
    
    input("\nPresione Enter para continuar...")

# ==============================================
# Funciones del menú de administrador
# ==============================================

def administrar_usuarios(db: Session) -> None:
    """Muestra el menú de administración de usuarios."""
    mostrar_encabezado("ADMINISTRAR USUARIOS")
    print("1. Listar todos los usuarios")
    print("2. Buscar usuario")
    print("3. Editar usuario")
    print("4. Desactivar/activar usuario")
    print("0. Volver al menú principal")
    
    opcion = input("\nSeleccione una opción: ")
    
    if opcion == '1':
        listar_usuarios(db)
    elif opcion == '2':
        buscar_usuario(db)
    elif opcion == '3':
        editar_usuario(db)
    elif opcion == '4':
        cambiar_estado_usuario(db)
    elif opcion == '0':
        return
    else:
        print("\nOpción no válida.")
        input("Presione Enter para continuar...")

def gestionar_empleados(db: Session) -> None:
    """Muestra el menú de gestión de empleados."""
    mostrar_encabezado("GESTIÓN DE EMPLEADOS")
    print("1. Listar empleados")
    print("2. Buscar empleado")
    print("3. Registrar nuevo empleado")
    print("4. Editar empleado")
    print("5. Desactivar/Activar empleado")
    print("0. Volver al menú principal")
    
    opcion = input("\nSeleccione una opción: ")
    
    if opcion == '1':
        listar_empleados(db)
    elif opcion == '2':
        buscar_empleado(db)
    elif opcion == '3':
        registrar_empleado(db)
    elif opcion == '4':
        editar_empleado(db)
    elif opcion == '5':
        cambiar_estado_empleado(db)
    elif opcion == '0':
        return
    else:
        print("\nOpción no válida.")
        input("Presione Enter para continuar...")

def gestionar_sedes(db: Session) -> None:
    """Muestra el menú de gestión de sedes."""
    while True:
        mostrar_encabezado("GESTIÓN DE SEDES")
        print("1. Listar todas las sedes")
        print("2. Buscar sede por ciudad")
        print("3. Agregar nueva sede")
        print("4. Editar sede")
        print("5. Cambiar estado de sede")
        print("0. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            listar_sedes(db)
        elif opcion == '2':
            buscar_sede_por_ciudad(db)
        elif opcion == '3':
            agregar_sede(db)
        elif opcion == '4':
            editar_sede(db)
        elif opcion == '5':
            cambiar_estado_sede(db)
        elif opcion == '0':
            break
        else:
            print("\nOpción no válida.")
            input("Presione Enter para continuar...")

def gestionar_transportes(db: Session) -> None:
    """Muestra el menú de gestión de transportes."""
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
        
        if opcion == '1':
            listar_transportes(db)
        elif opcion == '2':
            buscar_transporte_por_placa(db)
        elif opcion == '3':
            agregar_transporte(db)
        elif opcion == '4':
            editar_transporte(db)
        elif opcion == '5':
            cambiar_estado_transporte(db)
        elif opcion == '6':
            asignar_transporte_a_sede(db)
        elif opcion == '0':
            break
        else:
            print("\nOpción no válida.")
            input("Presione Enter para continuar...")

def gestionar_clientes(db: Session) -> None:
    """Muestra el menú de gestión de clientes."""
    mostrar_encabezado("GESTIÓN DE CLIENTES")
    print("1. Registrar nuevo cliente")
    print("2. Listar clientes activos")
    print("3. Buscar cliente")
    print("4. Historial de envíos por cliente")
    print("0. Volver al menú principal")
    
    opcion = input("\nSeleccione una opción: ")
    
    if opcion == '1':
        registrar_cliente(db)
    elif opcion == '2':
        listar_clientes_activos(db)
    elif opcion == '3':
        buscar_cliente(db)
    elif opcion == '4':
        historial_envios_cliente(db)
    elif opcion == '0':
        return
    else:
        print("\nOpción no válida.")
        input("Presione Enter para continuar...")

def gestionar_paquetes_admin(db: Session) -> None:
    """Muestra el menú de gestión de paquetes para administradores."""
    mostrar_encabezado("GESTIÓN DE PAQUETES")
    print("1. Registrar nuevo paquete")
    print("2. Listar todos los paquetes")
    print("3. Buscar paquete")
    print("4. Actualizar estado de paquete")
    print("5. Generar reporte de paquetes")
    print("0. Volver al menú principal")
    
    opcion = input("\nSeleccione una opción: ")
    
    if opcion == '1':
        registrar_paquete(db)
    elif opcion == '2':
        listar_paquetes(db)
    elif opcion == '3':
        buscar_paquete(db)
    elif opcion == '4':
        actualizar_estado_paquete(db)
    elif opcion == '5':
        generar_reporte_paquetes(db)
    elif opcion == '0':
        return
    else:
        print("\nOpción no válida.")
        input("Presione Enter para continuar...")

def mostrar_reportes_admin(db: Session) -> None:
    """Muestra el menú de reportes para administradores."""
    mostrar_encabezado("REPORTES")
    print("1. Reporte de envíos por período")
    print("2. Reporte de ingresos")
    print("3. Reporte de paquetes por estado")
    print("4. Reporte de clientes frecuentes")
    print("0. Volver al menú principal")
    
    opcion = input("\nSeleccione una opción: ")
    
    if opcion == '1':
        reporte_envios_por_periodo(db)
    elif opcion == '2':
        reporte_ingresos(db)
    elif opcion == '3':
        reporte_paquetes_por_estado(db)
    elif opcion == '4':
        reporte_clientes_frecuentes(db)
    elif opcion == '0':
        return
    else:
        print("\nOpción no válida.")
        input("Presione Enter para continuar...")

# ==============================================
# Funciones del menú de empleado
# ==============================================

def registrar_envio(db: Session, empleado_data: Dict[str, Any]) -> None:
    """Permite a un empleado registrar un nuevo envío."""
    mostrar_encabezado("REGISTRAR NUEVO ENVÍO")
    print("Funcionalidad en desarrollo...")
    input("\nPresione Enter para continuar...")

def buscar_cliente_empleado(db: Session) -> None:
    """Permite a un empleado buscar un cliente."""
    mostrar_encabezado("BUSCAR CLIENTE")
    print("Funcionalidad en desarrollo...")
    input("\nPresione Enter para continuar...")

def listar_clientes_activos_empleado(db: Session) -> None:
    """Muestra la lista de clientes activos para empleados."""
    mostrar_encabezado("CLIENTES ACTIVOS")
    print("Funcionalidad en desarrollo...")
    input("\nPresione Enter para continuar...")

def gestionar_paquetes_empleado(db: Session, empleado_data: Dict[str, Any]) -> None:
    """Permite a un empleado gestionar paquetes."""
    mostrar_encabezado("GESTIÓN DE PAQUETES")
    print("1. Registrar nuevo paquete")
    print("2. Actualizar estado de paquete")
    print("3. Buscar paquete")
    print("0. Volver al menú principal")
    
    opcion = input("\nSeleccione una opción: ")
    
    if opcion == '1':
        registrar_paquete_empleado(db, empleado_data)
    elif opcion == '2':
        actualizar_estado_paquete_empleado(db, empleado_data)
    elif opcion == '3':
        buscar_paquete_empleado(db)
    elif opcion == '0':
        return
    else:
        print("\nOpción no válida.")
        input("Presione Enter para continuar...")

# ==============================================
# Funciones del menú de cliente
# ==============================================

def enviar_paquete(db: Session, usuario_data: Dict[str, Any]) -> None:
    """Permite a un cliente solicitar el envío de un paquete."""
    mostrar_encabezado("SOLICITUD DE ENVÍO DE PAQUETE")
    
    try:
        # Obtener el ID del cliente
        cliente = cliente_crud.obtener_por_usuario(db, usuario_id=usuario_data['id_usuario'])
        if not cliente:
            print("\nError: No se encontró la información del cliente.")
            input("\nPresione Enter para continuar...")
            return
        
        print("\nComplete la información del envío:")
        print("-" * 40)
        
        # Obtener datos del paquete
        descripcion = input("Descripción del contenido: ")
        
        while True:
            try:
                peso = float(input("Peso (kg): "))
                if peso <= 0:
                    print("El peso debe ser mayor a 0")
                    continue
                break
            except ValueError:
                print("Por favor ingrese un número válido")
        
        print("\nSeleccione el tamaño del paquete:")
        print("1. Pequeño")
        print("2. Mediano")
        print("3. Grande")
        print("4. Gigante")
        
        tipo_opciones = ['1', '2', '3', '4']
        
        tipo = ''
        while tipo not in tipo_opciones:
            tipo = input("\nSeleccione el tipo de paquete (1-4): ")
            if tipo not in tipo_opciones:
                print("Opción no válida. Intente de nuevo.")
        
        # Mapear el tipo seleccionado a los valores exactos esperados por la validación
        tipo_mapa = {
            '1': 'pequeño',   # Se convertirá a 'Pequeño' por el validador
            '2': 'mediano',   # Se convertirá a 'Mediano' por el validador
            '3': 'grande',    # Se convertirá a 'Grande' por el validador
            '4': 'gigante',   # Se convertirá a 'Gigante' por el validador
            '5': 'sobre'      # No es un valor válido según el validador, lo quitaremos
        }
        
        # Obtener el tamaño del paquete
        tamaño_paquete = tipo_mapa[tipo]
        
        # Solicitar nivel de fragilidad
        fragilidad = ''
        while fragilidad.lower() not in ['baja', 'normal', 'alta']:
            fragilidad = input("\nNivel de fragilidad (Baja/Normal/Alta): ").strip().lower()
            if fragilidad not in ['baja', 'normal', 'alta']:
                print("Opción no válida. Intente de nuevo.")
        
        # Importar PaqueteCreate aquí para evitar importación circular
        from entities.paquete import PaqueteCreate
        
        # Importar PaqueteCreate aquí para evitar importación circular
        from entities.paquete import PaqueteCreate
        
        # Crear el objeto PaqueteCreate con los datos validados
        paquete_data = PaqueteCreate(
            peso=float(peso),
            tamaño=tamaño_paquete,  # Ya está en minúsculas según el mapeo
            fragilidad=fragilidad,  # Ya está en minúsculas según la validación
            contenido=descripcion,
            tipo='normal'  # Valor por defecto según la validación
        )
        
        # Crear un diccionario con los datos adicionales necesarios
        datos_adicionales = {
            'id_paquete': str(uuid4()),
            'id_cliente': str(cliente.id_cliente),
        }
        
        # Mostrar los datos del paquete
        print("\nDatos del paquete a crear:")
        print(f"ID Cliente: {datos_adicionales['id_cliente']}")
        print(f"Peso: {paquete_data.peso}")
        print(f"Tamaño: {paquete_data.tamaño}")
        print(f"Fragilidad: {paquete_data.fragilidad}")
        print(f"Contenido: {paquete_data.contenido}")
        print(f"Tipo: {paquete_data.tipo}")
        
        # Mostrar los datos que se están procesando
        print("\n=== DATOS DE DEPURACIÓN ===")
        print("Datos del paquete:", paquete_data.dict())
        print("Datos adicionales:", datos_adicionales)
        
        # Combinar los datos validados con los adicionales
        datos_creacion = {
            **paquete_data.dict(),
            **datos_adicionales,
            'creado_por': usuario_data['id_usuario']
        }
        
        print("Datos finales para crear el paquete:", datos_creacion)
        print("==========================\n")
        
        # Llamar al método crear con los datos combinados
        nuevo_paquete = paquete_crud.crear(
            db=db, 
            datos_entrada=datos_creacion,
            creado_por=usuario_data['id_usuario']
        )
        
        if nuevo_paquete is None:
            print("\nError: No se pudo crear el paquete. Verifica que todos los datos sean válidos.")
            print("Posibles causas:")
            print("- El tamaño del paquete debe ser uno de: pequeño, mediano, grande, gigante")
            print("- El peso debe estar entre 0.1kg y 50.0kg")
            print("- La fragilidad debe ser: baja, normal o alta")
            print("- El tipo debe ser: normal o express")
            return
            
        print(f"\n¡Paquete registrado exitosamente!")
        print(f"Número de seguimiento: {nuevo_paquete.id_paquete}")
        
    except Exception as e:
        print(f"\nError al registrar el paquete: {str(e)}")
        import traceback
        traceback.print_exc()
    
    input("\nPresione Enter para continuar...")

def seguimiento_paquetes(db: Session, usuario_data: Dict[str, Any]) -> None:
    """Permite a un cliente rastrear sus paquetes."""
    mostrar_encabezado("RASTREO DE PAQUETES")
    
    try:
        # Obtener el ID del cliente
        cliente = cliente_crud.obtener_por_usuario(db, usuario_id=usuario_data['id_usuario'])
        if not cliente:
            print("\nError: No se encontró la información del cliente.")
            input("\nPresione Enter para continuar...")
            return
        
        print("\nOpciones de búsqueda:")
        print("1. Buscar por número de seguimiento")
        print("2. Ver todos mis paquetes")
        print("0. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            num_seguimiento = input("\nIngrese el número de seguimiento: ").strip()
            paq = paquete_crud.obtener_por_id(db, id_paquete=num_seguimiento)
            
            if paq and str(paq.id_cliente) == str(cliente.id_cliente):
                mostrar_detalle_paquete(paq)
            else:
                print("\nNo se encontró ningún paquete con ese número de seguimiento.")
                
        elif opcion == '2':
            paquetes, total = paquete_crud.obtener_por_cliente(db, id_cliente=cliente.id_cliente)
            if paquetes and total > 0:
                print("\nTus paquetes:")
                print("-" * 80)
                print(f"{'N° SEGUIMIENTO':<20} {'DESCRIPCIÓN':<30} {'ESTADO':<15} {'FECHA REGISTRO'}")
                print("-" * 80)
                for p in paquetes:
                    # Obtener el ID del paquete como cadena
                    id_paquete = str(getattr(p, 'id_paquete', 'N/A'))
                    # Obtener la descripción (usando 'contenido' como respaldo si 'descripcion' no existe)
                    descripcion = getattr(p, 'descripcion', getattr(p, 'contenido', 'Sin descripción'))
                    # Limitar la longitud de la descripción para la visualización
                    descripcion = str(descripcion)[:28] if descripcion else 'Sin descripción'
                    # Obtener la fecha (usando 'fecha_registro' como respaldo si 'fecha_creacion' no existe)
                    fecha = getattr(p, 'fecha_creacion', getattr(p, 'fecha_registro', None))
                    fecha_str = fecha.strftime('%Y-%m-%d') if fecha else 'N/A'
                    # Obtener el estado, con valor por defecto si no existe
                    estado = getattr(p, 'estado', 'DESCONOCIDO')
                    # Imprimir la línea formateada
                    print(f"{id_paquete:<20} {descripcion:<30} {estado:<15} {fecha_str}")
                    
                
                # Opción para ver detalles de un paquete específico
                ver_detalle = input("\n¿Desea ver los detalles de un paquete? (s/n): ").lower()
                if ver_detalle == 's':
                    num_seguimiento = input("Ingrese el número de seguimiento: ").strip()
                    paq = next((p for p in paquetes if str(p.id_paquete) == num_seguimiento), None)
                    if paq:
                        mostrar_detalle_paquete(paq)
                    else:
                        print("Número de seguimiento no válido.")
            else:
                print("\nNo tienes paquetes registrados.")
                
    except Exception as e:
        print(f"\nError al buscar paquetes: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def mis_paquetes(db: Session, usuario_data: Dict[str, Any]) -> None:
    """Muestra el historial de paquetes del cliente."""
    mostrar_encabezado("MIS PAQUETES")
    
    try:
        # Obtener el ID del cliente
        cliente = cliente_crud.obtener_por_usuario(db, usuario_id=usuario_data['id_usuario'])
        if not cliente:
            print("\nError: No se encontró la información del cliente.")
            input("\nPresione Enter para continuar...")
            return
        
        # Obtener los paquetes del cliente
        paquetes, total = paquete_crud.obtener_por_cliente(db, id_cliente=cliente.id_cliente)
        
        if not paquetes or total == 0:
            print("\nNo tienes paquetes registrados.")
            input("\nPresione Enter para continuar...")
            return
        
        # Filtrar por estado si el usuario lo desea
        print("\nFiltros disponibles:")
        print("1. Ver todos los paquetes")
        print("2. Solo pendientes")
        print("3. Solo en tránsito")
        print("4. Solo entregados")
        print("0. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        estados_filtro = {
            '1': None,  # Todos
            '2': 'registrado',
            '3': 'en_transito',
            '4': 'entregado'
        }
        
        if opcion == '0':
            return
            
        if opcion not in estados_filtro:
            print("\nOpción no válida.")
            input("\nPresione Enter para continuar...")
            return
        
        # Filtrar paquetes si es necesario
        paquetes_filtrados = paquetes
        if opcion != '1':  # Si no es 'todos'
            estado = estados_filtro[opcion]
            paquetes_filtrados = [p for p in paquetes if hasattr(p, 'estado') and p.estado == estado]
            
            if not paquetes_filtrados:
                print(f"\nNo tienes paquetes con estado '{estado}'.")
                input("\nPresione Enter para continuar...")
                return
        
        # Mostrar los paquetes
        print("\nTus paquetes:")
        print("-" * 100)
        print(f"{'N° SEGUIMIENTO':<20} {'DESCRIPCIÓN':<30} {'TIPO':<15} {'PESO (kg)':<10} {'ESTADO':<15} {'FECHA'}")
        print("-" * 100)
        
        for p in paquetes_filtrados:
            # Convertir UUID a string y mostrar solo los primeros 8 caracteres para mejor legibilidad
            id_str = str(p.id_paquete)[:8]
            # Usar getattr para manejar atributos que podrían no existir
            descripcion = getattr(p, 'descripcion', getattr(p, 'contenido', 'Sin descripción'))[:28]
            tipo = getattr(p, 'tipo', 'N/A')
            peso = getattr(p, 'peso', 0.0)
            estado = getattr(p, 'estado', 'N/A')
            fecha = getattr(p, 'fecha_registro', getattr(p, 'fecha_creacion', None))
            fecha_str = fecha.strftime('%Y-%m-%d') if fecha else 'N/A'
            
            print(f"{id_str:<8}... {descripcion:<30} {tipo:<15} {peso:<10.2f} {estado:<15} {fecha_str}")
        
        # Opción para ver detalles de un paquete específico
        ver_detalle = input("\n¿Desea ver los detalles de un paquete? (s/n): ").strip().lower()
        if ver_detalle == 's':
            num_seguimiento = input("Ingrese el número de seguimiento (primeros caracteres): ").strip()
            # Buscar coincidencias parciales del ID
            paquetes_coincidentes = [p for p in paquetes if str(p.id_paquete).startswith(num_seguimiento)]
            
            if len(paquetes_coincidentes) == 1:
                mostrar_detalle_paquete(paquetes_coincidentes[0])
            elif len(paquetes_coincidentes) > 1:
                print("\nVarios paquetes coinciden con esa búsqueda. Por favor sea más específico.")
                print("Coincidencias encontradas:")
                for p in paquetes_coincidentes:
                    print(f"- {str(p.id_paquete)[:8]}...")
            else:
                print("\nNo se encontró ningún paquete con ese número de seguimiento.")
                
            input("\nPresione Enter para continuar...")
                
    except Exception as e:
        print(f"\nError al obtener los paquetes: {str(e)}")
        input("\nPresione Enter para continuar...")

def mostrar_detalle_paquete(paq: Any) -> None:
    """Muestra los detalles completos de un paquete."""
    print("\n" + "=" * 60)
    print("DETALLE DEL PAQUETE".center(60))
    print("=" * 60)
    print(f"N° de seguimiento: {paq.id_paquete}")
    print(f"Descripción: {paq.descripcion}")
    print(f"Tipo: {paq.tipo}")
    print(f"Peso: {paq.peso} kg")
    print(f"Estado: {paq.estado.upper()}")
    print(f"Fecha de registro: {paq.fecha_registro.strftime('%Y-%m-%d %H:%M')}")
    
    # Mostrar información adicional si está disponible
    if hasattr(paq, 'fecha_entrega') and paq.fecha_entrega:
        print(f"Fecha de entrega: {paq.fecha_entrega.strftime('%Y-%m-%d %H:%M')}")
    
    if hasattr(paq, 'observaciones') and paq.observaciones:
        print(f"\nObservaciones: {paq.observaciones}")
    
    print("=" * 60)
    input("\nPresione Enter para continuar...")

def mostrar_perfil(db: Session, usuario_data: Dict[str, Any]) -> None:
    """
    Muestra el perfil detallado del usuario actual, con información específica
    según el tipo de usuario (cliente o empleado).
    
    Args:
        db: Sesión de base de datos
        usuario_data: Diccionario con los datos del usuario
    """
    from cruds import cliente_crud, empleado_crud, rol_crud
    
    mostrar_encabezado("MI PERFIL DE USUARIO")
    
    # Obtener datos básicos del usuario
    nombre_usuario = usuario_data.get('nombre_usuario', 'No especificado')
    email = usuario_data.get('email', 'No especificado')
    
    # Obtener el nombre del rol a partir del ID
    rol_id = usuario_data.get('id_rol')
    rol_nombre = 'Sin asignar'
    if rol_id:
        try:
            rol = rol_crud.get(db, id=rol_id)
            if rol:
                rol_nombre = rol.nombre_rol.capitalize()
        except Exception as e:
            print(f"\nError al obtener el rol: {e}")
    
    estado = 'Activo' if usuario_data.get('activo', False) else 'Inactivo'
    fecha_creacion = usuario_data.get('fecha_creacion', 'No disponible')
    ultimo_acceso = usuario_data.get('ultimo_acceso', 'Nunca')
    
    # Asegurar que el correo no sea None
    if email is None:
        email = 'No especificado'
    
    # Formatear fechas si están disponibles
    if isinstance(fecha_creacion, datetime):
        fecha_creacion = fecha_creacion.strftime('%d/%m/%Y %H:%M')
    if isinstance(ultimo_acceso, datetime):
        ultimo_acceso = ultimo_acceso.strftime('%d/%m/%Y %H:%M')
    
    # Mostrar información básica del perfil
    print("\n" + "=" * 80)
    print("INFORMACIÓN BÁSICA".center(80))
    print("=" * 80)
    print(f"{'Usuario:':<20} {nombre_usuario}")
    print(f"{'Correo:':<20} {email}")
    print(f"{'Rol:':<20} {rol_nombre}")
    print(f"{'Estado:':<20} {estado}")
    
    # Mostrar información específica según el tipo de usuario
    if rol_nombre.lower() == 'cliente':
        # Obtener información adicional del cliente
        cliente = cliente_crud.obtener_por_usuario(db, usuario_id=usuario_data['id_usuario'])
        if cliente:
            print("\n" + "=" * 80)
            print("INFORMACIÓN DEL CLIENTE".center(80))
            print("=" * 80)
            print(f"{'Nombre completo:':<20} {cliente.primer_nombre} {cliente.segundo_nombre or ''} {cliente.primer_apellido} {cliente.segundo_apellido or ''}".replace('  ', ' '))
            print(f"{'Tipo:':<20} {cliente.tipo.capitalize() if hasattr(cliente, 'tipo') else 'No especificado'}")
            print(f"{'Documento:':<20} {getattr(cliente, 'numero_documento', 'No especificado')}")
            print(f"{'Teléfono:':<20} {getattr(cliente, 'telefono', 'No especificado')}")
            print(f"{'Dirección:':<20} {getattr(cliente, 'direccion', 'No especificada')}")
            
            # Mostrar estadísticas de paquetes si están disponibles
            if hasattr(cliente, 'paquetes'):
                total_paquetes = len(cliente.paquetes)
                entregados = sum(1 for p in cliente.paquetes if getattr(p, 'estado', '') == 'entregado')
                print(f"\n{'Paquetes totales:':<20} {total_paquetes}")
                print(f"{'Paquetes entregados:':<20} {entregados}")
    
    elif rol.lower() in ['empleado', 'administrador']:
        # Obtener información adicional del empleado
        empleado = empleado_crud.obtener_por_usuario(db, usuario_id=usuario_data['id_usuario'])
        if empleado:
            print("\n" + "=" * 80)
            print("INFORMACIÓN DEL EMPLEADO".center(80))
            print("=" * 80)
            print(f"{'Nombre completo:':<20} {empleado.primer_nombre} {empleado.segundo_nombre or ''} {empleado.primer_apellido} {empleado.segundo_apellido or ''}".replace('  ', ' '))
            print(f"{'Tipo:':<20} {empleado.tipo_empleado.capitalize() if hasattr(empleado, 'tipo_empleado') else 'No especificado'}")
            
            if hasattr(empleado, 'fecha_ingreso'):
                fecha_ingreso = empleado.fecha_ingreso.strftime('%d/%m/%Y') if empleado.fecha_ingreso else 'No especificada'
                print(f"{'Fecha de ingreso:':<20} {fecha_ingreso}")
            
            if hasattr(empleado, 'sede') and empleado.sede:
                print(f"{'Sede:':<20} {empleado.sede.nombre if hasattr(empleado.sede, 'nombre') else 'No especificada'}")
    
    # Mostrar información de la cuenta
    print("\n" + "=" * 80)
    print("INFORMACIÓN DE LA CUENTA".center(80))
    print("=" * 80)
    print(f"{'Creado el:':<20} {fecha_creacion}")
    print(f"{'Último acceso:':<20} {ultimo_acceso}")
    
    # Mostrar opciones adicionales según el rol
    print("\n" + "=" * 80)
    print("ACCIONES DISPONIBLES".center(80))
    print("=" * 80)
    
    opciones = []
    
    # Opciones para todos los usuarios
    opciones.append(("1", "Actualizar datos personales"))
    
    # Opciones específicas por rol
    if rol_nombre.lower() == 'cliente':
        opciones.append(("2", "Ver historial de envíos"))
    
    # Opción para volver
    opciones.append(("0", "Volver al menú principal"))
    
    # Mostrar opciones
    for codigo, texto in opciones:
        print(f"{codigo}. {texto}")
    
    # Manejar la selección del usuario
    while True:
        try:
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == '0':
                return
            elif opcion == '1':
                # Aquí iría la lógica para actualizar datos personales
                print("\nFunción de actualización de datos personales no implementada aún.")
                input("Presione Enter para continuar...")
                break
            elif opcion == '2' and rol_nombre.lower() == 'cliente':
                # Mostrar historial de envíos
                mis_paquetes(db, usuario_data)
                break
            else:
                print("\nOpción no válida. Intente de nuevo.")
        except Exception as e:
            print(f"\nError: {str(e)}")
            input("Presione Enter para continuar...")

# ==============================================
# Funciones auxiliares para gestión de sedes
# ==============================================

def listar_sedes(db: Session) -> None:
    """Lista todas las sedes en el sistema."""
    mostrar_encabezado("LISTADO DE SEDES")
    try:
        sedes = sede_crud.get_multi(db)
        if not sedes:
            print("No hay sedes registradas.")
            input("\nPresione Enter para continuar...")
            return
        
        # Preparar datos para mostrar en tabla
        datos = []
        for sede in sedes:
            datos.append([
                sede.id_sede,
                sede.ciudad,
                sede.direccion,
                sede.telefono,
                'Activa' if sede.activo else 'Inactiva'
            ])
        
        # Mostrar tabla
        print("\n" + tabulate(datos, headers=["ID", "Ciudad", "Dirección", "Teléfono", "Estado"], tablefmt="grid"))
        
    except Exception as e:
        print(f"\nError al listar sedes: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def buscar_sede_por_ciudad(db: Session) -> None:
    """Busca sedes por ciudad."""
    mostrar_encabezado("BUSCAR SEDE POR CIUDAD")
    try:
        ciudad = input("\nIngrese el nombre de la ciudad a buscar: ").strip()
        if not ciudad:
            print("Debe ingresar un nombre de ciudad.")
            input("\nPresione Enter para continuar...")
            return
        
        sedes = sede_crud.get_by_ciudad(db, ciudad=ciudad)
        if not sedes:
            print(f"\nNo se encontraron sedes en la ciudad de {ciudad}.")
            input("\nPresione Enter para continuar...")
            return
        
        # Preparar datos para mostrar en tabla
        datos = []
        for sede in sedes:
            datos.append([
                sede.id_sede,
                sede.ciudad,
                sede.direccion,
                sede.telefono,
                'Activa' if sede.activo else 'Inactiva'
            ])
        
        # Mostrar tabla
        print(f"\nSedes encontradas en {ciudad}:")
        print(tabulate(datos, headers=["ID", "Ciudad", "Dirección", "Teléfono", "Estado"], tablefmt="grid"))
        
    except Exception as e:
        print(f"\nError al buscar sedes: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def agregar_sede(db: Session) -> None:
    """Agrega una nueva sede."""
    mostrar_encabezado("AGREGAR NUEVA SEDE")
    try:
        print("\nComplete la información de la nueva sede:")
        print("-" * 40)
        
        ciudad = input("Ciudad: ").strip()
        direccion = input("Dirección: ").strip()
        telefono = input("Teléfono: ").strip()
        
        # Validar datos requeridos
        if not all([ciudad, direccion, telefono]):
            print("\nTodos los campos son obligatorios.")
            input("Presione Enter para continuar...")
            return
        
        # Crear objeto de sede
        sede_data = SedeCreate(
            ciudad=ciudad,
            direccion=direccion,
            telefono=telefono
        )
        
        # Guardar la sede
        nueva_sede = sede_crud.create(db, obj_in=sede_data, creado_por=uuid4())
        
        print(f"\n¡Sede registrada exitosamente con ID: {nueva_sede.id_sede}!")
        
    except Exception as e:
        print(f"\nError al registrar la sede: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def editar_sede(db: Session) -> None:
    """Edita una sede existente."""
    mostrar_encabezado("EDITAR SEDE")
    try:
        # Listar sedes para seleccionar
        sedes = sede_crud.get_multi(db)
        if not sedes:
            print("No hay sedes registradas para editar.")
            input("\nPresione Enter para continuar...")
            return
        
        # Mostrar lista de sedes
        print("\nSeleccione la sede a editar:")
        for i, sede in enumerate(sedes, 1):
            print(f"{i}. {sede.ciudad} - {sede.direccion}")
        
        try:
            opcion = int(input("\nNúmero de sede a editar (0 para cancelar): "))
            if opcion == 0:
                return
            
            sede = sedes[opcion - 1]
            
            # Mostrar datos actuales
            print("\nDatos actuales:")
            print(f"Ciudad: {sede.ciudad}")
            print(f"Dirección: {sede.direccion}")
            print(f"Teléfono: {sede.telefono}")
            
            # Solicitar nuevos datos
            print("\nIngrese los nuevos datos (deje en blanco para no modificar):")
            ciudad = input(f"Ciudad [{sede.ciudad}]: ").strip() or sede.ciudad
            direccion = input(f"Dirección [{sede.direccion}]: ").strip() or sede.direccion
            telefono = input(f"Teléfono [{sede.telefono}]: ").strip() or sede.telefono
            
            # Crear objeto de actualización
            update_data = {
                "ciudad": ciudad,
                "direccion": direccion,
                "telefono": telefono
            }
            
            # Actualizar la sede
            sede_actualizada = sede_crud.update(db, db_obj=sede, obj_in=update_data)
            
            print("\n¡Sede actualizada exitosamente!")
            
        except (ValueError, IndexError):
            print("\nOpción no válida.")
        
    except Exception as e:
        print(f"\nError al editar la sede: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def cambiar_estado_sede(db: Session) -> None:
    """Cambia el estado (activo/inactivo) de una sede."""
    mostrar_encabezado("CAMBIAR ESTADO DE SEDE")
    try:
        # Listar solo sedes activas
        sedes = sede_crud.get_multi(db)
        if not sedes:
            print("No hay sedes registradas.")
            input("\nPresione Enter para continuar...")
            return
        
        # Mostrar lista de sedes
        print("\nSeleccione la sede para cambiar su estado:")
        for i, sede in enumerate(sedes, 1):
            estado = "Activa" if sede.activo else "Inactiva"
            print(f"{i}. {sede.ciudad} - {sede.direccion} ({estado})")
        
        try:
            opcion = int(input("\nNúmero de sede (0 para cancelar): "))
            if opcion == 0:
                return
            
            sede = sedes[opcion - 1]
            nuevo_estado = not sede.activo
            
            # Confirmar acción
            accion = "activar" if nuevo_estado else "desactivar"
            confirmar = input(f"\n¿Está seguro de {accion} la sede {sede.ciudad}? (s/n): ").lower()
            
            if confirmar == 's':
                # Actualizar estado
                sede.activo = nuevo_estado
                db.commit()
                db.refresh(sede)
                
                estado = "activada" if nuevo_estado else "desactivada"
                print(f"\n¡Sede {estado} exitosamente!")
            else:
                print("\nOperación cancelada.")
            
        except (ValueError, IndexError):
            print("\nOpción no válida.")
        
    except Exception as e:
        print(f"\nError al cambiar el estado de la sede: {str(e)}")
    
    input("\nPresione Enter para continuar...")

# ==============================================
# Funciones auxiliares para gestión de transportes
# ==============================================

def listar_transportes(db: Session) -> None:
    """Lista todos los transportes en el sistema."""
    mostrar_encabezado("LISTADO DE TRANSPORTES")
    try:
        transportes = transporte_crud.get_multi(db)
        if not transportes:
            print("No hay transportes registrados.")
            input("\nPresione Enter para continuar...")
            return
        
        # Preparar datos para mostrar en tabla
        datos = []
        for transporte in transportes:
            datos.append([
                transporte.id_transporte,
                f"{transporte.marca} {transporte.modelo}",
                transporte.placa,
                transporte.tipo_vehiculo,
                f"{transporte.capacidad_carga} kg",
                transporte.estado.title(),
                'Activo' if transporte.activo else 'Inactivo'
            ])
        
        # Mostrar tabla
        print("\n" + tabulate(datos, headers=["ID", "Vehículo", "Placa", "Tipo", "Capacidad", "Estado", "Activo"], tablefmt="grid"))
        
    except Exception as e:
        print(f"\nError al listar transportes: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def buscar_transporte_por_placa(db: Session) -> None:
    """Busca un transporte por su placa."""
    mostrar_encabezado("BUSCAR TRANSPORTE POR PLACA")
    try:
        placa = input("\nIngrese la placa del vehículo a buscar: ").strip().upper()
        if not placa:
            print("Debe ingresar una placa.")
            input("\nPresione Enter para continuar...")
            return
        
        transporte = transporte_crud.get_by_placa(db, placa=placa)
        if not transporte:
            print("\nNo se encontró ningún vehículo con esa placa.")
            input("\nPresione Enter para continuar...")
            return
        
        # Mostrar detalles del transporte
        print("\nDetalles del vehículo:")
        print("-" * 40)
        print(f"ID: {transporte.id_transporte}")
        print(f"Tipo: {transporte.tipo_vehiculo}")
        print(f"Marca: {transporte.marca}")
        print(f"Modelo: {transporte.modelo}")
        print(f"Año: {transporte.año}")
        print(f"Placa: {transporte.placa}")
        print(f"Capacidad: {transporte.capacidad_carga} kg")
        print(f"Estado: {transporte.estado.title()}")
        print(f"Activo: {'Sí' if transporte.activo else 'No'}")
        
        # Mostrar información de la sede si está asignado
        if transporte.id_sede:
            sede = sede_crud.get(db, id=transporte.id_sede)
            if sede:
                print(f"\nAsignado a sede: {sede.ciudad} - {sede.direccion}")
        
    except Exception as e:
        print(f"\nError al buscar el transporte: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def agregar_transporte(db: Session) -> None:
    """Agrega un nuevo transporte."""
    mostrar_encabezado("AGREGAR NUEVO TRANSPORTE")
    try:
        print("\nComplete la información del nuevo vehículo:")
        print("-" * 40)
        
        # Obtener datos del transporte
        tipo_vehiculo = input("Tipo de vehículo (ej. camión, moto, furgoneta): ").strip()
        marca = input("Marca: ").strip()
        modelo = input("Modelo: ").strip()
        placa = input("Placa: ").strip().upper()
        
        # Validar año
        while True:
            try:
                año = int(input("Año: ").strip())
                if 1900 <= año <= datetime.now().year + 1:  # Permitir el próximo año
                    break
                print(f"El año debe estar entre 1900 y {datetime.now().year + 1}")
            except ValueError:
                print("Por favor ingrese un año válido.")
        
        # Validar capacidad
        while True:
            try:
                capacidad_carga = float(input("Capacidad de carga (kg): ").strip())
                if capacidad_carga > 0:
                    break
                print("La capacidad debe ser mayor a 0")
            except ValueError:
                print("Por favor ingrese un número válido.")
        
        # Validar estado
        print("\nEstados disponibles:")
        print("1. Disponible")
        print("2. En mantenimiento")
        print("3. En ruta")
        print("4. Fuera de servicio")
        
        estados = {
            '1': 'disponible',
            '2': 'mantenimiento',
            '3': 'en_ruta',
            '4': 'fuera_servicio'
        }
        
        while True:
            opcion_estado = input("\nSeleccione el estado (1-4): ").strip()
            if opcion_estado in estados:
                estado = estados[opcion_estado]
                break
            print("Opción no válida. Intente de nuevo.")
        
        # Crear objeto de transporte
        transporte_data = TransporteCreate(
            tipo_vehiculo=tipo_vehiculo,
            marca=marca,
            modelo=modelo,
            placa=placa,
            año=año,
            capacidad_carga=capacidad_carga,
            estado=estado,
            id_sede=None  # Se puede asignar después
        )
        
        # Guardar el transporte
        nuevo_transporte = transporte_crud.create(db, obj_in=transporte_data)
        
        print(f"\n¡Vehículo registrado exitosamente con ID: {nuevo_transporte.id_transporte}!")
        
        # Preguntar si desea asignar a una sede
        asignar_ahora = input("\n¿Desea asignar este vehículo a una sede ahora? (s/n): ").lower()
        if asignar_ahora == 's':
            asignar_transporte_a_sede_especifico(db, nuevo_transporte.id_transporte)
        
    except Exception as e:
        print(f"\nError al registrar el vehículo: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def editar_transporte(db: Session) -> None:
    """Edita un transporte existente."""
    mostrar_encabezado("EDITAR TRANSPORTE")
    try:
        # Listar transportes para seleccionar
        transportes = transporte_crud.get_multi(db)
        if not transportes:
            print("No hay transportes registrados para editar.")
            input("\nPresione Enter para continuar...")
            return
        
        # Mostrar lista de transportes
        print("\nSeleccione el vehículo a editar:")
        for i, transporte in enumerate(transportes, 1):
            print(f"{i}. {transporte.marca} {transporte.modelo} - {transporte.placa}")
        
        try:
            opcion = int(input("\nNúmero de vehículo a editar (0 para cancelar): "))
            if opcion == 0:
                return
            
            transporte = transportes[opcion - 1]
            
            # Mostrar datos actuales
            print("\nDatos actuales:")
            print(f"Tipo: {transporte.tipo_vehiculo}")
            print(f"Marca: {transporte.marca}")
            print(f"Modelo: {transporte.modelo}")
            print(f"Año: {transporte.año}")
            print(f"Placa: {transporte.placa}")
            print(f"Capacidad: {transporte.capacidad_carga} kg")
            print(f"Estado: {transporte.estado.title()}")
            
            # Solicitar nuevos datos
            print("\nIngrese los nuevos datos (deje en blanco para no modificar):")
            tipo_vehiculo = input(f"Tipo de vehículo [{transporte.tipo_vehiculo}]: ").strip() or transporte.tipo_vehiculo
            marca = input(f"Marca [{transporte.marca}]: ").strip() or transporte.marca
            modelo = input(f"Modelo [{transporte.modelo}]: ").strip() or transporte.modelo
            placa = input(f"Placa [{transporte.placa}]: ").strip().upper() or transporte.placa
            
            # Validar año
            while True:
                año_input = input(f"Año [{transporte.año}]: ").strip()
                if not año_input:
                    año = transporte.año
                    break
                try:
                    año = int(año_input)
                    if 1900 <= año <= datetime.now().year + 1:
                        break
                    print(f"El año debe estar entre 1900 y {datetime.now().year + 1}")
                except ValueError:
                    print("Por favor ingrese un año válido.")
            
            # Validar capacidad
            while True:
                capacidad_input = input(f"Capacidad de carga (kg) [{transporte.capacidad_carga}]: ").strip()
                if not capacidad_input:
                    capacidad_carga = transporte.capacidad_carga
                    break
                try:
                    capacidad_carga = float(capacidad_input)
                    if capacidad_carga > 0:
                        break
                    print("La capacidad debe ser mayor a 0")
                except ValueError:
                    print("Por favor ingrese un número válido.")
            
            # Validar estado
            print("\nEstados disponibles:")
            print("1. Disponible")
            print("2. En mantenimiento")
            print("3. En ruta")
            print("4. Fuera de servicio")
            
            estados = {
                '1': 'disponible',
                '2': 'mantenimiento',
                '3': 'en_ruta',
                '4': 'fuera_servicio'
            }
            
            print(f"\nEstado actual: {transporte.estado}")
            cambiar_estado = input("¿Desea cambiar el estado? (s/n): ").lower()
            if cambiar_estado == 's':
                while True:
                    opcion_estado = input("Seleccione el nuevo estado (1-4): ").strip()
                    if opcion_estado in estados:
                        estado = estados[opcion_estado]
                        break
                    print("Opción no válida. Intente de nuevo.")
            else:
                estado = transporte.estado
            
            # Crear objeto de actualización
            update_data = {
                "tipo_vehiculo": tipo_vehiculo,
                "marca": marca,
                "modelo": modelo,
                "placa": placa,
                "año": año,
                "capacidad_carga": capacidad_carga,
                "estado": estado
            }
            
            # Actualizar el transporte
            transporte_actualizado = transporte_crud.update(db, db_obj=transporte, obj_in=update_data)
            
            print("\n¡Vehículo actualizado exitosamente!")
            
        except (ValueError, IndexError):
            print("\nOpción no válida.")
        
    except Exception as e:
        print(f"\nError al editar el vehículo: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def cambiar_estado_transporte(db: Session) -> None:
    """Cambia el estado (activo/inactivo) de un transporte."""
    mostrar_encabezado("CAMBIAR ESTADO DE TRANSPORTE")
    try:
        # Listar transportes activos
        transportes = transporte_crud.get_multi(db)
        if not transportes:
            print("No hay transportes registrados.")
            input("\nPresione Enter para continuar...")
            return
        
        # Mostrar lista de transportes
        print("\nSeleccione el vehículo para cambiar su estado:")
        for i, transporte in enumerate(transportes, 1):
            estado = "Activo" if transporte.activo else "Inactivo"
            print(f"{i}. {transporte.marca} {transporte.modelo} - {transporte.placa} ({estado})")
        
        try:
            opcion = int(input("\nNúmero de vehículo (0 para cancelar): "))
            if opcion == 0:
                return
            
            transporte = transportes[opcion - 1]
            nuevo_estado = not transporte.activo
            
            # Confirmar acción
            accion = "activar" if nuevo_estado else "desactivar"
            confirmar = input(f"\n¿Está seguro de {accion} el vehículo {transporte.marca} {transporte.modelo}? (s/n): ").lower()
            
            if confirmar == 's':
                # Actualizar estado
                transporte.activo = nuevo_estado
                db.commit()
                db.refresh(transporte)
                
                estado = "activado" if nuevo_estado else "desactivado"
                print(f"\n¡Vehículo {estado} exitosamente!")
            else:
                print("\nOperación cancelada.")
            
        except (ValueError, IndexError):
            print("\nOpción no válida.")
        
    except Exception as e:
        print(f"\nError al cambiar el estado del vehículo: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def asignar_transporte_a_sede(db: Session, id_transporte: UUID = None) -> None:
    """Asigna un transporte a una sede."""
    mostrar_encabezado("ASIGNAR TRANSPORTE A SEDE")
    try:
        # Si no se proporciona un ID de transporte, mostrar lista para seleccionar
        if id_transporte is None:
            transportes = transporte_crud.get_multi(db)
            if not transportes:
                print("No hay transportes registrados.")
                input("\nPresione Enter para continuar...")
                return
            
            # Mostrar lista de transportes
            print("\nSeleccione el vehículo a asignar:")
            for i, transporte in enumerate(transportes, 1):
                sede_actual = f" - Sede: {transporte.sede.ciudad}" if transporte.sede else " - Sin asignar"
                print(f"{i}. {transporte.marca} {transporte.modelo} ({transporte.placa}){sede_actual}")
            
            try:
                opcion = int(input("\nNúmero de vehículo (0 para cancelar): "))
                if opcion == 0:
                    return
                
                transporte = transportes[opcion - 1]
                id_transporte = transporte.id_transporte
                
            except (ValueError, IndexError):
                print("\nOpción no válida.")
                input("\nPresione Enter para continuar...")
                return
        
        # Obtener el transporte
        transporte = transporte_crud.get(db, id=id_transporte)
        if not transporte:
            print("\nNo se encontró el vehículo especificado.")
            input("\nPresione Enter para continuar...")
            return
        
        # Listar sedes disponibles
        sedes = sede_crud.get_multi(db)
        if not sedes:
            print("No hay sedes registradas. Debe crear una sede primero.")
            input("\nPresione Enter para continuar...")
            return
        
        # Mostrar lista de sedes
        print(f"\nAsignar vehículo: {transporte.marca} {transporte.modelo} ({transporte.placa})")
        print("\nSeleccione la sede de destino:")
        print("0. Desasignar de la sede actual")
        for i, sede in enumerate(sedes, 1):
            print(f"{i}. {sede.ciudad} - {sede.direccion}")
        
        try:
            opcion = int(input("\nNúmero de sede (0 para desasignar): "))
            if opcion < 0 or opcion > len(sedes):
                print("\nOpción no válida.")
                input("\nPresione Enter para continuar...")
                return
            
            if opcion == 0:
                # Desasignar de la sede actual
                if transporte.id_sede is None:
                    print("\nEste vehículo no está asignado a ninguna sede.")
                else:
                    transporte.id_sede = None
                    db.commit()
                    db.refresh(transporte)
                    print("\n¡Vehículo desasignado exitosamente!")
            else:
                # Asignar a la sede seleccionada
                sede = sedes[opcion - 1]
                transporte.id_sede = sede.id_sede
                db.commit()
                db.refresh(transporte)
                print(f"\n¡Vehículo asignado a la sede {sede.ciudad} exitosamente!")
            
        except ValueError:
            print("\nOpción no válida.")
        
    except Exception as e:
        print(f"\nError al asignar el vehículo a la sede: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def asignar_transporte_a_sede_especifico(db: Session, id_transporte: UUID) -> None:
    """Versión específica de asignar_transporte_a_sede para un transporte ya seleccionado."""
    asignar_transporte_a_sede(db, id_transporte)

# ==============================================
# Funciones de reportes
# ==============================================

def mostrar_reportes(db: Session) -> None:
    """Muestra el menú de reportes."""
    while True:
        mostrar_encabezado("REPORTES")
        print("1. Reporte de envíos por período")
        print("2. Reporte de ingresos")
        print("3. Reporte de paquetes por estado")
        print("4. Reporte de clientes frecuentes")
        print("5. Reporte de eficiencia de transportes")
        print("0. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            reporte_envios_por_periodo(db)
        elif opcion == '2':
            reporte_ingresos(db)
        elif opcion == '3':
            reporte_paquetes_por_estado(db)
        elif opcion == '4':
            reporte_clientes_frecuentes(db)
        elif opcion == '5':
            reporte_eficiencia_transportes(db)
        elif opcion == '0':
            break
        else:
            print("\nOpción no válida.")
            input("Presione Enter para continuar...")

def reporte_envios_por_periodo(db: Session) -> None:
    """Genera un reporte de envíos por período de tiempo."""
    mostrar_encabezado("REPORTE DE ENVÍOS POR PERÍODO")
    try:
        print("\nIngrese el rango de fechas para el reporte:")
        fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ").strip()
        fecha_fin = input("Fecha de fin (YYYY-MM-DD, presione Enter para usar hoy): ").strip()
        
        # Validar fechas
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date() if fecha_fin else date.today()
            
            if fecha_inicio > fecha_fin:
                print("\nLa fecha de inicio no puede ser mayor a la fecha de fin.")
                input("\nPresione Enter para continuar...")
                return
                
        except ValueError:
            print("\nFormato de fecha inválido. Use YYYY-MM-DD.")
            input("\nPresione Enter para continuar...")
            return
        
        # Obtener datos del reporte
        query = """
        SELECT 
            DATE(fecha_registro) as fecha,
            COUNT(*) as total_envios,
            SUM(CASE WHEN estado = 'entregado' THEN 1 ELSE 0 END) as entregados,
            SUM(CASE WHEN estado = 'en_transito' THEN 1 ELSE 0 END) as en_transito,
            SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as pendientes
        FROM 
            paquetes
        WHERE 
            fecha_registro BETWEEN :fecha_inicio AND :fecha_fin + INTERVAL '1 day'
        GROUP BY 
            DATE(fecha_registro)
        ORDER BY 
            fecha
        """
        
        resultados = db.execute(
            query,
            {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
        ).fetchall()
        
        if not resultados:
            print(f"\nNo hay envíos registrados entre {fecha_inicio} y {fecha_fin}.")
            input("\nPresione Enter para continuar...")
            return
        
        # Mostrar resultados
        print(f"\nREPORTE DE ENVÍOS: {fecha_inicio} a {fecha_fin}")
        print("=" * 60)
        print(f"{'Fecha':<12} {'Total':<8} {'Entregados':<10} {'En tránsito':<12} {'Pendientes':<10}")
        print("-" * 60)
        
        totales = {
            'total': 0,
            'entregados': 0,
            'en_transito': 0,
            'pendientes': 0
        }
        
        for fila in resultados:
            print(f"{fila.fecha.strftime('%Y-%m-%d'):<12} {fila.total_envios:<8} {fila.entregados:<10} {fila.en_transito:<12} {fila.pendientes:<10}")
            totales['total'] += fila.total_envios
            totales['entregados'] += fila.entregados
            totales['en_transito'] += fila.en_transito
            totales['pendientes'] += fila.pendientes
        
        print("-" * 60)
        print(f"{'TOTAL':<12} {totales['total']:<8} {totales['entregados']:<10} {totales['en_transito']:<12} {totales['pendientes']:<10}")
        
        # Preguntar si desea exportar a CSV
        exportar = input("\n¿Desea exportar este reporte a CSV? (s/n): ").lower()
        if exportar == 's':
            nombre_archivo = f"reporte_envios_{fecha_inicio}_a_{fecha_fin}.csv"
            try:
                with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
                    f.write("Fecha,Total,Entregados,En tránsito,Pendientes\n")
                    for fila in resultados:
                        f.write(f"{fila.fecha.strftime('%Y-%m-%d')},{fila.total_envios},{fila.entregados},{fila.en_transito},{fila.pendientes}\n")
                print(f"\nReporte exportado exitosamente como '{nombre_archivo}'")
            except Exception as e:
                print(f"\nError al exportar el reporte: {str(e)}")
        
    except Exception as e:
        print(f"\nError al generar el reporte: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def reporte_ingresos(db: Session) -> None:
    """Genera un reporte de ingresos por período de tiempo."""
    mostrar_encabezado("REPORTE DE INGRESOS")
    print("\nFuncionalidad en desarrollo...")
    input("\nPresione Enter para continuar...")

def reporte_paquetes_por_estado(db: Session) -> None:
    """Genera un reporte de paquetes por estado."""
    mostrar_encabezado("REPORTE DE PAQUETES POR ESTADO")
    try:
        # Obtener datos del reporte
        query = """
        SELECT 
            estado,
            COUNT(*) as cantidad,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM paquetes), 2) as porcentaje
        FROM 
            paquetes
        GROUP BY 
            estado
        ORDER BY 
            cantidad DESC
        """
        
        resultados = db.execute(query).fetchall()
        
        if not resultados:
            print("\nNo hay paquetes registrados.")
            input("\nPresione Enter para continuar...")
            return
        
        # Mostrar resultados
        print("\nREPORTE DE PAQUETES POR ESTADO")
        print("=" * 50)
        print(f"{'Estado':<20} {'Cantidad':<10} {'Porcentaje':<10}")
        print("-" * 50)
        
        total = sum(fila.cantidad for fila in resultados)
        
        for fila in resultados:
            print(f"{fila.estado.title():<20} {fila.cantidad:<10} {fila.porcentaje}%")
        
        print("-" * 50)
        print(f"{'TOTAL':<20} {total:<10} 100.00%")
        
    except Exception as e:
        print(f"\nError al generar el reporte: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def reporte_clientes_frecuentes(db: Session) -> None:
    """Genera un reporte de los clientes más frecuentes."""
    mostrar_encabezado("REPORTE DE CLIENTES FRECUENTES")
    print("\nFuncionalidad en desarrollo...")
    input("\nPresione Enter para continuar...")

def reporte_eficiencia_transportes(db: Session) -> None:
    """Genera un reporte de eficiencia de transportes."""
    mostrar_encabezado("REPORTE DE EFICIENCIA DE TRANSPORTES")
    print("\nFuncionalidad en desarrollo...")
    input("\nPresione Enter para continuar...")

# ==============================================
# Funciones de configuración del sistema
# ==============================================

def configuracion_sistema(db: Session) -> None:
    """Muestra el menú de configuración del sistema."""
    while True:
        mostrar_encabezado("CONFIGURACIÓN DEL SISTEMA")
        print("1. Parámetros generales")
        print("2. Configuración de envíos")
        print("3. Copia de seguridad")
        print("4. Registro de actividades")
        print("0. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            configuracion_parametros_generales(db)
        elif opcion == '2':
            configuracion_envios(db)
        elif opcion == '3':
            configuracion_copia_seguridad(db)
        elif opcion == '4':
            configuracion_registro_actividades(db)
        elif opcion == '0':
            break
        else:
            print("\nOpción no válida.")
            input("Presione Enter para continuar...")

def configuracion_parametros_generales(db: Session) -> None:
    """Configuración de parámetros generales del sistema."""
    mostrar_encabezado("PARÁMETROS GENERALES")
    print("\nConfiguración de parámetros generales del sistema.")
    
    try:
        # Aquí se podrían cargar y editar parámetros desde una tabla de configuración
        # Por ahora, solo mostramos un mensaje de ejemplo
        print("\nParámetros actuales:")
        print("- Nombre de la empresa: SwiftPost")
        print("- Moneda: USD")
        print("- Zona horaria: America/Bogota")
        print("- Elementos por página: 10")
        
        # Ejemplo de cómo se podría implementar la edición
        editar = input("\n¿Desea editar estos parámetros? (s/n): ").lower()
        if editar == 's':
            print("\nFuncionalidad de edición en desarrollo...")
        
    except Exception as e:
        print(f"\nError al cargar la configuración: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def configuracion_envios(db: Session) -> None:
    """Configuración de parámetros de envíos."""
    mostrar_encabezado("CONFIGURACIÓN DE ENVÍOS")
    print("\nConfiguración de parámetros de envíos.")
    
    try:
        # Aquí se podrían cargar y editar parámetros de envíos
        print("\nParámetros actuales:")
        print("- Tiempo máximo de entrega: 5 días hábiles")
        print("- Peso máximo por paquete: 30 kg")
        print("- Tasa de envío base: $5.00")
        print("- Recargo por peso: $0.50 por kg adicional")
        
        editar = input("\n¿Desea editar estos parámetros? (s/n): ").lower()
        if editar == 's':
            print("\nFuncionalidad de edición en desarrollo...")
        
    except Exception as e:
        print(f"\nError al cargar la configuración: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def configuracion_copia_seguridad(db: Session) -> None:
    """Gestión de copias de seguridad."""
    mostrar_encabezado("COPIAS DE SEGURIDAD")
    
    try:
        print("\nOpciones de copia de seguridad:")
        print("1. Crear copia de seguridad ahora")
        print("2. Restaurar desde copia de seguridad")
        print("3. Configurar copias automáticas")
        print("0. Volver")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            print("\nCreando copia de seguridad...")
            # Aquí iría la lógica para crear la copia de seguridad
            print("¡Copia de seguridad creada exitosamente!")
        elif opcion == '2':
            print("\nRestaurando desde copia de seguridad...")
            # Aquí iría la lógica para restaurar desde copia de seguridad
            print("¡Restauración completada exitosamente!")
        elif opcion == '3':
            print("\nConfigurando copias automáticas...")
            # Aquí iría la lógica para configurar copias automáticas
            print("¡Configuración guardada exitosamente!")
        elif opcion != '0':
            print("\nOpción no válida.")
        
    except Exception as e:
        print(f"\nError en la gestión de copias de seguridad: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def configuracion_registro_actividades(db: Session) -> None:
    """Configuración del registro de actividades del sistema."""
    mostrar_encabezado("REGISTRO DE ACTIVIDADES")
    
    try:
        print("\nConfiguración del registro de actividades:")
        print("1. Nivel de registro: INFO")
        print("2. Directorio de registros: /var/log/swiftpost")
        print("3. Tamaño máximo por archivo: 10 MB")
        print("4. Número de archivos a mantener: 5")
        
        print("\nOpciones:")
        print("1. Cambiar nivel de registro")
        print("2. Ver registro de actividades")
        print("3. Exportar registro")
        print("0. Volver")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            print("\nNiveles disponibles:")
            print("1. DEBUG - Información detallada, útil para desarrollo")
            print("2. INFO - Confirmación de que las cosas funcionan como se espera")
            print("3. WARNING - Algo inesperado sucedió, pero la aplicación sigue funcionando")
            print("4. ERROR - La aplicación no pudo realizar alguna función")
            print("5. CRITICAL - Error grave que puede hacer que la aplicación falle")
            
            nivel = input("\nSeleccione el nivel de registro (1-5): ")
            niveles = {'1': 'DEBUG', '2': 'INFO', '3': 'WARNING', '4': 'ERROR', '5': 'CRITICAL'}
            
            if nivel in niveles:
                # Aquí iría la lógica para cambiar el nivel de registro
                print(f"\nNivel de registro cambiado a: {niveles[nivel]}")
            else:
                print("\nOpción no válida.")
                
        elif opcion == '2':
            print("\nMostrando las últimas 50 entradas del registro:")
            print("-" * 80)
            # Aquí iría la lógica para mostrar las entradas del registro
            print("[2023-05-15 09:30:15] INFO: Usuario admin inició sesión")
            print("[2023-05-15 09:32:45] INFO: Nuevo paquete registrado (ID: 12345)")
            print("[2023-05-15 10:15:22] WARNING: Intento de inicio de sesión fallido para usuario 'test'")
            print("...")
            
        elif opcion == '3':
            nombre_archivo = input("\nIngrese el nombre del archivo para exportar: ").strip()
            if nombre_archivo:
                # Aquí iría la lógica para exportar el registro
                print(f"\nRegistro exportado exitosamente como '{nombre_archivo}'")
        
    except Exception as e:
        print(f"\nError en la configuración del registro: {str(e)}")
    
    input("\nPresione Enter para continuar...")

# ==============================================
# Función principal
# ==============================================

def main() -> None:
    """Función principal de la aplicación."""
    try:
        # Inicializar la base de datos
        db = SessionLocal()
        create_tables()
        init_roles(db)
        inicializar_tipos_documento(db)
        
        # Limpiar caché de roles al iniciar
        from auth import clear_roles_cache
        clear_roles_cache()
        
        # Forzar la carga inicial de roles
        from auth import get_roles
        get_roles(db)
        
        usuario_actual = None
        
        while True:
            opcion = mostrar_menu(usuario_actual)
            
            if not usuario_actual:
                # Menú para usuarios no autenticados
                if opcion == '1':  # Iniciar sesión
                    usuario_actual = login(db)
                elif opcion == '2':  # Registrarse como cliente
                    registrar_usuario(db, es_empleado=False)
                elif opcion == '0':  # Salir
                    print("\n¡Gracias por usar SwiftPost!")
                    break
                else:
                    print("\nOpción no válida. Intente de nuevo.")
            else:
                # Determinar el rol del usuario
                from auth import is_admin, is_employee, is_client
                
                if is_admin(usuario_actual):
                    # Menú de administrador
                    if opcion == '1':  # Administrar usuarios
                        administrar_usuarios(db)
                    elif opcion == '2':  # Gestionar empleados
                        gestionar_empleados(db)
                    elif opcion == '3':  # Gestionar clientes
                        gestionar_clientes(db)
                    elif opcion == '4':  # Gestionar sedes
                        gestionar_sedes(db)
                    elif opcion == '5':  # Gestionar transportes
                        gestionar_transportes(db)
                    elif opcion == '6':  # Gestionar paquetes
                        gestionar_paquetes_admin(db)
                    elif opcion == '7':  # Reportes
                        mostrar_reportes_admin(db)
                    elif opcion == '8':  # Configuración del sistema
                        configuracion_sistema(db)
                    elif opcion == '0':  # Cerrar sesión
                        print(f"\nSesión cerrada. ¡Hasta pronto, {usuario_actual['nombre_usuario']}!")
                        usuario_actual = None
                    else:
                        print("\nOpción no válida. Intente de nuevo.")
                        
                elif is_employee(usuario_actual):
                    # Menú de empleado
                    if opcion == '1':  # Registrar envío
                        registrar_envio(db, usuario_actual)
                    elif opcion == '2':  # Buscar cliente
                        buscar_cliente_empleado(db)
                    elif opcion == '3':  # Listar clientes activos
                        listar_clientes_activos_empleado(db)
                    elif opcion == '4':  # Gestionar paquetes
                        gestionar_paquetes_empleado(db, usuario_actual)
                    elif opcion == '5':  # Ver reportes
                        mostrar_reportes(db)
                    elif opcion == '6':  # Mi perfil
                        mostrar_perfil(usuario_actual)
                    elif opcion == '0':  # Cerrar sesión
                        print(f"\nSesión cerrada. ¡Hasta pronto, {usuario_actual['nombre_usuario']}!")
                        usuario_actual = None
                    else:
                        print("\nOpción no válida. Intente de nuevo.")
                        
                else:  # Cliente
                    # Menú de cliente
                    if opcion == '1':  # Solicitar recogida
                        enviar_paquete(db, usuario_actual)
                    elif opcion == '2':  # Rastrear envío
                        seguimiento_paquetes(db, usuario_actual)
                    elif opcion == '3':  # Historial de envíos
                        mis_paquetes(db, usuario_actual)
                    elif opcion == '4':  # Mis datos
                        mostrar_perfil(db, usuario_actual)
                    elif opcion == '0':  # Cerrar sesión
                        print(f"\nSesión cerrada. ¡Hasta pronto, {usuario_actual['nombre_usuario']}!")
                        usuario_actual = None
                    else:
                        print("\nOpción no válida. Intente de nuevo.")
    
    except KeyboardInterrupt:
        print("\n\n¡Hasta pronto!")
    except Exception as e:
        logger.critical(f"Error crítico en la aplicación: {e}", exc_info=True)
        print(f"\nError inesperado: {e}")
    finally:
        db.close()
        logger.info("Sesión de base de datos cerrada")  # Cerrar la sesión de base de datos al salir


if __name__ == "__main__":
    main()
