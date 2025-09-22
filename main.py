import os
import getpass
from cruds.usuario_crud import UsuarioCRUD
from entities.usuario import Usuario
from typing import Optional
from database.config import SessionLocal


class SwiftPost:
    def __init__(self):
        self.db = SessionLocal()
        self.usuario_crud = UsuarioCRUD(self.db)
        self.usuario_actual: Optional[Usuario] = None

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
                        "ERROR: El nombre de usuario es obligatorio", "error"
                    )
                    intentos += 1
                    continue

                contrasena = getpass.getpass("Contrasena: ")

                if not contrasena:
                    self.mostrar_mensaje("ERROR: La contrasena es obligatoria", "error")
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
            f"\nERROR: Maximo de intentos ({max_intentos}) excedido. Acceso denegado.",
            "error",
        )
        return False

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
    app = SwiftPost()
    try:
        app.login()
    finally:
        app.db.close()


if __name__ == "__main__":
    main()
