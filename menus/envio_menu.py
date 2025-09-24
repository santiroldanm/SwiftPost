"""
Módulo para el menú de registro de envíos para empleados.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime, date

from cruds.sede_crud import sede as sede_crud
from cruds.cliente_crud import cliente as cliente_crud
from cruds.paquete_crud import paquete as paquete_crud
from cruds.tipo_documento_crud import tipo_documento as tipo_documento_crud
from services.servicio_mensajeria import (
    ServicioMensajeria, 
    Coordenada, 
    ParametrosEnvio, 
    TipoEnvio, 
    TamañoPaquete
)
from entities.paquete import PaqueteCreate
from entities.cliente import ClienteCreate


def mostrar_encabezado(titulo: str = ""):
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 80)
    if titulo:
        print(f"{titulo:^80}")
        print("=" * 80)


def buscar_o_crear_cliente(db: Session) -> Optional[Any]:
    """
    Permite buscar un cliente existente o crear uno nuevo.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Cliente seleccionado o None si se cancela
    """
    print("\n" + "=" * 60)
    print("SELECCIONAR CLIENTE PARA EL ENVÍO")
    print("=" * 60)
    print("1. Buscar cliente existente")
    print("2. Registrar nuevo cliente")
    print("0. Cancelar")
    
    while True:
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "0":
            return None
        elif opcion == "1":
            return buscar_cliente_existente(db)
        elif opcion == "2":
            return crear_nuevo_cliente(db)
        else:
            print("Opción inválida. Intente nuevamente.")


def buscar_cliente_existente(db: Session) -> Optional[Any]:
    """
    Busca un cliente existente por documento o nombre.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Cliente encontrado o None
    """
    print("\nBUSCAR CLIENTE EXISTENTE")
    print("-" * 30)
    print("1. Buscar por número de documento")
    print("2. Buscar por nombre")
    print("0. Volver")
    
    while True:
        opcion = input("\nSeleccione método de búsqueda: ").strip()
        
        if opcion == "0":
            return None
        elif opcion == "1":
            documento = input("Ingrese número de documento: ").strip()
            if documento:
                cliente = cliente_crud.obtener_por_documento(db, documento)
                if cliente:
                    mostrar_info_cliente(cliente)
                    confirmar = input("\n¿Es este el cliente correcto? (s/n): ").strip().lower()
                    if confirmar in ['s', 'si', 'sí']:
                        return cliente
                    else:
                        continue
                else:
                    print("No se encontró cliente con ese documento.")
                    crear = input("¿Desea crear un nuevo cliente? (s/n): ").strip().lower()
                    if crear in ['s', 'si', 'sí']:
                        return crear_nuevo_cliente(db)
        elif opcion == "2":
            nombre = input("Ingrese nombre del cliente: ").strip()
            if nombre:
                clientes = cliente_crud.buscar_por_nombre(db, nombre)
                if clientes:
                    return seleccionar_de_lista_clientes(clientes)
                else:
                    print("No se encontraron clientes con ese nombre.")
        else:
            print("Opción inválida.")


def seleccionar_de_lista_clientes(clientes: List[Any]) -> Optional[Any]:
    """
    Muestra una lista de clientes para seleccionar.
    
    Args:
        clientes: Lista de clientes encontrados
        
    Returns:
        Cliente seleccionado o None
    """
    print(f"\nSe encontraron {len(clientes)} cliente(s):")
    print("-" * 80)
    print(f"{'#':<3} | {'NOMBRE':<30} | {'DOCUMENTO':<15} | {'TELÉFONO':<15}")
    print("-" * 80)
    
    for i, cliente in enumerate(clientes, 1):
        nombre_completo = f"{cliente.primer_nombre} {cliente.primer_apellido}"
        documento = getattr(cliente, 'numero_documento', 'N/A')
        telefono = getattr(cliente, 'telefono', 'N/A')
        print(f"{i:<3} | {nombre_completo[:28]:<30} | {documento:<15} | {telefono:<15}")
    
    while True:
        try:
            opcion = input(f"\nSeleccione cliente (1-{len(clientes)}) o 0 para cancelar: ").strip()
            if opcion == "0":
                return None
            
            indice = int(opcion) - 1
            if 0 <= indice < len(clientes):
                return clientes[indice]
            else:
                print(f"Opción inválida. Ingrese un número entre 1 y {len(clientes)}")
        except ValueError:
            print("Por favor ingrese un número válido.")


def crear_nuevo_cliente(db: Session) -> Optional[Any]:
    """
    Crea un nuevo cliente para el envío.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Cliente creado o None si se cancela
    """
    print("\nREGISTRAR NUEVO CLIENTE")
    print("-" * 30)
    
    try:
         
        tipos_documento = tipo_documento_crud.obtener_todos(db)
        if not tipos_documento:
            print("Error: No hay tipos de documento configurados.")
            return None
        
        print("Tipos de documento disponibles:")
        for i, tipo in enumerate(tipos_documento, 1):
            print(f"{i}. {tipo.nombre}")
        
        while True:
            try:
                opcion = int(input(f"Seleccione tipo de documento (1-{len(tipos_documento)}): "))
                if 1 <= opcion <= len(tipos_documento):
                    tipo_documento = tipos_documento[opcion - 1]
                    break
                else:
                    print(f"Opción inválida. Ingrese un número entre 1 y {len(tipos_documento)}")
            except ValueError:
                print("Por favor ingrese un número válido.")
        
        numero_documento = input("Número de documento: ").strip()
        primer_nombre = input("Primer nombre: ").strip()
        segundo_nombre = input("Segundo nombre (opcional): ").strip() or None
        primer_apellido = input("Primer apellido: ").strip()
        segundo_apellido = input("Segundo apellido (opcional): ").strip() or None
        telefono = input("Teléfono: ").strip()
        correo = input("Correo electrónico: ").strip()
        direccion = input("Dirección: ").strip()
        
        if not all([numero_documento, primer_nombre, primer_apellido, telefono, correo, direccion]):
            print("Error: Todos los campos obligatorios deben ser completados.")
            return None
        
            cliente_data = ClienteCreate(
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            numero_documento=numero_documento,
            direccion=direccion,
            telefono=telefono,
            correo=correo,
            tipo="remitente",
            id_tipo_documento=str(tipo_documento.id_tipo_documento)
        )
        
        from cruds.usuario_crud import usuario as usuario_crud
        from entities.usuario import UsuarioCreate
        from auth.security import obtener_id_rol
        
        rol_cliente_id = obtener_id_rol(db, "cliente")
        if not rol_cliente_id:
            print("Error: No se encontró el rol de cliente.")
            return None
        
         
        nombre_usuario = f"{primer_nombre.lower()}.{primer_apellido.lower()}.{numero_documento[-4:]}"
        password_temporal = f"temp{numero_documento[-4:]}"
        
        usuario_data = UsuarioCreate(
            nombre_usuario=nombre_usuario,
            password=password_temporal,
            id_rol=str(rol_cliente_id)
        )
        
        usuario = usuario_crud.crear_usuario(db, datos_usuario=usuario_data)
        if not usuario:
            print("Error: No se pudo crear el usuario para el cliente.")
            return None
        
        cliente = cliente_crud.crear(
            db, 
            datos_entrada=cliente_data, 
            usuario_id=usuario.id_usuario
        )
        
        if cliente:
            print(f"\n✅ Cliente creado exitosamente!")
            print(f"Usuario: {nombre_usuario}")
            print(f"Contraseña temporal: {password_temporal}")
            mostrar_info_cliente(cliente)
            return cliente
        else:
            print("Error: No se pudo crear el cliente.")
            return None
            
    except Exception as e:
        print(f"Error al crear cliente: {str(e)}")
        return None


def mostrar_info_cliente(cliente: Any):
    """
    Muestra la información de un cliente.
    
    Args:
        cliente: Objeto cliente
    """
    print(f"\n📋 INFORMACIÓN DEL CLIENTE:")
    nombre_completo = f"{cliente.primer_nombre} {cliente.segundo_nombre or ''} {cliente.primer_apellido} {cliente.segundo_apellido or ''}".strip()
    print(f"   Nombre: {nombre_completo}")
    print(f"   Documento: {getattr(cliente, 'numero_documento', 'N/A')}")
    print(f"   Teléfono: {getattr(cliente, 'telefono', 'N/A')}")
    print(f"   Correo: {getattr(cliente, 'correo', 'N/A')}")
    print(f"   Dirección: {getattr(cliente, 'direccion', 'N/A')}")


def seleccionar_sede_con_coordenadas(db: Session, titulo: str) -> Optional[Any]:
    """
    Permite seleccionar una sede que tenga coordenadas configuradas.
    
    Args:
        db: Sesión de base de datos
        titulo: Título para mostrar
        
    Returns:
        Sede seleccionada o None
    """
    print(f"\n{titulo}")
    print("-" * 50)
    
    sedes = sede_crud.obtener_activas(db)
    if not sedes:
        print("No hay sedes disponibles.")
        return None
    
     
    sedes_con_coordenadas = [
        sede for sede in sedes 
        if hasattr(sede, 'latitud') and sede.latitud is not None
    ]
    
    if not sedes_con_coordenadas:
        print("No hay sedes con coordenadas configuradas.")
        print("Las coordenadas son necesarias para calcular costos de envío.")
        return None
    
    print(f"{'#':<3} | {'NOMBRE':<25} | {'CIUDAD':<15} | {'COORDENADAS':<20}")
    print("-" * 70)
    
    for i, sede in enumerate(sedes_con_coordenadas, 1):
        lat = round(sede.latitud, 4)
        lng = round(sede.longitud, 4) if sede.longitud else 0
        alt = round(sede.altitud, 0) if sede.altitud else 0
        coordenadas = f"{lat},{lng},{alt}m"
        
        print(f"{i:<3} | {sede.nombre[:23]:<25} | {sede.ciudad[:13]:<15} | {coordenadas:<20}")
    
    while True:
        try:
            opcion = input(f"\nSeleccione sede (1-{len(sedes_con_coordenadas)}) o 0 para cancelar: ").strip()
            if opcion == "0":
                return None
            
            indice = int(opcion) - 1
            if 0 <= indice < len(sedes_con_coordenadas):
                return sedes_con_coordenadas[indice]
            else:
                print(f"Opción inválida. Ingrese un número entre 1 y {len(sedes_con_coordenadas)}")
        except ValueError:
            print("Por favor ingrese un número válido.")


def capturar_datos_paquete() -> Optional[Dict[str, Any]]:
    """
    Captura los datos del paquete para el envío.
    
    Returns:
        Diccionario con datos del paquete o None si se cancela
    """
    print("\nDATOS DEL PAQUETE")
    print("-" * 30)
    
    contenido = input("Descripción del contenido: ").strip()
    if not contenido:
        print("La descripción del contenido es obligatoria.")
        return None
    
     
    while True:
        try:
            peso_str = input("Peso del paquete (kg): ").strip()
            if not peso_str:
                print("El peso es obligatorio.")
                continue
            peso = float(peso_str)
            if peso <= 0:
                print("El peso debe ser mayor a 0.")
                continue
            if peso > 50:
                print("El peso máximo permitido es 50 kg.")
                continue
            break
        except ValueError:
            print("Por favor ingrese un número válido.")
    
     
    print("\nTamaños disponibles:")
    tamaños = list(TamañoPaquete)
    for i, tamaño in enumerate(tamaños, 1):
        print(f"{i}. {tamaño.value.title()}")
    
    while True:
        try:
            opcion = int(input(f"Seleccione tamaño (1-{len(tamaños)}): "))
            if 1 <= opcion <= len(tamaños):
                tamaño = tamaños[opcion - 1]
                break
            else:
                print(f"Opción inválida. Ingrese un número entre 1 y {len(tamaños)}")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    print("\nTipos de envío disponibles:")
    tipos = list(TipoEnvio)
    for i, tipo in enumerate(tipos, 1):
        print(f"{i}. {tipo.value.title()}")
    
    while True:
        try:
            opcion = int(input(f"Seleccione tipo de envío (1-{len(tipos)}): "))
            if 1 <= opcion <= len(tipos):
                tipo_envio = tipos[opcion - 1]
                break
            else:
                print(f"Opción inválida. Ingrese un número entre 1 y {len(tipos)}")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
 
    while True:
        fragil_str = input("¿Es un paquete frágil? (s/n): ").strip().lower()
        if fragil_str in ['s', 'si', 'sí']:
            fragilidad = "alta"
            es_fragil = True
            break
        elif fragil_str in ['n', 'no']:
            fragilidad = "normal"
            es_fragil = False
            break
        else:
            print("Por favor responda 's' para sí o 'n' para no.")
    
 
    while True:
        try:
            valor_str = input("Valor declarado para seguro (opcional, presione Enter para omitir): ").strip()
            if not valor_str:
                valor_declarado = 0.0
                break
            valor_declarado = float(valor_str)
            if valor_declarado < 0:
                print("El valor declarado no puede ser negativo.")
                continue
            break
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    return {
        "contenido": contenido,
        "peso": peso,
        "tamaño": tamaño.value,
        "tipo_envio": tipo_envio.value,
        "fragilidad": fragilidad,
        "es_fragil": es_fragil,
        "valor_declarado": valor_declarado,
        "tamaño_enum": tamaño,
        "tipo_envio_enum": tipo_envio
    }


def mostrar_resumen_envio(cliente: Any, sede_origen: Any, sede_destino: Any, 
                         datos_paquete: Dict[str, Any], cotizacion: Dict[str, Any]):
    """
    Muestra el resumen completo del envío antes de confirmar.
    
    Args:
        cliente: Cliente del envío
        sede_origen: Sede de origen
        sede_destino: Sede de destino
        datos_paquete: Datos del paquete
        cotizacion: Cotización calculada
    """
    print("\n" + "=" * 80)
    print("RESUMEN DEL ENVÍO")
    print("=" * 80)
    
 
    nombre_cliente = f"{cliente.primer_nombre} {cliente.primer_apellido}"
    print(f"\n👤 CLIENTE:")
    print(f"   Nombre: {nombre_cliente}")
    print(f"   Documento: {getattr(cliente, 'numero_documento', 'N/A')}")
    print(f"   Teléfono: {getattr(cliente, 'telefono', 'N/A')}")
    
    
    print(f"\n📍 RUTA:")
    print(f"   Origen: {sede_origen.nombre} - {sede_origen.ciudad}")
    print(f"   Destino: {sede_destino.nombre} - {sede_destino.ciudad}")
    print(f"   Distancia: {cotizacion['distancia_km']} km")
    
    
    print(f"\n📦 PAQUETE:")
    print(f"   Contenido: {datos_paquete['contenido']}")
    print(f"   Peso: {datos_paquete['peso']} kg")
    print(f"   Tamaño: {datos_paquete['tamaño'].title()}")
    print(f"   Tipo de envío: {datos_paquete['tipo_envio'].title()}")
    print(f"   Fragilidad: {'Alta' if datos_paquete['es_fragil'] else 'Normal'}")
    if datos_paquete['valor_declarado'] > 0:
        print(f"   Valor declarado: ${datos_paquete['valor_declarado']:,.0f}")
    
    
    print(f"\n💰 COSTOS:")
    print(f"   Costo total: ${cotizacion['costo_total']:,.0f}")
    print(f"   Tiempo estimado: {cotizacion['tiempo_promedio_horas']} horas")
    
    print("=" * 80)


def registrar_envio_completo(db: Session, empleado_data: Dict[str, Any]) -> None:
    """
    Función principal para registrar un envío completo.
    
    Args:
        db: Sesión de base de datos
        empleado_data: Datos del empleado que registra el envío
    """
    mostrar_encabezado("REGISTRAR NUEVO ENVÍO")
    
    try:
        
        print("PASO 1: SELECCIONAR CLIENTE")
        cliente = buscar_o_crear_cliente(db)
        if not cliente:
            print("Operación cancelada.")
            input("\nPresione Enter para continuar...")
            return
        
        
        print("\nPASO 2: SELECCIONAR SEDE DE ORIGEN")
        sede_origen = seleccionar_sede_con_coordenadas(db, "SEDE DE ORIGEN")
        if not sede_origen:
            print("Operación cancelada.")
            input("\nPresione Enter para continuar...")
            return
        
        
        print("\nPASO 3: SELECCIONAR SEDE DE DESTINO")
        sede_destino = seleccionar_sede_con_coordenadas(db, "SEDE DE DESTINO")
        if not sede_destino:
            print("Operación cancelada.")
            input("\nPresione Enter para continuar...")
            return
        
        if sede_origen.id_sede == sede_destino.id_sede:
            print("Error: La sede de origen y destino no pueden ser la misma.")
            input("\nPresione Enter para continuar...")
            return
        
        
        print("\nPASO 4: DATOS DEL PAQUETE")
        datos_paquete = capturar_datos_paquete()
        if not datos_paquete:
            print("Operación cancelada.")
            input("\nPresione Enter para continuar...")
            return
        
        
        print("\nPASO 5: CALCULANDO COSTO DEL ENVÍO...")
        
        coord_origen = Coordenada(
            latitud=sede_origen.latitud,
            longitud=sede_origen.longitud,
            altitud=sede_origen.altitud or 0
        )
        
        coord_destino = Coordenada(
            latitud=sede_destino.latitud,
            longitud=sede_destino.longitud,
            altitud=sede_destino.altitud or 0
        )
        
        parametros = ParametrosEnvio(
            peso_kg=datos_paquete['peso'],
            tamaño=datos_paquete['tamaño_enum'],
            tipo_envio=datos_paquete['tipo_envio_enum'],
            es_fragil=datos_paquete['es_fragil'],
            valor_declarado=datos_paquete['valor_declarado']
        )
        
        cotizacion = ServicioMensajeria.generar_cotizacion_completa(
            coord_origen, coord_destino, parametros
        )
        
        
        print("\nPASO 6: CONFIRMACIÓN")
        mostrar_resumen_envio(cliente, sede_origen, sede_destino, datos_paquete, cotizacion)
        
        confirmar = input("\n¿Confirma el registro de este envío? (s/n): ").strip().lower()
        if confirmar not in ['s', 'si', 'sí']:
            print("Envío cancelado.")
            input("\nPresione Enter para continuar...")
            return
        
        
        print("\nPASO 7: REGISTRANDO ENVÍO...")
        
        paquete_data = PaqueteCreate(
            peso=datos_paquete['peso'],
            tamaño=datos_paquete['tamaño'],
            fragilidad=datos_paquete['fragilidad'],
            contenido=datos_paquete['contenido'],
            tipo=datos_paquete['tipo_envio']
        )
        
        datos_adicionales = {
            "id_paquete": str(uuid4()),
            "id_cliente": str(cliente.id_cliente),
            "costo_envio": cotizacion['costo_total'],
            "sede_origen": str(sede_origen.id_sede),
            "sede_destino": str(sede_destino.id_sede),
            "distancia_km": cotizacion['distancia_km'],
            "tiempo_estimado_horas": cotizacion['tiempo_promedio_horas']
        }
        
        datos_creacion = {
            **paquete_data.dict(),
            **datos_adicionales,
            "creado_por": empleado_data["id_usuario"],
        }
        
        nuevo_paquete = paquete_crud.crear_registro(
            db=db, 
            datos_entrada=datos_creacion, 
            creado_por=empleado_data["id_usuario"]
        )
        
        if nuevo_paquete:
            print(f"\  ¡ENVÍO REGISTRADO EXITOSAMENTE!")
            print(f"  Número de seguimiento: {nuevo_paquete.id_paquete}")
            print(f"  Costo total: ${cotizacion['costo_total']:,.0f}")
            print(f"  Tiempo estimado: {cotizacion['tiempo_promedio_horas']} horas")
            print(f"  Cliente: {cliente.primer_nombre} {cliente.primer_apellido}")
        else:
            print("❌ Error: No se pudo registrar el envío.")
        
    except Exception as e:
        print(f"\n❌ Error al registrar envío: {str(e)}")
    
    input("\nPresione Enter para continuar...")
