"""
Módulo para las funciones del menú de gestión de clientes.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from cruds.cliente_crud import cliente as cliente_crud
from cruds.paquete_crud import paquete as paquete_crud
from entities.usuario import Usuario
from entities.cliente import Cliente

def mostrar_encabezado(titulo: str = ""):
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 80)
    if titulo:
        print(f"{titulo:^80}")
        print("=" * 80)

def listar_clientes_activos(db: Session) -> None:
    """Lista todos los clientes activos en el sistema."""
    try:
        clientes = (
            db.query(Cliente, Usuario)
            .join(Usuario, Cliente.usuario_id == Usuario.id_usuario)
            .filter(Cliente.activo == True)
            .order_by(Cliente.primer_apellido, Cliente.primer_nombre)
            .all()
        )
        
        if not clientes:
            print("\nNo hay clientes activos registrados.")
            input("Presione Enter para continuar...")
            return
        
        headers = ["ID", "NOMBRE COMPLETO", "DOCUMENTO", "TELÉFONO", "CORREO", "TIPO"]
        datos = []
        for cliente, usuario in clientes:
            nombre_completo = f"{cliente.primer_nombre} {cliente.segundo_nombre or ''} {cliente.primer_apellido} {cliente.segundo_apellido or ''}".strip()
            datos.append([
                cliente.id_cliente,
                nombre_completo,
                cliente.numero_documento,
                cliente.telefono,
                cliente.correo,
                cliente.tipo.capitalize()
            ])
        
        col_id = 38
        col_nombre = 25
        col_documento = 15
        col_telefono = 15
        col_correo = 30
        col_tipo = 10

        header_line = (f"{headers[0]:<{col_id}} | "
                       f"{headers[1]:<{col_nombre}} | "
                       f"{headers[2]:<{col_documento}} | "
                       f"{headers[3]:<{col_telefono}} | "
                       f"{headers[4]:<{col_correo}} | "
                       f"{headers[5]:<{col_tipo}}")
        print(header_line)
        print("-" * len(header_line))

        for cliente_data in datos:
            row_line = (f"{str(cliente_data[0]):<{col_id}} | "
                        f"{cliente_data[1]:<{col_nombre}} | "
                        f"{cliente_data[2]:<{col_documento}} | "
                        f"{cliente_data[3]:<{col_telefono}} | "
                        f"{cliente_data[4]:<{col_correo}} | "
                        f"{cliente_data[5]:<{col_tipo}}")
            print(row_line)
        
    except Exception as e:
        print(f"\nError al listar clientes: {str(e)}")
    
    input("\nPresione Enter para continuar...")

def buscar_cliente(db: Session) -> None:
    """Busca un cliente por nombre, documento o correo."""
    mostrar_encabezado("BUSCAR CLIENTE")
    criterio = input("Ingrese documento: ").strip()
    if not criterio:
        print("\nDebe ingresar un criterio de búsqueda.")
        input("Presione Enter para continuar...")
        return

    clientes = cliente_crud.obtener_por_documento(db, criterio=criterio)

    if not clientes:
        print("\nNo se encontraron clientes con ese criterio.")
    else:
        print(f"\nResultados de la búsqueda para '{criterio}':")
        headers = ["ID", "NOMBRE COMPLETO", "DOCUMENTO", "TELÉFONO", "CORREO"]
        datos = []
        for cliente in clientes:
            nombre_completo = f"{cliente.primer_nombre} {cliente.segundo_nombre or ''} {cliente.primer_apellido} {cliente.segundo_apellido or ''}".strip()
            datos.append([
                cliente.id_cliente,
                nombre_completo,
                cliente.numero_documento,
                cliente.telefono,
                cliente.correo
            ])
        col_id = 38
        col_nombre = 25
        col_documento = 15
        col_telefono = 15
        col_correo = 30

        header_line = (f"{headers[0]:<{col_id}} | "
                       f"{headers[1]:<{col_nombre}} | "
                       f"{headers[2]:<{col_documento}} | "
                       f"{headers[3]:<{col_telefono}} | "
                       f"{headers[4]:<{col_correo}}")
        print(header_line)
        print("-" * len(header_line))

        for cliente_data in datos:
            row_line = (f"{str(cliente_data[0]):<{col_id}} | "
                        f"{cliente_data[1]:<{col_nombre}} | "
                        f"{cliente_data[2]:<{col_documento}} | "
                        f"{cliente_data[3]:<{col_telefono}} | "
                        f"{cliente_data[4]:<{col_correo}}")
            print(row_line)

    input("\nPresione Enter para continuar...")

def historial_envios_cliente(db: Session) -> None:
    """Muestra el historial de envíos de un cliente específico."""
    mostrar_encabezado("HISTORIAL DE ENVÍOS POR CLIENTE")
    documento = input("Ingrese el número de documento del cliente: ").strip()
    if not documento:
        print("\nDebe ingresar un número de documento.")
        input("Presione Enter para continuar...")
        return

    cliente = cliente_crud.obtener_por_documento(db, numero_documento=documento)
    if not cliente:
        print(f"\nNo se encontró un cliente con el documento '{documento}'.")
        input("Presione Enter para continuar...")
        return

    paquetes = paquete_crud.obtener_por_cliente(db, id_cliente=cliente.id_cliente)

    if not paquetes:
        print(f"\nEl cliente {cliente.primer_nombre} {cliente.primer_apellido} no tiene envíos registrados.")
    else:
        nombre_completo = f"{cliente.primer_nombre} {cliente.primer_apellido}"
        print(f"\nHistorial de envíos para {nombre_completo}:")
        headers = ["ID PAQUETE", "CONTENIDO", "ESTADO", "FECHA ENVÍO", "FECHA ENTREGA"]
        datos = []
        for p in paquetes:
            datos.append([
                p.id_paquete,
                p.contenido,
                p.estado,
                p.fecha_envio.strftime('%Y-%m-%d') if p.fecha_envio else 'N/A',
                p.fecha_entrega.strftime('%Y-%m-%d') if p.fecha_entrega else 'N/A'
            ])
        col_id = 38
        col_contenido = 30
        col_estado = 15
        col_fecha_envio = 15
        col_fecha_entrega = 15

        header_line = (f"{headers[0]:<{col_id}} | "
                       f"{headers[1]:<{col_contenido}} | "
                       f"{headers[2]:<{col_estado}} | "
                       f"{headers[3]:<{col_fecha_envio}} | "
                       f"{headers[4]:<{col_fecha_entrega}}")
        print(header_line)
        print("-" * len(header_line))

        for paquete_data in datos:
            row_line = (f"{str(paquete_data[0]):<{col_id}} | "
                        f"{paquete_data[1]:<{col_contenido}} | "
                        f"{paquete_data[2]:<{col_estado}} | "
                        f"{paquete_data[3]:<{col_fecha_envio}} | "
                        f"{paquete_data[4]:<{col_fecha_entrega}}")
            print(row_line)

    input("\nPresione Enter para continuar...")

def registrar_nuevo_cliente_admin(db: Session) -> None:
    """Función para que el administrador registre un nuevo cliente."""
    from menus.auth_menu import registrar_usuario
    print("\n--- Registro de Nuevo Cliente (Admin) ---")
    registrar_usuario(db)

def gestionar_clientes(db: Session) -> None:
    """Muestra el menú de gestión de clientes."""
    while True:
        mostrar_encabezado("GESTIÓN DE CLIENTES")
        print("1. Registrar nuevo cliente")
        print("2. Listar clientes activos")
        print("3. Buscar cliente")
        print("4. Historial de envíos por cliente")
        print("0. Volver al menú principal")
    
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            registrar_nuevo_cliente_admin(db)
        elif opcion == '2':
            listar_clientes_activos(db)
        elif opcion == '3':
            buscar_cliente(db)
        elif opcion == '4':
            historial_envios_cliente(db)
        elif opcion == '0':
            break
        else:
            print("\nOpción no válida.")
            input("Presione Enter para continuar...")
