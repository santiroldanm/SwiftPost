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
        """
        Valida los datos básicos de un cliente.
        
        Args:
            datos: Diccionario con los datos del cliente a validar
            
        Returns:
            bool: True si todos los datos son válidos, False de lo contrario
        """
        try:
            print("\n=== VALIDACIÓN DE DATOS DEL CLIENTE ===")
            
            # Validar nombres
            if not self._validar_longitud_texto('primer_nombre', datos.get('primer_nombre', '')):
                print("Error: El primer nombre no cumple con la longitud requerida")
                return False
                
            if 'segundo_nombre' in datos and datos['segundo_nombre'] is not None:
                if not self._validar_longitud_texto('segundo_nombre', datos['segundo_nombre']):
                    print("Error: El segundo nombre no cumple con la longitud requerida")
                    return False
            
            # Validar apellidos
            if not self._validar_longitud_texto('primer_apellido', datos.get('primer_apellido', '')):
                print("Error: El primer apellido no cumple con la longitud requerida")
                return False
                
            if 'segundo_apellido' in datos and datos['segundo_apellido'] is not None:
                if not self._validar_longitud_texto('segundo_apellido', datos['segundo_apellido']):
                    print("Error: El segundo apellido no cumple con la longitud requerida")
                    return False
            
            # Validar email
            if not self._validar_email(datos.get('correo', '')):
                print("Error: El correo electrónico no es válido")
                return False
                
            # Validar teléfono
            if 'telefono' not in datos or not self._validar_telefono(str(datos['telefono'])):
                print("Error: El teléfono no es válido")
                return False
                
            # Validar número de documento
            if not self._validar_documento(datos.get('numero_documento', '')):
                print("Error: El número de documento no es válido")
                return False
                
            # Validar ID de tipo de documento
            if 'id_tipo_documento' not in datos or not datos['id_tipo_documento']:
                print("Error: Falta el ID del tipo de documento")
                return False
                
            # Validar dirección
            direccion = datos.get('direccion', '')
            if not direccion:
                print("Error: La dirección es requerida")
                return False
                
            if len(direccion) < self.longitud_minima_direccion:
                print(f"Error: La dirección es demasiado corta (mínimo {self.longitud_minima_direccion} caracteres)")
                return False
                
            if len(direccion) > self.longitud_maxima_direccion:
                print(f"Error: La dirección es demasiado larga (máximo {self.longitud_maxima_direccion} caracteres)")
                return False
                
            # Validar tipo (remitente/receptor)
            tipo = datos.get('tipo', '').lower()
            if tipo not in ['remitente', 'receptor']:
                print("Error: El tipo debe ser 'remitente' o 'receptor'")
                return False
                
            print("✓ Todos los datos son válidos")
            return True
            
        except Exception as e:
            print(f"Error inesperado durante la validación: {str(e)}")
            return False
    
    def obtener_por_documento(self, db: Session, numero_documento: str) -> Optional[Cliente]:
        """Obtiene un cliente por su número de documento."""
        if not numero_documento or not self._validar_documento(numero_documento):
            return None
        return db.query(Cliente).filter(Cliente.numero_documento == numero_documento).first()

    # Alias para compatibilidad con el main existente
    def get_activos(
        self, 
        db: Session, 
        saltar: int = 0, 
        limite: int = 100
    ):
        return self.obtener_activos(db, saltar=saltar, limite=limite)
    
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
        
    def obtener_por_usuario(self, db: Session, usuario_id: UUID) -> Optional[Cliente]:
        """Obtiene un cliente por su ID de usuario."""
        if not usuario_id:
            return None
        return db.query(Cliente).filter(Cliente.usuario_id == str(usuario_id)).first()
    
    def crear(
        self, 
        db: Session, 
        *, 
        datos_entrada: ClienteCreate, 
        usuario_id: UUID,
    ) -> Optional[Cliente]:
        """Crea un nuevo cliente con validación de datos."""
        try:
            print("\n=== DEBUG: Iniciando creación de cliente ===")
            print(f"Datos de entrada: {datos_entrada}")
            
            # Convertir a diccionario si es necesario
            if isinstance(datos_entrada, dict):
                datos = datos_entrada.copy()
            else:
                datos = datos_entrada.dict()
            
            print(f"Datos convertidos a diccionario: {datos}")
            
            # Validar datos
            if not self._validar_datos_cliente(datos):
                print("Error: Validación de datos fallida")
                return None
                
            # Verificar duplicados
            if self.obtener_por_documento(db, datos['numero_documento']):
                print(f"Error: Ya existe un cliente con el documento {datos['numero_documento']}")
                return None
                
            if self.obtener_por_email(db, datos['correo']):
                print(f"Error: Ya existe un cliente con el correo {datos['correo']}")
                return None
            
            # Asegurarse de que los campos requeridos estén presentes
            datos_creacion = {
                'primer_nombre': datos['primer_nombre'],
                'primer_apellido': datos['primer_apellido'],
                'numero_documento': datos['numero_documento'],
                'id_tipo_documento': datos['id_tipo_documento'],
                'correo': datos['correo'].lower(),
                'telefono': datos['telefono'],
                'direccion': datos['direccion'],
                'tipo': datos['tipo'],
                'creado_por': str(usuario_id),  # Agregar el ID del usuario que crea el registro
                'usuario_id': str(usuario_id),  # Asegurar que sea string
                'activo': True,
                'fecha_creacion': datetime.utcnow()
            }
            
            print(f"Creando cliente con usuario_id: {datos_creacion['usuario_id']} (tipo: {type(datos_creacion['usuario_id'])})")
            
            # Agregar campos opcionales si existen
            if 'segundo_nombre' in datos and datos['segundo_nombre']:
                datos_creacion['segundo_nombre'] = datos['segundo_nombre']
                
            if 'segundo_apellido' in datos and datos['segundo_apellido']:
                datos_creacion['segundo_apellido'] = datos['segundo_apellido']
            
            print(f"Datos para crear el cliente: {datos_creacion}")
            
            # Crear el cliente
            cliente = Cliente(**datos_creacion)
            
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
            
            print(f"Cliente creado exitosamente con ID: {cliente.id_cliente}")
            return cliente
            
        except Exception as e:
            print(f"Error al crear el cliente: {e}")
            import traceback
            traceback.print_exc()
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
