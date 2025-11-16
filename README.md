# SwiftPost - Sistema de Gestión de Mensajería

## Descripción
SwiftPost es un sistema completo de gestión de mensajería con arquitectura cliente-servidor. Incluye una API REST desarrollada con FastAPI y SQLAlchemy para el backend, y una aplicación web moderna construida con Angular 20 para el frontend. El sistema permite administrar el ciclo completo de operaciones de una empresa de mensajería: clientes, empleados, sedes, transportes, paquetes y seguimiento de entregas.

## Características Principales

### Backend
- API REST con FastAPI y documentación automática (Swagger/ReDoc)
- Base de datos PostgreSQL con Neon
- ORM SQLAlchemy 2.0 con manejo de relaciones
- Sistema de autenticación y autorización
- Arquitectura limpia con separación de responsabilidades
- Migraciones de base de datos con Alembic
- Validaciones con Pydantic 2.0
- Soft delete en todas las entidades
- CORS configurado para desarrollo
- Módulo de analíticas con generación de reportes PDF
- Endpoints especializados para estadísticas y métricas

### Frontend
- Aplicación web con Angular 20
- Angular Material para componentes UI
- Gráficos interactivos con Chart.js y ng2-charts
- Routing con Angular Router
- Formularios reactivos con validaciones
- Diseño responsive y moderno
- Server-Side Rendering (SSR) con Angular Universal

## Tecnologías Utilizadas

### Backend
- Python 3.10+
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- PostgreSQL (Neon)
- Alembic 1.13.1
- Pydantic 2.5.0
- Uvicorn 0.24.0
- ReportLab 4.2.0 (generación de PDFs)

### Frontend
- Angular 20.3
- TypeScript 5.9
- Angular Material 20.2
- Chart.js 4.5
- RxJS 7.8
- Angular SSR

## Requisitos Previos
- Python 3.10 o superior
- Node.js 18+ y npm
- PostgreSQL o Neon Database
- pip (gestor de paquetes de Python)
- Git

## Instalación

### Backend

1. Clonar el repositorio:
```bash
git clone https://github.com/santiroldanm/SwiftPost
cd SwiftPost
```

2. Acceder al directorio del backend:
```bash
cd Backend
```

3. Crear y activar entorno virtual (recomendado):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r ../requirements.txt
```

5. Configurar variables de entorno:
Crear archivo `.env` en el directorio `Backend` con:
```
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/database
```

### Frontend

1. Acceder al directorio del frontend:
```bash
cd Frontend
```

2. Instalar dependencias:
```bash
npm install
```

## Ejecución

### Backend

Desde el directorio `Backend`:
```bash
python main.py
```

El servidor estará disponible en:
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc

### Frontend

Desde el directorio `Frontend`:
```bash
npm start
```

La aplicación web estará disponible en:
- http://localhost:4200

## Estructura del Proyecto
```text
SwiftPost/
├── Backend/                      # Servidor API REST
│   ├── apis/                     # Endpoints de la API REST
│   │   ├── auth.py              # Autenticación y tokens
│   │   ├── usuario.py           # Gestión de usuarios
│   │   ├── cliente.py           # Gestión de clientes
│   │   ├── empleado.py          # Gestión de empleados
│   │   ├── sede.py              # Gestión de sedes
│   │   ├── paquete.py           # Gestión de paquetes
│   │   ├── transporte.py        # Gestión de transportes
│   │   ├── detalle_entrega.py   # Gestión de entregas
│   │   ├── rol.py               # Gestión de roles
│   │   ├── tipo_documento.py    # Tipos de documento
│   │   └── analytics.py         # Analíticas y reportes
│   ├── auth/                    # Sistema de autenticación
│   │   └── security.py          # Funciones de seguridad
│   ├── cruds/                   # Operaciones CRUD
│   │   ├── base_crud.py         # CRUD base genérico
│   │   ├── usuario_crud.py
│   │   ├── cliente_crud.py
│   │   ├── empleado_crud.py
│   │   ├── sede_crud.py
│   │   ├── paquete_crud.py
│   │   ├── transporte_crud.py
│   │   ├── detalle_entrega_crud.py
│   │   ├── rol_crud.py
│   │   └── tipo_documento_crud.py
│   ├── entities/                # Modelos de base de datos
│   │   ├── usuario.py
│   │   ├── cliente.py
│   │   ├── empleado.py
│   │   ├── sede.py
│   │   ├── paquete.py
│   │   ├── transporte.py
│   │   ├── detalle_entrega.py
│   │   ├── rol.py
│   │   └── tipo_documento.py
│   ├── schemas/                 # Schemas de Pydantic
│   │   ├── auth_schema.py
│   │   ├── usuario_schema.py
│   │   ├── cliente_schema.py
│   │   ├── empleado_schema.py
│   │   ├── sede_schema.py
│   │   ├── paquete_schema.py
│   │   ├── transporte_schema.py
│   │   ├── detalle_entrega_schema.py
│   │   ├── rol_schema.py
│   │   └── tipo_documento_schema.py
│   ├── database/                # Configuración de base de datos
│   │   └── config.py
│   ├── migrations/              # Migraciones de Alembic
│   ├── menus/                   # Menús del sistema (legacy)
│   ├── scripts/                 # Scripts auxiliares
│   ├── services/                # Servicios de negocio
│   ├── .env                     # Variables de entorno
│   └── main.py                  # Punto de entrada de la API
├── Frontend/                     # Aplicación web Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/            # Servicios core y guards
│   │   │   ├── features/        # Módulos de funcionalidades
│   │   │   ├── shared/          # Componentes compartidos
│   │   │   ├── app.routes.ts    # Configuración de rutas
│   │   │   └── app.ts           # Componente principal
│   │   ├── environments/        # Configuración de entornos
│   │   ├── index.html
│   │   ├── main.ts
│   │   └── styles.css
│   ├── angular.json             # Configuración de Angular
│   ├── package.json             # Dependencias de Node
│   └── tsconfig.json            # Configuración de TypeScript
├── requirements.txt              # Dependencias de Python
└── README.md                     # Este archivo
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

