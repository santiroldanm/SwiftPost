import math
from src.cliente import cliente 
from src.paquete import paquete 

class servicioMensajeria:
  def __init__(self):

    self.paquetes = []
    self.clientes = []
    self.ciudades =  {
    # Colombia
    "Bogota":      (4.711,   -74.072, 2582),
    "Medellin":    (6.244,   -75.581, 1495),
    "Cali":        (3.452,   -76.532, 1018),
    "Cartagena":   (10.391,  -75.479, 2),
    "Barranquilla":(10.991,  -74.788, 10),
    "Santa marta": (11.241,  -74.199, 0),
    "Bucaramanga": (7.120,   -73.123, 960),
    "Cúcuta":      (7.889,   -72.496, 320),
    "Pereira":     (4.815,   -75.695, 1411),
    "Manizales":   (5.069,   -75.517, 2150),
    "Pasto":       (1.216,   -77.281, 2527),
    "Ibague":      (4.439,   -75.232, 1285),
    "Villavicencio":(4.142,  -73.626, 467),
    "Armenia":     (4.534,   -75.681, 1480),
      
        # Mundo
    "Nueva York":     (40.713,  -74.006, 10),
    "Paris":          (48.857,   2.352, 35),
    "Londres":        (51.507,   -0.128, 11),
    "Tokio":          (35.690,  139.692, 40),
    "Sídney":        (-33.869, 151.209, 58),
    "Roma":           (41.903,   12.496, 21),
    "Berlin":         (52.520,   13.405, 34),
    "Dubái":          (25.277,   55.296, -2),
    "Pekin":          (39.904,  116.407, 44),
    "Moscu":          (55.756,   37.617, 156),
    "Ciudad de mexico":(19.433, -99.133, 2240),
    "Buenos aires":   (-34.604, -58.382, 25),
    "Toronto":        (43.653,  -79.383, 76),
    "Estambul":       (41.008,   28.978, 39),
    "Johannesburgo":  (-26.204,  28.047, 1753),

    }
    

    
  def crearCliente(self) -> None:

    nombre = str(input("¿Cual es tu nombre? \n"))
    apellido = str(input("¿Cual es tu apellido ? \n"))
    while(True):
      telefono: str = (input("Cual es tu numero telefonico \n"))
      if(not telefono.isdigit()):
        print("telefono no valido, ingresa un valor numerico \n")
      else: break

    correo: str = ""
    while(True):
      correo = input("Cual es tu correo electronico  \n")
      if correo and "@" in correo and "." in correo:
        break
      else:
        print("Correo no válido \n")   
      
    Cliente = cliente(len(self.clientes)+1, nombre, apellido, "", telefono, correo)
    self.clientes.append(Cliente)
    print("REGISTRO EXITOSO \n")
  
  
  
  def crearPaquete(self) -> str:
    if(len(self.clientes) == 0):
      print ("No hay clientes registrados \n")
      return
    else:
      ids = [cliente.getId() for cliente in self.clientes]
    
      while(True): 
        print("Clientes registrados:")
        for cliente in self.clientes:
            print(f"ID {cliente.getId()} nombre: {cliente.getNombre()} {cliente.getApellido()} \n ")
        
        seleccion = input("Seleccione uno por su ID \n").strip()
        
        if seleccion.isdigit() and int(seleccion) in ids:
            cliente_seleccionado = None
            for cliente in self.clientes:
                if cliente.getId() == int(seleccion):
                    cliente_seleccionado = cliente
                    break
            if cliente_seleccionado:
                # Aquí continuas con la lógica para registrar el paquete
                
                tamaño:str = ""
                while(True):
                    opcion = input("¿Cual es el tamaño de tu paquete? \n  Selecciona una opcion: \n 1. Pequeño: máximo del tamaño de una caja grande de cereales \n 2. Normal: máximo del tamaño de un televisor pequeño \n 3. Grande: Digamos un televisor de 50 pulgadas y máximo del tamaño de una lavadora pequeña \n 4. Muy grande \n").strip()
                    if  opcion == "1":
                        tamaño = "pequeño"
                        break
                    elif  opcion == "2":   
                        tamaño = "mediano"
                        break
                    elif  opcion == "3":
                        tamaño = "grande"
                        break
                    elif  opcion == "4": 
                        tamaño = "gigante"
                        break
                    else:
                        print("Escoja una opcion valida \n")
                
                fragilidad: str = ""
                indiceFragilidad: int = 0
                while(True):
                    opcion = input("¿Cual es la fragilidad de tu paquete? \n  Selecciona una opcion: \n 1. Alta \n 2. Normal \n 3. Baja \n")
                    if opcion == "1":
                        fragilidad = "alta"
                        indiceFragilidad = 1.05
                        break
                    elif  opcion == "2":   
                        fragilidad = "normal"
                        indiceFragilidad = 1
                        break
                    elif  opcion == "3":
                        fragilidad = "baja"
                        indiceFragilidad = 0.95
                        break
                    else:
                        print ("Escoja una opcion valida \n") 
                
                peso: int = 0
                while(True):
                    Peso = input ("Ingrese el peso del paquete en kilos \n")
                    if(Peso.isnumeric()):
                        peso = int(Peso)
                        break
                    else:
                        print("Por favor, ingrese un valor numérico válido.")
                
                descripcion = str(input("Agrega una breve descripcion del paquete: \n"))
                origen: str = self.escogerCiudad("origen")
                destino: str = self.escogerCiudad("destino")
                distancia: float = self.calcularDistancia(origen, destino)
                
                if(distancia < 1):
                    print("Su envio es local por lo que para conocer el precio exacto habría que especificar la zona :( \n")
                    precio = peso * indiceFragilidad * 10000
                else:
                    precio: float = distancia / 2 * peso * indiceFragilidad
                    print(f"El costo de su envio sería de mas o menos en cop {round(precio, 2)} \n")
                
                Paquete = paquete(len(self.paquetes)+1, float(peso), tamaño, fragilidad, descripcion, origen, destino, int(seleccion), precio)
                cliente_seleccionado.registrarPaquete(Paquete)
                self.paquetes.append(Paquete)
                print(" REGISTRO EXITOSO \n")
                
                # Este break rompe el while(True) principal, terminando la función
                break
        else:
            print("No has seleccionado una opción válida \n")
          
    
  def buscarPorId(self,id:int) -> list:
    for cliente in self.clientes:
      if cliente.getId() == id:
        return cliente
    
  def rastrearPaquete(self):
     if not self.paquetes:
      print("No hay paquetes registrados para rastrear")
      return

     id_paquete = input("Ingrese el ID del paquete a rastrear: ").strip()
     if not id_paquete.isdigit():
        print("ID inválido, debe ser un número.")
        return
     id_paquete = int(id_paquete)
    
     for paquete in self.paquetes:
      if paquete.getId() == id_paquete:
        print("Información del paquete:")
        print(f"ID: {paquete.getId()}")
        print(f"Descripción: {paquete.getDescripcion()}")
        print(f"Tamaño: {paquete.getTamaño()}")
        print(f"Fragilidad: {paquete.getFragilidad()}")
        print(f"Peso: {paquete.getPeso()} kg")
        print(f"Origen: {paquete.getOrigen()}")
        print(f"Destino: {paquete.getDestino()}")
        print(f"Estado: {paquete.getEstado()}")
        print(f"Costo de Envío: {paquete.getPrecioEnvio()}")
      
      # Buscar el cliente dueño del paquete
      cliente_id = paquete.getId_propietario()
      cliente = self.buscarPorId(cliente_id)
      if cliente:
          print("Cliente remitente:")
          print(f"ID: {cliente.getId()} - {cliente.getNombre()} {cliente.getApellido()}")
          print(f"Teléfono: {cliente.getTelefono()}")
          print(f"Correo: {cliente.getCorreo()}")
      return

     print(f"No se encontró ningún paquete con ID {id_paquete}.")
  
  def calcularPrecioEnvio(self) -> None:
    peso: int = 0
    while(True):
      Peso = input ("Ingrese el peso del paquete en kilos \n")
      if(Peso.isnumeric):
        peso = int(Peso)
        break
    while(True):
      opcion = input("¿Cual es la fragilidad de tu paquete? \n  Selecciona una opcion: \n 1. Alta \n 2. Normal \n 3. Baja \n")
      if opcion == "1":
        fragilidad = 1.1
        break
      elif  opcion == "2":   
        fragilidad = 1
        break
      elif  opcion == "3":
        fragilidad = 0.95 
        break
      else:
        print ("Escoja una opcion valida \n") 
    
    ciudadOrigen: str = self.escogerCiudad("origen")
    ciudadDestino: str = self.escogerCiudad("destino")
    distancia: float = self.calcularDistancia(ciudadOrigen, ciudadDestino)
    
    if(distancia < 1):
      print("Su envio es local por lo que para conocer el precio exacto habría que especificar la zona :( \n")
      precio = peso*fragilidad*10000
    else:
      precio: float = distancia/2*(peso)*fragilidad
      print(f"El costo de su envio sería de mas o menos en cop{round(precio, 2)} \n")
      

  def escogerCiudad(self, tipo: str):
    caso:str = "Selecciona tu ciudad de "+tipo
    while(True):
      print(caso+ "\n")
      for nombre in self.ciudades.keys():
        print("-"+nombre+"\n")
      seleccion:str = input(caso+"\n").title()
      ciudad = self.buscarCiudad(seleccion)
      if (ciudad):
        return seleccion.strip()        
      caso = "No seleccionaste correctamente \n"
  
  def buscarCiudad(self, ciudad: str) -> bool:
    nombreNormalizado = ciudad.strip()
    return nombreNormalizado in self.ciudades      
 
  def calcularDistancia(self, origen: str, destino: str) -> float:
    ciudad1 = self.ciudades[origen]
    ciudad2 = self.ciudades[destino]

    R = 6371.0  # radio de la Tierra en km
    lat1, lon1, alt1 = ciudad1
    lat2, lon2, alt2 = ciudad2

    # Pasar a radianes
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Radio desde el centro de la Tierra hasta la ciudad (km)
    r1 = R + alt1 / 1000.0
    r2 = R + alt2 / 1000.0

    # Coordenadas cartesianas
    x1 = r1 * math.cos(lat1) * math.cos(lon1)
    y1 = r1 * math.cos(lat1) * math.sin(lon1)
    z1 = r1 * math.sin(lat1)

    x2 = r2 * math.cos(lat2) * math.cos(lon2)
    y2 = r2 * math.cos(lat2) * math.sin(lon2)
    z2 = r2 * math.sin(lat2)

    # Distancia Euclidiana
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
  
  def listarPaquetes(self):
    if(len(self.paquetes)==0):
      print("No hay paquetes registrados \n")
    for i in self.paquetes:
     print(f" ---- Id: {i.getId()} Id_dueño: {i.getId_propietario()} Origen: {i.getOrigen()} Destino: {i.getDestino()} Peso: {i.getPeso()} Estado: {i.getEstado()} Descripcion: {i.getDescripcion()} \n")

  def actualizarEstadoPaquete(self):
    estados_validos = ["Registrado", "En transito", "Entregado", "Enviado"]
    self.listarPaquetes()
    
    # Seleccionar ID válido
    while True:
        id_input = input("Selecciona el id del paquete que quiere modificar: ").strip()
        
        if id_input.isdigit():
            id_paquete = int(id_input)
            
            # Verifica que el ID exista entre los paquetes
            existe = any(paquete.getId() == id_paquete for paquete in self.paquetes)
            if existe:
                break  # ID válido, salimos del bucle
            else:
                print("Seleccionaste un ID que no existe. Intenta de nuevo.\n")
        else:
            print("Debes ingresar un número entero válido.\n")
    
    # Mostrar estados válidos
    print("Estados permitidos:\n")
    for estado in estados_validos:
        print(f"- {estado} \n")
    
    # Seleccionar nuevo estado
    nuevo_estado = input("¿A cuál estado se actualizó el envío? \n").strip().title()
    
    if nuevo_estado not in estados_validos:
        print("Estado no válido. Los estados permitidos son: Registrado, En transito, Entregado, Enviado \n")
        return

    for paquete in self.paquetes:
        if paquete.getId() == id_paquete:
            paquete.setEstado(nuevo_estado)  # se usa el setter en paquete.py
            print(f"Estado del paquete {id_paquete} actualizado a: {nuevo_estado}\n")
            return
    
    print(f"No se encontró ningún paquete con ID {id_paquete} \n")


