import os
import getpass
from cruds.usuario_crud import UsuarioCRUD
from entities.usuario import Usuario
from typing import Optional
from database.config import SessionLocal, create_tables
from menus.admin_menu import AdminMenu
from menus.empleado_menu import EmpleadoMenu
from menus.cliente_menu import ClienteMenu


class SwiftPost:
    def __init__(self):
        self.db = None
        self.usuario_crud = None
        self.usuario_actual: Optional[Usuario] = None

    def __enter__(self):
        self.db = SessionLocal()
        self.usuario_crud = UsuarioCRUD(self.db)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()

    def login(self):
        self.limpiarConsola()
        print("\n" + "=" * 50)
        print("\033[1;34m" + "SWIFTPOST".center(50) + "\033[0m")
        print("El Sistema de Mensajería #1 a nivel mundial".center(50))
        print("=" * 50)
        print("\n" + "INICIO DE SESIÓN".center(50) + "\n")
        print("-" * 50)

        intentos = 0
        max_intentos = 3

        while intentos < max_intentos:
            try:
                self.mostrar_mensaje(
                    f"Intento {intentos + 1} de {max_intentos}", "info"
                )

                nombre_usuario = input("Usuario: ").strip()

                if not nombre_usuario:
                    self.mostrar_mensaje(
                        "ADVERTENCIA: El nombre de usuario es obligatorio",
                        "advertencia",
                    )
                    intentos += 1
                    continue

                contrasena = getpass.getpass("Contrasena: ")

                if not contrasena:
                    self.mostrar_mensaje(
                        "ADVERTENCIA: La contrasena es obligatoria", "advertencia"
                    )
                    intentos += 1
                    continue

                usuario = self.usuario_crud.autenticar(nombre_usuario, contrasena)

                if usuario is not None:
                    self.usuario_actual = usuario
                    self.mostrar_mensaje(
                        f"\nEXITO: ¡Bienvenido, {usuario.primer_nombre} {usuario.primer_apellido}!",
                        "exito",
                    )
                    if self.usuario_crud.es_admin(self.usuario_actual):
                        self.mostrar_mensaje(
                            "INFO: Tienes privilegios de administrador", "info"
                        )
                    return True
                else:
                    self.mostrar_mensaje(
                        "ERROR: Credenciales incorrectas o usuario inactivo", "error"
                    )
                    intentos += 1

            except KeyboardInterrupt:
                self.mostrar_mensaje(
                    "\n\nINFO: Operacion cancelada por el usuario", "info"
                )
                return False
            except Exception as e:
                self.mostrar_mensaje(f"ERROR: Error durante el login: {e}", "error")
                intentos += 1

        self.mostrar_mensaje(
            f"\nERROR: Maximo de intentos ({max_intentos}) excedido.",
            "error",
        )
        return False

    def ejecutar(self) -> None:
        try:
            self.mostrar_mensaje("INICIANDO SWIFTPOST...", "info")
            self.mostrar_mensaje("Conectando y configurando base de datos...", "info")

            if not self.db:
                self.db = SessionLocal()
                self.usuario_crud = UsuarioCRUD(self.db)

            create_tables()
            self.mostrar_mensaje("SWIFTPOST LISTO PARA USAR", "exito")

            if not self.login():
                self.mostrar_mensaje("ERROR: Acceso denegado", "error")
                return

            if not hasattr(self, "usuario_actual") or not self.usuario_actual:
                self.mostrar_mensaje(
                    "ERROR: No se pudo obtener la información del usuario.", "error"
                )
                return

            if self.usuario_crud.es_admin(self.usuario_actual):
                menu = AdminMenu(db=self.db, usuario_actual=self.usuario_actual)
            elif self.usuario_crud.es_empleado(self.usuario_actual):
                menu = EmpleadoMenu(self.db)
            else:
                menu = ClienteMenu(self.db)

            menu.mostrar_menu()

        except KeyboardInterrupt:
            self.mostrar_mensaje("\n\nSistema interrumpido por el usuario.", "error")
        except Exception as e:
            self.mostrar_mensaje(f"\nError crítico: {e}", "error")

    def mostrar_mensaje(self, mensaje, tipo="info"):
        """Muestra un mensaje formateado según su tipo

        Args:
            mensaje: El mensaje a mostrar
            tipo: El tipo de mensaje (info(azul), exito(verde), advertencia(amarillo), error(rojo))
        """
        colores = {
            "info": "\033[94m",
            "exito": "\033[92m",
            "advertencia": "\033[93m",
            "error": "\033[91m",
            "reset": "\033[0m",
        }
        print(f"{colores.get(tipo, '')}{mensaje}{colores['reset']}")

    @staticmethod
    def limpiarConsola():
        os.system("cls" if os.name == "nt" else "clear")


def main():
    with SwiftPost() as sistema:
        sistema.ejecutar()


if __name__ == "__main__":
    main()
