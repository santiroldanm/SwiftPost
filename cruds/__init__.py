"""
Paquete que contiene los módulos CRUD para interactuar con las entidades de la base de datos.
"""
from .cliente_crud import ClienteCRUD
from .empleado_crud import EmpleadoCRUD
from .paquete_crud import PaqueteCRUD
from .detalle_entrega_crud import DetalleEntregaCRUD
from .rol_crud import RolCRUD
from .sede_crud import SedeCRUD
from .tipo_documento_crud import TipoDocumentoCRUD
from .transporte_crud import TransporteCRUD
from .usuario_crud import UsuarioCRUD
__all__ = [
    'ClienteCRUD',
    'EmpleadoCRUD',
    'PaqueteCRUD',
    'DetalleEntregaCRUD',
    'RolCRUD',
    'SedeCRUD',
    'TipoDocumentoCRUD',
    'TransporteCRUD',
    'UsuarioCRUD',
]