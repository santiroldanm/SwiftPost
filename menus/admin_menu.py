from src.admin_accion import AdminAcciones
from sqlalchemy.orm import Session


class AdminMenu:
    def __init__(self, db: Session, usuario_actual):
        self.db = db
        self.usuario_actual = usuario_actual

    def mostrar_menu(self):
        admin = AdminAcciones(db=self.db)
        admin.usuario_actual = self.usuario_actual
        while True:
            print("\n" + "=" * 50)
            print("MENÚ ADMINISTRADOR".center(50))
            print("=" * 50)
            print("1. Gestión de Empleados")
            print("2. Gestión de Sucursales")
            print("3. Gestión de Transportes")
            print("4. Estadísticas Generales")
            print("5. Mi Perfil")
            print("0. Cerrar Sesión")

            opcion = int(input("\nSeleccione una opción: ").strip())

            if opcion == 1:
                admin.gestionar_empleados()
            elif opcion == 2:
                admin.gestionar_sucursales()
            elif opcion == 3:
                admin.gestionar_transportes()
            elif opcion == 4:
                admin.estadisticas_generales()
            elif opcion == 5:
                admin.perfil()
            elif opcion == 0:
                break
