from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
from sqlalchemy.orm import Session
from entities.detalle_entrega import (
    DetalleEntrega,
    DetalleEntregaCreate,
    DetalleEntregaUpdate,
)
from .base_crud import CRUDBase


class DetalleEntregaCRUD(
    CRUDBase[DetalleEntrega, DetalleEntregaCreate, DetalleEntregaUpdate]
):
    """Operaciones CRUD para la entidad DetalleEntrega con validaciones."""

    def __init__(self, db: Session):
        super().__init__(DetalleEntrega, db)
        self.longitud_minima_descripcion = 5
        self.longitud_maxima_descripcion = 500
        self.peso_minimo = 0.1
        self.peso_maximo = 100.0
        self.valor_minimo = 0.0
        self.valor_maximo = 1000000.0
        self.db = db

    def obtener_por_id(self, id_detalle: UUID) -> Optional[DetalleEntrega]:
        """Obtiene un detalle de entrega por su ID."""
        if not id_detalle:
            return None
        try:
            return (
                self.db.query(DetalleEntrega)
                .filter(DetalleEntrega.id_detalle == id_detalle)
                .first()
            )
        except Exception as e:
            print(f"Error al obtener detalle de entrega: {e}")
            return None

    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[DetalleEntrega]:
        """Obtiene todos los detalles de entrega con paginación."""
        try:
            return self.db.query(DetalleEntrega).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error al obtener detalles de entrega: {e}")
            return []

    def obtener_por_cliente_remitente(
        self,
        id_cliente_remitente: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DetalleEntrega]:
        """
        Obtiene detalles de entrega por ID de cliente remitente con paginación.
        Args:
            db: Sesión de base de datos
            id_cliente_remitente: ID del cliente remitente
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de detalles de entrega, total de registros)
        """
        if not id_cliente_remitente:
            return []
        consulta = self.db.query(DetalleEntrega).filter(
            DetalleEntrega.id_cliente_remitente == id_cliente_remitente
        )
        resultados = consulta.offset(skip).limit(limit).all()
        return resultados

    def obtener_por_cliente_receptor(
        self, id_cliente_receptor: UUID, skip: int = 0, limit: int = 100
    ) -> List[DetalleEntrega]:
        """
        Obtiene detalles de entrega por ID de cliente receptor con paginación.
        Args:
            id_cliente_receptor: ID del cliente receptor
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de detalles de entrega, total de registros)
        """
        if not id_cliente_receptor:
            return []
        consulta = self.db.query(DetalleEntrega).filter(
            DetalleEntrega.id_cliente_receptor == id_cliente_receptor
        )
        resultados = consulta.offset(skip).limit(limit).all()
        return resultados

    def crear(
        self, *, datos_entrada: DetalleEntregaCreate, creado_por: UUID
    ) -> Optional[DetalleEntrega]:
        """
        Crea un nuevo detalle de entrega.
        Args:
            datos_entrada: Datos para crear el detalle de entrega
            creado_por: ID del usuario que crea el registro
        Returns:
            El detalle de entrega creado o None si hay un error
        """
        try:
            datos = (
                datos_entrada.model_dump()
                if hasattr(datos_entrada, "model_dump")
                else datos_entrada.dict()
            )

            detalle = DetalleEntrega(
                **datos,
                creado_por=creado_por,
                actualizado_por=creado_por,
                fecha_creacion=datetime.now(),
                activo=True,
            )
            self.db.add(detalle)
            self.db.commit()
            self.db.refresh(detalle)
            return detalle
        except Exception as e:
            self.db.rollback()
            print(f"Error al crear detalle de entrega: {e}")
            return None

    def actualizar(
        self,
        *,
        objeto_db: DetalleEntrega,
        datos_entrada: Union[DetalleEntregaUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> Optional[DetalleEntrega]:
        """
        Actualiza un detalle de entrega existente.
        Args:
            objeto_db: Objeto de detalle de entrega a actualizar
            datos_entrada: Datos para actualizar
            actualizado_por: ID del usuario que actualiza el registro
        Returns:
            El detalle de entrega actualizado o None si hay un error
        """
        try:
            if isinstance(datos_entrada, dict):
                datos_actualizados = datos_entrada
            else:
                datos_actualizados = (
                    datos_entrada.model_dump(exclude_unset=True)
                    if hasattr(datos_entrada, "model_dump")
                    else datos_entrada.dict(exclude_unset=True)
                )

            for campo, valor in datos_actualizados.items():
                if hasattr(objeto_db, campo):
                    setattr(objeto_db, campo, valor)

            objeto_db.actualizado_por = actualizado_por
            objeto_db.fecha_actualizacion = datetime.now()

            self.db.add(objeto_db)
            self.db.commit()
            self.db.refresh(objeto_db)
            return objeto_db
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar detalle de entrega: {e}")
            return None

    def obtener_por_paquete(self, id_paquete: UUID) -> Optional[DetalleEntrega]:
        """
        Obtiene el detalle de entrega por ID de paquete.
        Args:
            id_paquete: ID del paquete
        Returns:
            El detalle de entrega asociado o None si no existe
        """
        if not id_paquete:
            return None
        try:
            return (
                self.db.query(DetalleEntrega)
                .filter(DetalleEntrega.id_paquete == id_paquete)
                .first()
            )
        except Exception as e:
            print(f"Error al obtener detalle por paquete: {e}")
            return None

    def obtener_por_estado(
        self, estado: str, skip: int = 0, limit: int = 100
    ) -> List[DetalleEntrega]:
        """
        Obtiene detalles de entrega por estado con paginación.
        Args:
            estado: Estado de la entrega a buscar
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver
        Returns:
            Lista de detalles de entrega
        """
        if not estado:
            return []
        try:
            consulta = self.db.query(DetalleEntrega).filter(
                DetalleEntrega.estado_envio == estado
            )
            return consulta.offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error al obtener por estado: {e}")
            return []

    def actualizar_estado(
        self, *, id_detalle: UUID, nuevo_estado: str, actualizado_por: UUID
    ) -> Optional[DetalleEntrega]:
        """
        Actualiza el estado de un detalle de entrega.
        Args:
            id_detalle: ID del detalle de entrega
            nuevo_estado: Nuevo estado de la entrega
            actualizado_por: ID del usuario que actualiza el estado
        Returns:
            El detalle de entrega actualizado o None si hay un error
        """
        try:
            detalle = self.obtener_por_id(id_detalle)
            if not detalle:
                return None

            detalle.estado_envio = nuevo_estado
            detalle.actualizado_por = actualizado_por
            detalle.fecha_actualizacion = datetime.now()

            if nuevo_estado == "Entregado" and not detalle.fecha_entrega:
                detalle.fecha_entrega = datetime.now()

            self.db.add(detalle)
            self.db.commit()
            self.db.refresh(detalle)
            return detalle
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar estado: {e}")
            return None

    def desactivar(self, *, id_detalle: UUID, actualizado_por: UUID) -> bool:
        """
        Desactiva un detalle de entrega (soft delete).
        Args:
            id_detalle: ID del detalle a desactivar
            actualizado_por: ID del usuario que realiza la desactivación
        Returns:
            True si se desactivó correctamente, False en caso contrario
        """
        try:
            detalle = self.obtener_por_id(id_detalle)
            if not detalle:
                return False

            if not detalle.activo:
                print("Advertencia: El detalle ya está inactivo")
                return False

            detalle.activo = False
            detalle.actualizado_por = actualizado_por
            detalle.fecha_actualizacion = datetime.now()

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error al desactivar detalle: {e}")
            return False
