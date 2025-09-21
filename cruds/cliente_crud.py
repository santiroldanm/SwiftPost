from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from sqlalchemy.orm import Session

from entities.cliente import Cliente, ClienteCreate, ClienteUpdate
from .base_crud import CRUDBase


class ClienteCRUD(CRUDBase[Cliente, ClienteCreate, ClienteUpdate]):
    """Operaciones CRUD para la entidad Cliente con validaciones."""
    
    def __init__(self):
        super().__init__(Cliente)
        # Configuraciones específicas para Cliente
        self.longitud_minima_nombre = 2
        self.longitud_maxima_nombre = 50
        self.longitud_minima_direccion = 5
        self.longitud_maxima_direccion = 200
    
    def _validar_datos_cliente(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos básicos de un cliente."""
        # Validar nombres
        if not self._validar_longitud_texto('primer_nombre', datos.get('primer_nombre', '')):
            return False
        if 'segundo_nombre' in datos and not self._validar_longitud_texto('segundo_nombre', datos['segundo_nombre']):
            return False
        
        # Validar apellidos
        if not self._validar_longitud_texto('primer_apellido', datos.get('primer_apellido', '')):
            return False
        if 'segundo_apellido' in datos and not self._validar_longitud_texto('segundo_apellido', datos['segundo_apellido']):
            return False
        
        # Validar email
        if not self._validar_email(datos.get('correo', '')):
            return False
            
        # Validar teléfono
        if 'telefono' in datos and not self._validar_telefono(str(datos['telefono'])):
            return False
            
        # Validar documento
        if not self._validar_documento(datos.get('documento', '')):
            return False
            
        # Validar dirección
        direccion = datos.get('direccion', '')
        if (not direccion or 
            len(direccion) < self.longitud_minima_direccion or 
            len(direccion) > self.longitud_maxima_direccion):
            return False
            
        # Validar tipo (remitente/receptor)
        if datos.get('tipo') not in ['remitente', 'receptor']:
            return False
            
        return True
    
    def obtener_por_documento(self, db: Session, documento: str) -> Optional[Cliente]:
        """Obtiene un cliente por su número de documento."""
        if not documento or not self._validar_documento(documento):
            return None
        return db.query(Cliente).filter(Cliente.documento == documento).first()
    
    def obtener_por_email(self, db: Session, correo: str) -> Optional[Cliente]:
        """Obtiene un cliente por su correo electrónico."""
        if not correo or not self._validar_email(correo):
            return None
        return db.query(Cliente).filter(Cliente.correo == correo.lower()).first()
    
    def obtener_por_tipo(
        self, 
        db: Session, 
        tipo: str, 
        saltar: int = 0, 
        limite: int = 100
    ) -> Tuple[List[Cliente], int]:
        """Obtiene clientes por tipo (remitente/receptor) con paginación."""
        if tipo not in ['remitente', 'receptor']:
            return [], 0
            
        consulta = db.query(Cliente).filter(Cliente.tipo == tipo, Cliente.activo == True)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total
    
    def obtener_activos(
        self, 
        db: Session, 
        saltar: int = 0, 
        limite: int = 100
    ) -> Tuple[List[Cliente], int]:
        """Obtiene clientes activos con paginación."""
        consulta = db.query(Cliente).filter(Cliente.activo == True)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total
    
    def crear(
        self, 
        db: Session, 
        *, 
        datos_entrada: ClienteCreate, 
        creado_por: UUID
    ) -> Optional[Cliente]:
        """Crea un nuevo cliente con validación de datos."""
        datos = datos_entrada.dict()
        
        # Validar datos
        if not self._validar_datos_cliente(datos):
            return None
            
        # Verificar duplicados
        if self.obtener_por_documento(db, datos['documento']):
            return None
            
        if self.obtener_por_email(db, datos['correo']):
            return None
        
        # Crear el cliente
        try:
            cliente = Cliente(
                **datos,
                creado_por=creado_por,
                fecha_creacion=datetime.utcnow(),
                activo=True
            )
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
            return cliente
        except Exception:
            db.rollback()
            return None
    
    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: Cliente,
        datos_entrada: Union[ClienteUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> Optional[Cliente]:
        """Actualiza un cliente existente con validación de datos."""
        if isinstance(datos_entrada, dict):
            datos_actualizados = datos_entrada
        else:
            datos_actualizados = datos_entrada.dict(exclude_unset=True)
        
        # No permitir modificar el documento
        if 'documento' in datos_actualizados:
            del datos_actualizados['documento']
            
        # Validar datos actualizados
        datos_completos = objeto_db.__dict__.copy()
        datos_completos.update(datos_actualizados)
        
        if not self._validar_datos_cliente(datos_completos):
            return None
            
        # Verificar duplicado de correo
        if 'correo' in datos_actualizados and \
           datos_actualizados['correo'] != objeto_db.correo and \
           self.obtener_por_email(db, datos_actualizados['correo']):
            return None
        
        # Actualizar el cliente
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
    
    def desactivar(
        self, 
        db: Session, 
        *, 
        id: UUID, 
        actualizado_por: UUID
    ) -> bool:
        """Desactiva un cliente por su ID."""
        try:
            cliente = self.obtener_por_id(db, id)
            if not cliente or not cliente.activo:
                return False
                
            cliente.activo = False
            cliente.actualizado_por = actualizado_por
            cliente.fecha_actualizacion = datetime.utcnow()
            
            db.add(cliente)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


# Instancia única para importar
cliente = ClienteCRUD()
