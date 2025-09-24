# SwiftPost - Sistema de Gestión de Mensajería

## 📋 Descripción
**SwiftPost** es un sistema de gestión de mensajería desarrollado en Python que permite administrar el ciclo completo de envíos de paquetes. Incluye módulos para la gestión de clientes, empleados, sedes, transportes y seguimiento de paquetes.

## 🎯 Propósito
El objetivo del proyecto es proporcionar una solución integral para la gestión de una empresa de mensajería, implementando buenas prácticas de desarrollo, arquitectura limpia y patrones de diseño.

## 🚀 Requisitos
- Python 3.10 o superior
- SQLAlchemy 2.0+
- Alembic (para migraciones de base de datos)
- Dependencias listadas en `requirements.txt`

## 🛠️ Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/santiroldanm/SwiftPost
   cd SwiftPost
   ```

2. Crear un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar la base de datos:
   ```bash
   alembic upgrade head
   ```

##  Ejecución

Para iniciar la aplicación:
```bash
python main.py
```

##  Estructura del Proyecto

```
SwiftPost/
├── alembic/               # Migraciones de base de datos
├── cruds/                 # Operaciones CRUD para cada entidad
│   ├── base_crud.py
│   ├── empleado_crud.py
│   ├── paquete_crud.py
│   └── sede_crud.py
│
├── database/              # Configuración de base de datos
│   ├── __init__.py
│   ├── base.py
│   ├── models.py
│   └── session.py
│
├── entities/              # Modelos Pydantic
│   ├── empleado.py
│   ├── paquete.py
│   └── sede.py
│
├── menus/                 # Interfaces de usuario en consola
│   ├── admin_menu.py
│   ├── empleado_menu.py
│   ├── main_menu.py
│   ├── paquete_menu.py
│   └── sede_menu.py
│
├── schemas/               # Esquemas SQLAlchemy
│   ├── empleado.py
│   ├── paquete.py
│   └── sede.py
│
├── .env.example          # Variables de entorno de ejemplo
├── alembic.ini          # Configuración de Alembic
├── main.py              # Punto de entrada de la aplicación
└── requirements.txt     # Dependencias del proyecto
```

## 📊 Lógica de Negocio

### Módulos Principales

1. **Gestión de Usuarios**
   - Autenticación y autorización
   - Roles: Administrador, Empleado, Cliente
   - Gestión de perfiles

2. **Gestión de Paquetes**
   - Registro de paquetes
   - Seguimiento en tiempo real
   - Actualización de estados
   - Cálculo de tarifas

3. **Gestión de Sedes**
   - Administración de ubicaciones
   - Control de inventario
   - Asignación de personal

4. **Gestión de Transporte**
   - Flota de vehículos
   - Rutas y horarios
   - Seguimiento GPS

### Flujo de Trabajo

1. **Recepción de Paquete**
   - Registro del paquete en el sistema
   - Asignación de número de seguimiento
   - Cálculo de tarifa

2. **Procesamiento**
   - Clasificación en la sede de origen
   - Asignación a ruta
   - Carga en vehículo

3. **Distribución**
   - Transporte a sede destino
   - Actualización de estado
   - Notificaciones al cliente

4. **Entrega**
   - Confirmación de recepción
   - Firma digital
   - Cierre del envío

## 📝 Ejemplo de Uso

1. Iniciar sesión con credenciales de administrador
2. Navegar por el menú principal
3. Gestionar empleados, sedes o paquetes
4. Realizar seguimiento de envíos
5. Generar reportes

## 🤝 Contribución

1. Hacer fork del proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Hacer commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Hacer push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
