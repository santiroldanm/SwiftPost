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
    sistema = servicioMensajeria()

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
            print("Seleccionaste Rastrear Paquete \n")
 
        elif opcion == "4":
            limpiarConsola()
            sistema.calcularPrecioEnvio()
        
        elif opcion == "5":
            limpiarConsola()

            sistema.listarPaquetes()

            for i in sistema.paquetes:
             print(f" Id: {i.getId()} Id_dueño: {i.getId_propietario()} Origen: {i.getOrigen()} Destino:{i.getDestino()} Peso: {i.getPeso()} Estado: {i.getEstado()} Descripcion: {i.getDescripcion()} \n")        

        
        elif opcion == "6":
            limpiarConsola()
            sistema.actualizarEstadoPaquete()

            print("Seleccionaste Actualizar Estado del Paquete")
        
        elif opcion == "7":
            limpiarConsola()
            print("Saliste del programa \n")
            break
        
        else:
            print("Opción no valida \n")

def limpiarConsola():
    os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    main()