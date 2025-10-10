# SwiftPost - Sistema de Gestión de Mensajería

## Descripción
SwiftPost es una API REST desarrollada con FastAPI y SQLAlchemy que permite administrar el ciclo completo de operaciones de una empresa de mensajería. El sistema gestiona clientes, empleados, sedes, transportes, paquetes y seguimiento de entregas mediante una arquitectura limpia y escalable.

## Características Principales
- API REST con FastAPI y documentación automática
- Base de datos PostgreSQL con Neon
- ORM SQLAlchemy 2.0 con manejo de relaciones
- Sistema de autenticación y autorización
- Arquitectura limpia con separación de responsabilidades
- Migraciones de base de datos con Alembic
- Validaciones con Pydantic 2.0
- Soft delete en todas las entidades
- CORS configurado para desarrollo

## Tecnologías Utilizadas
- Python 3.10+
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- PostgreSQL (Neon)
- Alembic 1.13.1
- Pydantic 2.5.0
- Uvicorn 0.24.0

## Requisitos Previos
- Python 3.10 o superior
- PostgreSQL o Neon Database
- pip (gestor de paquetes de Python)
- Git

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/santiroldanm/SwiftPost
```

2. Acceder al directorio del proyecto:
```bash
cd SwiftPost
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

Iniciar el servidor de desarrollo:
```bash
python main.py
```

El servidor estará disponible en:
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc

## Estructura del Proyecto
```text
SwiftPost/
├── apis/                  # Endpoints de la API REST
│   ├── auth.py           # Autenticación y tokens
│   ├── usuario.py        # Gestión de usuarios
│   ├── cliente.py        # Gestión de clientes
│   ├── empleado.py       # Gestión de empleados
│   ├── sede.py           # Gestión de sedes
│   ├── paquete.py        # Gestión de paquetes
│   ├── transporte.py     # Gestión de transportes
│   ├── detalle_entrega.py # Gestión de entregas
│   ├── rol.py            # Gestión de roles
│   └── tipo_documento.py # Tipos de documento
├── auth/                 # Sistema de autenticación
│   └── security.py       # Funciones de seguridad
├── cruds/                # Operaciones CRUD
│   ├── base_crud.py      # CRUD base genérico
│   ├── usuario_crud.py
│   ├── cliente_crud.py
│   ├── empleado_crud.py
│   ├── sede_crud.py
│   ├── paquete_crud.py
│   ├── transporte_crud.py
│   ├── detalle_entrega_crud.py
│   ├── rol_crud.py
│   └── tipo_documento_crud.py
├── entities/             # Modelos de base de datos
│   ├── usuario.py
│   ├── cliente.py
│   ├── empleado.py
│   ├── sede.py
│   ├── paquete.py
│   ├── transporte.py
│   ├── detalle_entrega.py
│   ├── rol.py
│   └── tipo_documento.py
├── schemas/              # Schemas de Pydantic
│   ├── auth_schema.py
│   ├── usuario_schema.py
│   ├── cliente_schema.py
│   ├── empleado_schema.py
│   ├── sede_schema.py
│   ├── paquete_schema.py
│   ├── transporte_schema.py
│   ├── detalle_entrega_schema.py
│   ├── rol_schema.py
│   └── tipo_documento_schema.py
├── database/             # Configuración de base de datos
│   └── config.py
├── migrations/           # Migraciones de Alembic
├── scripts/              # Scripts auxiliares
├── .env                  # Variables de entorno
├── alembic.ini          # Configuración de Alembic
├── main.py              # Punto de entrada de la aplicación
└── requirements.txt     # Dependencias del proyecto
```

## Módulos de la API

### 1. Autenticación (auth)
- POST /auth/login - Iniciar sesión
- POST /auth/register - Registrar usuario
- POST /auth/refresh - Refrescar token

### 2. Usuarios
- GET /usuarios - Listar usuarios
- GET /usuarios/{id} - Obtener usuario por ID
- POST /usuarios - Crear usuario
- PUT /usuarios/{id} - Actualizar usuario
- DELETE /usuarios/{id} - Eliminar usuario (soft delete)

### 3. Clientes
- GET /clientes - Listar clientes
- GET /clientes/{id} - Obtener cliente por ID
- POST /clientes - Crear cliente
- PUT /clientes/{id} - Actualizar cliente
- DELETE /clientes/{id} - Eliminar cliente

### 4. Empleados
- GET /empleados - Listar empleados
- GET /empleados/{id} - Obtener empleado por ID
- POST /empleados - Crear empleado
- PUT /empleados/{id} - Actualizar empleado
- DELETE /empleados/{id} - Eliminar empleado

### 5. Sedes
- GET /sedes - Listar sedes
- GET /sedes/{id} - Obtener sede por ID
- POST /sedes - Crear sede
- PUT /sedes/{id} - Actualizar sede
- DELETE /sedes/{id} - Eliminar sede

### 6. Paquetes
- GET /paquetes - Listar paquetes
- GET /paquetes/{id} - Obtener paquete por ID
- POST /paquetes - Crear paquete
- PUT /paquetes/{id} - Actualizar paquete
- DELETE /paquetes/{id} - Eliminar paquete

### 7. Transportes
- GET /transportes - Listar transportes
- GET /transportes/{id} - Obtener transporte por ID
- POST /transportes - Crear transporte
- PUT /transportes/{id} - Actualizar transporte
- DELETE /transportes/{id} - Eliminar transporte

### 8. Detalles de Entrega
- GET /detalles-entrega - Listar entregas
- GET /detalles-entrega/{id} - Obtener entrega por ID
- GET /detalles-entrega/pendientes - Entregas pendientes
- GET /detalles-entrega/cliente/{id} - Entregas por cliente
- GET /detalles-entrega/paquete/{id} - Entrega por paquete
- POST /detalles-entrega - Crear entrega
- PUT /detalles-entrega/{id} - Actualizar entrega
- DELETE /detalles-entrega/{id} - Eliminar entrega

### 9. Roles
- GET /roles - Listar roles
- GET /roles/{id} - Obtener rol por ID
- POST /roles - Crear rol
- PUT /roles/{id} - Actualizar rol
- DELETE /roles/{id} - Eliminar rol

### 10. Tipos de Documento
- GET /tipos-documento - Listar tipos
- GET /tipos-documento/{id} - Obtener tipo por ID
- GET /tipos-documento/codigo/{codigo} - Obtener por código
- POST /tipos-documento - Crear tipo
- PUT /tipos-documento/{id} - Actualizar tipo
- DELETE /tipos-documento/{id} - Eliminar tipo

## Arquitectura

### Patrón de Diseño
El proyecto implementa una arquitectura en capas:

1. Capa de Presentación (APIs): Endpoints REST con FastAPI
2. Capa de Negocio (CRUDs): Lógica de negocio y operaciones
3. Capa de Acceso a Datos (Entities): Modelos SQLAlchemy
4. Capa de Validación (Schemas): Validación con Pydantic

### Características de Implementación
- CRUD Base genérico para reutilización de código
- Soft delete en todas las entidades principales
- Validaciones exhaustivas con Pydantic
- Manejo de relaciones entre entidades
- Paginación en listados
- Timestamps automáticos (creado/actualizado)
- Auditoría de cambios (creado_por/actualizado_por)


## Autores
- Santiago Roldán Muñoz
- Emmanuel Pérez Vivas
- Jeison Olaya 

## Licencia
Este proyecto es de uso académico.
