"""
Modelos Pydantic para las respuestas de autenticación de la API
"""

from pydantic import BaseModel
from typing import Optional


class RespuestaAPI(BaseModel):
    mensaje: str
    exito: bool = True
    datos: Optional[dict] = None


class RespuestaError(BaseModel):
    mensaje: str
    exito: bool = False
    error: str
    codigo: int
