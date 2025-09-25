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

    def __init__(self):
        super().__init__(DetalleEntrega)
        self.longitud_minima_descripcion = 5
        self.longitud_maxima_descripcion = 500
        self.peso_minimo = 0.1
        self.peso_maximo = 100.0
        self.valor_minimo = 0.0
        self.valor_maximo = 1000000.0

    def _validar_datos_entrega(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos básicos de un detalle de entrega."""
        descripcion = datos.get("descripcion", "")
        if (
            not descripcion
            or len(descripcion) < self.longitud_minima_descripcion
            or len(descripcion) > self.longitud_maxima_descripcion
        ):
            return False
        peso = datos.get("peso", 0)
        if not (self.peso_minimo <= float(peso) <= self.peso_maximo):
            return False
        valor_declarado = datos.get("valor_declarado", 0)
        if not (self.valor_minimo <= float(valor_declarado) <= self.valor_maximo):
            return False
        fecha_envio = datos.get("fecha_envio")
        if fecha_envio and fecha_envio < datetime.utcnow().date():
            return False
        return True

    def obtener_por_cliente_remitente(
        self,
        db: Session,
        id_cliente_remitente: UUID,
        saltar: int = 0,
        limite: int = 100,
    ) -> Tuple[List[DetalleEntrega], int]:
        """
        Obtiene detalles de entrega por ID de cliente remitente con paginación.
        Args:
            db: Sesión de base de datos
            id_cliente_remitente: ID del cliente remitente
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de detalles de entrega, total de registros)
        """
        if not id_cliente_remitente:
            return [], 0
        consulta = db.query(DetalleEntrega).filter(
            DetalleEntrega.id_cliente_remitente == id_cliente_remitente
        )
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def obtener_por_cliente_receptor(
        self, db: Session, id_cliente_receptor: UUID, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[DetalleEntrega], int]:
        """
        Obtiene detalles de entrega por ID de cliente receptor con paginación.
        Args:
            db: Sesión de base de datos
            id_cliente_receptor: ID del cliente receptor
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de detalles de entrega, total de registros)
        """
        if not id_cliente_receptor:
            return [], 0
        consulta = db.query(DetalleEntrega).filter(
            DetalleEntrega.id_cliente_receptor == id_cliente_receptor
        )
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def crear(
        self, db: Session, *, datos_entrada: DetalleEntregaCreate, creado_por: UUID
    ) -> Optional[DetalleEntrega]:
        """
        Crea un nuevo detalle de entrega con validación de datos.
        Args:
            db: Sesión de base de datos
            datos_entrada: Datos para crear el detalle de entrega
            creado_por: ID del usuario que crea el registro
        Returns:
            El detalle de entrega creado o None si hay un error
        """
        datos = datos_entrada.dict()
        if not self._validar_datos_entrega(datos):
            return None
        try:
            detalle = DetalleEntrega(
                **datos,
                creado_por=creado_por,
                fecha_creacion=datetime.utcnow(),
                activo=True
            )
            db.add(detalle)
            db.commit()
            db.refresh(detalle)
            return detalle
        except Exception:
            db.rollback()
            return None

    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: DetalleEntrega,
        datos_entrada: Union[DetalleEntregaUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> Optional[DetalleEntrega]:
        """
        Actualiza un detalle de entrega existente con validación de datos.
        Args:
            db: Sesión de base de datos
            objeto_db: Objeto de detalle de entrega a actualizar
            datos_entrada: Datos para actualizar
            actualizado_por: ID del usuario que actualiza el registro
        Returns:
            El detalle de entrega actualizado o None si hay un error
        """
        if isinstance(datos_entrada, dict):
            datos_actualizados = datos_entrada
        else:
            datos_actualizados = datos_entrada.dict(exclude_unset=True)
        datos_completos = objeto_db.__dict__.copy()
        datos_completos.update(datos_actualizados)
        if not self._validar_datos_entrega(datos_completos):
            return None
        try:
            for campo, valor in datos_actualizados.items():
                if hasattr(objeto_db, campo):
                    setattr(objeto_db, campo, valor)
            objeto_db.actualizado_por = actualizado_por
            objeto_db.fecha_actualizacion = datetime.utcnow()
            db.add(objeto_db)
            db.commit()
            db.refresh(objeto_db)
            return objeto_db
        except Exception:
            db.rollback()
            return None

    def obtener_por_empleado(
        self, db: Session, id_empleado: UUID, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[DetalleEntrega], int]:
        """
        Obtiene detalles de entrega por ID de empleado con paginación.
        Args:
            db: Sesión de base de datos
            id_empleado: ID del empleado asignado
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de detalles de entrega, total de registros)
        """
        if not id_empleado:
            return [], 0
        consulta = db.query(DetalleEntrega).filter(
            DetalleEntrega.id_empleado == id_empleado
        )
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def obtener_por_estado(
        self, db: Session, estado: str, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[DetalleEntrega], int]:
        """
        Obtiene detalles de entrega por estado con paginación.
        Args:
            db: Sesión de base de datos
            estado: Estado de la entrega a buscar
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de detalles de entrega, total de registros)
        """
        if not estado:
            return [], 0
        consulta = db.query(DetalleEntrega).filter(DetalleEntrega.estado == estado)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def actualizar_estado(
        self,
        db: Session,
        *,
        objeto_db: DetalleEntrega,
        nuevo_estado: str,
        actualizado_por: UUID
    ) -> Optional[DetalleEntrega]:
        """
        Actualiza el estado de un detalle de entrega.
        Args:
            db: Sesión de base de datos
            objeto_db: Objeto de detalle de entrega a actualizar
            nuevo_estado: Nuevo estado de la entrega
            actualizado_por: ID del usuario que actualiza el estado
        Returns:
            El detalle de entrega actualizado o None si hay un error
        """
        try:
            objeto_db.estado = nuevo_estado
            objeto_db.actualizado_por = actualizado_por
            objeto_db.fecha_actualizacion = datetime.utcnow()
            if nuevo_estado == "entregado" and not objeto_db.fecha_entrega:
                objeto_db.fecha_entrega = datetime.utcnow()
            db.add(objeto_db)
            db.commit()
            db.refresh(objeto_db)
            return objeto_db
        except Exception:
            db.rollback()
            return None


detalle_entrega = DetalleEntregaCRUD()


def test_crear_detalle_entrega(db_session):
    datos = DetalleEntregaCreate(
        descripcion="Paquete frágil",
        peso=2.5,
        valor_declarado=1000.0,
        id_cliente_remitente=uuid.uuid4(),
        id_cliente_receptor=uuid.uuid4(),
        id_empleado=uuid.uuid4(),
    )
    resultado = detalle_entrega.crear(
        db=db_session, datos_entrada=datos, creado_por=uuid.uuid4()
    )
    assert resultado is not None
    assert resultado.id is not None
    assert resultado.descripcion == "Paquete frágil"
