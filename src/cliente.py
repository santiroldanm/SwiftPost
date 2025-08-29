class cliente:
    def __init__(self, id: int, nombre: str, apellido: str, direccion: str, telefono: str, correo: str):
        self.__id = id
        self.__apellido = apellido
        self.__nombre = nombre
        self.__direccion = direccion
        self.__telefono = telefono
        self.__correo = correo
        self.__paquetes = []

    # Getters
    def getId(self): 
        return self.__id

    def getNombre(self): 
        return self.__nombre
    
    def getApellido(self): 
        return self.__apellido
    
    def getDireccion(self): 
        return self.__direccion

    def getTelefono(self): 
        return self.__telefono

    def getCorreo(self):
        return self.__correo

    def getPaquetes(self): 
        return self.__paquetes

    def setNombre(self, nombre: str):
        if nombre.strip()!= "" and len(nombre) > 0:
            self.__nombre = nombre

    def setTelefono(self, telefono: str):
        if telefono.isdigit():
            self.__telefono = telefono

    def setCorreo(self, correo: str):
        if correo and "@" in correo and "." in correo: #VALIDACIÓN BÁSICA
            self.__correo = correo
        else:
            print("Correo no válido.")

    def registrarPaquete(self, paquete):
        self.__paquetes.append(paquete)

    def verHistorial(self):
        return self.__paquetes
    
    def descuentoVIP(self, precio_base):
        return 0

class cliente_vip(cliente):
    def __init__(self, id, nombre, apellido, direccion, telefono, correo, nivel: str = "VIP", descuento=0.1):
        super().__init__(id, nombre, apellido, direccion, telefono, correo)
        self.__nivel = nivel
        self.descuento = descuento  # 10% por defecto

    def getNivel(self) -> str:
        return self.__nivel
        
    # Polimorfismo: mismo nombre de método, diferente comportamiento
    def descuentoVIP(self, precio_base):
        return precio_base * self.descuento