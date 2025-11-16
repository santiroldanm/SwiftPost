from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
from sqlalchemy.orm import Session
from entities.paquete import Paquete, PaqueteCreate, PaqueteUpdate
from .base_crud import CRUDBase


class PaqueteCRUD(CRUDBase[Paquete, PaqueteCreate, PaqueteUpdate]):
    """Operaciones CRUD para la entidad Paquete con validaciones."""

    def __init__(self, db: Session):
        super().__init__(Paquete, db)
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
        self.db = db

    def obtener_todos(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        activos: bool = True,
        id_remitente: Optional[UUID] = None,
        id_destinatario: Optional[UUID] = None,
        estado: Optional[str] = None,
        tipo: Optional[str] = None,
        fragilidad: Optional[str] = None,
        search: Optional[str] = None,
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
            fragilidad: Filtrar por fragilidad del paquete
            search: Buscar por contenido o tipo

        Returns:
            Lista de objetos Paquete que coinciden con los criterios
        """
        query = self.db.query(Paquete)

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
        
        if fragilidad:
            query = query.filter(Paquete.fragilidad == fragilidad.lower())
        
        if search is not None and search.strip():
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (Paquete.contenido.ilike(search_term)) |
                (Paquete.tipo.ilike(search_term))
            )

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

    def obtener_por_id_paquete(self, id_paquete: UUID) -> Optional[Paquete]:
        """Obtiene un paquete por su ID."""
        if not id_paquete:
            return None
        return self.db.query(Paquete).filter(Paquete.id_paquete == id_paquete).first()

    def obtener_por_cliente(
        self, id_cliente: UUID, skip: int = 0, limit: int = 100
    ) -> List[Paquete]:
        """
                Obtiene paquetes por ID de cliente con paginación.
                Args:
                    db: Sesión de base de datos
                    id_cliente: ID del cliente
                    skip
        : Número de registros a omitir (para paginación)
                    limit: Número máximo de registros a devolver
                Returns:
                    Tupla con (lista de paquetes)
        """
        if not id_cliente:
            return [], 0
        consulta = self.db.query(Paquete).filter(Paquete.id_cliente == id_cliente)
        resultados = consulta.offset(skip).limit(limit).all()
        return resultados

    def obtener_por_estado(
        self, estado: str, skip: int = 0, limit: int = 100
    ) -> List[Paquete]:
        """
                Obtiene paquetes por estado con paginación.
                Args:
                    estado: Estado del paquete
                    skip
        : Número de registros a omitir (para paginación)
                    limit: Número máximo de registros a devolver
                Returns:
                    Tupla con (lista de paquetes)
        """
        if estado not in self.estados_permitidos:
            return [], 0
        consulta = self.db.query(Paquete).filter(Paquete.estado == estado)
        resultados = consulta.offset(skip).limit(limit).all()
        return resultados

    def obtener_por_tipo(
        self, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[Paquete]:
        """
                Obtiene paquetes por tipo con paginación.
                Args:
                    tipo: Tipo de paquete
                    skip
        : Número de registros a omitir (para paginación)
                    limit: Número máximo de registros a devolver
                Returns:
                    Tupla con (lista de paquetes)
        """
        if tipo not in self.tipos_permitidos:
            return [], 0
        consulta = self.db.query(Paquete).filter(Paquete.tipo == tipo)
        resultados = consulta.offset(skip).limit(limit).all()
        return resultados

    def crear_paquete(
        self,
        *,
        datos_entrada: Union[PaqueteCreate, Dict[str, Any]],
        id_cliente: UUID,
        creado_por: UUID,
    ) -> Optional[Paquete]:
        """
        Crea un paquete. id_cliente y creado_por pueden ser uuid.UUID o strings convertibles.
        Retorna Paquete o None en caso de error (imprime el motivo).
        """
        from uuid import UUID as StdUUID
        from datetime import datetime

        try:
            if hasattr(datos_entrada, "model_dump"):
                datos = datos_entrada.model_dump()
            elif hasattr(datos_entrada, "dict"):
                datos = datos_entrada.dict()
            elif isinstance(datos_entrada, dict):
                datos = dict(datos_entrada)
            else:
                datos = dict(datos_entrada)
        except Exception as e:
            print("Error: datos_entrada no convertible a dict:", e)
            return None

        if hasattr(self, "_validar_datos_paquete"):
            try:
                if not self._validar_datos_paquete(datos):
                    print("Error: validación del paquete falló")
                    return None
            except Exception as e:
                print("Error en validación de paquete:", e)
                return None

        try:
            id_cliente = (
                id_cliente
                if isinstance(id_cliente, StdUUID)
                else StdUUID(str(id_cliente))
            )
            creado_por = (
                creado_por
                if isinstance(creado_por, StdUUID)
                else StdUUID(str(creado_por))
            )
        except Exception as e:
            print("Error: id_cliente o creado_por no son UUID válidos:", e)
            return None

        datos_filtrados = {
            k: v
            for k, v in dict(datos).items()
            if k not in ("id_paquete", "fecha_creacion", "fecha_actualizacion")
        }

        datos_filtrados["id_cliente"] = id_cliente
        datos_filtrados["creado_por"] = creado_por
        datos_filtrados["actualizado_por"] = None
        datos_filtrados.setdefault("fecha_creacion", datetime.now())
        datos_filtrados.setdefault("activo", True)

        try:
            paquete = Paquete(**datos_filtrados)
            self.db.add(paquete)
            self.db.commit()
            self.db.refresh(paquete)
            return paquete
        except Exception as e:
            self.db.rollback()
            print("Error al crear paquete:", e)
            return None

    def actualizar(
        self,
        *,
        objeto_db: Paquete,
        datos_entrada: Union[Dict[str, Any], Any],
        actualizado_por: Union[str, UUID],
    ) -> Optional[Paquete]:
        """
        Actualiza un paquete existente.
        Lanza ValueError con mensajes claros en caso de fallo (endpoint debe capturarlo y devolver 400).
        """
        try:
            if isinstance(datos_entrada, dict):
                datos_actualizados: Dict[str, Any] = dict(datos_entrada)
            elif hasattr(datos_entrada, "model_dump"):
                datos_actualizados = datos_entrada.model_dump(exclude_unset=True)
            elif hasattr(datos_entrada, "dict"):
                datos_actualizados = datos_entrada.dict(exclude_unset=True)
            else:
                datos_actualizados = dict(datos_entrada)
        except Exception as e:
            raise ValueError(f"Payload inválido: {e}")

        try:
            if hasattr(objeto_db, "to_dict"):
                datos_completos = objeto_db.to_dict()
            else:
                datos_completos = {
                    col.name: getattr(objeto_db, col.name)
                    for col in objeto_db.__table__.columns
                }
            datos_completos.update(datos_actualizados)
        except Exception as e:
            raise ValueError(f"Error preparando datos para validación: {e}")

        if hasattr(self, "_validar_datos_paquete"):
            try:
                ok = self._validar_datos_paquete(datos_completos)
            except Exception as e:
                raise ValueError(f"Error en validación interna: {e}")
            if not ok:
                raise ValueError(
                    "Validación del paquete falló (revisa reglas de negocio)."
                )

        try:
            actualizado_uuid = (
                actualizado_por
                if isinstance(actualizado_por, UUID)
                else UUID(str(actualizado_por))
            )
        except Exception as e:
            raise ValueError(f"actualizado_por no es un UUID válido: {e}")

        try:
            usuario_existe = False
            try:
                from cruds.usuario_crud import UsuarioCRUD

                usuario_crud = UsuarioCRUD(self.db)
                usuario_existe = (
                    usuario_crud.obtener_por_id(actualizado_uuid) is not None
                )
            except Exception:
                try:
                    from entities.usuario import Usuario

                    usuario_existe = (
                        self.db.query(Usuario)
                        .filter(Usuario.id_usuario == str(actualizado_uuid))
                        .first()
                        is not None
                    )
                except Exception:
                    usuario_existe = False

            if not usuario_existe:
                raise ValueError(
                    f"Usuario para 'actualizado_por' no encontrado: {actualizado_uuid}"
                )
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error al verificar usuario de actualización: {e}")

        try:
            for campo, valor in datos_actualizados.items():
                if hasattr(objeto_db, campo):
                    setattr(objeto_db, campo, valor)

            objeto_db.actualizado_por = actualizado_uuid
            objeto_db.fecha_actualizacion = datetime.utcnow()

            self.db.add(objeto_db)
            self.db.commit()
            self.db.refresh(objeto_db)
            return objeto_db

        except Exception as e:
            try:
                self.db.rollback()
            except Exception:
                pass
            print("Error al actualizar paquete:", e)
            raise ValueError(f"Error al actualizar paquete: {e}")

    def actualizar_estado(
        self, *, id: UUID, nuevo_estado: str, actualizado_por: UUID
    ) -> Optional[Paquete]:
        """
        Actualiza el estado de un paquete.
        Args:
            id: ID del paquete a actualizar
            nuevo_estado: Nuevo estado del paquete
            actualizado_por: ID del usuario que actualiza el estado
        Returns:
            El paquete actualizado o None si hay un error
        """
        if nuevo_estado not in self.estados_permitidos:
            return None
        try:
            paquete = self.obtener_por_id(id)
            if not paquete:
                return None
            paquete.estado = nuevo_estado
            paquete.actualizado_por = str(actualizado_por)
            paquete.fecha_actualizacion = datetime.utcnow()
            if nuevo_estado == "entregado" and not paquete.fecha_entrega:
                paquete.fecha_entrega = datetime.utcnow()
            self.db.add(paquete)
            self.db.commit()
            self.db.refresh(paquete)
            return paquete
        except Exception:
            self.db.rollback()
            return None

    def obtener_por_id(self, id_paquete: UUID) -> Optional[Paquete]:
        """
        Obtiene un paquete por su ID (id_paquete).
        Retorna el objeto Paquete o None si no existe.
        """
        if not id_paquete:
            return None

        try:
            paquete = (
                self.db.query(Paquete).filter(Paquete.id_paquete == id_paquete).first()
            )
            return paquete
        except Exception as e:
            print(f"Error al obtener paquete por id_paquete: {e}")
            return None

    def desactivar_paquete(self, *, id_paquete: UUID, actualizado_por: UUID) -> bool:
        """
        Desactiva un paquete (soft delete).

        Args:
            id_paquete: ID del paquete a desactivar
            actualizado_por: ID del usuario que realiza la desactivación

        Returns:
            bool: True si se desactivó correctamente, False en caso contrario
        """
        try:
            paquete = self.obtener_por_id(id_paquete)

            if not paquete:
                print(f" Error: Paquete no encontrado con ID: {id_paquete}")
                return False

            if not paquete.activo:
                print(f" Advertencia: El paquete ya está inactivo")
                return False

            paquete.activo = False
            paquete.actualizado_por = str(actualizado_por)
            paquete.fecha_actualizacion = datetime.utcnow()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f" Error al desactivar paquete: {e}")
            import traceback

            traceback.print_exc()
            return False
