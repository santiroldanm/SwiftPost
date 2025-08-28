import os

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
    while True:
        menu()
        opcion = input("Seleccione una opción: ")

#ACTUALIZAR EL MENÚ SEGÚN SE VAYAN CREANDO FUNCIONES
        if opcion == "1":
            limpiarConsola()
            print("Seleccionaste Registrar Cliente")
        
        elif opcion == "2":
            limpiarConsola()
            print("Seleccionaste Enviar Paquete")
        
        elif opcion == "3":
            limpiarConsola()
            print("Seleccionaste Rastrear Paquete")
        
        elif opcion == "4":
            limpiarConsola()
            print("Seleccionaste Calcular Costo del Envío")
        
        elif opcion == "5":
            limpiarConsola()
            print("Seleccionaste Listar Paquetes")
        
        elif opcion == "6":
            limpiarConsola()
            print("Seleccionaste Actualizar Estado del Paquete")
        
        elif opcion == "7":
            limpiarConsola()
            print("Saliste del programa")
            break
        
        else:
            print("Opción no valida")

def limpiarConsola():
    os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    main()