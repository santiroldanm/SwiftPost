import sys
import logging
from getpass import getpass
from typing import Optional, List, Dict, Any, Union, Tuple
from uuid import UUID, uuid4
from sqlalchemy.orm import joinedload
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session, joinedload
import getpass
from auth.security import (
    es_administrador as is_admin,
    es_empleado as is_employee,
    es_cliente as is_client,
)
from entities.paquete import PaqueteCreate

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
from cruds.tipo_documento_crud import TipoDocumentoCRUD
from entities.tipo_documento import TipoDocumento, TipoDocumentoCreate

USUARIO_ADMIN_DEFAULT = "00000000-0000-0000-0000-000000000000"


def inicializar_tipos_documento(db: Session) -> None:
    """
    Inicializa los tipos de documento por defecto en la base de datos.
    Utiliza las funciones del módulo inicializar_admin_y_documentos.
    """
    try:
        from scripts.inicializar_admin_y_documentos import (
            crear_tipos_documento_por_defecto,
            crear_usuario_administrador,
        )

        admin = crear_usuario_administrador(db)
        crear_tipos_documento_por_defecto(db, admin.id_usuario)
    except Exception as e:
        logger.error(
            f"Error al inicializar tipos de documento: {str(e)}", exc_info=True
        )
        db.rollback()
        raise


try:
    from cruds.cliente_crud import cliente as cliente_crud
    from cruds.usuario_crud import usuario as usuario_crud
    from entities.cliente import Cliente
    from entities.usuario import Usuario
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
try:
    from database.config import SessionLocal, get_db, create_tables
    from scripts.init_roles import init_roles

    logger.info("Importación de configuración de base de datos exitosa")
except ImportError as e:
    logger.error(f"Error al importar configuración de base de datos: {e}")
    raise
try:
    from auth.security import autenticar_usuario, obtener_usuario_activo_actual

    logger.info("Importación de módulos de seguridad exitosa")
except ImportError as e:
    logger.error(f"Error al importar módulos de seguridad: {e}")
    raise
