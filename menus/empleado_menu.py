# menus/empleado_menu.py
class EmpleadoMenu:
    def __init__(self, db):
        self.db = db

    def mostrar_menu(self):
        while True:
            print("\n" + "=" * 50)
            print("MENÚ EMPLEADO".center(50))
            print("=" * 50)
            print("1. Gestionar Pedidos")
            print("2. Ver Inventario")
            print("3. Reportar Problemas")
            print("4. Mi Perfil")
            print("0. Cerrar Sesión")

            opcion = input("\nSeleccione una opción: ").strip()

            if opcion == "0":
                print("\nCerrando sesión de empleado...")
                break
            # Add other options handling here
