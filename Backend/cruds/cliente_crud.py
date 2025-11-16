from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
from sqlalchemy.orm import Session
from entities.cliente import Cliente, ClienteCreate, ClienteUpdate
from .base_crud import CRUDBase


class ClienteCRUD(CRUDBase[Cliente, ClienteCreate, ClienteUpdate]):
    """Operaciones CRUD para la entidad Cliente con validaciones."""

    def __init__(self, db: Session):
        super().__init__(Cliente, db)
        self.longitud_minima_nombre = 2
        self.longitud_maxima_nombre = 50
        self.longitud_minima_direccion = 5
        self.longitud_maxima_direccion = 200
        self.db = db

    def _validar_datos_cliente(self, datos: Dict[str, Any]) -> bool:
        """
        Valida los datos básicos de un cliente.
        Args:
            datos: Diccionario con los datos del cliente a validar
        Returns:
            bool: True si todos los datos son válidos, False de lo contrario
        """
        try:
            if not self._validar_longitud_texto(
                "primer_nombre", datos.get("primer_nombre", "")
            ):
                print("Error: El primer nombre no cumple con la longitud requerida")
                return False
            if "segundo_nombre" in datos and datos["segundo_nombre"] is not None:
                if not self._validar_longitud_texto(
                    "segundo_nombre", datos["segundo_nombre"]
                ):
                    print(
                        "Error: El segundo nombre no cumple con la longitud requerida"
                    )
                    return False
            if not self._validar_longitud_texto(
                "primer_apellido", datos.get("primer_apellido", "")
            ):
                print("Error: El primer apellido no cumple con la longitud requerida")
                return False
            if "segundo_apellido" in datos and datos["segundo_apellido"] is not None:
                if not self._validar_longitud_texto(
                    "segundo_apellido", datos["segundo_apellido"]
                ):
                    print(
                        "Error: El segundo apellido no cumple con la longitud requerida"
                    )
                    return False
            if not self._validar_email(datos.get("correo", "")):
                print("Error: El correo electrónico no es válido")
                return False
            if "telefono" not in datos or not self._validar_telefono(
                str(datos["telefono"])
            ):
                print("Error: El teléfono no es válido")
                return False
            if not self._validar_documento(datos.get("numero_documento", "")):
                print("Error: El número de documento no es válido")
                return False
            direccion = datos.get("direccion", "")
            if not direccion:
                print("Error: La dirección es requerida")
                return False
            if len(direccion) < self.longitud_minima_direccion:
                print(
                    f"Error: La dirección es demasiado corta (mínimo {self.longitud_minima_direccion} caracteres)"
                )
                return False
            if len(direccion) > self.longitud_maxima_direccion:
                print(
                    f"Error: La dirección es demasiado larga (máximo {self.longitud_maxima_direccion} caracteres)"
                )
                return False
            tipo = datos.get("tipo", "").lower()
            if tipo not in ["remitente", "receptor"]:
                print("Error: El tipo debe ser 'remitente' o 'receptor'")
                return False
            print("✓ Todos los datos son válidos")
            return True
        except Exception as e:
            print(f"Error inesperado durante la validación: {str(e)}")
            return False

    def obtener_clientes(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """
        Obtener lista de clientes con paginación

        Args:
            skip: Número de registros a omitir
            limit: Límite de registros a retornar

        Returns:
            Lista de clientes
        """
        return self.db.query(Cliente).offset(skip).limit(limit).all()

    def obtener_por_id(self, id: Union[UUID, str]) -> Optional[Cliente]:
        """Obtiene un cliente por su ID."""
        try:
            if not id:
                return None
            """ Convertir a string para la consulta """
            id_str = str(id) if isinstance(id, UUID) else id
            return self.db.query(Cliente).filter(Cliente.id_cliente == id_str).first()
        except Exception as e:
            print(f"Error al obtener cliente por ID {id}: {str(e)}")
            return None

    def obtener_por_documento(self, numero_documento: str) -> Optional[Cliente]:
        """Obtiene un cliente por su número de documento."""
        if not numero_documento or not self._validar_documento(numero_documento):
            return None
        return (
            self.db.query(Cliente)
            .filter(Cliente.numero_documento == numero_documento)
            .first()
        )

    def obtener_por_email(self, correo: str) -> Optional[Cliente]:
        """Obtiene un cliente por su correo electrónico."""
        if not correo or not self._validar_email(correo):
            return None
        return self.db.query(Cliente).filter(Cliente.correo == correo.lower()).first()

    def obtener_por_tipo(
        self, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[Cliente]:
        """Obtiene clientes por tipo (remitente/receptor) con paginación."""
        if tipo not in ["remitente", "receptor"]:
            return []
        consulta = self.db.query(Cliente).filter(
            Cliente.tipo == tipo, Cliente.activo == True
        )
        resultados = consulta.offset(skip).limit(limit).all()
        return resultados

    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Obtiene clientes activos con paginación."""
        consulta = self.db.query(Cliente).filter(Cliente.activo == True)
        resultados = consulta.offset(skip).limit(limit).all()
        return resultados

    def obtener_por_usuario(self, usuario_id: UUID) -> Optional[Cliente]:
        """Obtiene un cliente por su ID de usuario."""
        if not usuario_id:
            return None
        return (
            self.db.query(Cliente).filter(Cliente.usuario_id == str(usuario_id)).first()
        )

    def crear_cliente(
        self,
        *,
        datos_entrada: ClienteCreate,
        usuario_id: UUID,
        id_tipo_documento: UUID,
    ) -> Optional[Cliente]:
        """Crea un nuevo cliente con validación de datos."""
        try:
            if isinstance(datos_entrada, dict):
                datos = datos_entrada.copy()
            else:
                datos = datos_entrada.dict()
            if not self._validar_datos_cliente(datos):
                print("Error: Validación de datos fallida")
                return None
            if self.obtener_por_documento(datos["numero_documento"]):
                print(
                    f"Error: Ya existe un cliente con el documento {datos['numero_documento']}"
                )
                return None
            if self.obtener_por_email(datos["correo"]):
                print(f"Error: Ya existe un cliente con el correo {datos['correo']}")
                return None
            datos_creacion = {
                "primer_nombre": datos["primer_nombre"],
                "primer_apellido": datos["primer_apellido"],
                "numero_documento": datos["numero_documento"],
                "id_tipo_documento": id_tipo_documento,
                "correo": datos["correo"].lower(),
                "telefono": datos["telefono"],
                "direccion": datos["direccion"],
                "tipo": datos["tipo"],
                "creado_por": str(usuario_id),
                "usuario_id": datos["usuario_id"],
                "activo": True,
                "fecha_creacion": datetime.now(),
            }
            if "segundo_nombre" in datos and datos["segundo_nombre"]:
                datos_creacion["segundo_nombre"] = datos["segundo_nombre"]
            if "segundo_apellido" in datos and datos["segundo_apellido"]:
                datos_creacion["segundo_apellido"] = datos["segundo_apellido"]
            cliente = Cliente(**datos_creacion)
            self.db.add(cliente)
            self.db.commit()
            self.db.refresh(cliente)
            return cliente
        except Exception as e:
            print(f"Error al crear el cliente: {e}")
            import traceback

            traceback.print_exc()
            self.db.rollback()
            return None

    def actualizar_cliente(
        self,
        *,
        objeto_db: Cliente,
        datos_entrada: Union[ClienteUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> Optional[Cliente]:
        """Actualiza un cliente existente con validación de datos."""
        if isinstance(datos_entrada, dict):
            datos_actualizados = datos_entrada
        else:
            datos_actualizados = datos_entrada.dict(exclude_unset=True)
        if "documento" in datos_actualizados:
            del datos_actualizados["documento"]
        datos_completos = objeto_db.__dict__.copy()
        datos_completos.update(datos_actualizados)
        if not self._validar_datos_cliente(datos_completos):
            return None
        if (
            "correo" in datos_actualizados
            and datos_actualizados["correo"] != objeto_db.correo
            and self.obtener_por_email(datos_actualizados["correo"])
        ):
            return None
        try:
            for campo, valor in datos_actualizados.items():
                if hasattr(objeto_db, campo):
                    setattr(objeto_db, campo, valor)
            objeto_db.actualizado_por = actualizado_por
            objeto_db.fecha_actualizacion = datetime.now()
            self.db.add(objeto_db)
            self.db.commit()
            self.db.refresh(objeto_db)
            return objeto_db
        except Exception:
            self.db.rollback()
            return None

    def desactivar(self, *, id: UUID, actualizado_por: UUID) -> bool:
        """Desactiva un cliente por su ID."""
        try:
            cliente = self.obtener_por_id(id)
            if not cliente or not cliente.activo:
                return False
            cliente.activo = False
            cliente.actualizado_por = actualizado_por
            cliente.fecha_actualizacion = datetime.utcnow()
            self.db.add(cliente)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def eliminar_cliente(self, cliente_id: UUID, actualizado_por: UUID) -> bool:
        """
        Marca un cliente como eliminado (soft delete).
        """
        try:
            cliente = self.obtener_por_id(cliente_id)
            if not cliente:
                return False

            cliente.activo = False
            cliente.fecha_actualizacion = datetime.now()
            cliente.actualizado_por = actualizado_por
            self.db.commit()
            self.db.refresh(cliente)
            return True

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al eliminar cliente: {str(e)}")

    def buscar_por_nombre(self, nombre: str, limite: int = 10) -> List[Cliente]:
        """
        Busca clientes por nombre (primer nombre o primer apellido).

        Args:
            db: Sesión de base de datos
            nombre: Nombre a buscar
            limite: Número máximo de resultados

        Returns:
            List[Cliente]: Lista de clientes encontrados
        """
        try:
            if not nombre or len(nombre.strip()) < 2:
                return []

            nombre_busqueda = f"%{nombre.strip().lower()}%"

            return (
                self.db.query(Cliente)
                .filter(
                    (Cliente.primer_nombre.ilike(nombre_busqueda))
                    | (Cliente.primer_apellido.ilike(nombre_busqueda))
                    | (Cliente.segundo_nombre.ilike(nombre_busqueda))
                    | (Cliente.segundo_apellido.ilike(nombre_busqueda))
                )
                .filter(Cliente.activo == True)
                .limit(limite)
                .all()
            )
        except Exception as e:
            print(f"Error al buscar clientes por nombre: {str(e)}")
            return []
