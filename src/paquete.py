class Paquete:
    def __init__(self, id: int, origen: str, destino: str, peso: float):
        self.__id = id
        self.__origen = origen
        self.__destino = destino
        self.__peso = peso
        self.__estado = "Registrado" #REGISTRADO, EN TRÁNSITO, EN OFICINA DESTINO, EN ENTREGA, ENTREGADO, DEVUELTO

    # GETTERS Y SETTERS (ENCAPSULAMIENTO)
    def getId(self): 
        return self.__id

    def getOrigen(self):
        return self.__origen
    
    def getDestino(self):
        return self.__destino
    
    def getPeso(self):
        return self.__peso

    def getEstado(self): 
        return self.__estado

    def setId(self, id: int):
        #GENERAMOS ID RANDOM
    
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

    #FALTA HACER EL SET ESTADO, LA OPCIÓN 6 DEL MENÚ