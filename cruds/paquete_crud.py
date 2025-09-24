from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
from sqlalchemy.orm import Session
from entities.paquete import Paquete, PaqueteCreate, PaqueteUpdate
from .base_crud import CRUDBase


class PaqueteCRUD(CRUDBase[Paquete, PaqueteCreate, PaqueteUpdate]):
    """Operaciones CRUD para la entidad Paquete con validaciones."""

    def __init__(self):
        super().__init__(Paquete)
        self.estados_permitidos = [
            "registrado",
            "en_transito",
            "en_reparto",
            "entregado",
            "no_entregado",
            "devuelto",
        ]
        self.tipos_permitidos = ["normal", "express"]
        self.tamanos_permitidos = ["pequeño", "mediano", "grande", "gigante"]
        self.peso_minimo = 0.1
        self.peso_maximo = 50.0
        self.valor_minimo = 0.0
        self.valor_maximo = 1000000.0

    def obtener_todos(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        activos: bool = True,
        id_remitente: Optional[UUID] = None,
        id_destinatario: Optional[UUID] = None,
        estado: Optional[str] = None,
        tipo: Optional[str] = None,
    ) -> List[Paquete]:
        """
        Obtiene todos los paquetes con filtros opcionales.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver
            activos: Si es True, solo devuelve paquetes activos
            id_remitente: Filtrar por ID del remitente
            id_destinatario: Filtrar por ID del destinatario
            estado: Filtrar por estado del paquete
            tipo: Filtrar por tipo de envío (normal/express)

        Returns:
            Lista de objetos Paquete que coinciden con los criterios
        """
        query = db.query(Paquete)

        if activos:
            query = query.filter(Paquete.activo == True)

        if id_remitente:
            query = query.filter(Paquete.id_remitente == id_remitente)

        if id_destinatario:
            query = query.filter(Paquete.id_destinatario == id_destinatario)

        if estado:
            query = query.filter(Paquete.estado == estado.lower())

        if tipo:
            query = query.filter(Paquete.tipo == tipo.lower())

        return query.offset(skip).limit(limit).all()

    def _validar_datos_paquete(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos básicos de un paquete."""
        print("\n=== VALIDACIÓN DE DATOS DEL PAQUETE ===")
        print("Datos recibidos:", datos)
        try:
            descripcion = datos.get("contenido", datos.get("descripcion", ""))
            print(
                f"Validando descripción: '{descripcion}' (longitud: {len(descripcion) if descripcion else 0})"
            )
            if not descripcion or len(descripcion) < 5 or len(descripcion) > 500:
                print(f"Error: La descripción debe tener entre 5 y 500 caracteres")
                return False
            peso = float(datos.get("peso", 0))
            print(
                f"Validando peso: {peso} kg (rango: {self.peso_minimo}-{self.peso_maximo} kg)"
            )
            if not (self.peso_minimo <= peso <= self.peso_maximo):
                print(
                    f"Error: El peso debe estar entre {self.peso_minimo} y {self.peso_maximo} kg"
                )
                return False
            tipo = datos.get("tipo", "").lower()
            print(
                f"Validando tipo: '{tipo}' (permitidos: {', '.join(self.tipos_permitidos)})"
            )
            if tipo not in self.tipos_permitidos:
                print(
                    f"Error: Tipo de envío inválido. Debe ser uno de: {', '.join(self.tipos_permitidos)}"
                )
                return False
            fragilidad = datos.get("fragilidad", "").lower()
            fragilidades_validas = ["baja", "normal", "alta"]
            print(
                f"Validando fragilidad: '{fragilidad}' (permitidas: {', '.join(fragilidades_validas)})"
            )
            if fragilidad not in fragilidades_validas:
                print(
                    f"Error: La fragilidad debe ser una de: {', '.join(fragilidades_validas)}"
                )
                return False
            tamaño = datos.get("tamaño", "").lower()
            print(
                f"Validando tamaño: '{tamaño}' (permitidos: {', '.join(self.tamanos_permitidos)})"
            )
            if tamaño not in self.tamanos_permitidos:
                print(
                    f"Error: Tamaño de paquete inválido. Debe ser uno de: {', '.join(self.tamanos_permitidos)}"
                )
                return False
            estado = datos.get("estado", "registrado")
            print(
                f"Validando estado: '{estado}' (permitidos: {', '.join(self.estados_permitidos)})"
            )
            if estado not in self.estados_permitidos:
                print(
                    f"Error: Estado inválido. Debe ser uno de: {', '.join(self.estados_permitidos)}"
                )
                return False
            print("¡Todas las validaciones pasaron con éxito!")
            print("======================================\n")
            return True
        except (ValueError, TypeError) as e:
            print(f"Error de validación: {str(e)}")
            return False

    def obtener_por_id_paquete(
        self, db: Session, id_paquete: UUID
    ) -> Optional[Paquete]:
        """Obtiene un paquete por su ID."""
        if not id_paquete:
            return None
        return db.query(Paquete).filter(Paquete.id_paquete == id_paquete).first()

    def obtener_por_cliente(
        self, db: Session, id_cliente: UUID, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Paquete], int]:
        """
        Obtiene paquetes por ID de cliente con paginación.
        Args:
            db: Sesión de base de datos
            id_cliente: ID del cliente
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de paquetes, total de registros)
        """
        if not id_cliente:
            return [], 0
        consulta = db.query(Paquete).filter(Paquete.id_cliente == id_cliente)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def obtener_por_estado(
        self, db: Session, estado: str, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Paquete], int]:
        """
        Obtiene paquetes por estado con paginación.
        Args:
            db: Sesión de base de datos
            estado: Estado del paquete
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de paquetes, total de registros)
        """
        if estado not in self.estados_permitidos:
            return [], 0
        consulta = db.query(Paquete).filter(Paquete.estado == estado)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def obtener_por_tipo(
        self, db: Session, tipo: str, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Paquete], int]:
        """
        Obtiene paquetes por tipo con paginación.
        Args:
            db: Sesión de base de datos
            tipo: Tipo de paquete
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de paquetes, total de registros)
        """
        if tipo not in self.tipos_permitidos:
            return [], 0
        consulta = db.query(Paquete).filter(Paquete.tipo == tipo)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def crear_registro(
        self,
        db: Session,
        *,
        datos_entrada: Union[PaqueteCreate, Dict[str, Any]],
        creado_por: UUID,
    ) -> Optional[Paquete]:
        """
        Crea un nuevo paquete con validación de datos.
        Args:
            db: Sesión de base de datos
            datos_entrada: Datos para crear el paquete (puede ser un objeto PaqueteCreate o un diccionario)
            creado_por: ID del usuario que crea el registro
        Returns:
            El paquete creado o None si hay un error
        """
        if hasattr(datos_entrada, "model_dump"):
            datos = datos_entrada.model_dump()
        elif hasattr(datos_entrada, "dict"):
            datos = datos_entrada.dict()
        else:
            datos = dict(datos_entrada)
        datos["creado_por"] = creado_por
        if "fecha_creacion" not in datos:
            datos["fecha_creacion"] = datetime.now()
        if not self._validar_datos_paquete(datos):
            return None
        if "estado" not in datos:
            datos["estado"] = "registrado"
        try:
            if isinstance(datos.get("fecha_creacion"), type(datetime.now)):
                datos["fecha_creacion"] = datos["fecha_creacion"]()
            
            campos_permitidos = {
                "id_paquete",
                "id_cliente",
                "peso",
                "tamaño",
                "fragilidad",
                "contenido",
                "tipo",
                "estado",
                "activo",
                "fecha_creacion",
                "fecha_actualizacion",
                "creado_por",
                "actualizado_por",
            }
            datos_filtrados = {k: v for k, v in datos.items() if k in campos_permitidos}
            paquete = Paquete(**datos_filtrados)
            db.add(paquete)
            db.commit()
            db.refresh(paquete)
            return paquete
        except Exception as e:
            db.rollback()
            print(f"Error al crear paquete: {str(e)}")
            return None

    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: Paquete,
        datos_entrada: Union[PaqueteUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> Optional[Paquete]:
        """
        Actualiza un paquete existente con validación de datos.
        Args:
            db: Sesión de base de datos
            objeto_db: Objeto de paquete a actualizar
            datos_entrada: Datos para actualizar
            actualizado_por: ID del usuario que actualiza el registro
        Returns:
            El paquete actualizado o None si hay un error
        """
        if isinstance(datos_entrada, dict):
            datos_actualizados = datos_entrada
        else:
            datos_actualizados = datos_entrada.dict(exclude_unset=True)
        datos_completos = objeto_db.__dict__.copy()
        datos_completos.update(datos_actualizados)
        if not self._validar_datos_paquete(datos_completos):
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

    def actualizar_estado(
        self, db: Session, *, id: UUID, nuevo_estado: str, actualizado_por: UUID
    ) -> Optional[Paquete]:
        """
        Actualiza el estado de un paquete.
        Args:
            db: Sesión de base de datos
            id: ID del paquete a actualizar
            nuevo_estado: Nuevo estado del paquete
            actualizado_por: ID del usuario que actualiza el estado
        Returns:
            El paquete actualizado o None si hay un error
        """
        if nuevo_estado not in self.estados_permitidos:
            return None
        try:
            paquete = self.obtener_por_id(db, id)
            if not paquete:
                return None
            paquete.estado = nuevo_estado
            paquete.actualizado_por = actualizado_por
            paquete.fecha_actualizacion = datetime.utcnow()
            if nuevo_estado == "entregado" and not paquete.fecha_entrega:
                paquete.fecha_entrega = datetime.utcnow()
            db.add(paquete)
            db.commit()
            db.refresh(paquete)
            return paquete
        except Exception:
            db.rollback()
            return None


paquete = PaqueteCRUD()
