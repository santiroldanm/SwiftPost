 
class paquete:
    def __init__(self, id: int, peso: float, tamaño: str, fragilidad: str, descripcion: str, origen: str, destino: str, id_propietario:int, precioEnvio: int):
        self.__id = id
        self.__id_propietario = id_propietario
        self.__peso = peso
        self.__tamaño = tamaño
        self.__fragilidad = fragilidad
        self.__descripcion = descripcion
        self.__origen = origen
        self.__destino = destino
        self.__estado = "Registrado"
        self.__precioEnvio = precioEnvio
    # GETTERS Y SETTERS (ENCAPSULAMIENTO)
    def getId(self)-> (int): 
        return self.__id
    
    def getId_propietario(self)-> (int): 
        return self.__id_propietario

    def getOrigen(self) -> (str):
        return self.__origen
    
    def getDestino(self) -> (str):
        return self.__destino
    
    def getPeso(self) -> (int):
        return self.__peso

    def getEstado(self) -> (str):
        return self.__estado
    
    def getTamaño(self) -> (str):
        return self.__tamaño
    
    def getFragilidad(self) -> (str):
        return self.__fragilidad
    
    def getDescripcion(self) -> (str):
        return self.__descripcion
    
    def getPrecioEnvio(self)-> (int): 
        return self.__precioEnvio
    
    def setOrigen(self, origen: str):
        if origen.strip() != "":
            self.__origen = origen
        else:
            print("El origen no puede estar vacío.")

    def setDestino(self, destino: str)-> None:
        if destino.strip() != "":
            self.__destino = destino
        else:
            print("El destino no puede estar vacío.")

    def setPeso(self, peso: float)-> None:
        if peso > 0:
            self.__peso = peso
        else:
            print("El peso debe ser mayor que 0.")
  
    def setTamaño(self, tamaño:str)-> None:
        self.__tamaño = tamaño
 
    def setFragilidad(self, fragilidad:str)-> None:
        self.__fragilidad = fragilidad
    
    def setEstado(self, estado: str)-> None:
        estados_validos = ["Registrado", "En transito", "Entregado", "Enviado"]
        if estado in estados_validos:
            self.__estado = estado
        else:
            print("Estado inválido \n")

    def setDescripcion(self, descripcion: str)-> None:
        self.__descripcion = descripcion

        
    def setPrecioEnvio(self, precioEnvio)-> None:
        self.__precioEnvio = precioEnvio
    # Creo que hacer el set de id_propietario no es considerable
    
    def calcularExpress(self)-> None:
        return self.getPrecioEnvio()

#Herencia
class paquete_express(paquete):
    def __init__(self, id: int, peso: float, tamaño: str, fragilidad: str, descripcion: str, origen: str, destino: str, id_propietario:int, precioEnvio: int, recargo: float = 0.0):
        super().__init__(id, peso, tamaño, fragilidad, descripcion, origen, destino, id_propietario, precioEnvio)
        self.recargo = recargo

    # Polimorfismo: redefine el cálculo de costo
    def calcularExpress(self):
        return self.getPrecioEnvio() * (1 + self.recargo)