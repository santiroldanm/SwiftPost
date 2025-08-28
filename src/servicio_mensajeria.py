import math
from src.cliente import cliente 
from src.paquete import paquete 


class servicioMensajeria:
 def __init__(self):
    self.paquetes = []
    self.clientes = []
    self.ciudades =  {
    # Colombia
    "Bogotá":      (4.711,   -74.072, 2582),
    "Medellín":    (6.244,   -75.581, 1495),
    "Cali":        (3.452,   -76.532, 1018),
    "Cartagena":   (10.391,  -75.479, 2),
    "Barranquilla":(10.991,  -74.788, 10),
    "Santa Marta": (11.241,  -74.199, 0),
    "Bucaramanga": (7.120,   -73.123, 960),
    "Cúcuta":      (7.889,   -72.496, 320),
    "Pereira":     (4.815,   -75.695, 1411),
    "Manizales":   (5.069,   -75.517, 2150),
    "Pasto":       (1.216,   -77.281, 2527),
    "Ibagué":      (4.439,   -75.232, 1285),
    "Villavicencio":(4.142,  -73.626, 467),
    "Armenia":     (4.534,   -75.681, 1480),
      
         # Mundo
    "Nueva York":     (40.713,  -74.006, 10),
    "París":          (48.857,   2.352, 35),
    "Londres":        (51.507,   -0.128, 11),
    "Tokio":          (35.690,  139.692, 40),
    "Sídney":        (-33.869, 151.209, 58),
    "Roma":           (41.903,   12.496, 21),
    "Berlín":         (52.520,   13.405, 34),
    "Dubái":          (25.277,   55.296, -2),
    "Pekín":          (39.904,  116.407, 44),
    "Moscú":          (55.756,   37.617, 156),
    "Ciudad de México":(19.433, -99.133, 2240),
    "Buenos Aires":   (-34.604, -58.382, 25),
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
        print("Correo no válido.")   
      
    Cliente = cliente(len(self.clientes)+1, nombre, apellido, "", telefono, correo)
    self.clientes.append(Cliente)
    print("REGISTRO EXITOSO \n")
  
  
  
def crearPaquete(self) -> str:
  if(len(self.clientes) == 0):
   print ("No hay clientes registrados")
   return
  else:
    ids=[]
    while(True): 
     for cliente in self.clientes:
      print(f"ID {cliente.getId()} nombre: {cliente.getNombre()} {cliente.getApellido()} \n ")
      ids.append(cliente.getId())
     seleccion = input("Seleccione uno por su ID \n").strip()
     if(seleccion.isdigit()):
      if int(seleccion) in ids:
       break
     else:
      print("No has seleccionado una opcion valida") 
      ids.clear
      
  
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
  while(True):
    opcion = input("¿Cual es la fragilidad de tu paquete? \n  Selecciona una opcion: \n 1. Alta \n 2. Normal \n 3. Baja \n")
    if opcion == "1":
     fragilidad = "alta"
     break
    elif  opcion == "2":   
     fragilidad = "normal"
     break
    elif  opcion == "3":
      fragilidad = "baja"
      break
    else:
      print ("Escoja una opcion valida \n") 
              
  while(True):
    peso = (input("¿Cual es el peso de tu paquete en kilos? \n"))
    if(not peso.isnumeric):
      print("Peso no valido, ingresa un valor numerico \n ")
    else: break
    
  descripcion = str(input("Agrega una breve descripcion del paquete: \n"))
  origen: str = escogerCiudad("origen")
  destino: str = escogerCiudad("destino")
  distancia: float = calcularDistancia(origen, destino)
  precio: int = distancia/2*(peso*2000)*fragilidad

  Paquete = paquete(len(self.clientes)+1, float(peso), tamaño, fragilidad, descripcion, origen, destino, int(seleccion), precio)  
  cliente.registrarPaquete(Paquete)
  self.paquetes.append(Paquete)
  print(" REGISTRO EXITOSO \n")
  
  
  def buscarPorId(self,id:int) -> list:
    for cliente in self.clientes:
      if cliente.id == id:
       return cliente
    
  
  def calcularPrecioEnvio() -> str:
    peso: int = 0
    while(True):
     Peso =input ("Ingrese el peso del paquete en kilos \n")
     if(peso.isnumeric):
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
     
     ciudadOrigen: str = escogerCiudad("origen")
     ciudadDestino: str = escogerCiudad("destino")
     distancia: float = calcularDistancia(ciudadOrigen, ciudadDestino)
     
     
     precio = distancia/2*(peso*2000)*fragilidad
     print(f"El costo de su envio sería de {precio} \n") 
  
  def escogerCiudad(self, tipo: str):
      while(True):
        print(caso)
        if(tipo==1):
         for nombre in self.ciudades.keys():
          print(nombre+"\n")
         seleccion = input(f"Selecciona tu ciudad de {tipo} \n")
         ciudad = buscarCiudad(seleccion)
         if (ciudad):
           return seleccion.strip()        
        else:
          for nombre in self.ciudades.keys():
           print(nombre+"\n")
          seleccion = input(f"Selecciona tu ciudad de {tipo} \n")
          ciudad = buscarCiudad(seleccion)
          if (ciudad):
           return seleccion.strip()
        caso = "No seleccionaste correctamente \n"
  
  def buscarCiudad(self, ciudad: str) -> bool:
    nombre_normalizado = ciudad.strip().title()
    return nombre_normalizado in self.ciudades      
 
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
   for i in self.paquetes:
    print(f" Id: {i.getId()} Id_dueño: {i.getId_propietario()} Origen: {i.getOrigen()} Destino:{i.getDestino()} Peso: {i.getPeso()} Estado: {i.getEstado()} Descripcion: {i.getDescripcion()} \n")