from cliente import cliente 
from paquete import paquete 

class servicioMensajeria:
 def __init__(self):
    self.paquetes = []
    self.clientes = []
    
    
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
    if correo and "@" in correo and "." in correo: #VALIDACIÓN BÁSICA
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
  origen = str(input("Cual es la direccion de origen: \n"))
  destino = str(input("Cual es la direccion de destino: \n"))

  Paquete = paquete(len(self.clientes)+1, float(peso), tamaño, fragilidad, descripcion, origen, destino, int(seleccion))  
  cliente.registrarPaquete(Paquete)
  self.paquetes.append(Paquete)
  print(" REGISTRO EXITOSO \n")
  
  
  def buscarPorId(self,id:int) -> list:
    for cliente in self.clientes:
      if cliente.id == id:
       return cliente
            