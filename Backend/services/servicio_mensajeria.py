"""
Servicio de mensajería para cálculo de distancias y costos de envío.
"""

import math
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TipoEnvio(Enum):
    """Tipos de envío disponibles."""

    NORMAL = "normal"
    EXPRESS = "express"
    PREMIUM = "premium"


class TamañoPaquete(Enum):
    """Tamaños de paquete disponibles."""

    PEQUEÑO = "pequeño"
    MEDIANO = "mediano"
    GRANDE = "grande"
    GIGANTE = "gigante"


@dataclass
class Coordenada:
    """Representa una coordenada tridimensional."""

    latitud: float
    longitud: float
    altitud: float = 0.0

    def __post_init__(self):
        """Valida las coordenadas."""
        if not (-90 <= self.latitud <= 90):
            raise ValueError("La latitud debe estar entre -90 y 90 grados")
        if not (-180 <= self.longitud <= 180):
            raise ValueError("La longitud debe estar entre -180 y 180 grados")


@dataclass
class ParametrosEnvio:
    """Parámetros para calcular el costo de envío."""

    peso_kg: float
    tamaño: TamañoPaquete
    tipo_envio: TipoEnvio
    es_fragil: bool = False
    valor_declarado: float = 0.0


class ServicioMensajeria:
    """Servicio principal para cálculos de mensajería."""

    TARIFA_BASE_KM = {
        TipoEnvio.NORMAL: 150,
        TipoEnvio.EXPRESS: 250,
        TipoEnvio.PREMIUM: 400,
    }

    MULTIPLICADOR_TAMAÑO = {
        TamañoPaquete.PEQUEÑO: 1.0,
        TamañoPaquete.MEDIANO: 1.3,
        TamañoPaquete.GRANDE: 1.7,
        TamañoPaquete.GIGANTE: 2.2,
    }

    COSTO_MINIMO = 5000

    COSTO_BASE_PESO = 2000

    MULTIPLICADOR_FRAGIL = 1.15

    PORCENTAJE_SEGURO = 0.005

    @staticmethod
    def calcular_distancia_haversine(coord1: Coordenada, coord2: Coordenada) -> float:
        """
        Calcula la distancia entre dos coordenadas usando la fórmula de Haversine.

        Args:
            coord1: Coordenada de origen
            coord2: Coordenada de destino

        Returns:
            float: Distancia en kilómetros
        """
        R = 6371.0

        lat1_rad = math.radians(coord1.latitud)
        lon1_rad = math.radians(coord1.longitud)
        lat2_rad = math.radians(coord2.latitud)
        lon2_rad = math.radians(coord2.longitud)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distancia_horizontal = R * c

        diferencia_altitud = abs(coord2.altitud - coord1.altitud) / 1000

        distancia_total = math.sqrt(distancia_horizontal**2 + diferencia_altitud**2)

        return distancia_total

    @classmethod
    def calcular_costo_envio(
        cls,
        coord_origen: Coordenada,
        coord_destino: Coordenada,
        parametros: ParametrosEnvio,
    ) -> Dict[str, Any]:
        """
        Calcula el costo total de un envío.

        Args:
            coord_origen: Coordenada de la sede de origen
            coord_destino: Coordenada de la sede de destino
            parametros: Parámetros del envío

        Returns:
            Dict con el desglose de costos
        """
        distancia_km = cls.calcular_distancia_haversine(coord_origen, coord_destino)

        tarifa_km = cls.TARIFA_BASE_KM[parametros.tipo_envio]
        costo_distancia = distancia_km * tarifa_km

        costo_peso = parametros.peso_kg * cls.COSTO_BASE_PESO

        multiplicador_tamaño = cls.MULTIPLICADOR_TAMAÑO[parametros.tamaño]

        costo_base = (costo_distancia + costo_peso) * multiplicador_tamaño

        if parametros.es_fragil:
            costo_base *= cls.MULTIPLICADOR_FRAGIL

        costo_seguro = parametros.valor_declarado * cls.PORCENTAJE_SEGURO

        costo_total = costo_base + costo_seguro

        costo_final = max(costo_total, cls.COSTO_MINIMO)

        return {
            "distancia_km": round(distancia_km, 2),
            "costo_distancia": round(costo_distancia, 2),
            "costo_peso": round(costo_peso, 2),
            "multiplicador_tamaño": multiplicador_tamaño,
            "costo_base": round(costo_base, 2),
            "costo_seguro": round(costo_seguro, 2),
            "costo_total": round(costo_final, 2),
            "tipo_envio": parametros.tipo_envio.value,
            "tamaño": parametros.tamaño.value,
            "peso_kg": parametros.peso_kg,
            "es_fragil": parametros.es_fragil,
            "valor_declarado": parametros.valor_declarado,
        }

    @classmethod
    def obtener_tiempo_estimado(
        cls, distancia_km: float, tipo_envio: TipoEnvio
    ) -> Dict[str, int]:
        """
        Calcula el tiempo estimado de entrega.

        Args:
            distancia_km: Distancia en kilómetros
            tipo_envio: Tipo de envío

        Returns:
            Dict con tiempo mínimo y máximo en horas
        """
        velocidades = {
            TipoEnvio.NORMAL: 25,
            TipoEnvio.EXPRESS: 40,
            TipoEnvio.PREMIUM: 60,
        }

        velocidad = velocidades[tipo_envio]
        tiempo_base_horas = distancia_km / velocidad

        tiempo_procesamiento = {
            TipoEnvio.NORMAL: 4,
            TipoEnvio.EXPRESS: 2,
            TipoEnvio.PREMIUM: 1,
        }

        tiempo_total = tiempo_base_horas + tiempo_procesamiento[tipo_envio]

        return {
            "tiempo_minimo_horas": math.ceil(tiempo_total * 0.8),
            "tiempo_maximo_horas": math.ceil(tiempo_total * 1.2),
            "tiempo_promedio_horas": math.ceil(tiempo_total),
        }

    @classmethod
    def generar_cotizacion_completa(
        cls,
        coord_origen: Coordenada,
        coord_destino: Coordenada,
        parametros: ParametrosEnvio,
    ) -> Dict[str, Any]:
        """
        Genera una cotización completa con costos y tiempos.

        Args:
            coord_origen: Coordenada de origen
            coord_destino: Coordenada de destino
            parametros: Parámetros del envío

        Returns:
            Dict con cotización completa
        """
        costos = cls.calcular_costo_envio(coord_origen, coord_destino, parametros)

        tiempos = cls.obtener_tiempo_estimado(
            costos["distancia_km"], parametros.tipo_envio
        )

        return {
            **costos,
            **tiempos,
            "fecha_cotizacion": "2025-09-24",
            "valida_hasta_horas": 24,
        }
