# SwiftPost

## Descripción
**SwiftPost** es una aplicación de consola desarrollada en Python que simula un sistema de mensajería.  
El programa permite registrar clientes, gestionar paquetes, rastrear envíos y aplicar principios de programación orientada a objetos como **herencia** y **polimorfismo**.

## Propósito
El objetivo del proyecto es modelar el funcionamiento de un servicio de mensajería básico, mostrando cómo estructurar aplicaciones modulares en Python.  
También sirve como ejemplo educativo para reforzar conceptos de **POO** y **buenas prácticas de desarrollo**.

## Requisitos
- Python 3.10 o superior  
- No se requieren librerías externas, únicamente la librería estándar de Python.

## Funcionalidades
- Registro de clientes con sus datos básicos.  
- Creación y gestión de paquetes asociados a clientes.  
- Rastreo de paquetes mediante su ID.   
- Menús interactivos en consola para gestionar el sistema.

## Instalación
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/santiroldanm/SwiftPost
   ```
   
  2. Acceder al directorio del proyecto:
     ```bash
      cd SwiftPost
      ```
## Ejecución
Para iniciar la aplicación, ejecutar el archivo principal desde la terminal:
  ```bash
  py main.py
  ```

## Ejemplo de Uso
Al ejecutar el programa, se muestra un menú interactivo en consola donde se pueden realizar operaciones como:

1. Registrar un cliente.  
2. Registrar un paquete.  
3. Rastrear un paquete ingresando su ID.
4. Calcular el precio de un envío.
5. Listar Paquetes.
6. Actualizar el estado de un paquete.
7. Salir del sistema.  

El usuario debe seguir las instrucciones en pantalla para interactuar con el sistema.
  
## Estructura del Proyecto
  - main.py:
  Este es el punto de entrada de la aplicación. Se encarga de inicializar el sistema y coordinar las interacciones principales, como crear clientes, paquetes y utilizar el servicio de mensajería.

- src/:
Esta carpeta contiene todo el código fuente del proyecto. La modularización ayuda a mantener el código limpio, organizado y fácil de mantener.

- cliente.py: Define la clase Cliente, que modela a un usuario del servicio. Contiene atributos como nombre, teléfono y correo.

- paquete.py: Define la clase Paquete, que representa un objeto a ser enviado. Incluye detalles como peso, origen, destino y estado de entrega.

- servicio_mensajeria.py: Contiene la lógica principal del sistema. Aquí se gestionan las operaciones, como registrar clientes y paquetes, calcular costos de envio y actualizar el estado de las entregas.
