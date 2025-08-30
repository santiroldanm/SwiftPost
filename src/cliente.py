class cliente:
    def __init__(self, id: int, nombre: str, apellido: str, direccion: str, telefono: int, correo: str):
        self.__id = id
        self.__apellido = apellido
        self.__nombre = nombre
        self.__direccion = direccion
        self.__telefono = telefono
        self.__correo = correo
        self.__paquetes: list[object] = []

    # Getters
    def getId(self)-> id: 
        return self.__id

    def getNombre(self)-> str: 
        return self.__nombre
    
    def getApellido(self)-> str: 
        return self.__apellido
    
    def getDireccion(self)-> str:
        return self.__direccion

    def getTelefono(self) -> int:
        return self.__telefono

    def getCorreo(self)-> str:
        return self.__correo

    def getPaquetes(self)-> list[object]:
        return self.__paquetes

    def setNombre(self, nombre: str)-> None:
        if nombre.strip()!= "" and len(nombre) > 0:
            self.__nombre = nombre

    def setTelefono(self, telefono: str)-> None:
        if telefono.isdigit():
            self.__telefono = telefono

    def setCorreo(self, correo: str) -> None:
        if correo and "@" in correo and "." in correo: #VALIDACIÓN BÁSICA
            self.__correo = correo
        else:
            print("Correo no válido.")

    def registrarPaquete(self, paquete) -> None:
        self.__paquetes.append(paquete)

    def verHistorial(self) -> list[object]:
        return self.__paquetes
    
    def descuentoVIP(self, precio_base:float) -> int: # PRECIO BASE???
        return 0

class cliente_vip(cliente):
    def __init__(self, id:int, nombre:str, apellido:str, direccion:str, telefono:int, correo:str, nivel: str = "VIP", descuento:float=0.1):
        super().__init__(id, nombre, apellido, direccion, telefono, correo)
        self.__nivel = nivel
        self.descuento = descuento  # 10% por defecto

    def getNivel(self) -> str:
        return self.__nivel
        
    # Polimorfismo: mismo nombre de método, diferente comportamiento
    def descuentoVIP(self, precio_base:float) -> float:
        return precio_base * self.descuento