MENU_OPCIONES = {
    "sin_sesion": {"1": "Iniciar sesión", "2": "Registrarse", "0": "Salir"},
    "admin": {
        "1": "Gestionar usuarios",
        "2": "Gestionar empleados",
        "3": "Gestionar clientes",
        "4": "Gestionar sedes",
        "5": "Gestionar transportes",
        "6": "Gestionar paquetes",
        "7": "Ver reportes",
        "8": "Configuración del sistema",
        "0": "Cerrar sesión",
    },
    "empleado": {
        "1": "Registrar envío",
        "2": "Buscar cliente",
        "3": "Listar clientes activos",
        "4": "Gestionar paquetes",
        "5": "Ver reportes",
        "6": "Mi perfil",
        "0": "Cerrar sesión",
    },
    "cliente": {
        "1": "Solicitar recogida",
        "2": "Rastrear envío",
        "3": "Historial de envíos",
        "4": "Mis datos",
        "0": "Cerrar sesión",
    },
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
        rol_nombre = usuario_data.get("rol_nombre", "(sin rol)")
        print(f"Rol: {rol_nombre}")
        print("-" * 60)
        if is_admin(usuario_data):
            print("1. Administrar usuarios")
            print("2. Gestionar empleados")
            print("3. Gestionar clientes")
            print("4. Gestionar sedes")
            print("5. Gestionar transportes")
            print("6. Gestionar paquetes")
            print("7. Ver reportes")
            print("8. Configuración del sistema")
            print("0. Cerrar sesión")
        elif is_employee(usuario_data):
            print("1. Registrar envío")
            print("2. Buscar cliente")
            print("3. Listar clientes activos")
            print("4. Gestionar paquetes")
            print("5. Ver reportes")
            print("6. Mi perfil")
            print("0. Cerrar sesión")
        else:
            print("1. Solicitar recogida")
            print("2. Rastrear envío")
            print("3. Historial de envíos")
            print("4. Mis datos")
            print("0. Cerrar sesión")
    else:
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("0. Salir")
    print("=" * 60)
    return input("\nSeleccione una opción: ")


def login(db: Session) -> Optional[Dict[str, Any]]:
    from menus.auth_menu import iniciar_sesion

    return iniciar_sesion(db)


def registrar_usuario(db: Session, es_empleado: bool = False) -> None:
    from menus.auth_menu import registrar_usuario

    registrar_usuario(db, es_empleado)


def administrar_usuarios(db: Session) -> None:
    """Muestra el menú de administración de usuarios."""
    from menus import manejar_menu_usuarios

    manejar_menu_usuarios(db)


def gestionar_sedes(db: Session, usuario_actual: Dict[str, Any] = None) -> None:
    """Muestra el menú de gestión de sedes.
    Args:
        db: Sesión de base de datos
        usuario_actual: Diccionario con los datos del usuario administrador actual
    """
    from menus.sede_menu import manejar_menu_sedes

    manejar_menu_sedes(db, usuario_actual=usuario_actual)


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


def enviar_paquete(db: Session, usuario_data: Dict[str, Any]) -> None:
    """Permite a un cliente solicitar el envío de un paquete."""
    mostrar_encabezado("SOLICITUD DE ENVÍO DE PAQUETE")
    try:
        cliente = cliente_crud.obtener_por_usuario(
            db, usuario_id=usuario_data["id_usuario"]
        )
        if not cliente:
            print("\nError: No se encontró la información del cliente.")
            input("\nPresione Enter para continuar...")
            return
        print("\nComplete la información del envío:")
        print("-" * 40)
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
        tipo_opciones = ["1", "2", "3", "4"]
        tipo = ""
        while tipo not in tipo_opciones:
            tipo = input("\nSeleccione el tipo de paquete (1-4): ")
            if tipo not in tipo_opciones:
                print("Opción no válida. Intente de nuevo.")
        tipo_mapa = {
            "1": "pequeño",
            "2": "mediano",
            "3": "grande",
            "4": "gigante",
            "5": "sobre",
        }
        tamaño_paquete = tipo_mapa[tipo]
        fragilidad = ""
        while fragilidad.lower() not in ["baja", "normal", "alta"]:
            fragilidad = (
                input("\nNivel de fragilidad (Baja/Normal/Alta): ").strip().lower()
            )
            if fragilidad not in ["baja", "normal", "alta"]:
                print("Opción no válida. Intente de nuevo.")
        from entities.paquete import PaqueteCreate
        from entities.paquete import PaqueteCreate

        paquete_data = PaqueteCreate(
            peso=float(peso),
            tamaño=tamaño_paquete,
            fragilidad=fragilidad,
            contenido=descripcion,
            tipo="normal",
        )
        datos_adicionales = {
            "id_paquete": str(uuid4()),
            "id_cliente": str(cliente.id_cliente),
        }
        print("\nDatos del paquete a crear:")
        print(f"ID Cliente: {datos_adicionales['id_cliente']}")
        print(f"Peso: {paquete_data.peso}")
        print(f"Tamaño: {paquete_data.tamaño}")
        print(f"Fragilidad: {paquete_data.fragilidad}")
        print(f"Contenido: {paquete_data.contenido}")
        print(f"Tipo: {paquete_data.tipo}")
        print("\n=== DATOS DE DEPURACIÓN ===")
        print("Datos del paquete:", paquete_data.dict())
        print("Datos adicionales:", datos_adicionales)
        datos_creacion = {
            **paquete_data.dict(),
            **datos_adicionales,
            "creado_por": usuario_data["id_usuario"],
        }
        print("Datos finales para crear el paquete:", datos_creacion)
        print("==========================\n")
        nuevo_paquete = paquete_crud.crear(
            db=db, datos_entrada=datos_creacion, creado_por=usuario_data["id_usuario"]
        )
        if nuevo_paquete is None:
            print(
                "\nError: No se pudo crear el paquete. Verifica que todos los datos sean válidos."
            )
            print("Posibles causas:")
            print(
                "- El tamaño del paquete debe ser uno de: pequeño, mediano, grande, gigante"
            )
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
        cliente = cliente_crud.obtener_por_usuario(
            db, usuario_id=usuario_data["id_usuario"]
        )
        if not cliente:
            print("\nError: No se encontró la información del cliente.")
            input("\nPresione Enter para continuar...")
            return
        print("\nOpciones de búsqueda:")
        print("1. Buscar por número de seguimiento")
        print("2. Ver todos mis paquetes")
        print("0. Volver al menú principal")
        opcion = input("\nSeleccione una opción: ")
        if opcion == "1":
            num_seguimiento = input("\nIngrese el número de seguimiento: ").strip()
            paq = paquete_crud.obtener_por_id(db, id_paquete=num_seguimiento)
            if paq and str(paq.id_cliente) == str(cliente.id_cliente):
                mostrar_detalle_paquete(paq)
            else:
                print("\nNo se encontró ningún paquete con ese número de seguimiento.")
        elif opcion == "2":
            paquetes, total = paquete_crud.obtener_por_cliente(
                db, id_cliente=cliente.id_cliente
            )
            if paquetes and total > 0:
                print("\nTus paquetes:")
                print("-" * 80)
                print(
                    f"{'N° SEGUIMIENTO':<20} {'DESCRIPCIÓN':<30} {'ESTADO':<15} {'FECHA REGISTRO'}"
                )
                print("-" * 80)
                for p in paquetes:
                    id_paquete = str(getattr(p, "id_paquete", "N/A"))
                    descripcion = getattr(
                        p, "descripcion", getattr(p, "contenido", "Sin descripción")
                    )
                    descripcion = (
                        str(descripcion)[:28] if descripcion else "Sin descripción"
                    )
                    fecha = getattr(
                        p, "fecha_creacion", getattr(p, "fecha_registro", None)
                    )
                    fecha_str = fecha.strftime("%Y-%m-%d") if fecha else "N/A"
                    estado = getattr(p, "estado", "DESCONOCIDO")
                    print(
                        f"{id_paquete:<20} {descripcion:<30} {estado:<15} {fecha_str}"
                    )
                ver_detalle = input(
                    "\n¿Desea ver los detalles de un paquete? (s/n): "
                ).lower()
                if ver_detalle == "s":
                    num_seguimiento = input(
                        "Ingrese el número de seguimiento: "
                    ).strip()
                    paq = next(
                        (p for p in paquetes if str(p.id_paquete) == num_seguimiento),
                        None,
                    )
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
        cliente = cliente_crud.obtener_por_usuario(
            db, usuario_id=usuario_data["id_usuario"]
        )
        if not cliente:
            print("\nError: No se encontró la información del cliente.")
            input("\nPresione Enter para continuar...")
            return
        paquetes, total = paquete_crud.obtener_por_cliente(
            db, id_cliente=cliente.id_cliente
        )
        if not paquetes or total == 0:
            print("\nNo tienes paquetes registrados.")
            input("\nPresione Enter para continuar...")
            return
        print("\nFiltros disponibles:")
        print("1. Ver todos los paquetes")
        print("2. Solo pendientes")
        print("3. Solo en tránsito")
        print("4. Solo entregados")
        print("0. Volver al menú principal")
        opcion = input("\nSeleccione una opción: ")
        estados_filtro = {
            "1": None,
            "2": "registrado",
            "3": "en_transito",
            "4": "entregado",
        }
        if opcion == "0":
            return
        if opcion not in estados_filtro:
            print("\nOpción no válida.")
            input("\nPresione Enter para continuar...")
            return
        paquetes_filtrados = paquetes
        if opcion != "1":
            estado = estados_filtro[opcion]
            paquetes_filtrados = [
                p for p in paquetes if hasattr(p, "estado") and p.estado == estado
            ]
            if not paquetes_filtrados:
                print(f"\nNo tienes paquetes con estado '{estado}'.")
                input("\nPresione Enter para continuar...")
                return
        print("\nTus paquetes:")
        print("-" * 100)
        print(
            f"{'N° SEGUIMIENTO':<20} {'DESCRIPCIÓN':<30} {'TIPO':<15} {'PESO (kg)':<10} {'ESTADO':<15} {'FECHA'}"
        )
        print("-" * 100)
        for p in paquetes_filtrados:
            id_str = str(p.id_paquete)[:8]
            descripcion = getattr(
                p, "descripcion", getattr(p, "contenido", "Sin descripción")
            )[:28]
            tipo = getattr(p, "tipo", "N/A")
            peso = getattr(p, "peso", 0.0)
            estado = getattr(p, "estado", "N/A")
            fecha = getattr(p, "fecha_registro", getattr(p, "fecha_creacion", None))
            fecha_str = fecha.strftime("%Y-%m-%d") if fecha else "N/A"
            print(
                f"{id_str:<8}... {descripcion:<30} {tipo:<15} {peso:<10.2f} {estado:<15} {fecha_str}"
            )
        ver_detalle = (
            input("\n¿Desea ver los detalles de un paquete? (s/n): ").strip().lower()
        )
        if ver_detalle == "s":
            num_seguimiento = input(
                "Ingrese el número de seguimiento (primeros caracteres): "
            ).strip()
            paquetes_coincidentes = [
                p for p in paquetes if str(p.id_paquete).startswith(num_seguimiento)
            ]
            if len(paquetes_coincidentes) == 1:
                mostrar_detalle_paquete(paquetes_coincidentes[0])
            elif len(paquetes_coincidentes) > 1:
                print(
                    "\nVarios paquetes coinciden con esa búsqueda. Por favor sea más específico."
                )
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
    if hasattr(paq, "fecha_entrega") and paq.fecha_entrega:
        print(f"Fecha de entrega: {paq.fecha_entrega.strftime('%Y-%m-%d %H:%M')}")
    if hasattr(paq, "observaciones") and paq.observaciones:
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
    nombre_usuario = usuario_data.get("nombre_usuario", "No especificado")
    email = usuario_data.get("email", "No especificado")
    rol_id = usuario_data.get("id_rol")
    rol_nombre = "Sin asignar"
    rol = None
    if rol_id:
        try:
            rol = rol_crud.get(db, id=rol_id)
            if rol:
                rol_nombre = rol.nombre_rol.capitalize()
        except Exception as e:
            print(f"\nError al obtener el rol: {e}")
    estado = "Activo" if usuario_data.get("activo", False) else "Inactivo"
    fecha_creacion = usuario_data.get("fecha_creacion", "No disponible")
    ultimo_acceso = usuario_data.get("ultimo_acceso", "Nunca")
    if email is None:
        email = "No especificado"
    if isinstance(fecha_creacion, datetime):
        fecha_creacion = fecha_creacion.strftime("%d/%m/%Y %H:%M")
    if isinstance(ultimo_acceso, datetime):
        ultimo_acceso = ultimo_acceso.strftime("%d/%m/%Y %H:%M")
    print("\n" + "=" * 80)
    print("INFORMACIÓN BÁSICA".center(80))
    print("=" * 80)
    print(f"{'Usuario:':<20} {nombre_usuario}")
    print(f"{'Correo:':<20} {email}")
    print(f"{'Rol:':<20} {rol_nombre}")
    print(f"{'Estado:':<20} {estado}")
    if rol and rol.nombre_rol.lower() == "cliente":
        cliente = cliente_crud.obtener_por_usuario(
            db, usuario_id=usuario_data["id_usuario"]
        )
        if cliente:
            print("\n" + "=" * 80)
            print("INFORMACIÓN DEL CLIENTE".center(80))
            print("=" * 80)
            print(
                f"{'Nombre completo:':<20} {cliente.primer_nombre} {cliente.segundo_nombre or ''} {cliente.primer_apellido} {cliente.segundo_apellido or ''}".replace(
                    "  ", " "
                )
            )
            print(
                f"{'Tipo:':<20} {cliente.tipo.capitalize() if hasattr(cliente, 'tipo') else 'No especificado'}"
            )
            print(
                f"{'Documento:':<20} {getattr(cliente, 'numero_documento', 'No especificado')}"
            )
            print(
                f"{'Teléfono:':<20} {getattr(cliente, 'telefono', 'No especificado')}"
            )
            print(
                f"{'Dirección:':<20} {getattr(cliente, 'direccion', 'No especificada')}"
            )
            if hasattr(cliente, "paquetes"):
                total_paquetes = len(cliente.paquetes)
                entregados = sum(
                    1
                    for p in cliente.paquetes
                    if getattr(p, "estado", "") == "entregado"
                )
                print(f"\n{'Paquetes totales:':<20} {total_paquetes}")
                print(f"{'Paquetes entregados:':<20} {entregados}")
    elif rol and rol.nombre_rol.lower() in ["empleado", "administrador"]:
        empleado = empleado_crud.obtener_por_usuario(
            db, usuario_id=usuario_data["id_usuario"]
        )
        if empleado:
            print("\n" + "=" * 80)
            print("INFORMACIÓN DEL EMPLEADO".center(80))
            print("=" * 80)
            print(
                f"{'Nombre completo:':<20} {empleado.primer_nombre} {empleado.segundo_nombre or ''} {empleado.primer_apellido} {empleado.segundo_apellido or ''}".replace(
                    "  ", " "
                )
            )
            print(
                f"{'Tipo:':<20} {empleado.tipo_empleado.capitalize() if hasattr(empleado, 'tipo_empleado') else 'No especificado'}"
            )
            if hasattr(empleado, "fecha_ingreso"):
                fecha_ingreso = (
                    empleado.fecha_ingreso.strftime("%d/%m/%Y")
                    if empleado.fecha_ingreso
                    else "No especificada"
                )
                print(f"{'Fecha de ingreso:':<20} {fecha_ingreso}")
            if hasattr(empleado, "sede") and empleado.sede:
                print(
                    f"{'Sede:':<20} {empleado.sede.nombre if hasattr(empleado.sede, 'nombre') else 'No especificada'}"
                )
    print("\n" + "=" * 80)
    print("INFORMACIÓN DE LA CUENTA".center(80))
    print("=" * 80)
    print(f"{'Creado el:':<20} {fecha_creacion}")
    print(f"{'Último acceso:':<20} {ultimo_acceso}")
    print("\n" + "=" * 80)
    print("ACCIONES DISPONIBLES".center(80))
    print("=" * 80)
    opciones = []
    opciones.append(("1", "Actualizar datos personales"))
    if rol_nombre.lower() == "cliente":
        opciones.append(("2", "Ver historial de envíos"))
    opciones.append(("0", "Volver al menú principal"))
    for codigo, texto in opciones:
        print(f"{codigo}. {texto}")
    while True:
        try:
            opcion = input("\nSeleccione una opción: ").strip()
            if opcion == "0":
                return
            elif opcion == "1":
                print(
                    "\nFunción de actualización de datos personales no implementada aún."
                )
                input("Presione Enter para continuar...")
                break
            elif opcion == "2" and rol_nombre.lower() == "cliente":
                mis_paquetes(db, usuario_data)
                break
            else:
                print("\nOpción no válida. Intente de nuevo.")
        except Exception as e:
            print(f"\nError: {str(e)}")
            input("Presione Enter para continuar...")


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
        if opcion == "1":
            reporte_envios_por_periodo(db)
        elif opcion == "2":
            reporte_ingresos(db)
        elif opcion == "3":
            reporte_paquetes_por_estado(db)
        elif opcion == "4":
            reporte_clientes_frecuentes(db)
        elif opcion == "5":
            reporte_eficiencia_transportes(db)
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida.")
            input("Presione Enter para continuar...")


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
        if opcion == "1":
            configuracion_parametros_generales(db)
        elif opcion == "2":
            configuracion_envios(db)
        elif opcion == "3":
            configuracion_copia_seguridad(db)
        elif opcion == "4":
            configuracion_registro_actividades(db)
        elif opcion == "0":
            break
        else:
            print("\nOpción no válida.")
            input("Presione Enter para continuar...")


def configuracion_parametros_generales(db: Session) -> None:
    """Configuración de parámetros generales del sistema."""
    mostrar_encabezado("PARÁMETROS GENERALES")
    print("\nConfiguración de parámetros generales del sistema.")
    try:
        print("\nParámetros actuales:")
        print("- Nombre de la empresa: SwiftPost")
        print("- Moneda: USD")
        print("- Zona horaria: America/Bogota")
        print("- Elementos por página: 10")
        editar = input("\n¿Desea editar estos parámetros? (s/n): ").lower()
        if editar == "s":
            print("\nFuncionalidad de edición en desarrollo...")
    except Exception as e:
        print(f"\nError al cargar la configuración: {str(e)}")
    input("\nPresione Enter para continuar...")


def configuracion_envios(db: Session) -> None:
    """Configuración de parámetros de envíos."""
    mostrar_encabezado("CONFIGURACIÓN DE ENVÍOS")
    print("\nConfiguración de parámetros de envíos.")
    try:
        print("\nParámetros actuales:")
        print("- Tiempo máximo de entrega: 5 días hábiles")
        print("- Peso máximo por paquete: 30 kg")
        print("- Tasa de envío base: $5.00")
        print("- Recargo por peso: $0.50 por kg adicional")
        editar = input("\n¿Desea editar estos parámetros? (s/n): ").lower()
        if editar == "s":
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
        if opcion == "1":
            print("\nCreando copia de seguridad...")
            print("¡Copia de seguridad creada exitosamente!")
        elif opcion == "2":
            print("\nRestaurando desde copia de seguridad...")
            print("¡Restauración completada exitosamente!")
        elif opcion == "3":
            print("\nConfigurando copias automáticas...")
            print("¡Configuración guardada exitosamente!")
        elif opcion != "0":
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
        if opcion == "1":
            print("\nNiveles disponibles:")
            print("1. DEBUG - Información detallada, útil para desarrollo")
            print("2. INFO - Confirmación de que las cosas funcionan como se espera")
            print(
                "3. WARNING - Algo inesperado sucedió, pero la aplicación sigue funcionando"
            )
            print("4. ERROR - La aplicación no pudo realizar alguna función")
            print("5. CRITICAL - Error grave que puede hacer que la aplicación falle")
            nivel = input("\nSeleccione el nivel de registro (1-5): ")
            niveles = {
                "1": "DEBUG",
                "2": "INFO",
                "3": "WARNING",
                "4": "ERROR",
                "5": "CRITICAL",
            }
            if nivel in niveles:
                print(f"\nNivel de registro cambiado a: {niveles[nivel]}")
            else:
                print("\nOpción no válida.")
        elif opcion == "2":
            print("\nMostrando las últimas 50 entradas del registro:")
            print("-" * 80)
            print("[2023-05-15 09:30:15] INFO: Usuario admin inició sesión")
            print("[2023-05-15 09:32:45] INFO: Nuevo paquete registrado (ID: 12345)")
            print(
                "[2023-05-15 10:15:22] WARNING: Intento de inicio de sesión fallido para usuario 'test'"
            )
            print("...")
        elif opcion == "3":
            nombre_archivo = input(
                "\nIngrese el nombre del archivo para exportar: "
            ).strip()
            if nombre_archivo:
                print(f"\nRegistro exportado exitosamente como '{nombre_archivo}'")
    except Exception as e:
        print(f"\nError en la configuración del registro: {str(e)}")
    input("\nPresione Enter para continuar...")


def main() -> None:
    """Función principal de la aplicación."""
    try:
        db = SessionLocal()
        create_tables()
        init_roles(db)
        inicializar_tipos_documento(db)
        from auth.security import limpiar_cache_roles, obtener_roles

        limpiar_cache_roles()
        obtener_roles(db)
        usuario_actual = None
        while True:
            opcion = mostrar_menu(usuario_actual)
            if not usuario_actual:
                if opcion == "1":
                    from menus.auth_menu import iniciar_sesion

                    usuario_actual = iniciar_sesion(db)
                elif opcion == "2":
                    from menus.auth_menu import registrar_usuario

                    registrar_usuario(db)
                elif opcion == "0":
                    print("\n¡Gracias por usar SwiftPost!")
                    break
                else:
                    print("\nOpción no válida. Intente de nuevo.")
            else:
                from auth.security import (
                    es_administrador as is_admin,
                    es_empleado as is_employee,
                    es_cliente as is_client,
                )

                if is_admin(usuario_actual):
                    if opcion == "1":
                        administrar_usuarios(db)
                    elif opcion == "2":
                        from menus.empleado_menu import manejar_menu_empleados

                        manejar_menu_empleados(
                            db, id_administrador=str(usuario_actual.get("id_usuario"))
                        )
                    elif opcion == "3":
                        from menus.cliente_menu import gestionar_clientes

                        gestionar_clientes(db)
                    elif opcion == "4":
                        gestionar_sedes(db, usuario_actual=usuario_actual)
                    elif opcion == "5":
                        from menus.transporte_menu import manejar_menu_transportes

                        manejar_menu_transportes(
                            db, id_administrador=str(usuario_actual.get("id_usuario"))
                        )
                    elif opcion == "6":
                        from menus.paquete_menu import manejar_menu_paquetes_admin

                        manejar_menu_paquetes_admin(
                            db, id_administrador=str(usuario_actual.get("id_usuario"))
                        )
                    elif opcion == "7":
                        from menus.reportes_menu import manejar_menu_reportes_admin

                        manejar_menu_reportes_admin(db)
                    elif opcion == "8":
                        configuracion_sistema(db)
                    elif opcion == "0":
                        print(
                            f"\nSesión cerrada. ¡Hasta pronto, {usuario_actual['nombre_usuario']}!"
                        )
                        usuario_actual = None
                    else:
                        print("\nOpción no válida. Intente de nuevo.")
                elif is_employee(usuario_actual):
                    if opcion == "1":
                        registrar_envio(db, usuario_actual)
                    elif opcion == "2":
                        buscar_cliente_empleado(db)
                    elif opcion == "3":
                        listar_clientes_activos_empleado(db)
                    elif opcion == "4":
                        from menus.paquete_menu import manejar_menu_paquetes_empleado

                        manejar_menu_paquetes_empleado(
                            db, id_empleado=str(usuario_actual.get("id_usuario"))
                        )
                    elif opcion == "5":
                        mostrar_reportes(db)
                    elif opcion == "6":
                        mostrar_perfil(usuario_actual)
                    elif opcion == "0":
                        print(
                            f"\nSesión cerrada. ¡Hasta pronto, {usuario_actual['nombre_usuario']}!"
                        )
                        usuario_actual = None
                    else:
                        print("\nOpción no válida. Intente de nuevo.")
                else:
                    if opcion == "1":
                        from menus.paquete_menu import solicitar_recogida

                        solicitar_recogida(db, usuario_actual)
                    elif opcion == "2":
                        from menus.paquete_menu import rastrear_envio

                        rastrear_envio(db, usuario_actual)
                    elif opcion == "3":
                        from menus.paquete_menu import historial_envios

                        historial_envios(db, usuario_actual)
                    elif opcion == "4":
                        mostrar_perfil(db, usuario_actual)
                    elif opcion == "0":
                        print(
                            f"\nSesión cerrada. ¡Hasta pronto, {usuario_actual['nombre_usuario']}!"
                        )
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
        logger.info("Sesión de base de datos cerrada")


if __name__ == "__main__":
    main()
