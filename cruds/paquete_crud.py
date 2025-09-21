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
        # Configuraciones específicas para Paquete
        self.estados_permitidos = ['registrado', 'en_transito', 'en_reparto', 'entregado', 'no_entregado', 'devuelto']
        self.tipos_permitidos = ['sobre', 'paquete_pequeno', 'paquete_mediano', 'paquete_grande', 'caja']
        self.peso_minimo = 0.1  # en kg
        self.peso_maximo = 50.0  # en kg
        self.valor_minimo = 0.0
        self.valor_maximo = 1000000.0  # Valor máximo declarado
    
    def _validar_datos_paquete(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos básicos de un paquete."""
        # Validar descripción
        descripcion = datos.get('descripcion', '')
        if not descripcion or len(descripcion) < 5 or len(descripcion) > 500:
            return False
        
        # Validar peso
        peso = datos.get('peso', 0)
        if not (self.peso_minimo <= float(peso) <= self.peso_maximo):
            return False
            
        # Validar valor declarado
        valor_declarado = datos.get('valor_declarado', 0)
        if not (self.valor_minimo <= float(valor_declarado) <= self.valor_maximo):
            return False
        
        # Validar tipo
        if datos.get('tipo') not in self.tipos_permitidos:
            return False
            
        # Validar estado si está presente
        if 'estado' in datos and datos['estado'] not in self.estados_permitidos:
            return False
            
        return True
    
    def obtener_por_cliente(
        self, 
        db: Session, 
        id_cliente: UUID, 
        saltar: int = 0, 
        limite: int = 100
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
        self, 
        db: Session, 
        estado: str, 
        saltar: int = 0, 
        limite: int = 100
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
        self, 
        db: Session, 
        tipo: str, 
        saltar: int = 0, 
        limite: int = 100
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
    
    def crear(
        self, 
        db: Session, 
        *, 
        datos_entrada: PaqueteCreate, 
        creado_por: UUID
    ) -> Optional[Paquete]:
        """
        Crea un nuevo paquete con validación de datos.
        
        Args:
            db: Sesión de base de datos
            datos_entrada: Datos para crear el paquete
            creado_por: ID del usuario que crea el registro
            
        Returns:
            El paquete creado o None si hay un error
        """
        datos = datos_entrada.dict()
        
        # Validar datos
        if not self._validar_datos_paquete(datos):
            return None
        
        # Establecer estado por defecto si no se proporciona
        if 'estado' not in datos:
            datos['estado'] = 'registrado'
        
        # Crear el paquete
        try:
            paquete = Paquete(
                **datos,
                creado_por=creado_por,
                fecha_creacion=datetime.utcnow()
            )
            db.add(paquete)
            db.commit()
            db.refresh(paquete)
            return paquete
        except Exception:
            db.rollback()
            return None
    
    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: Paquete,
        datos_entrada: Union[PaqueteUpdate, Dict[str, Any]],
        actualizado_por: UUID
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
        
        # Validar datos actualizados
        datos_completos = objeto_db.__dict__.copy()
        datos_completos.update(datos_actualizados)
        
        if not self._validar_datos_paquete(datos_completos):
            return None
        
        # Actualizar el paquete
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
        self, 
        db: Session, 
        *, 
        id: UUID, 
        nuevo_estado: str, 
        actualizado_por: UUID
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
            
            # Si el estado es 'entregado', registrar la fecha de entrega
            if nuevo_estado == 'entregado' and not paquete.fecha_entrega:
                paquete.fecha_entrega = datetime.utcnow()
            
            db.add(paquete)
            db.commit()
            db.refresh(paquete)
            return paquete
        except Exception:
            db.rollback()
            return None


# Instancia única para importar
paquete = PaqueteCRUD()
