import sys
import logging
from typing import Optional, Any
from sqlalchemy.orm import Session

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("swiftpost.log")],
)
logger = logging.getLogger(__name__)

# Importar configuración de la base de datos
from database.config import SessionLocal, create_tables
from scripts.init_roles import init_roles

# Importar los menús
from menus import menu_inicio, menu_cliente, menu_empleado, menu_admin
from menus.base import mostrar_encabezado, confirmar_accion


def main() -> None:
    """
    Función principal de la aplicación.
    Actúa como enrutador entre los diferentes menús según el rol del usuario.
    """
    # Configuración inicial
    try:
        # Crear tablas si no existen
        create_tables()

        # Inicializar roles si es necesario
        db_init = SessionLocal()
        try:
            init_roles(db_init)
            logger.info("Base de datos inicializada correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar roles: {str(e)}", exc_info=True)
            print(f"Error al inicializar la base de datos: {str(e)}")
            return
        finally:
            db_init.close()

    except Exception as e:
        logger.critical(
            f"Error crítico durante la inicialización: {str(e)}", exc_info=True
        )
        print(f"Error crítico: {str(e)}")
        return

    # Variable para controlar el bucle principal
    salir_aplicacion = False
    usuario_actual = None

    try:
        # Bucle principal de la aplicación
        while not salir_aplicacion:
            try:
                # Crear una nueva sesión para cada iteración
                db = SessionLocal()

                # Si no hay usuario autenticado, mostrar menú de inicio
                if not usuario_actual:
                    try:
                        usuario_actual, salir = menu_inicio(db)
                        if salir:
                            salir_aplicacion = True
                            continue
                    except Exception as e:
                        logger.error(
                            f"Error en menú de inicio: {str(e)}", exc_info=True
                        )
                        input(
                            "\nError en el menú de inicio. Presione Enter para continuar..."
                        )
                        continue
                else:
                    # Usuario autenticado - determinar rol y mostrar menú correspondiente
                    rol_nombre = ""  # Inicializar con valor por defecto
                    try:
                        # Obtener el rol del usuario
                        if hasattr(usuario_actual, "rol") and usuario_actual.rol:
                            rol_nombre = usuario_actual.rol.nombre_rol.lower()
                        else:
                            print("\n¡Error! No se pudo determinar el rol del usuario.")
                            usuario_actual = None
                            continue

                        # Enrutar al menú correspondiente según el rol
                        if rol_nombre == "administrador":
                            salir_sesion = menu_admin(db, usuario_actual)
                        elif rol_nombre == "empleado":
                            salir_sesion = menu_empleado(db, usuario_actual)
                        elif rol_nombre == "cliente":
                            salir_sesion = menu_cliente(db, usuario_actual)
                        else:
                            print(f"\n¡Error! Rol '{rol_nombre}' no reconocido.")
                            usuario_actual = None
                            continue

                        # Manejar cierre de sesión
                        if salir_sesion:
                            print("\nSesión cerrada correctamente.")
                            usuario_actual = None

                    except KeyboardInterrupt:
                        if confirmar_accion("\n¿Desea cerrar la aplicación? (s/n): "):
                            salir_aplicacion = True
                        continue
                    except Exception as e:
                        error_msg = f"Error en el menú"
                        if (
                            rol_nombre
                        ):  # Solo agregar el nombre del rol si está definido
                            error_msg += f" de {rol_nombre}"
                        logger.error(f"{error_msg}: {str(e)}", exc_info=True)
                        input("\nOcurrió un error. Presione Enter para continuar...")
                        continue

            except Exception as e:
                logger.error(f"Error en el bucle principal: {str(e)}", exc_info=True)
                input("\nOcurrió un error inesperado. Presione Enter para continuar...")

            finally:
                # Cerrar la sesión de la base de datos en cada iteración
                try:
                    if "db" in locals() and db is not None:
                        db.close()
                except Exception as e:
                    logger.error(
                        f"Error al cerrar la sesión de la base de datos: {str(e)}"
                    )

    except KeyboardInterrupt:
        print("\n\n¡Aplicación interrumpida por el usuario!")
        logger.info("Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.critical(f"Error crítico en la aplicación: {str(e)}", exc_info=True)
        print(f"\nError inesperado: {str(e)}")
    finally:
        print("\n¡Gracias por usar SwiftPost! ¡Hasta pronto!")
        logger.info("Aplicación finalizada")


if __name__ == "__main__":
    main()
