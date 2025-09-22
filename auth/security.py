"""
Módulo de seguridad para manejo de contraseñas
"""

import hashlib
import secrets
from typing import Tuple


class Security:
    """Gestor de contraseñas con hash seguro"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Generar hash seguro de una contraseña

        Args:
            password: Contraseña en texto plano

        Returns:
            Hash de la contraseña con salt
        """
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return f"{salt}:{password_hash.hex()}"

    @staticmethod
    def verificar_contrasena(password_ingresada: str, password_almacenada: str) -> bool:
        """
        Verifica si la contraseña ingresada coincide con la almacenada

        Args:
            password_ingresada: Contraseña proporcionada por el usuario
            password_almacenada: Contraseña almacenada en la base de datos

        Returns:
            bool: True si las contraseñas coinciden, False en caso contrario
        """
        return secrets.compare_digest(password_ingresada, password_almacenada)

    @staticmethod
    def validar_contrasena(password: str) -> Tuple[bool, str]:
        """
        Validar la fortaleza de una contraseña

        Args:
            password: Contraseña a validar

        Returns:
            Tupla con (es_valida, mensaje)
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"

        if len(password) > 128:
            return False, "La contraseña no puede exceder 128 caracteres"

        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener al menos una letra mayúscula"

        if not any(c.islower() for c in password):
            return False, "La contraseña debe contener al menos una letra minúscula"

        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener al menos un número"

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "La contraseña debe contener al menos un carácter especial"

        return True, "Contraseña válida"

    @staticmethod
    def generar_contrasena_segura(length: int = 12) -> str:
        """
        Generar una contraseña segura aleatoria

        Args:
            length: Longitud de la contraseña

        Returns:
            Contraseña segura generada
        """
        import string

        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        password = "".join(secrets.choice(characters) for _ in range(length))
        return password
