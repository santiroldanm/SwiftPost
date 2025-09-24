import math
import re
from src.cliente import cliente
from src.cliente import cliente_vip
from src.paquete import paquete
from src.paquete import paquete_express


class servicioMensajeria:
    def __init__(self):

        self.__paquetes: list[paquete] = []
        self.__clientes: list[cliente] = []
        self.__ciudades: dict = {
            "Bogota": (4.711, -74.072, 2582),
            "Medellin": (6.244, -75.581, 1495),
            "Cali": (3.452, -76.532, 1018),
            "Cartagena": (10.391, -75.479, 2),
            "Barranquilla": (10.991, -74.788, 10),
            "Santa marta": (11.241, -74.199, 0),
            "Bucaramanga": (7.120, -73.123, 960),
            "Cúcuta": (7.889, -72.496, 320),
            "Pereira": (4.815, -75.695, 1411),
            "Manizales": (5.069, -75.517, 2150),
            "Pasto": (1.216, -77.281, 2527),
            "Ibague": (4.439, -75.232, 1285),
            "Villavicencio": (4.142, -73.626, 467),
            "Armenia": (4.534, -75.681, 1480),
            "Nueva York": (40.713, -74.006, 10),
            "Paris": (48.857, 2.352, 35),
            "Londres": (51.507, -0.128, 11),
            "Tokio": (35.690, 139.692, 40),
            "Sídney": (-33.869, 151.209, 58),
            "Roma": (41.903, 12.496, 21),
            "Berlin": (52.520, 13.405, 34),
            "Dubái": (25.277, 55.296, -2),
            "Pekin": (39.904, 116.407, 44),
            "Moscu": (55.756, 37.617, 156),
            "Ciudad de mexico": (19.433, -99.133, 2240),
            "Buenos aires": (-34.604, -58.382, 25),
            "Toronto": (43.653, -79.383, 76),
            "Estambul": (41.008, 28.978, 39),
            "Johannesburgo": (-26.204, 28.047, 1753),
        }

    def crearCliente(self) -> None:
        print("\n=== REGISTRO DE CLIENTE ===\n")

        while True:

            nombre = input("Ingrese su nombre: Juan \n")

            patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$"

            if re.match(patron, nombre):
                break
            else:
                print("Nombre inválido   \n ")

        while True:
            apellido = input("Ingrese su apellido: Pérez \n").strip()
            if re.match(patron, apellido):
                break
            else:
                print("Apellido inválido   \n ")

        while True:
            telefono: str = input("Ingrese su número telefónico: ").strip()
            if not telefono.isdigit():
                print("Número telefónico no válido. Debe contener solo dígitos.\n")
            elif len(telefono) < 6:
                print("Número telefónico no válido. Mínimo debe contener 6 dígitos \n")
            else:
                break

        correo: str = ""
        while True:
            correo = input("Ingrese su correo electrónico: ").strip()
            if correo and "@" in correo and "." in correo:
                break
            else:
                print("Correo electrónico no válido. Intente nuevamente.\n")

        tipo = input("¿El cliente es VIP? (s/n): ").strip().lower()

        if tipo == "s":
            Cliente = cliente_vip(
                len(self.__clientes) + 1,
                nombre,
                apellido,
                "",
                telefono,
                correo,
                descuento=0.15,
            )
            print("\nCliente VIP registrado con éxito.")
            print(
                f"ID: {Cliente.getId()} | Nombre: {Cliente.getNombre()} {Cliente.getApellido()}"
            )
            print("Beneficio: 10% de descuento")
        else:
            Cliente = cliente(
                len(self.__clientes) + 1, nombre, apellido, "", telefono, correo
            )
            print("\nCliente registrado con éxito.")
            print(
                f"ID: {Cliente.getId()} | Nombre: {Cliente.getNombre()} {Cliente.getApellido()}"
            )

        self.__clientes.append(Cliente)
        print("\n=============================\n")

    def crearPaquete(self) -> str:
        print("\n=== REGISTRO DE PAQUETE ===\n")

        if len(self.__clientes) == 0:
            print(
                "No hay clientes registrados. Registre un cliente antes de crear un paquete.\n"
            )
            return
        else:
            ids = [cliente.getId() for cliente in self.__clientes]

            while True:
                print("Clientes registrados:")
                for cliente in self.__clientes:
                    print(
                        f"ID: {cliente.getId()} | Nombre: {cliente.getNombre()} {cliente.getApellido()}"
                    )

                seleccion = input("\nSeleccione un cliente por su ID: ").strip()

                if seleccion.isdigit() and int(seleccion) in ids:
                    cliente_seleccionado = None
                    for cliente in self.__clientes:
                        if cliente.getId() == int(seleccion):
                            cliente_seleccionado = cliente
                            break

                    if cliente_seleccionado:
                        tamaño: str = ""
                        while True:
                            opcion = input(
                                "\nSeleccione el tamaño del paquete:\n"
                                "1. Pequeño: máx. tamaño de caja de cereales grande\n"
                                "2. Mediano: máx. tamaño de un televisor pequeño\n"
                                "3. Grande: máx. tamaño de un televisor de 50'' o lavadora pequeña\n"
                                "4. Gigante\n"
                                "Opción: "
                            ).strip()
                            if opcion == "1":
                                tamaño = "pequeño"
                                break
                            elif opcion == "2":
                                tamaño = "mediano"
                                break
                            elif opcion == "3":
                                tamaño = "grande"
                                break
                            elif opcion == "4":
                                tamaño = "gigante"
                                break
                            else:
                                print("Opción no válida. Intente nuevamente.\n")

                        fragilidad: str = ""
                        indiceFragilidad: float = 0
                        while True:
                            opcion = input(
                                "\nSeleccione el nivel de fragilidad:\n"
                                "1. Alta\n"
                                "2. Normal\n"
                                "3. Baja\n"
                                "Opción: "
                            ).strip()
                            if opcion == "1":
                                fragilidad = "alta"
                                indiceFragilidad = 1.05
                                break
                            elif opcion == "2":
                                fragilidad = "normal"
                                indiceFragilidad = 1.0
                                break
                            elif opcion == "3":
                                fragilidad = "baja"
                                indiceFragilidad = 0.95
                                break
                            else:
                                print("Opción no válida. Intente nuevamente.\n")

                        peso: float = 0
                        while True:
                            Peso = input(
                                "\nIngrese el peso del paquete en kilos: "
                            ).strip()
                            if Peso.isdigit():
                                peso = float(Peso)
                                break
                            else:
                                print("Por favor, ingrese un valor numérico válido.\n")

                        descripcion = input(
                            "\nAgregue una breve descripción del paquete: "
                        ).strip()

                        origen: str = self.escogerCiudad("origen")
                        destino: str = self.escogerCiudad("destino")

                        distancia: float = self.calcularDistancia(origen, destino)
                        if distancia < 1:
                            print(
                                "\nSu envío es local. Para conocer el precio exacto habría que especificar la zona."
                            )
                            precio = (peso * 2) * indiceFragilidad * 1000
                        else:
                            precio: float = (
                                distancia / 2 * (peso**1.2) * indiceFragilidad
                            )
                            print(
                                f"\nEl costo aproximado del envío es: COP {round(precio, 2)}"
                            )

                        tipo = (
                            input("\n¿El paquete es express? (s/n): ").strip().lower()
                        )
                        if tipo == "s":
                            Paquete = paquete_express(
                                len(self.__paquetes) + 1,
                                float(peso),
                                tamaño,
                                fragilidad,
                                descripcion,
                                origen,
                                destino,
                                int(seleccion),
                                precio,
                                recargo=0.25,
                            )
                        else:
                            Paquete = paquete(
                                len(self.__paquetes) + 1,
                                float(peso),
                                tamaño,
                                fragilidad,
                                descripcion,
                                origen,
                                destino,
                                int(seleccion),
                                precio,
                            )

                        cliente_seleccionado.registrarPaquete(Paquete)
                        self.__paquetes.append(Paquete)

                        print("\n=== RESUMEN DEL PAQUETE ===")
                        print(
                            f"ID: {Paquete.getId()} | Cliente: {cliente_seleccionado.getNombre()} {cliente_seleccionado.getApellido()}"
                        )
                        print(
                            f"Tamaño: {tamaño} | Fragilidad: {fragilidad} | Peso: {peso} kg"
                        )
                        print(f"Origen: {origen} -> Destino: {destino}")

                        precio_base = Paquete.getPrecioEnvio()
                        recargo_express = 0
                        precio_con_recargo = precio_base

                        if isinstance(Paquete, paquete_express):
                            recargo_express = Paquete.calcularExpress() - precio_base
                            precio_con_recargo = Paquete.calcularExpress()

                        descuento = cliente_seleccionado.descuentoVIP(
                            precio_con_recargo
                        )

                        precio_final = precio_con_recargo - descuento

                        print("\n=== RESUMEN DEL PRECIO ===")
                        print(f"Precio base: COP {round(precio_base, 2)}")

                        if recargo_express > 0:
                            print(f"Recargo Express: COP {round(recargo_express, 2)}")

                        if descuento > 0:
                            print(f"Descuento VIP: COP {round(descuento, 2)}")

                        print(f"Precio final estimado: COP {round(precio_final, 2)}")
                        print("=============================\n")
                        break

    def buscarPorId(self, id: int) -> cliente | None:
        for cliente in self.__clientes:
            if cliente.getId() == id:
                return cliente
        return None

    def rastrearPaquete(self) -> None:
        print("\n=== RASTREO DE PAQUETE ===\n")
        if not self.__paquetes:
            print("No hay paquetes registrados para rastrear.\n")
            return

        id_paquete = input("Ingrese el ID del paquete a rastrear: ").strip()
        if not id_paquete.isdigit():
            print("ID inválido. Debe ser un número.\n")
            return
        id_paquete = int(id_paquete)

        for paquete in self.__paquetes:
            if paquete.getId() == id_paquete:
                print("\n=== INFORMACIÓN DEL PAQUETE ===")
                print(f"ID:            {paquete.getId()}")
                print(f"Descripción:   {paquete.getDescripcion()}")
                print(f"Tamaño:        {paquete.getTamaño()}")
                print(f"Fragilidad:    {paquete.getFragilidad()}")
                print(f"Peso:          {paquete.getPeso()} kg")
                print(f"Origen:        {paquete.getOrigen()}")
                print(f"Destino:       {paquete.getDestino()}")
                print(f"Estado:        {paquete.getEstado()}")

                cliente_id = paquete.getId_propietario()
                cliente = self.buscarPorId(cliente_id)
                if cliente:
                    print("\n=== INFORMACIÓN DEL CLIENTE ===")
                    print(f"ID:            {cliente.getId()}")
                    print(
                        f"Nombre:        {cliente.getNombre()} {cliente.getApellido()}"
                    )
                    print(f"Teléfono:      {cliente.getTelefono()}")
                    print(f"Correo:        {cliente.getCorreo()}")

                    print("\n=== DETALLE DE COSTOS ===")
                    precio_base: float = paquete.getPrecioEnvio()
                    precio_con_recargo: float = paquete.calcularExpress()
                    recargo: float = precio_con_recargo - precio_base
                    descuento: float = cliente.descuentoVIP(precio_con_recargo)
                    precio_total = precio_con_recargo - descuento

                    print(f"Precio base:   COP {round(precio_base, 2)}")
                    if recargo > 0:
                        print(f"Recargo Expr.: COP {round(recargo, 2)}")
                    if descuento > 0:
                        print(f"Descuento VIP: COP {round(descuento, 2)}")
                    print(f"-------------------------------")
                    print(f"PRECIO TOTAL:  COP {round(precio_total, 2)}")

                print("===============================\n")
                return

        print(f"No se encontró ningún paquete con ID {id_paquete}.\n")

    def calcularPrecioEnvio(self) -> None:
        print("\n=== CALCULAR COSTO DE ENVIO ===\n")
        while True:
            peso_str: str = input("Ingrese el peso del paquete en kilos: ").strip()
            if peso_str.isdigit():
                peso: float = float(peso_str)
                break
            else:
                print("Por favor ingrese un valor numérico válido.\n")

        fragilidad_factor: float = 1.0
        while True:
            print("\nSeleccione el nivel de fragilidad del paquete:")
            print("  1. Alta   (recargo 10%)")
            print("  2. Normal (sin recargo)")
            print("  3. Baja   (descuento 5%)")
            opcion: str = input("Opción: ").strip()

            if opcion == "1":
                fragilidad_factor = 1.1
                fragilidad_txt = "Alta"
                break
            elif opcion == "2":
                fragilidad_factor = 1.0
                fragilidad_txt = "Normal"
                break
            elif opcion == "3":
                fragilidad_factor = 0.95
                fragilidad_txt = "Baja"
                break
            else:
                print("Opción inválida. Intente de nuevo.\n")

        ciudad_origen: str = self.escogerCiudad("origen")
        ciudad_destino: str = self.escogerCiudad("destino")
        distancia: float = self.calcularDistancia(ciudad_origen, ciudad_destino)

        if distancia < 1:
            print("\n=== ENVÍO LOCAL ===")
            print("El precio exacto puede variar según la zona.")
            precio = (peso * 2) * fragilidad_factor * 1000
        else:
            precio: float = distancia / 2 * (peso**1.2) * fragilidad_factor

        print("\n=== RESUMEN DEL ENVÍO ===")
        print(f"Peso:         {peso} kg")
        print(f"Fragilidad:   {fragilidad_txt} (factor {fragilidad_factor})")
        print(f"Origen:       {ciudad_origen}")
        print(f"Destino:      {ciudad_destino}")
        print(f"Distancia:    {round(distancia, 2)} km")
        print("----------------------------")
        print(f"Precio estimado: COP {round(precio, 2)}\n")

    def buscarPaquete(self) -> None:
        print("\n=== BUSCAR PAQUETES ===")
        print("1. Listar todos")
        print("2. Buscar por ID de cliente")
        print("3. Buscar por estado")
        print("4. Buscar por ID de paquete")
        opcion: str = input("Selecciona una opción: ").strip()

        if opcion == "1":
            self.listarPaquetes()
        elif opcion == "2":
            id_cliente: str = input("Ingresa el ID del cliente: ").strip()
            if id_cliente.isdigit():
                self.listarPaquetes(id_cliente=int(id_cliente))
            else:
                print("ID inválido\n")
        elif opcion == "3":
            estado: str = (
                input(
                    "Ingresa el estado (Registrado, En transito, Entregado, Enviado): "
                )
                .strip()
                .title()
            )
            self.listarPaquetes(estado=estado)
        elif opcion == "4":
            id_paquete: str = input("Ingresa el ID del paquete: ").strip()
            if id_paquete.isdigit():
                self.listarPaquetes(id_paquete=int(id_paquete))
            else:
                print("ID inválido\n")
        else:
            print("Opción no válida\n")

    def escogerCiudad(self, tipo: str) -> str:
        while True:
            print(f"\n=== Selección de ciudad de {tipo.upper()} === \n")
            ciudades: list = list(self.__ciudades.keys())

            columnas: int = 3
            ancho: int = 20

            for i in range(0, len(ciudades), columnas):
                fila: str = ""
                for j in range(columnas):
                    if i + j < len(ciudades):
                        num: int = i + j + 1
                        nombre: str = ciudades[i + j]
                        fila += f"{num}. {nombre}".ljust(ancho)
                print(fila)

            seleccion = input("\nIngrese el número de la ciudad: ").strip()

            if seleccion.isdigit():
                indice = int(seleccion) - 1
                if 0 <= indice < len(ciudades):
                    return ciudades[indice]

            print("Selección inválida. Intente nuevamente.\n")

    def buscarCiudad(self, ciudad: str) -> bool:
        nombreNormalizado = ciudad.strip()
        return nombreNormalizado in self.__ciudades

    def calcularDistancia(self, origen: str, destino: str) -> float:
        ciudad1: tuple = self.__ciudades[origen]
        ciudad2: tuple = self.__ciudades[destino]

        R: float = 6371.0

        lat1: float = 0
        lat2: float = 0
        lon1: float = 0
        lon2: float = 0
        alt1: float = 0
        alt2: float = 0

        lat1, lon1, alt1 = ciudad1
        lat2, lon2, alt2 = ciudad2

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        r1: float = R + alt1 / 1000.0
        r2: float = R + alt2 / 1000.0

        x1: float = r1 * math.cos(lat1) * math.cos(lon1)
        y1: float = r1 * math.cos(lat1) * math.sin(lon1)
        z1: float = r1 * math.sin(lat1)

        x2: float = r2 * math.cos(lat2) * math.cos(lon2)
        y2: float = r2 * math.cos(lat2) * math.sin(lon2)
        z2: float = r2 * math.sin(lat2)

        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    def listarPaquetes(
        self, id_cliente: int = None, estado: str = None, id_paquete: int = None
    ) -> None:
        print("\n=== LISTADO DE PAQUETES REGISTRADOS ===\n")

        if not self.__paquetes:
            print("=== No hay paquetes registrados ===\n")
            return

        if id_paquete is not None:
            paquete = next(
                (p for p in self.__paquetes if p.getId() == id_paquete), None
            )
            if not paquete:
                print("Paquete no encontrado\n")
                return
            self._imprimirPaquete(paquete)
            return

        if id_cliente is not None:
            cliente = self.buscarPorId(id_cliente)
            if not cliente:
                print("Cliente no encontrado\n")
                return
            print(
                f"Dueño: {cliente.getId()} - {cliente.getNombre()} {cliente.getApellido()}\n"
            )
            for p in cliente.getPaquetes():
                self._imprimirPaquete(p)
            return

        if estado is not None:
            encontrados = [
                p
                for p in self.__paquetes
                if p.getEstado().lower() == estado.strip().lower()
            ]
            if not encontrados:
                print(f"No hay paquetes con estado '{estado}'\n")
                return
            for p in encontrados:
                self._imprimirPaquete(p)
            return

        for p in self.__paquetes:
            cliente = self.buscarPorId(p.getId_propietario())
            if cliente:
                dueño = (
                    f"{cliente.getId()} - {cliente.getNombre()} {cliente.getApellido()}"
                )
            else:
                dueño = f"{p.getId_propietario()} (Cliente no encontrado)"
            print(f"Dueño        : {dueño}")
            self._imprimirPaquete(p)

    def _imprimirPaquete(self, p):
        """Método auxiliar para imprimir la info de un paquete."""
        print("--------------------------------------------")
        print(f"ID Paquete   : {p.getId()}")
        print(f"Origen       : {p.getOrigen()}")
        print(f"Destino      : {p.getDestino()}")
        print(f"Peso         : {p.getPeso()} kg")
        print(f"Tamaño       : {p.getTamaño()}")
        print(f"Fragilidad   : {p.getFragilidad()}")
        print(f"Estado       : {p.getEstado()}")
        print(f"Descripción  : {p.getDescripcion()}")
        print(f"Costo envío  : {round(p.calcularExpress(), 2)} COP")
        print("--------------------------------------------\n")

    def actualizarEstadoPaquete(self) -> None:
        print("\n=== ACTUALIZAR ESTADO DE PAQUETES ===")
        estados_validos: list = ["Registrado", "Enviado", "En transito", "Entregado"]

        # Mostrar listado de paquetes
        if len(self.__paquetes) == 0:
            print("\n No hay paquetes registrados \n")
            return

        self.listarPaquetes()

        # Seleccionar ID de paquete
        while True:
            id_input = input(
                "Selecciona el ID del paquete que deseas modificar: "
            ).strip()
            if id_input.isdigit():
                id_paquete = int(id_input)

                paquete = next(
                    (p for p in self.__paquetes if p.getId() == id_paquete), None
                )
                if paquete:
                    break

                else:
                    print("El ID no corresponde a ningún paquete. Intenta de nuevo.\n")
            else:

                print("Ingresa un número entero válido.\n")

        # Mostrar opciones de estado numeradas
        print("\n=== ESTADOS DISPONIBLES ===")
        for i, estado in enumerate(estados_validos, start=1):
            print(f"{i}. {estado}")

        # Seleccionar nuevo estado por número
        while True:
            opcion = input("Selecciona el número del nuevo estado: ").strip()
            if opcion.isdigit():
                indice = int(opcion) - 1
                if 0 <= indice < len(estados_validos):
                    nuevo_estado = estados_validos[indice]
                    break
            print("Opción inválida. Ingresa un número del 1 al 4.\n")

        # Actualizar estado
        paquete.setEstado(nuevo_estado)
        print("\n===================================")
        print(f"Estado del paquete {id_paquete} actualizado correctamente")
        print(f"Nuevo estado: {nuevo_estado}")
        print("===================================\n")
