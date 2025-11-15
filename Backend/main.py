"""
SWIFTPOST - Sistema de Mensajería con ORM SQLAlchemy y Neon PostgreSQL
API REST con FastAPI - Sin interfaz de consola
"""

import uvicorn
from apis import (
    auth,
    usuario,
    cliente,
    empleado,
    sede,
    paquete,
    transporte,
    detalle_entrega,
    rol,
    tipo_documento,
)
from database.config import create_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SWIFTPOST - El Sistema #1 de Mensajería",
    description="API REST para gestionar clientes, empleados, paquetes, usuarios, etc",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(cliente.router)
app.include_router(empleado.router)
app.include_router(sede.router)
app.include_router(paquete.router)
app.include_router(transporte.router)
app.include_router(detalle_entrega.router)
app.include_router(rol.router)
app.include_router(tipo_documento.router)


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    print("Iniciando SWIFTPOST Sistema de Mensajería...")
    print("Configurando base de datos...")
    create_tables()
    print("Sistema SWIFTPOST listo para usar.")
    print("Documentación disponible en: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    print("Cerrando SWIFTPOST Sistema de Mensajería...")
    print("Sistema SWIFTPOST cerrado.")


@app.get("/", tags=["raíz"])
async def root():
    """Endpoint raíz que devuelve información básica de la API."""
    return {
        "mensaje": "Bienvenido a SWIFTPOST Sistema #1 de Mensajería",
        "version": "1.0.0",
        "documentacion": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "usuarios": "/usuarios",
            "clientes": "/clientes",
        },
    }


def main():
    """Función principal para ejecutar el servidor"""
    print("Iniciando servidor FastAPI...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()

