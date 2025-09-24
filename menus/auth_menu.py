"""
Módulo para manejar la autenticación de usuarios (inicio de sesión y registro).
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from getpass import getpass

from auth.security import autenticar_usuario as authenticate_user
from cruds.usuario_crud import usuario as usuario_crud
from cruds.cliente_crud import cliente as cliente_crud
from cruds.tipo_documento_crud import tipo_documento as tipo_documento_crud
from entities.usuario import UsuarioCreate
from entities.cliente import ClienteCreate
from auth.security import obtener_id_rol

def mostrar_encabezado(titulo: str = ""):
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 60)
    if titulo:
        print(f"{titulo:^60}")
        print("=" * 60)

def iniciar_sesion(db: Session) -> Optional[Dict[str, Any]]:
    """Maneja el proceso de inicio de sesión."""
    mostrar_encabezado("INICIAR SESIÓN")
    username = input("Nombre de usuario: ")
    password = getpass("Contraseña: ")
    
    user_data = authenticate_user(db, nombre_usuario=username, contraseña=password)
    if not user_data:
        print("\nError: Usuario o contraseña incorrectos.")
        input("Presione Enter para continuar...")
        return None
    
    if not user_data.get('activo', False):
        print("\nError: Este usuario está inactivo.")
        input("Presione Enter para continuar...")
        return None
    
    rol_nombre = user_data.get('rol_nombre', 'cliente')
    print(f"\n¡Bienvenido, {user_data['nombre_usuario']}! (Rol: {rol_nombre.capitalize()})")
    return user_data

def registrar_usuario(db: Session) -> None:
    """Maneja el registro de nuevos clientes."""
    mostrar_encabezado("REGISTRAR NUEVO CLIENTE")
    rol_id = obtener_id_rol(db, 'cliente')
    
    if not rol_id:
        print("\nError: No se pudo determinar el rol del usuario.")
        input("Presione Enter para continuar...")
        return
    
    print("\nPor favor ingrese los siguientes datos:")
    username = input("Nombre de usuario: ")
    
    if usuario_crud.obtener_por_nombre_usuario(db, nombre_usuario=username):
        print("\nError: El nombre de usuario ya está en uso.")
        input("Presione Enter para continuar...")
        return
    
    password = getpass("Contraseña: ")
    confirm_password = getpass("Confirmar contraseña: ")
    
    if password != confirm_password:
        print("\nError: Las contraseñas no coinciden.")
        input("Presione Enter para continuar...")
        return
    
    usuario_in = UsuarioCreate(
        nombre_usuario=username,
        password=password,
        id_rol=rol_id
    )
    
    try:
        usuario = usuario_crud.crear_usuario(db, datos_usuario=usuario_in)
        
        print("\nPor favor ingrese los datos del cliente:")
        print("-" * 40)
        
        primer_nombre = input("Primer nombre: ").strip()
        segundo_nombre = input("Segundo nombre (opcional): ").strip() or None
        primer_apellido = input("Primer apellido: ").strip()
        segundo_apellido = input("Segundo apellido (opcional): ").strip() or None
        
        if not primer_nombre or not primer_apellido:
            print("\nError: El primer nombre y el primer apellido son obligatorios.")
            db.rollback()
            input("Presione Enter para continuar...")
            return
            
        tipos_documento = tipo_documento_crud.obtener_activos(db)
        if not tipos_documento:
            print("\nError: No hay tipos de documento disponibles.")
            db.rollback()
            input("Presione Enter para continuar...")
            return
            
        print("\nTipos de documento disponibles:")
        for i, tipo in enumerate(tipos_documento, 1):
            print(f"{i}. {tipo.nombre.upper()} ({tipo.codigo.upper()})")
        
        id_tipo_documento = None
        while True:
            try:
                opcion = int(input("\nSeleccione el número del tipo de documento: ").strip())
                if 1 <= opcion <= len(tipos_documento):
                    id_tipo_documento = tipos_documento[opcion-1].id_tipo_documento
                    break
                print(f"Error: Ingrese un número entre 1 y {len(tipos_documento)}")
            except ValueError:
                print("Error: Ingrese un número válido")
        
        numero_documento = input("Número de documento: ").strip()
        if cliente_crud.obtener_por_documento(db, numero_documento):
            print(f"\nError: Ya existe un cliente con el documento {numero_documento}")
            db.rollback()
            input("Presione Enter para continuar...")
            return
            
        correo = input("Correo electrónico: ").strip().lower()
        if cliente_crud.obtener_por_email(db, correo):
            print(f"\nError: Ya existe un cliente con el correo {correo}")
            db.rollback()
            input("Presione Enter para continuar...")
            return
        
        direccion = input("Dirección: ").strip()
        telefono = input("Teléfono: ").strip()

        cliente_data = ClienteCreate(
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            numero_documento=numero_documento,
            direccion=direccion,
            telefono=telefono,
            correo=correo,
            tipo='remitente', # Por defecto
            id_tipo_documento=str(id_tipo_documento),
            usuario_id=str(usuario.id_usuario)
        )
        
        cliente_crud.crear(db, datos_entrada=cliente_data, usuario_id=usuario.id_usuario)
        db.commit()
        print(f"\n¡Cliente {usuario.nombre_usuario} registrado exitosamente!")
        
    except Exception as e:
        db.rollback()
        print(f"\nError al crear el usuario: {str(e)}")
    
    input("\nPresione Enter para continuar...")