### 11. Analíticas
- GET /analytics/paquetes-ultimos-30-dias - Estadísticas de paquetes por día
- GET /analytics/sedes-mas-activas - Sedes con mayor actividad
- GET /analytics/reporte-pdf - Generar reporte en PDF

## Arquitectura

### Arquitectura General
El proyecto implementa una arquitectura cliente-servidor con separación clara entre frontend y backend:

**Backend (FastAPI)**
- Arquitectura en capas con separación de responsabilidades
- API RESTful con documentación automática
- Comunicación mediante JSON

**Frontend (Angular)**
- Arquitectura basada en componentes
- Servicios para comunicación con API
- Guards para protección de rutas
- Módulos organizados por funcionalidades

### Patrón de Diseño Backend
El backend implementa una arquitectura en capas:

1. **Capa de Presentación (APIs)**: Endpoints REST con FastAPI
2. **Capa de Negocio (CRUDs)**: Lógica de negocio y operaciones
3. **Capa de Acceso a Datos (Entities)**: Modelos SQLAlchemy
4. **Capa de Validación (Schemas)**: Validación con Pydantic

### Características de Implementación

**Backend:**
- CRUD Base genérico para reutilización de código
- Soft delete en todas las entidades principales
- Validaciones exhaustivas con Pydantic
- Manejo de relaciones entre entidades
- Paginación en listados
- Timestamps automáticos (creado/actualizado)
- Auditoría de cambios (creado_por/actualizado_por)
- Generación de reportes PDF con ReportLab
- Endpoints de analíticas para dashboards

**Frontend:**
- Arquitectura modular con lazy loading
- Componentes reutilizables con Angular Material
- Servicios HTTP para consumo de API
- Guards de autenticación y autorización
- Formularios reactivos con validaciones
- Gráficos interactivos con Chart.js
- Diseño responsive con CSS moderno

## Funcionalidades del Sistema

### Gestión de Entidades
- **Clientes**: Registro, actualización y consulta de clientes
- **Empleados**: Administración de personal de la empresa
- **Sedes**: Gestión de sucursales y ubicaciones
- **Transportes**: Control de vehículos y medios de transporte
- **Paquetes**: Registro y seguimiento de envíos
- **Detalles de Entrega**: Historial completo de entregas

### Seguridad
- Autenticación de usuarios con tokens
- Control de acceso basado en roles
- Protección de rutas en frontend
- Validación de datos en backend y frontend

### Analíticas y Reportes
- Dashboard con estadísticas en tiempo real
- Gráficos de paquetes enviados por período
- Análisis de sedes más activas
- Generación de reportes en PDF
- Métricas de rendimiento del sistema

### Interfaz de Usuario
- Diseño moderno y responsive
- Navegación intuitiva
- Formularios con validación en tiempo real
- Tablas con paginación y búsqueda
- Notificaciones y feedback visual

## Desarrollo

### Scripts Disponibles

**Backend:**
```bash
# Iniciar servidor de desarrollo
python main.py

# Crear migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

**Frontend:**
```bash
# Servidor de desarrollo
npm start

# Build de producción
npm run build

# Ejecutar tests
npm test

# Linting
ng lint
```

## Configuración Adicional

### Variables de Entorno (Backend)
El archivo `.env` en el directorio `Backend` debe contener:
```env
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/database
SECRET_KEY=tu_clave_secreta_para_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Configuración del Frontend
El archivo `src/environments/environment.ts` debe configurarse con la URL del backend:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

## Base de Datos

### Modelo de Datos
El sistema maneja las siguientes entidades principales:
- **Usuario**: Credenciales y perfiles de acceso
- **Rol**: Roles y permisos del sistema
- **TipoDocumento**: Tipos de identificación
- **Cliente**: Información de clientes
- **Empleado**: Datos del personal
- **Sede**: Sucursales de la empresa
- **Transporte**: Vehículos y medios de transporte
- **Paquete**: Información de envíos
- **DetalleEntrega**: Registro de entregas realizadas

### Relaciones
- Un cliente puede tener múltiples paquetes
- Un paquete tiene un detalle de entrega
- Una sede puede ser origen o destino de entregas
- Un empleado puede gestionar múltiples entregas
- Un transporte puede realizar múltiples entregas

## Notas Importantes

- El backend debe estar ejecutándose antes de iniciar el frontend
- Asegúrate de tener configurada correctamente la base de datos PostgreSQL
- Las migraciones se ejecutan automáticamente al iniciar el backend
- El sistema usa soft delete, por lo que los registros no se eliminan físicamente
- Los tokens JWT expiran según la configuración en las variables de entorno
- CORS está configurado para permitir todas las conexiones en desarrollo

## Contribución

Este es un proyecto académico. Para contribuir:
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## Autores
- Santiago Roldán Muñoz
- Emmanuel Pérez Vivas
- Jeison Olaya 

## Licencia
Este proyecto es de uso académico.
