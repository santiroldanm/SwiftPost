from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from entities.sede import Sede, SedeCreate, SedeUpdate
from .base_crud import CRUDBase


class SedeCRUD(CRUDBase[Sede, SedeCreate, SedeUpdate]):
    """Operaciones CRUD para la entidad Sede con validaciones."""

    def __init__(self):
        super().__init__(Sede)

    def obtener_por_id(self, db: Session, id: Union[UUID, str]) -> Optional[Sede]:
        """
        Obtiene una sede por su ID.

        Args:
            db: Sesión de base de datos
            id: ID de la sede a buscar

        Returns:
            Optional[Sede]: La sede encontrada o None si no existe
        """
        try:
            if not id:
                return None

            if db.is_active and db.in_transaction():
                try:
                    db.rollback()
                except:
                    pass

            return db.query(Sede).filter(Sede.id_sede == id).first()
        except SQLAlchemyError as e:
            print(f"Error de base de datos al obtener sede por ID {id}: {str(e)}")
            try:
                db.rollback()
            except:
                pass
            return None
        except Exception as e:
            print(f"Error al obtener sede por ID {id}: {str(e)}")
            return None

    def obtener_por_ciudad(
        self, db: Session, ciudad: str, saltar: int = 0, limite: int = 100
    ) -> List[Sede]:
        """
        Obtiene sedes por ciudad con paginación.

        Args:
            db: Sesión de base de datos
            ciudad: Nombre de la ciudad
            saltar: Número de registros a omitir
            limite: Número máximo de registros a devolver

        Returns:
            List[Sede]: Lista de sedes en la ciudad especificada
        """
        try:
            if not ciudad or not ciudad.strip():
                return []

            if db.is_active and db.in_transaction():
                try:
                    db.rollback()
                except:
                    pass

            return (
                db.query(Sede)
                .filter(Sede.ciudad.ilike(f"%{ciudad.strip()}%"))
                .offset(saltar)
                .limit(limite)
                .all()
            )
        except SQLAlchemyError as e:
            print(
                f"Error de base de datos al obtener sedes por ciudad {ciudad}: {str(e)}"
            )
            try:
                db.rollback()
            except:
                pass
            return []
        except Exception as e:
            print(f"Error al obtener sedes por ciudad {ciudad}: {str(e)}")
            return []

    def obtener_activas(
        self, db: Session, saltar: int = 0, limite: int = 100
    ) -> List[Sede]:
        """
        Obtiene sedes activas con paginación.

        Args:
            db: Sesión de base de datos
            saltar: Número de registros a omitir
            limite: Número máximo de registros a devolver

        Returns:
            List[Sede]: Lista de sedes activas
        """
        try:
            return (
                db.query(Sede)
                .filter(Sede.activo == True)
                .offset(saltar)
                .limit(limite)
                .all()
            )
        except Exception as e:
            print(f"Error al obtener sedes activas: {str(e)}")
            return []

    def crear_registro(
        self,
        db: Session,
        *,
        datos_entrada: Union[SedeCreate, Dict[str, Any]],
        creado_por: UUID,
    ) -> Optional[Sede]:
        """
        Crea una nueva sede.

        Args:
            db: Sesión de base de datos
            datos_entrada: Datos de la sede a crear
            creado_por: ID del usuario que crea la sede

        Returns:
            Optional[Sede]: La sede recién creada o None si hay error
        """
        try:
            if db.is_active and db.in_transaction():
                try:
                    db.rollback()
                except:
                    pass

            if hasattr(datos_entrada, "model_dump"):
                datos = datos_entrada.model_dump()
            elif hasattr(datos_entrada, "dict"):
                datos = datos_entrada.dict()
            else:
                datos = dict(datos_entrada)

            if "nombre" in datos:
                sede_existente = (
                    db.query(Sede).filter(Sede.nombre == datos["nombre"]).first()
                )
                if sede_existente:
                    print(
                        f"Error: Ya existe una sede con el nombre '{datos['nombre']}'"
                    )
                    return None

            datos["creado_por"] = str(creado_por)
            db_obj = Sede(**datos)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except SQLAlchemyError as e:
            try:
                db.rollback()
            except:
                pass
            print(f"Error de base de datos al crear sede: {str(e)}")
            return None
        except Exception as e:
            try:
                db.rollback()
            except:
                pass
            print(f"Error al crear sede: {str(e)}")
            return None

    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: Sede,
        datos_entrada: Union[SedeUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> Optional[Sede]:
        """
        Actualiza una sede existente.

        Args:
            db: Sesión de base de datos
            objeto_db: Objeto de sede a actualizar
            datos_entrada: Datos para actualizar
            actualizado_por: ID del usuario que actualiza

        Returns:
            Optional[Sede]: La sede actualizada o None si hay error
        """
        try:
            if hasattr(datos_entrada, "model_dump"):
                datos_actualizados = datos_entrada.model_dump(exclude_unset=True)
            elif hasattr(datos_entrada, "dict"):
                datos_actualizados = datos_entrada.dict(exclude_unset=True)
            else:
                datos_actualizados = dict(datos_entrada)

            if "nombre" in datos_actualizados:
                sede_existente = (
                    db.query(Sede)
                    .filter(
                        Sede.nombre == datos_actualizados["nombre"],
                        Sede.id_sede != objeto_db.id_sede,
                    )
                    .first()
                )
                if sede_existente:
                    print(
                        f"Error: Ya existe otra sede con el nombre '{datos_actualizados['nombre']}'"
                    )
                    return None

            datos_actualizados["actualizado_por"] = str(actualizado_por)

            for campo, valor in datos_actualizados.items():
                if hasattr(objeto_db, campo):
                    setattr(objeto_db, campo, valor)

            db.add(objeto_db)
            db.commit()
            db.refresh(objeto_db)
            return objeto_db

        except Exception as e:
            db.rollback()
            print(f"Error al actualizar sede: {str(e)}")
            return None

    def desactivar(
        self, db: Session, *, id: UUID, actualizado_por: UUID
    ) -> Optional[Sede]:
        """
        Desactiva una sede.

        Args:
            db: Sesión de base de datos
            id: ID de la sede a desactivar
            actualizado_por: ID del usuario que desactiva

        Returns:
            Optional[Sede]: La sede desactivada o None si hay error
        """
        try:
            sede = self.obtener_por_id(db, id)
            if not sede:
                print(f"Error: No se encontró la sede con ID {id}")
                return None

            sede.activo = False
            sede.actualizado_por = str(actualizado_por)
            db.add(sede)
            db.commit()
            db.refresh(sede)
            return sede

        except Exception as e:
            db.rollback()
            print(f"Error al desactivar sede: {str(e)}")
            return None

    def obtener_por_nombre(self, db: Session, nombre: str) -> Optional[Sede]:
        """
        Obtiene una sede por su nombre.

        Args:
            db: Sesión de base de datos
            nombre: Nombre de la sede

        Returns:
            Optional[Sede]: La sede encontrada o None si no existe
        """
        try:
            if not nombre or not nombre.strip():
                return None
            return (
                db.query(Sede).filter(Sede.nombre.ilike(f"%{nombre.strip()}%")).first()
            )
        except Exception as e:
            print(f"Error al obtener sede por nombre {nombre}: {str(e)}")
            return None


sede = SedeCRUD()
