"""
Módulo para el menú de cotización de envíos para empleados.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from cruds.sede_crud import sede as sede_crud
from services.servicio_mensajeria import (
    ServicioMensajeria, 
    Coordenada, 
    ParametrosEnvio, 
    TipoEnvio, 
    TamañoPaquete
)


def mostrar_encabezado(titulo: str = ""):
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 80)
    if titulo:
        print(f"{titulo:^80}")
        print("=" * 80)


def seleccionar_sede(db: Session, titulo: str) -> Optional[Any]:
    """
    Permite al usuario seleccionar una sede de la lista.
    
    Args:
        db: Sesión de base de datos
        titulo: Título para mostrar
        
    Returns:
        Sede seleccionada o None si se cancela
    """
    print(f"\n{titulo}")
    print("-" * 50)
    
    sedes = sede_crud.obtener_activas(db)
    if not sedes:
        print("No hay sedes disponibles.")
        return None
    
        """ Filtrar sedes con coordenadas """
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


def capturar_parametros_envio() -> Optional[ParametrosEnvio]:
    """
    Captura los parámetros del envío del usuario.
    
    Returns:
        ParametrosEnvio o None si se cancela
    """
    print("\nPARÁMETROS DEL ENVÍO")
    print("-" * 30)
    
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
            es_fragil = True
            break
        elif fragil_str in ['n', 'no']:
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
    
    return ParametrosEnvio(
        peso_kg=peso,
        tamaño=tamaño,
        tipo_envio=tipo_envio,
        es_fragil=es_fragil,
        valor_declarado=valor_declarado
    )


def mostrar_cotizacion(cotizacion: Dict[str, Any], sede_origen: Any, sede_destino: Any):
    """
    Muestra la cotización de forma formateada.
    
    Args:
        cotizacion: Diccionario con la cotización
        sede_origen: Sede de origen
        sede_destino: Sede de destino
    """
    print("\n" + "=" * 80)
    print("COTIZACIÓN DE ENVÍO".center(80))
    print("=" * 80)
    
    print(f"\n📍 ORIGEN: {sede_origen.nombre} - {sede_origen.ciudad}")
    print(f"📍 DESTINO: {sede_destino.nombre} - {sede_destino.ciudad}")
    
    print(f"\n DETALLES DEL PAQUETE:")
    print(f"   Peso: {cotizacion['peso_kg']} kg")
    print(f"   Tamaño: {cotizacion['tamaño'].title()}")
    print(f"   Tipo de envío: {cotizacion['tipo_envio'].title()}")
    print(f"   Frágil: {'Sí' if cotizacion['es_fragil'] else 'No'}")
    if cotizacion['valor_declarado'] > 0:
        print(f"   Valor declarado: ${cotizacion['valor_declarado']:,.0f}")
    
    print(f"\n DISTANCIA: {cotizacion['distancia_km']} km")
    
    print(f"\n DESGLOSE DE COSTOS:")
    print(f"   Costo por distancia: ${cotizacion['costo_distancia']:,.0f}")
    print(f"   Costo por peso: ${cotizacion['costo_peso']:,.0f}")
    print(f"   Multiplicador tamaño: x{cotizacion['multiplicador_tamaño']}")
    if cotizacion['es_fragil']:
        print(f"   Recargo por fragilidad: +15%")
    if cotizacion['costo_seguro'] > 0:
        print(f"   Seguro: ${cotizacion['costo_seguro']:,.0f}")
    
    print(f"\n COSTO TOTAL: ${cotizacion['costo_total']:,.0f}")
    
    print(f"\n TIEMPO ESTIMADO:")
    print(f"   Mínimo: {cotizacion['tiempo_minimo_horas']} horas")
    print(f"   Máximo: {cotizacion['tiempo_maximo_horas']} horas")
    print(f"   Promedio: {cotizacion['tiempo_promedio_horas']} horas")
    
    print(f"\n Cotización válida por {cotizacion['valida_hasta_horas']} horas")
    print("=" * 80)


def cotizar_envio(db: Session) -> None:
    """
    Función principal para cotizar un envío.
    
    Args:
        db: Sesión de base de datos
    """
    mostrar_encabezado("COTIZACIÓN DE ENVÍO")
    
    try:
        sede_origen = seleccionar_sede(db, "SELECCIONAR SEDE DE ORIGEN")
        if not sede_origen:
            print("Operación cancelada.")
            input("\nPresione Enter para continuar...")
            return
        
        sede_destino = seleccionar_sede(db, "SELECCIONAR SEDE DE DESTINO")
        if not sede_destino:
            print("Operación cancelada.")
            input("\nPresione Enter para continuar...")
            return
        
        if sede_origen.id_sede == sede_destino.id_sede:
            print("Error: La sede de origen y destino no pueden ser la misma.")
            input("\nPresione Enter para continuar...")
            return
        
        parametros = capturar_parametros_envio()
        if not parametros:
            print("Operación cancelada.")
            input("\nPresione Enter para continuar...")
            return
        
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
        
        cotizacion = ServicioMensajeria.generar_cotizacion_completa(
            coord_origen, coord_destino, parametros
        )
        
        mostrar_cotizacion(cotizacion, sede_origen, sede_destino)
        
        generar = input("\n¿Desea generar el detalle de entrega? (s/n): ").strip().lower()
        if generar in ['s', 'si', 'sí']:
            print("\n🚧 Funcionalidad de detalle de entrega en desarrollo...")
            print("Por ahora puede usar esta cotización para registrar el envío manualmente.")
        
    except Exception as e:
        print(f"\nError al generar cotización: {str(e)}")
    
    input("\nPresione Enter para continuar...")


def menu_cotizacion(db: Session) -> None:
    """
    Menú principal de cotización para empleados.
    
    Args:
        db: Sesión de base de datos
    """
    while True:
        mostrar_encabezado("SERVICIO DE COTIZACIÓN")
        print("1. Cotizar envío")
        print("2. Ver tarifas")
        print("0. Volver al menú anterior")
        print("=" * 80)
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            cotizar_envio(db)
        elif opcion == "2":
            mostrar_tarifas()
        elif opcion == "0":
            break
        else:
            print("Opción inválida. Intente nuevamente.")
            input("\nPresione Enter para continuar...")


def mostrar_tarifas():
    """Muestra las tarifas del servicio."""
    mostrar_encabezado("TARIFAS DEL SERVICIO")
    
    print(" TARIFAS BASE POR KILÓMETRO:")
    print(f"   Normal: $150 COP/km")
    print(f"   Express: $250 COP/km") 
    print(f"   Premium: $400 COP/km")
    
    print("\n MULTIPLICADORES POR TAMAÑO:")
    print(f"   Pequeño: x1.0")
    print(f"   MFediano: x1.3")
    print(f"   Grande: x1.7")
    print(f"   Gigante: x2.2")
    
    print("\n RECARGOS ADICIONALES:")
    print(f"   Paquete frágil: +15%")
    print(f"   Seguro por valor declarado: 0.5% del valor")
    
    print("\n OTROS COSTOS:")
    print(f"   Costo base por peso: $2,000 COP/kg")
    print(f"   Costo mínimo por envío: $5,000 COP")
    
    print("\n VELOCIDADES PROMEDIO:")
    print(f"   Normal: 25 km/h + 4h procesamiento")
    print(f"   Express: 40 km/h + 2h procesamiento")
    print(f"   Premium: 60 km/h + 1h procesamiento")
    
    input("\nPresione Enter para continuar...")
