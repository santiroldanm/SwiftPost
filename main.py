import os
from src.servicio_mensajeria import servicioMensajeria

def menu():
    print("\n" + "="*60)
    print("              SWIFTPOST - SISTEMA DE MENSAJERÍA              ")
    print("="*60)
    print("| 1 | Registrar cliente")
    print("| 2 | Enviar paquete")
    print("| 3 | Rastrear paquete")
    print("| 4 | Calcular costo de envío")
    print("| 5 | Listar paquetes")
    print("| 6 | Actualizar estado de paquete")
    print("| 7 | Salir")
    print("="*60)
    
def main() -> None:
    sistema: servicioMensajeria = servicioMensajeria()

    while True:
        menu()
        opcion = input("Seleccione una opción: \n")
#ACTUALIZAR EL MENÚ SEGÚN SE VAYAN CREANDO FUNCIONES
        if opcion == "1":
            limpiarConsola()
            sistema.crearCliente()
        
        elif opcion == "2":
            limpiarConsola()
            sistema.crearPaquete()        
        
        elif opcion == "3":
            limpiarConsola()
            sistema.rastrearPaquete()
  
        elif opcion == "4":
            limpiarConsola()
            sistema.calcularPrecioEnvio()
        
        elif opcion == "5":
            limpiarConsola()
            sistema.listarPaquetes()

        
        elif opcion == "6":
            limpiarConsola()
            sistema.actualizarEstadoPaquete()

         
        elif opcion == "7":
            limpiarConsola()
            print("¡Gracias por confiar en SwiftPost, nos vemos pronto! \n")
            break
        
        else:
            print("Opción no valida. Selecciona una opción correcta. \n")

def limpiarConsola():
    os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    main()