class paquete:
    def __init__(self, id: int, peso: float, tamaño: str, fragilidad: str, descripcion: str, origen: str, destino: str, id_propietario:int):
        self.__id = id
        self.__id_propietario = id_propietario
        self.__peso = peso
        self.__tamaño = tamaño
        self.__fragilidad = fragilidad
        self.__descripcion = descripcion
        self.__origen = origen
        self.__destino = destino
        self.__estado = "Registrado"

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
    
    def setOrigen(self, origen: str):
        if origen.strip() != "":
            self.__origen = origen
        else:
            print("El origen no puede estar vacío.")

    def setDestino(self, destino: str):
        if destino.strip() != "":
            self.__destino = destino
        else:
            print("El destino no puede estar vacío.")

    def setPeso(self, peso: float):
        if peso > 0:
            self.__peso = peso
        else:
            print("El peso debe ser mayor que 0.")
  
    def setTamaño(self, tamaño:str):
        self.__tamaño = tamaño
 
    def setFragilidad(self, fragilidad:str):
        self.__fragilidad = fragilidad
    
    def setDescripcion(self, descripcion: str):
        self.__descripcion = descripcion

    def setEstado(self, estado: str):
        estados_validos = ["Registrado", "En tránsito", "Entregado"]
        if estado in estados_validos:
            self.__estado = estado
        else:
             print("Estado inválido.")
             
    # Creo que hacer el set de id_propietario no es considerable