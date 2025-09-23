"""
Paquete que contiene los módulos CRUD para interactuar con las entidades de la base de datos.
"""

# Importar las clases CRUD
from .cliente_crud import ClienteCRUD, cliente as cliente_crud
from .empleado_crud import EmpleadoCRUD, empleado as empleado_crud
from .paquete_crud import PaqueteCRUD, paquete as paquete_crud
from .detalle_entrega_crud import DetalleEntregaCRUD, detalle_entrega as detalle_entrega_crud
from .rol_crud import RolCRUD, rol as rol_crud
from .sede_crud import SedeCRUD, sede as sede_crud
from .tipo_documento_crud import TipoDocumentoCRUD, tipo_documento as tipo_documento_crud
from .transporte_crud import TransporteCRUD, transporte as transporte_crud
from .usuario_crud import UsuarioCRUD, usuario as usuario_crud

# Re-exportar las instancias con los nombres que espera el código existente
cliente = cliente_crud
empleado = empleado_crud
paquete = paquete_crud
detalle_entrega = detalle_entrega_crud
rol = rol_crud
sede = sede_crud
tipo_documento = tipo_documento_crud
transporte = transporte_crud
usuario = usuario_crud

# Exportar tanto las clases como las instancias
__all__ = [
    # Clases
    'ClienteCRUD',
    'EmpleadoCRUD',
    'PaqueteCRUD',
    'DetalleEntregaCRUD',
    'RolCRUD',
    'SedeCRUD',
    'TipoDocumentoCRUD',
    'TransporteCRUD',
    'UsuarioCRUD',
    
    # Instancias (nombres nuevos con _crud)
    'cliente_crud',
    'empleado_crud',
    'paquete_crud',
    'detalle_entrega_crud',
    'rol_crud',
    'sede_crud',
    'tipo_documento_crud',
    'transporte_crud',
    'usuario_crud',
    
    # Alias para compatibilidad con código existente
    'cliente',
    'empleado',
    'paquete',
    'detalle_entrega',
    'rol',
    'sede',
    'tipo_documento',
    'transporte',
    'usuario',
]
