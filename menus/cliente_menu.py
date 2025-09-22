# menus/cliente_menu.py
class ClienteMenu:
    def __init__(self, db):
        self.db = db

    def mostrar_menu(self):
        while True:
            print("\n" + "=" * 50)
            print("MENÚ CLIENTE".center(50))
            print("=" * 50)
            print("1. Ver Productos")
            print("2. Realizar Pedido")
            print("3. Ver Mis Pedidos")
            print("4. Mi Perfil")
            print("0. Cerrar Sesión")

            opcion = input("\nSeleccione una opción: ").strip()

            if opcion == "0":
                print("\nGracias por su visita. ¡Vuelva pronto!")
                break
            # Add other options handling here
